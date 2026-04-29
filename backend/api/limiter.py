"""
Global rate limiter configuration.
"""

import os

from slowapi import Limiter
from starlette.requests import Request


def _get_client_ip(request: Request) -> str:
    """Resolve client IP for rate limiting.

    By default, uses the direct connection IP (request.client.host).
    When TRUST_PROXY_HEADERS=true is set, reads X-Forwarded-For or X-Real-IP
    from the request headers.  Only enable this when running behind a trusted
    reverse proxy that sets these headers.
    """
    trust_proxy = os.environ.get("TRUST_PROXY_HEADERS", "false").lower() == "true"
    if trust_proxy:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=_get_client_ip)
