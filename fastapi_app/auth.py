from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth
import google.auth.exceptions

from typing import Dict

# Ensure firebase app is initialized by importing the initializer
from fastapi_app.firebase_app import firebase_app  # noqa: F401  (import side-effect)

security = HTTPBearer()

async def verify_firebase_token(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    token = creds.credentials
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid auth token: {str(e)}",
        )


async def verify_session_cookie(request: Request) -> Dict:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session cookie",
        )
    try:
        decoded_claims = firebase_auth.verify_session_cookie(session_cookie, check_revoked=True)
        return decoded_claims
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid session: {str(e)}",
        )
