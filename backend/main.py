from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Import schemas, database, and models
import schemas
import models
from database import engine, SessionLocal

# Create database tables if they do not exist
# In production, this is handled by database migrations (Alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Knowledge Platform API (PostgreSQL)")

# Give permission to the Next.js frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
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
# Performs Header Checks, Automatic Rejection & Extraction of the token
security = HTTPBearer()

# --- Dependency Injection for Auth ---
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> models.User:

    # credentials.credentials is the syntax used to extract the raw token string (like a JWT or API key) from an incoming HTTP request header
    token = credentials.credentials
    
    # Check if the token format matches our mock session token format
    # format: "mock-session-token-{user_id}"
    if not token.startswith("mock-session-token-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        user_id = int(token.split("-")[-1])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token structure",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Query PostgreSQL to see if this user actually exists in the database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user


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
        password=user_in.password # Day 8 will implement secure hashing
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
        
    # Verify plain text password (day 8 will implement bcrypt/argon2 hashing check)
    if user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate mock session token tied to the user's ID
    token = f"mock-session-token-{user.id}"
    
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


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
