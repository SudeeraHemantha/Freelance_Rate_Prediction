from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from app.core.logging import logger


def create_limiter() -> Limiter:
    """Initializes slowapi Limiter with Redis storage backend and graceful memory fallback."""
    storage_uri = settings.REDIS_URL
    try:
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[settings.RATE_LIMIT_PER_MINUTE],
            storage_uri=storage_uri
        )
        logger.info(f"Initialized slowapi rate limiter connected to storage: {storage_uri}")
        return limiter
    except Exception as err:
        logger.warning(f"Failed to connect slowapi to Redis ({err}). Falling back to in-memory rate limiter.")
        return Limiter(
            key_func=get_remote_address,
            default_limits=[settings.RATE_LIMIT_PER_MINUTE]
        )


limiter = create_limiter()
