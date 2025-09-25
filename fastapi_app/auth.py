from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import google.auth.exceptions

from typing import Dict

# Initialize Firebase Admin (only once)
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("firebase/serviceAccountKey.json")  # download from Firebase Console
    firebase_admin.initialize_app(cred)

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
