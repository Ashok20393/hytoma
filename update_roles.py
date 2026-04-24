from pymongo import MongoClient

client = MongoClient("mongodb+srv://ashokkurapati5_db_user:Ashok7093@cluster0.s5ium9e.mongodb.net/?appName=Cluster0")
db = client["crm_db"]

db.users.update_one(
    {"username": "revathi"},
    {"$set": {"role": "sales"}}
)

db.users.update_one(
    {"username": "manoj"},
    {"$set": {"role": "sales"}}
)

db.users.update_one(
    {"username": "suresh"},
    {"$set": {"role": "sales"}}
)

db.users.update_one(
    {"username": "naveen"},
    {"$set": {"role": "sales"}}
)

db.users.update_one(
    {"username": "admin"},
    {"$set": {"role": "admin"}}
)

db.users.update_many(
    {"role": {"$exists": False}},
    {"$set": {"role": "sales"}}
)

print("✅ Roles updated successfully")