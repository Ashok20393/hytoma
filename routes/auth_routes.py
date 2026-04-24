from fastapi import APIRouter, Response, Body
from utils.auth import create_token
from database.database import db

router = APIRouter()

@router.post("/login")                          # ✅ Response injected by FastAPI
def login(response: Response, data: dict = Body(...)):
    username = data.get("username")
    password = data.get("password")

    user = db.users.find_one({"username": username, "password": password})

    if not user:
        return {"error": "Invalid credentials"}

    token = create_token({"username": user["username"], "role": user["role"]})

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",   # ✅ correct for localhost
        secure=False,
        path="/"
    )
    return {"message": "Login success", "role": user["role"]}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"message": "Logged out"}