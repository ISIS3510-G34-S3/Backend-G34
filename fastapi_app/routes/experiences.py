from fastapi import APIRouter, HTTPException, Query
from firebase_admin import firestore
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    """
    R = 6371  # Radius of Earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


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


@router.get("/near/")
async def get_near_experiences(
    latitude: float = Query(..., description="User's current latitude"),
    longitude: float = Query(..., description="User's current longitude"),
    top_k: int = Query(5, description="Number of nearest experiences to return", gt=0)
):
    """
    Retrieves the top-k nearest experiences based on the user's location.
    """
    db = firestore.client()
    experiences_ref = db.collection("experiences")
    all_experiences = experiences_ref.stream()

    experiences_with_distance = []
    for doc in all_experiences:
        experience = doc.to_dict()
        exp_latitude = experience.get("latitude")
        exp_longitude = experience.get("longitude")

        if isinstance(exp_latitude, (float, int)) and isinstance(exp_longitude, (float, int)):
            distance = haversine_distance(latitude, longitude, exp_latitude, exp_longitude)
            experience["id"] = doc.id
            experiences_with_distance.append({"experience": experience, "distance": distance})

    # Sort experiences by distance in ascending order
    experiences_with_distance.sort(key=lambda x: x["distance"])

    # Get the top_k nearest experiences
    top_k_experiences = [item["experience"] for item in experiences_with_distance[:top_k]]

    return top_k_experiences