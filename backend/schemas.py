from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

# --- Configuration ---
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# --- Authentication Schemas ---

# Input for POST /auth/register
class UserRegister(BaseSchema):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

# Input for POST /auth/login
class UserLogin(BaseSchema):
    email: EmailStr
    password: str

# Output for user details (e.g., GET /users/me, and inside other responses)
class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    name: str
    role: str # Day 9: clients can see their own role (it is not a secret)
    created_at: datetime

# Output for login AND refresh (Day 10: two-token model)
class TokenResponse(BaseSchema):
    access_token: str   # short-lived JWT (15 min) - attached to every API call
    token_type: str = "bearer"
    refresh_token: str  # long-lived opaque token (7 days) - sent ONLY to /auth/refresh
    expires_in: int     # access-token lifetime in seconds, a hint for clients

class RefreshRequest(BaseSchema):
    refresh_token: str

class LogoutRequest(BaseSchema):
    refresh_token: str


# --- Document Schemas ---

# Input for POST /documents
class DocumentCreate(BaseSchema):
    filename: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, description="Raw content of the document")

# Output for document details (e.g., GET /documents, POST /documents)
class DocumentResponse(BaseSchema):
    id: int
    user_id: int
    filename: str
    content: str
    created_at: datetime
    updated_at: datetime


# --- Chat & Conversation Schemas ---

# Output for a message in a conversation (inside conversations or chat response)
class MessageResponse(BaseSchema):
    id: int
    conversation_id: int
    role: str = Field(..., pattern="^(user|ai)$")
    content: str
    created_at: datetime

# Input for POST /chat (to send a message in a conversation)
class ChatRequest(BaseSchema):
    message: str = Field(..., min_length=1)
    document_id: int
    # Optional conversation_id to continue an existing chat thread
    conversation_id: Optional[int] = None

# Output for POST /chat containing the messages exchange
class ChatResponse(BaseSchema):
    conversation_id: int
    user_message: MessageResponse
    ai_response: MessageResponse
