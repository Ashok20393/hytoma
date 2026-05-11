from fastapi import APIRouter, Body, Depends
from database.database import db
from bson import ObjectId
from datetime import datetime
from utils.auth import get_current_user

router = APIRouter()

inventory_collection = db["inventory"]
imports_collection = db["inventory_imports"]

@router.get("/inventory")
def get_inventory(user=Depends(get_current_user)):
    items = []
    for item in inventory_collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@router.post("/inventory")
def add_product(product: dict = Body(...), user=Depends(get_current_user)):
    product["createdAt"] = datetime.utcnow()
    product["updatedAt"] = datetime.utcnow()
    inventory_collection.insert_one(product)
    return {"message": "Product added"}

@router.get("/imports")
def get_imports(user=Depends(get_current_user)):
    items = []
    for item in imports_collection.find().sort("shipment_date", -1):
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@router.post("/imports")
def add_import(data: dict = Body(...), user=Depends(get_current_user)):
    data["createdAt"] = datetime.utcnow()
    # ✅ Update product total imported quantity
    if data.get("productId"):
        db["inventory"].update_one(
            {"_id": ObjectId(data["productId"])},
            {"$inc": {"totalImported": data.get("quantity", 0)}}
        )
    imports_collection.insert_one(data)
    return {"message": "Import logged"}

@router.delete("/imports/{id}")
def delete_import(id: str, user=Depends(get_current_user)):
    item = imports_collection.find_one({"_id": ObjectId(id)})
    if item and item.get("productId"):
        db["inventory"].update_one(
            {"_id": ObjectId(item["productId"])},
            {"$inc": {"totalImported": -item.get("quantity", 0)}}
        )
    imports_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Import deleted"}

@router.put("/inventory/{id}")
def update_product(id: str, data: dict = Body(...), user=Depends(get_current_user)):
    data["updatedAt"] = datetime.utcnow()
    if "_id" in data:
        del data["_id"]
    inventory_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )
    return {"message": "Product updated"}

@router.delete("/inventory/{id}")
def delete_product(id: str, user=Depends(get_current_user)):
    inventory_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Product deleted"}

