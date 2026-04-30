from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load .env explicitly
load_dotenv(dotenv_path=BASE_DIR / ".env")



from fastapi import FastAPI
from routes.lead_routes import router as lead_router
from routes.auth_routes import router as auth_router
from routes.inventory_routes import router as inventory_router
from routes.dashboard_routes import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
from routes.complaint_routes import router as complaint_router
from routes.movement_routes import router as movement_routes


app = FastAPI()

app.include_router(auth_router)
app.include_router(lead_router)
app.include_router(dashboard_router)
app.include_router(inventory_router)
app.include_router(complaint_router)
app.include_router(movement_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://hytoma.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "CRM Backend Running"}

