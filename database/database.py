from pymongo import MongoClient
import certifi

client = MongoClient(
    "mongodb+srv://ashokkurapati5_db_user:Ashok7093@cluster0.s5ium9e.mongodb.net/?appName=Cluster0",
    tlsCAFile=certifi.where()
)

db = client["crm_db"]

lead_collection = db["leads"]
target_collection = db["targets"]