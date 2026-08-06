import time
import jwt
from typing import Optional, Dict, Any
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logging import logger

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = 3600) -> str:
    """Generates a signed JWT bearer token valid for expires_delta seconds."""
    payload = data.copy()
    now = int(time.time())
    payload.update({
        "iat": now,
        "exp": now + (expires_delta or 3600),
        "iss": "freelance-rate-predictor"
    })
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token string."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


def verify_api_key_or_token(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(http_bearer)
) -> Dict[str, Any]:
    """
    Dependency that enforces API Security.
    Accepts either a valid X-API-Key header or a valid Authorization Bearer JWT token.
    """
    # 1. Validate API Key
    if api_key and api_key == settings.API_KEY:
        logger.info("Request authenticated via valid API Key.")
        return {"auth_type": "api_key", "client_id": "enterprise_client"}

    # 2. Validate Bearer Token
    if credentials and credentials.credentials:
        payload = verify_jwt_token(credentials.credentials)
        if payload:
            logger.info("Request authenticated via valid JWT Bearer token.")
            return {"auth_type": "jwt", "client_id": payload.get("sub", "authenticated_user")}

    # 3. Reject if unauthenticated
    logger.warning("Unauthenticated API request attempt blocked.")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API authentication credentials. Provide a valid X-API-Key header or Bearer token.",
        headers={"WWW-Authenticate": "Bearer"}
    )
