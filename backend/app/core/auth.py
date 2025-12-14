from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import get_settings
import logging
import time

settings = get_settings()
security = HTTPBearer()
logger = logging.getLogger(__name__)


async def verify_supabase_jwt(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Verify Supabase JWT token and extract user_id.

    This helper extracts unverified claims from the Supabase token and performs
    lightweight checks (presence of "sub" and expiry). It does NOT verify the
    token signature. For production, enable signature verification using
    `SUPABASE_JWT_SECRET` or JWKS verification.

    Returns:
        user_id: The authenticated user's ID

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        # >>> DEVELOPMENT: extract claims without verifying signature <<<
        # Use jose.jwt.get_unverified_claims to avoid audience/issuer validation
        payload = jwt.get_unverified_claims(token)

        user_id = payload.get("sub")
        if not user_id:
            logger.error("Token missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")

        # Verify token hasn't expired (exp is seconds since epoch)
        exp = payload.get("exp")
        if exp is not None:
            if time.time() > int(exp):
                logger.warning("Token expired")
                raise HTTPException(status_code=401, detail="Token has expired")

        logger.info(f"Authenticated user: {user_id}")
        return user_id

    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_current_user(user_id: str = Depends(verify_supabase_jwt)) -> str:
    """Dependency to get current authenticated user ID."""
    return user_id
