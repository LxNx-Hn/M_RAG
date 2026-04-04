"""
/api/auth — 사용자 인증 (JWT)
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import create_access_token, hash_password, verify_password
from api.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=4, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db=Depends(get_db)):
    """회원가입"""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        from sqlalchemy import select
        from api.models import User

        # 이메일 중복 확인
        result = await db.execute(select(User).where(User.email == req.email))
        if result.scalar_one_or_none():
            raise HTTPException(409, "이미 등록된 이메일입니다.")

        user = User(
            email=req.email,
            username=req.username,
            hashed_password=hash_password(req.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        token = create_access_token({"sub": user.id, "email": user.email})
        return TokenResponse(
            access_token=token,
            user={"id": user.id, "email": user.email, "username": user.username},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(500, f"Registration failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db=Depends(get_db)):
    """로그인"""
    if db is None:
        raise HTTPException(503, "Database not available")

    try:
        from sqlalchemy import select
        from api.models import User

        result = await db.execute(select(User).where(User.email == req.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(401, "이메일 또는 비밀번호가 올바르지 않습니다.")

        token = create_access_token({"sub": user.id, "email": user.email})
        return TokenResponse(
            access_token=token,
            user={"id": user.id, "email": user.email, "username": user.username},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(500, f"Login failed: {str(e)}")


@router.get("/me")
async def get_me(db=Depends(get_db)):
    """현재 사용자 정보 (토큰 기반)"""
    # Phase 4 확장: 토큰에서 사용자 ID 추출
    return {"id": "anonymous", "email": "", "username": "Guest"}
