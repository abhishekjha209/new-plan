from sqlalchemy import ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

# Import our base class
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False) # Day 8 will secure this
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    #  default=func.now() populates dates automatically using the server time when a row is inserted
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    # If a user is deleted, we cascade and delete all their documents and conversations automatically
    documents: Mapped[List["Document"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
        # sqlalchemy automatically cleans up when session.delete(user) is called
        # acts at ORM level, not DB level
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        # back_populates defines the "parent" attribute in the Conversation model (Conversation.user)
        back_populates="user", 
        cascade="all, delete-orphan" 
        # sqlalchemy automatically cleans up when session.delete(user) is called
        # acts at ORM level
    )



class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), # Foreign Key, and cascade deletion (at db level)
        nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(),  #  default=func.now() populates dates automatically using the server time when a row is inserted
        onupdate=func.now(),  # onupdate=func.now() to automatically bump updated_at on updates
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="documents")
    conversations: Mapped[List["Conversation"]] = relationship(
        # back_populates defines the "parent" attribute in the Conversation model (Conversation.document)
        back_populates="document", 
        cascade="all, delete-orphan"
    )


class Conversation(Base):
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="conversations")
    document: Mapped["Document"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", 
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), 
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False) # "user" or "ai"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
