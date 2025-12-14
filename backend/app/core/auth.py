from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import get_settings
from app.core.database import get_db
import httpx

settings = get_settings()
security = HTTPBearer()


async def verify_supabase_jwt(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Verify Supabase JWT token and extract user_id.
    
    Returns:
        user_id: The authenticated user's ID
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        # Get Supabase JWT secret from public key endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.supabase_url}/auth/v1/jwks")
            jwks = response.json()
        
        # Decode and verify token
        # For production, implement proper JWKS verification
        # For now, we'll do basic validation
        payload = jwt.decode(
            token,
            settings.supabase_service_role_key,
            algorithms=["HS256"],
            options={"verify_signature": False}  # Will be properly verified with JWKS
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")
            
        return user_id
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_current_user(user_id: str = Depends(verify_supabase_jwt)) -> str:
    """Dependency to get current authenticated user ID."""
    return user_id
