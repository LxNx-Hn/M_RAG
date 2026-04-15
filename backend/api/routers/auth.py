"""
/api/auth - user authentication endpoints
"""

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select

from api.auth import (
    create_access_token,
    get_current_token_payload,
    get_current_user_id,
    hash_password,
    revoke_token,
    verify_password,
)
from api.database import get_db
from api.limiter import limiter
from api.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def validate_password_policy(password: str) -> None:
    if len(password) < 10:
        raise HTTPException(400, "비밀번호는 최소 10자 이상이어야 합니다.")
    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(400, "비밀번호에 영문자를 최소 1개 포함해야 합니다.")
    if not re.search(r"\d", password):
        raise HTTPException(400, "비밀번호에 숫자를 최소 1개 포함해야 합니다.")
    if not re.search(r"[^\w\s]", password):
        raise HTTPException(400, "비밀번호에 특수문자를 최소 1개 포함해야 합니다.")


@router.post("/register", response_model=TokenResponse)
@limiter.limit("3/minute")
async def register(request: Request, req: RegisterRequest, db=Depends(get_db)):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    try:
        validate_password_policy(req.password)

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
    except Exception as exc:
        logger.error("Registration failed: %s", exc)
        raise HTTPException(500, "회원가입 처리 중 오류가 발생했습니다.")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, req: LoginRequest, db=Depends(get_db)):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    try:
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
    except Exception as exc:
        logger.error("Login failed: %s", exc)
        raise HTTPException(500, "로그인 처리 중 오류가 발생했습니다.")


@router.post("/logout")
@limiter.limit("30/minute")
async def logout(
    request: Request,
    payload: dict = Depends(get_current_token_payload),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")
    user_id = str(payload["sub"])
    await revoke_token(db, user_id, payload)
    return {"message": "로그아웃되었습니다."}


@router.get("/me")
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if db is None:
        raise HTTPException(503, "데이터베이스를 사용할 수 없습니다.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")

    return {"id": user.id, "email": user.email, "username": user.username}
