from fastapi import APIRouter, Depends, Response, HTTPException
import datetime
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from fastapi_app.auth import verify_firebase_token, verify_session_cookie
from firebase_admin import firestore

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginBody(BaseModel):
    idToken: str

@router.get("/me")
async def get_me(user=Depends(verify_firebase_token)):
    return {
        "uid": user["uid"],
        "email": user.get("email"),
        "role": user.get("role", "traveler")
    }


@router.post("/login")
async def login(body: LoginBody, response: Response):
    try:
        # Verify client-provided Firebase ID token
        decoded = firebase_auth.verify_id_token(body.idToken)
        uid = decoded["uid"]

        # Upsert user document in Firestore
        db = firestore.client()
        doc_ref = db.collection("users").document(uid)
        now_iso = datetime.datetime.utcnow().isoformat() + "Z"
        provider = (decoded.get("firebase", {}) or {}).get("sign_in_provider")
        user_data = {
            "uid": uid,
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture"),
            "provider": provider,
            "lastLogin": now_iso,
        }
        if not doc_ref.get().exists:
            user_data["createdAt"] = now_iso
            doc_ref.set(user_data)
        else:
            doc_ref.set(user_data, merge=True)

        # Create a session cookie valid for 14 days
        expires_in = datetime.timedelta(days=14)
        session_cookie = firebase_auth.create_session_cookie(body.idToken, expires_in=expires_in)

        # HttpOnly, Secure (set Secure=True if behind HTTPS), SameSite=Lax
        response.set_cookie(
            key="session",
            value=session_cookie,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=int(expires_in.total_seconds()),
            path="/",
        )
        return {"uid": uid, "status": "logged_in"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout(response: Response):
    # Clear cookie. Optionally revoke refresh tokens if needed.
    response.delete_cookie("session", path="/")
    return {"status": "logged_out"}


@router.get("/session/me")
async def session_me(user=Depends(verify_session_cookie)):
    return {
        "uid": user["uid"],
        "email": user.get("email"),
        "role": user.get("role", "traveler")
    }
