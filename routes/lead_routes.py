from fastapi import APIRouter, Body, Response, HTTPException, Depends
from database.database import lead_collection, target_collection
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel
from utils.auth import get_current_user, require_admin, create_token  

router = APIRouter()

class Target(BaseModel):
    salesPerson: str
    target: int



@router.get("/targets")
def get_targets():
    return list(target_collection.find({}, {"_id": 0}))

@router.put("/targets")
def update_target(data: Target):
    target_collection.update_one(
        {"salesPerson": data.salesPerson},
        {"$set": {"target": data.target}},
        upsert=True
    )
    return {"message": "Target updated"}

@router.post("/leads")
def create_lead(lead: dict):
    lead["createdAt"] = datetime.utcnow()
    lead_collection.insert_one(lead)
    return {"message": "Lead added"}

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}


@router.get("/leads")
def get_leads(user=Depends(get_current_user)):  # ✅ now uses correct auth from utils
    leads = []
    for lead in lead_collection.find():
        lead["_id"] = str(lead["_id"])
        leads.append(lead)
    return leads

@router.put("/leads/{id}")
def update_lead(id: str, user=Depends(get_current_user), updated_data: dict = Body(...)):
    if "_id" in updated_data:
        del updated_data["_id"]
    lead_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
    return {"message": "Lead updated"}

@router.delete("/leads/{id}")
def delete_lead(id: str):
    lead_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Deleted"}

@router.post("/login")
def login(response: Response, data: dict = Body(...)):  # ✅ Response first, no default value
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "Hytoma@123":
        token = create_token({
            "username": username,
            "role": "admin"
        })
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/"
        )

        return {"message": "Login success", "role": "admin"}

    return {"error": "Invalid credentials"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"message": "Logged out"}