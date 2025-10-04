from fastapi import APIRouter
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