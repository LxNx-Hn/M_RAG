"""
/api/conversations - conversation persistence endpoints
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select

from api.auth import get_current_user_id
from api.database import get_db
from api.limiter import limiter
from api.models import Conversation, Message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class CreateConversationRequest(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)


class CreateMessageRequest(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    metadata_json: dict = Field(default_factory=dict)


@router.get("")
@limiter.limit("60/minute")
async def list_conversations(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in conversations
        ]
    }


@router.post("")
@limiter.limit("30/minute")
async def create_conversation(
    request: Request,
    req: CreateConversationRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    conv = Conversation(user_id=user_id, title=req.title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat() if conv.created_at else None,
        "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
    }


@router.get("/{conversation_id}/messages")
@limiter.limit("60/minute")
async def get_messages(
    request: Request,
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(404, "대화를 찾을 수 없습니다.")

    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = msg_result.scalars().all()

    return {
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "metadata_json": m.metadata_json,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]
    }


@router.post("/{conversation_id}/messages")
@limiter.limit("60/minute")
async def add_message(
    request: Request,
    conversation_id: str,
    req: CreateMessageRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(404, "대화를 찾을 수 없습니다.")

    msg = Message(
        conversation_id=conversation_id,
        role=req.role,
        content=req.content,
        metadata_json=req.metadata_json,
    )
    db.add(msg)

    # Update conversation title from first user message
    if req.role == "user":
        msg_count_result = await db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.role == "user",
            )
        )
        existing_user_msgs = msg_count_result.scalars().all()
        if len(existing_user_msgs) == 0:
            conv.title = req.content[:50]

    conv.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(msg)

    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "metadata_json": msg.metadata_json,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    }


@router.delete("/{conversation_id}")
@limiter.limit("30/minute")
async def delete_conversation(
    request: Request,
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(404, "대화를 찾을 수 없습니다.")

    await db.delete(conv)
    await db.commit()
    return {"message": "대화가 삭제되었습니다."}
