"""
SQLAlchemy ORM models.
"""

import uuid
from datetime import datetime, timezone

try:
    from sqlalchemy import (
        JSON,
        Column,
        DateTime,
        ForeignKey,
        Integer,
        String,
        Text,
        UniqueConstraint,
    )
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

        conversations = relationship(
            "Conversation", back_populates="user", cascade="all, delete-orphan"
        )
        revoked_tokens = relationship("RevokedToken", cascade="all, delete-orphan")

    class Conversation(Base):
        __tablename__ = "conversations"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(
            String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )
        title = Column(String(255), default="New Conversation")
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        updated_at = Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

        user = relationship("User", back_populates="conversations")
        messages = relationship(
            "Message", back_populates="conversation", cascade="all, delete-orphan"
        )

    class Message(Base):
        __tablename__ = "messages"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        conversation_id = Column(
            String(36),
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        )
        role = Column(String(20), nullable=False)
        content = Column(Text, nullable=False)
        metadata_json = Column(JSON, default=dict)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

        conversation = relationship("Conversation", back_populates="messages")

    class Paper(Base):
        __tablename__ = "papers"
        __table_args__ = (
            UniqueConstraint(
                "user_id",
                "collection_name",
                "doc_id",
                name="uq_papers_user_collection_doc",
            ),
        )

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(
            String(36),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
        doc_id = Column(String(255), nullable=False, index=True)
        title = Column(String(500), nullable=False)
        collection_name = Column(
            String(255), nullable=False, default="papers", index=True
        )
        doc_type = Column(String(32), nullable=False, default="paper")
        file_name = Column(String(255), nullable=False)
        file_path = Column(String(1024), nullable=False)
        file_type = Column(String(32), nullable=False)
        total_pages = Column(Integer, nullable=False, default=0)
        num_chunks = Column(Integer, nullable=False, default=0)
        sections_json = Column(JSON, default=dict)
        document_json = Column(JSON, default=dict)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        updated_at = Column(
            DateTime,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

    class RevokedToken(Base):
        __tablename__ = "revoked_tokens"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = Column(
            String(36),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
        jti = Column(String(128), nullable=False, unique=True, index=True)
        expires_at = Column(DateTime, nullable=False)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

except ImportError as _sqlalchemy_import_error:
    raise ImportError(
        "sqlalchemy is required for M-RAG API models. "
        "Install with: pip install sqlalchemy aiosqlite"
    ) from _sqlalchemy_import_error
