from fastapi import APIRouter, HTTPException
from firebase_admin import firestore

router = APIRouter(prefix="/experiences", tags=["experiences"])

@router.get("/")
async def get_experiences():
    """
    Retrieves all experiences from the Firestore collection.
    """
    db = firestore.client()
    experiences_ref = db.collection("experiences")
    experiences = []
    for doc in experiences_ref.stream():
        experience_data = doc.to_dict()
        experience_data['id'] = doc.id
        experiences.append(experience_data)
    return experiences


@router.get("/{experience_id}")
async def get_experience(experience_id: str):
    """
    Retrieves a single experience by its ID.
    """
    db = firestore.client()
    doc_ref = db.collection("experiences").document(experience_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Experience not found")

    experience_data = doc.to_dict()
    experience_data["id"] = doc.id
    return experience_data