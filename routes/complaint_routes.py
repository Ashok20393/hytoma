from fastapi import APIRouter, Body, Depends
from database.database import db
from bson import ObjectId
from datetime import datetime
from utils.auth import get_current_user

router = APIRouter()

complaint_collection = db["complaints"]
social_collection = db["social_enquiries"]

# ── COMPLAINTS ──
@router.get("/complaints")
def get_complaints(user=Depends(get_current_user)):
    items = []
    for item in complaint_collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@router.post("/complaints")
def add_complaint(data: dict = Body(...), user=Depends(get_current_user)):
    data["createdAt"] = datetime.utcnow()
    data["status"] = "Open"
    complaint_collection.insert_one(data)
    return {"message": "Complaint added"}

@router.put("/complaints/{id}")
def update_complaint(id: str, data: dict = Body(...), user=Depends(get_current_user)):
    if "_id" in data:
        del data["_id"]
    complaint_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )
    return {"message": "Complaint updated"}

@router.delete("/complaints/{id}")
def delete_complaint(id: str, user=Depends(get_current_user)):
    complaint_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Complaint deleted"}

# ── SOCIAL ENQUIRIES ──
@router.get("/social-enquiries")
def get_social(user=Depends(get_current_user)):
    items = []
    for item in social_collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@router.post("/social-enquiries")
def add_social(data: dict = Body(...), user=Depends(get_current_user)):
    data["createdAt"] = datetime.utcnow()
    social_collection.insert_one(data)
    return {"message": "Enquiry added"}

@router.put("/social-enquiries/{id}")
def update_social(id: str, data: dict = Body(...), user=Depends(get_current_user)):
    if "_id" in data:
        del data["_id"]
    social_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )
    return {"message": "Enquiry updated"}

@router.delete("/social-enquiries/{id}")
def delete_social(id: str, user=Depends(get_current_user)):
    social_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Enquiry deleted"}