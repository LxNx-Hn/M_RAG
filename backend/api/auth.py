"""
JWT 인증 유틸리티
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "mrag-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    try:
        from jose import jwt
    except ImportError:
        logger.warning("python-jose not installed, returning dummy token")
        return "dummy-token"

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증 → payload 반환"""
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ImportError:
        logger.warning("python-jose not installed, skipping verification")
        return {"sub": "anonymous"}
    except Exception:
        return None


def hash_password(password: str) -> str:
    """비밀번호 해시"""
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except ImportError:
        logger.warning("passlib not installed, storing plain (DEV ONLY)")
        return password


def verify_password(plain: str, hashed: str) -> bool:
    """비밀번호 검증"""
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain, hashed)
    except ImportError:
        return plain == hashed
