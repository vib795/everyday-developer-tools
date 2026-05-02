from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings


def _build_limiter() -> Limiter:
    if settings.redis_url:
        return Limiter(
            key_func=get_remote_address,
            storage_uri=settings.redis_url,
            default_limits=[settings.rate_limit_default],
        )
    return Limiter(
        key_func=get_remote_address,
        default_limits=[settings.rate_limit_default],
    )


limiter = _build_limiter()
