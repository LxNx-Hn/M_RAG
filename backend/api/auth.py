"""JWT auth utilities and dependencies."""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from api.database import get_db
from api.models import RevokedToken

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set before starting the API")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
bearer_scheme = HTTPBearer(auto_error=False)


def _get_jwt():
    try:
        from jose import jwt
    except ImportError as exc:
        raise RuntimeError("python-jose is required for JWT operations") from exc
    return jwt


def _get_password_context():
    try:
        from passlib.context import CryptContext
    except ImportError as exc:
        raise RuntimeError(
            "passlib is required for password hashing and verification"
        ) from exc
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    jwt = _get_jwt()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "token_type": "access",
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify JWT token and return payload."""
    jwt = _get_jwt()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None


def hash_password(password: str) -> str:
    """Hash password."""
    pwd_context = _get_password_context()
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password."""
    pwd_context = _get_password_context()
    return pwd_context.verify(plain, hashed)


async def _validate_token_payload(payload: dict[str, Any], db) -> None:
    if "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("token_type") not in (None, "access"):
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = payload.get("jti")
    if not jti:
        return

    result = await db.execute(
        select(RevokedToken).where(
            RevokedToken.jti == str(jti),
            RevokedToken.expires_at > datetime.now(timezone.utc),
        )
    )
    revoked = result.scalar_one_or_none()
    if revoked is not None:
        raise HTTPException(status_code=401, detail="Token has been revoked")


async def get_current_token_payload(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db=Depends(get_db),
) -> dict[str, Any]:
    """Resolve and validate bearer token payload."""
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    payload = verify_token(creds.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    await _validate_token_payload(payload, db)
    return payload


async def get_current_user_id(
    payload: dict[str, Any] = Depends(get_current_token_payload),
) -> str:
    """Resolve user id from validated bearer token."""
    return str(payload["sub"])


async def revoke_token(db, user_id: str, payload: dict[str, Any]) -> None:
    """Store JWT jti into revocation table until token expiration."""
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or exp is None:
        return

    expires_at = datetime.fromtimestamp(int(exp), tz=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        return

    existing = await db.execute(
        select(RevokedToken).where(RevokedToken.jti == str(jti))
    )
    if existing.scalar_one_or_none() is not None:
        return

    db.add(
        RevokedToken(
            user_id=user_id,
            jti=str(jti),
            expires_at=expires_at,
        )
    )
    await db.commit()
