from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

router = APIRouter(prefix="/api/movements", tags=["movements"])

# ─── MongoDB Connection ───────────────────────────────────────────────────────
mongo_url = os.getenv("MONGO_URL")

if not mongo_url:
    raise Exception("❌ MONGO_URL is missing. Check your .env or Render env variables")

client = MongoClient(
    mongo_url,
    tlsCAFile=certifi.where()
)

db = client["crm_db"]
collection = db["product_movements"]



# ─── Helper ───────────────────────────────────────────────────────────────────
def serialize(doc) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


# ─── Schemas ──────────────────────────────────────────────────────────────────
class MovementCreate(BaseModel):
    product: str
    client: str
    person: str
    type: str
    date: str
    out_time: Optional[str] = None
    notes: Optional[str] = ""


class MovementUpdate(BaseModel):
    status: str
    return_time: Optional[str] = None


# ─── Routes ───────────────────────────────────────────────────────────────────

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
def update_movement_status(movement_id: str, data: MovementUpdate):
    if data.status not in ("Out", "Returned", "Installed"):
        raise HTTPException(status_code=400, detail="Invalid status")
    try:
        oid = ObjectId(movement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = collection.find_one_and_update(
        {"_id": oid},
        {"$set": {"status": data.status, "return_time": data.return_time}},
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
        stats[r["_id"]] = r["count"]
    stats["Total"] = sum(stats.values())
    return stats


@router.get("/meta/persons")
def get_persons():
    persons = collection.distinct("person")
    return sorted(persons)