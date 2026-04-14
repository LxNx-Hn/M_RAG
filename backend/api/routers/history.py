"""
/api/history - conversation history management
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from api.auth import get_current_user_id
from api.database import get_db
from api.models import Conversation, Message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["history"])


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)


class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    metadata_json: Optional[dict] = None


async def _get_owned_conversation(db, conversation_id: str, user_id: str) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(404, "Conversation not found.")
    return conversation


@router.get("/conversations")
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """List user-owned conversations."""
    if db is None:
        return {"conversations": []}

    try:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(50)
        )
        conversations = result.scalars().all()
        return {
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                }
                for conv in conversations
            ]
        }
    except Exception as exc:
        logger.error("List conversations failed: %s", exc)
        return {"conversations": []}


@router.post("/conversations")
async def create_conversation(
    req: ConversationCreate,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Create a conversation owned by current user."""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        conversation = Conversation(title=req.title, user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return {"id": conversation.id, "title": conversation.title}
    except Exception as exc:
        logger.error("Create conversation failed: %s", exc)
        raise HTTPException(500, "Failed to create conversation.")


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Get messages for an owned conversation."""
    if db is None:
        return {"messages": []}

    try:
        await _get_owned_conversation(db, conversation_id, user_id)
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return {
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.metadata_json,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Get messages failed: %s", exc)
        return {"messages": []}


@router.post("/conversations/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    req: MessageCreate,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Add message to an owned conversation."""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        await _get_owned_conversation(db, conversation_id, user_id)

        message = Message(
            conversation_id=conversation_id,
            role=req.role,
            content=req.content,
            metadata_json=req.metadata_json or {},
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return {"id": message.id, "role": message.role}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Add message failed: %s", exc)
        raise HTTPException(500, "Failed to add message.")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Delete an owned conversation."""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        conversation = await _get_owned_conversation(db, conversation_id, user_id)
        await db.delete(conversation)
        await db.commit()
        return {"message": "Conversation deleted."}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Delete conversation failed: %s", exc)
        raise HTTPException(500, "Failed to delete conversation.")

