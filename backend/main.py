from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import List, Dict, Any

# Import schemas from schemas.py
import schemas

app = FastAPI(title="AI Knowledge Platform API")

# Give permission to the Next.js frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Database (Day 5 Mock) ---
# In Day 6, these will be replaced with real PostgreSQL tables via SQLAlchemy
mock_db = {
    "users": {},         # user_id (int) -> dict
    "user_emails": {},   # email (str) -> user_id (int)
    "tokens": {},        # token (str) -> user_id (int)
    "documents": {},     # doc_id (int) -> dict
    "conversations": {}, # conv_id (int) -> dict
    "messages": {}       # msg_id (int) -> dict
}

security = HTTPBearer()

# --- Dependency Injection for Auth ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    user_id = mock_db["tokens"].get(token)
    
    if not user_id or user_id not in mock_db["users"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return mock_db["users"][user_id]


# --- Health Route ---
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running!"}


# --- Auth Endpoints ---

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserRegister):
    email_lower = user_in.email.lower()
    if email_lower in mock_db["user_emails"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_id = len(mock_db["users"]) + 1
    new_user = {
        "id": new_id,
        "email": email_lower,
        "name": user_in.name,
        "password": user_in.password, # Day 8 will implement secure hashing
        "created_at": datetime.now()
    }
    
    mock_db["users"][new_id] = new_user
    mock_db["user_emails"][email_lower] = new_id
    
    return new_user


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin):
    email_lower = credentials.email.lower()
    user_id = mock_db["user_emails"].get(email_lower)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    user = mock_db["users"][user_id]
    if user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate a simple mock token
    token = f"mock-session-token-{user_id}"
    mock_db["tokens"][token] = user_id
    
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserResponse)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user


# --- Document Endpoints ---

@app.post("/documents", response_model=schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(doc_in: schemas.DocumentCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    new_id = len(mock_db["documents"]) + 1
    now = datetime.now()
    
    new_doc = {
        "id": new_id,
        "user_id": current_user["id"],
        "filename": doc_in.filename,
        "content": doc_in.content,
        "created_at": now,
        "updated_at": now
    }
    
    mock_db["documents"][new_id] = new_doc
    return new_doc


@app.get("/documents", response_model=List[schemas.DocumentResponse])
def list_documents(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_docs = []
    for doc in mock_db["documents"].values():
        if doc["user_id"] == current_user["id"]:
            user_docs.append(doc)
    return user_docs


# --- Chat Endpoints ---

@app.post("/chat", response_model=schemas.ChatResponse)
def chat(chat_in: schemas.ChatRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    # 1. Validate the document exists and belongs to the user
    doc_id = chat_in.document_id
    doc = mock_db["documents"].get(doc_id)
    if not doc or doc["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    
    # 2. Get or create the conversation ID
    conv_id = chat_in.conversation_id
    if conv_id is not None:
        conv = mock_db["conversations"].get(conv_id)
        if not conv or conv["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conv_id} not found"
            )
    else:
        conv_id = len(mock_db["conversations"]) + 1
        mock_db["conversations"][conv_id] = {
            "id": conv_id,
            "user_id": current_user["id"],
            "document_id": doc_id,
            "created_at": datetime.now()
        }
        
    # 3. Create user message
    user_msg_id = len(mock_db["messages"]) + 1
    user_msg = {
        "id": user_msg_id,
        "conversation_id": conv_id,
        "role": "user",
        "content": chat_in.message,
        "created_at": datetime.now()
    }
    mock_db["messages"][user_msg_id] = user_msg
    
    # 4. Generate mock AI response referencing the document's content
    snippet = doc["content"][:80] + "..." if len(doc["content"]) > 80 else doc["content"]
    ai_content = (
        f"I've analyzed your document '{doc['filename']}' (content preview: '{snippet}').\n\n"
        f"Regarding your query: \"{chat_in.message}\"\n\n"
        f"This is a placeholder response. In Phase 3, we will connect the backend to the "
        f"Gemini API to answer your questions using the real content of your uploaded documents!"
    )
    
    ai_msg_id = len(mock_db["messages"]) + 1
    ai_msg = {
        "id": ai_msg_id,
        "conversation_id": conv_id,
        "role": "ai",
        "content": ai_content,
        "created_at": datetime.now()
    }
    mock_db["messages"][ai_msg_id] = ai_msg
    
    return {
        "conversation_id": conv_id,
        "user_message": user_msg,
        "ai_response": ai_msg
    }
