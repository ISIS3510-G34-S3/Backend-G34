from fastapi import APIRouter, Depends
from fastapi_app.auth import verify_firebase_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me")
async def get_me(user=Depends(verify_firebase_token)):
    return {
        "uid": user["uid"],
        "email": user.get("email"),
        "role": user.get("role", "traveler")
    }
