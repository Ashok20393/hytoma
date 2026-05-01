from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

router = APIRouter(prefix="/api/movements", tags=["movements"])

mongo_url = os.getenv("MONGO_URL")
if not mongo_url:
    raise Exception("❌ MONGO_URL is missing.")

client = MongoClient(mongo_url, tlsCAFile=certifi.where())
db = client["crm_db"]
collection = db["product_movements"]

def serialize(doc) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

class MovementCreate(BaseModel):
    product: str
    client: str
    person: str
    type: str
    date: str
    quantity: Optional[int] = 1       
    out_time: Optional[str] = None
    notes: Optional[str] = ""
    expected_date: Optional[str] = None

class MovementUpdate(BaseModel):
    status: Optional[str] = None
    return_time: Optional[str] = None
    product: Optional[str] = None     
    client: Optional[str] = None
    person: Optional[str] = None
    type: Optional[str] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None
    expected_date: Optional[str] = None

# ✅ stats and meta BEFORE /{movement_id} to avoid route conflict
@router.get("/stats/summary")
def get_stats(
    date: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    query = {}
    if date:
        query["date"] = date
    else:
        date_filter = {}
        if from_date: date_filter["$gte"] = from_date
        if to_date:   date_filter["$lte"] = to_date
        if date_filter: query["date"] = date_filter

    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = list(collection.aggregate(pipeline))
    stats = {"Out": 0, "Returned": 0, "Installed": 0}
    for r in result:
        if r["_id"] in stats:
            stats[r["_id"]] = r["count"]
    stats["Total"] = sum(stats.values())
    return stats

@router.get("/meta/persons")
def get_persons():
    persons = collection.distinct("person")
    return sorted(persons)

@router.get("/pending")
def get_pending():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    docs = list(collection.find({
        "status": {"$in": ["Out", "Pending"]}
    }).sort("expected_date", 1))
    result = [serialize(d) for d in docs]
    for item in result:
        if item.get("expected_date") and item["expected_date"] < today:
            item["overdue"] = True
        else:
            item["overdue"] = False
    return result

@router.get("")
def get_movements(
    date: Optional[str] = None,
    status: Optional[str] = None,
    person: Optional[str] = None,
    type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    query = {}
    if date:
        query["date"] = date
    else:
        date_filter = {}
        if from_date: date_filter["$gte"] = from_date
        if to_date:   date_filter["$lte"] = to_date
        if date_filter: query["date"] = date_filter

    if status: query["status"] = status
    if person: query["person"] = person
    if type:   query["type"] = type

    docs = list(collection.find(query).sort([("date", -1), ("out_time", -1)]))
    return [serialize(d) for d in docs]

@router.post("", status_code=201)
def create_movement(data: MovementCreate):
    doc = data.dict()
    doc["status"] = "Out"
    doc["return_time"] = None
    doc["created_at"] = datetime.utcnow().isoformat()
    result = collection.insert_one(doc)
    created = collection.find_one({"_id": result.inserted_id})
    return serialize(created)

@router.patch("/{movement_id}")
def update_movement(movement_id: str, data: MovementUpdate):
    try:
        oid = ObjectId(movement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # ✅ Only update fields that are provided
    update_data = {k: v for k, v in data.dict().items() if v is not None}

    if "status" in update_data and update_data["status"] not in ("Out", "Returned", "Installed"):
        raise HTTPException(status_code=400, detail="Invalid status")

    result = collection.find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Movement not found")
    return serialize(result)

@router.delete("/{movement_id}")
def delete_movement(movement_id: str):
    try:
        oid = ObjectId(movement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movement not found")
    return {"message": "Deleted"}

