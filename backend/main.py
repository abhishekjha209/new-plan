import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Import schemas, database, and models
import schemas
import models
import auth
import jwt  # exposes ExpiredSignatureError / InvalidTokenError for get_current_user
from database import engine, SessionLocal

# Create database tables if they do not exist
# In production, this is handled by database migrations (Alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Knowledge Platform API (PostgreSQL)")

# Retrieve allowed CORS origins from environment variables in production
# Supports comma-separated or semicolon-separated list: "https://my-frontend.vercel.app;http://localhost:3000"
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")

# Split by semicolon if present (avoids gcloud CLI comma-parsing issues), otherwise by comma
if ";" in allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(";")]
else:
    origins = [origin.strip() for origin in allowed_origins_env.split(",")]

# If "*" is in origins, we handle it safely by setting allow_origin_regex to match any origin
# This avoids browser-side CORS failures that occur when combining allow_credentials=True with allow_origins=["*"]
allow_all_origins = "*" in origins
if allow_all_origins:
    origins = []
    allow_origin_regex = ".*"
else:
    allow_origin_regex = None

# Give permission to the Next.js frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Session Dependency ---
#  We implement a generator function that yield-injects database connections:
def get_db():
    db = SessionLocal()
    try:
        yield db # providing an active database transaction
    finally:
        db.close()

# Security utility used to handle Bearer token authentication via the HTTP Authorization header.
# Performs Header Checks, Automatic Rejection & Extraction of the token.
# auto_error=False: we raise our own 401 (RFC 9110 wants 401 + WWW-Authenticate
# for missing credentials; Starlette's default would be 403).
security = HTTPBearer(auto_error=False)

# --- Dependency Injection for Auth ---
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:

    # 401, not 403: the request is UNAUTHENTICATED (no credentials at all).
    # 403 will mean "authenticated but not allowed" when we add roles on Day 9.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Verify signature AND expiry. jwt.decode raises on either failure.
    try:
        payload = auth.decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The 'sub' claim is our source of truth for WHO the token identifies.
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing a valid subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Signature proves the token is genuine, but the user may have been
    # deleted since it was issued - the database is still the final authority.
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# --- Authorization (Day 9): RBAC ---
# get_current_user answers WHO are you (401 if unknown).
# require_admin answers WHAT may you do (403 if known but not ADMIN).
# It DEPENDS ON get_current_user: FastAPI resolves the dependency chain
# per request, so require_admin only ever sees already-authenticated users.
# Design note: the role is read from the DB on every request, NOT from the JWT.
# A JWT claim would be stale until expiry (60 min) after a demotion; the DB is the authority.
def require_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# --- Health Route ---
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running on PostgreSQL!"}


# --- Auth Endpoints ---

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    email_lower = user_in.email.lower()
    
    # Query database to check for existing email
    existing_user = db.query(models.User).filter(models.User.email == email_lower).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = models.User(
        email=email_lower,
        name=user_in.name,
        password=auth.hash_password(user_in.password)  # bcrypt hash - plaintext is never persisted
    )
    
    db.add(new_user)     # 1. Register the object in SQLAlchemy session tracking
    db.commit()          # 2. Execute the SQL INSERT statement
    db.refresh(new_user) # 3. Reload the object from the DB, populating the id and server-set defaults (like created_at)
    
    return new_user


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    email_lower = credentials.email.lower()

    # Look up user in database
    user = db.query(models.User).filter(models.User.email == email_lower).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # bcrypt verify is deliberately slow (~100ms+). That cost is the defense
    # against offline brute force if the DB is ever stolen. Also: same vague
    # error message for unknown email vs wrong password - don't leak which
    # accounts exist.
    if not auth.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Issue a signed JWT. Server stores no session state; the token IS the session.
    token = auth.create_access_token(user.id)

    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# --- Admin Endpoints (Day 9) ---

@app.get("/admin/users", response_model=List[schemas.UserResponse])
def list_all_users(
    current_user: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # A normal user's queries filter by user_id (see list_documents).
    # An admin query has NO filter - that absence is the privilege.
    return db.query(models.User).all()


# --- Document Endpoints ---

@app.post("/documents", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    doc_in: schemas.DocumentCreate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_doc = models.Document(
        user_id=current_user.id,
        filename=doc_in.filename,
        content=doc_in.content
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return new_doc


@app.get("/documents", response_model=List[schemas.DocumentResponse])
def list_documents(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Document).filter(models.Document.user_id == current_user.id).all()


# --- Chat Endpoints ---

@app.post("/chat", response_model=schemas.ChatResponse)
def chat(
    chat_in: schemas.ChatRequest, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate the document exists and belongs to the user
    doc_id = chat_in.document_id
    doc = db.query(models.Document).filter(
        models.Document.id == doc_id, 
        models.Document.user_id == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    
    # 2. Get or create the conversation
    conv_id = chat_in.conversation_id
    if conv_id is not None:
        conv = db.query(models.Conversation).filter(
            models.Conversation.id == conv_id, 
            models.Conversation.user_id == current_user.id
        ).first()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conv_id} not found"
            )
    else:
        conv = models.Conversation(
            user_id=current_user.id,
            document_id=doc_id
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id
        
    # 3. Create user message
    user_msg = models.Message(
        conversation_id=conv_id,
        role="user",
        content=chat_in.message
    )
    db.add(user_msg)
    
    # 4. Generate mock AI response referencing the document's content
    snippet = doc.content[:80] + "..." if len(doc.content) > 80 else doc.content
    ai_content = (
        f"I've analyzed your document '{doc.filename}' (content preview: '{snippet}').\n\n"
        f"Regarding your query: \"{chat_in.message}\"\n\n"
        f"This is a placeholder response. In Phase 3, we will connect the backend to the "
        f"Gemini API to answer your questions using the real content of your uploaded documents!"
    )
    
    ai_msg = models.Message(
        conversation_id=conv_id,
        role="ai",
        content=ai_content
    )
    db.add(ai_msg)
    
    # Commit both messages at once
    db.commit()
    db.refresh(user_msg)
    db.refresh(ai_msg)
    
    return {
        "conversation_id": conv_id,
        "user_message": user_msg,
        "ai_response": ai_msg
    }
