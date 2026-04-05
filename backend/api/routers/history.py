"""
/api/history — 대화 기록 관리
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from api.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["history"])


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)


class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    metadata_json: Optional[dict] = None


@router.get("/conversations")
async def list_conversations(db=Depends(get_db)):
    """대화 목록 조회"""
    if db is None:
        return {"conversations": []}

    try:
        from sqlalchemy import select
        from api.models import Conversation

        result = await db.execute(
            select(Conversation).order_by(Conversation.updated_at.desc()).limit(50)
        )
        convs = result.scalars().all()
        return {
            "conversations": [
                {
                    "id": c.id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in convs
            ]
        }
    except Exception as e:
        logger.error(f"List conversations failed: {e}")
        return {"conversations": []}


@router.post("/conversations")
async def create_conversation(req: ConversationCreate, db=Depends(get_db)):
    """새 대화 생성"""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        from api.models import Conversation

        conv = Conversation(title=req.title)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return {"id": conv.id, "title": conv.title}
    except Exception as e:
        logger.error(f"Create conversation failed: {e}")
        raise HTTPException(500, str(e))


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, db=Depends(get_db)):
    """대화 메시지 조회"""
    if db is None:
        return {"messages": []}

    try:
        from sqlalchemy import select
        from api.models import Message

        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        msgs = result.scalars().all()
        return {
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "metadata": m.metadata_json,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in msgs
            ]
        }
    except Exception as e:
        logger.error(f"Get messages failed: {e}")
        return {"messages": []}


@router.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, req: MessageCreate, db=Depends(get_db)):
    """메시지 추가"""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        from api.models import Message

        msg = Message(
            conversation_id=conversation_id,
            role=req.role,
            content=req.content,
            metadata_json=req.metadata_json or {},
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return {"id": msg.id, "role": msg.role}
    except Exception as e:
        logger.error(f"Add message failed: {e}")
        raise HTTPException(500, str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db=Depends(get_db)):
    """대화 삭제"""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        from sqlalchemy import select
        from api.models import Conversation

        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(404, "대화를 찾을 수 없습니다.")

        await db.delete(conv)
        await db.commit()
        return {"message": "삭제 완료"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation failed: {e}")
        raise HTTPException(500, str(e))
