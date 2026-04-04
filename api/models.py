"""
SQLAlchemy ORM 모델
"""
import uuid
from datetime import datetime, timezone

try:
    from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
    from sqlalchemy.orm import DeclarativeBase, relationship

    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "users"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        email = Column(String(255), unique=True, nullable=False, index=True)
        username = Column(String(100), nullable=False)
        hashed_password = Column(String(255), nullable=False)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

        conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    class Conversation(Base):
        __tablename__ = "conversations"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
        title = Column(String(255), default="New Conversation")
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

        user = relationship("User", back_populates="conversations")
        messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    class Message(Base):
        __tablename__ = "messages"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
        role = Column(String(20), nullable=False)  # 'user' or 'assistant'
        content = Column(Text, nullable=False)
        metadata_json = Column(JSON, default=dict)  # route, sources, steps
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

        conversation = relationship("Conversation", back_populates="messages")

except ImportError:
    # SQLAlchemy 미설치 시 더미 클래스
    class Base:
        metadata = type('obj', (object,), {'create_all': lambda *a, **k: None})()

    class User:
        pass

    class Conversation:
        pass

    class Message:
        pass
