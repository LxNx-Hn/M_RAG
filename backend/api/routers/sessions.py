"""
/api/sessions - session management endpoints
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from api.auth import get_current_user_id
from api.database import get_db
from api.limiter import limiter
from api.models import Paper, Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["sessions"])

MAX_PAPERS_PER_SESSION = 30

# Auto icon selection based on paper title keywords
_ICON_RULES = [
    (
        {"nlp", "language", "text", "bert", "gpt", "llm", "transformer", "embedding"},
        "📝",
    ),
    ({"ai", "ml", "machine", "learning", "neural", "deep", "model"}, "🤖"),
    ({"medical", "health", "clinical", "patient", "disease"}, "🏥"),
    ({"law", "legal", "court", "regulation"}, "⚖️"),
    ({"math", "algorithm", "optimization", "compute"}, "🔢"),
    ({"image", "vision", "visual", "cnn", "detection"}, "🖼️"),
]


def _select_icon(title: str) -> str:
    words = set(title.lower().split())
    for keywords, icon in _ICON_RULES:
        if words & keywords:
            return icon
    return "📄"


class CreateSessionRequest(BaseModel):
    title: str = Field(default="", max_length=255)


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    icon: str | None = Field(default=None, max_length=10)


@router.get("")
@limiter.limit("60/minute")
async def list_sessions(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.updated_at.desc())
    )
    sessions = result.scalars().all()

    items = []
    for s in sessions:
        # Count papers in this session's collection
        paper_count_result = await db.execute(
            select(func.count(Paper.id)).where(
                Paper.user_id == user_id,
                Paper.collection_name == s.collection_name,
            )
        )
        paper_count = paper_count_result.scalar() or 0

        items.append(
            {
                "id": s.id,
                "title": s.title,
                "icon": s.icon,
                "collection_name": s.collection_name,
                "paper_count": paper_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
        )

    return {"sessions": items}


@router.post("")
@limiter.limit("10/minute")
async def create_session(
    request: Request,
    req: CreateSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    collection_name = f"session_{uuid.uuid4().hex[:12]}"
    title = req.title.strip() or "제목 없는 세션"
    icon = _select_icon(title)

    session_obj = Session(
        user_id=user_id,
        title=title,
        icon=icon,
        collection_name=collection_name,
    )
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)

    return {
        "id": session_obj.id,
        "title": session_obj.title,
        "icon": session_obj.icon,
        "collection_name": session_obj.collection_name,
        "paper_count": 0,
        "created_at": (
            session_obj.created_at.isoformat() if session_obj.created_at else None
        ),
        "updated_at": (
            session_obj.updated_at.isoformat() if session_obj.updated_at else None
        ),
    }


@router.patch("/{session_id}")
@limiter.limit("30/minute")
async def update_session(
    request: Request,
    session_id: str,
    req: UpdateSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.user_id == user_id)
    )
    session_obj = result.scalar_one_or_none()
    if session_obj is None:
        raise HTTPException(404, "세션을 찾을 수 없습니다.")

    if req.title is not None:
        session_obj.title = req.title.strip() or "제목 없는 세션"
    if req.icon is not None:
        session_obj.icon = req.icon

    session_obj.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session_obj)

    return {
        "id": session_obj.id,
        "title": session_obj.title,
        "icon": session_obj.icon,
        "collection_name": session_obj.collection_name,
    }


@router.delete("/{session_id}")
@limiter.limit("10/minute")
async def delete_session(
    request: Request,
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.user_id == user_id)
    )
    session_obj = result.scalar_one_or_none()
    if session_obj is None:
        raise HTTPException(404, "세션을 찾을 수 없습니다.")

    await db.delete(session_obj)
    await db.commit()
    return {"message": "세션이 삭제되었습니다."}
