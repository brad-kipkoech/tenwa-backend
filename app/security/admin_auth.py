from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from app.config import settings


security = HTTPBearer(auto_error=True)


def get_allowed_admin_emails() -> set[str]:
    return {
        email.strip().lower()
        for email in settings.ADMIN_ALLOWED_EMAILS.split(",")
        if email.strip()
    }


async def require_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase authentication is not configured.",
        )

    token = credentials.credentials

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_ANON_KEY,
                },
            )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify admin session.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session.",
        )

    user = response.json()
    email = (user.get("email") or "").lower()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user email not found.",
        )

    allowed_emails = get_allowed_admin_emails()

    if email not in allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access the admin dashboard.",
        )

    return user