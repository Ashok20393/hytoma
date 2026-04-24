from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi


load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URL"),
    tlsCAFile=certifi.where()
)

db = client["crm_db"]

lead_collection = db["leads"]
target_collection = db["targets"]