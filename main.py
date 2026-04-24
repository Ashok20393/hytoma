from fastapi import FastAPI
from routes.lead_routes import router as lead_router
from routes.auth_routes import router as auth_router
from routes.dashboard_routes import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.include_router(auth_router)
app.include_router(lead_router)
app.include_router(dashboard_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://hytoma.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "CRM Backend Running"}

