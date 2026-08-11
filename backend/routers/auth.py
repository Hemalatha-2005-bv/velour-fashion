"""
Auth router — register, login.
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
import bcrypt

from models.schemas import UserRegister, UserLogin, TokenResponse, UserOut
from middleware.auth import create_access_token, get_current_user
from utils.file_store import read_json, write_json

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    users = await read_json("users.json")
    # Check duplicate email
    if any(u["email"].lower() == data.email.lower() for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(data.password)
    new_user = {
        "id": user_id,
        "name": data.name,
        "email": data.email.lower(),
        "hashed_password": hashed_pw,
        "created_at": datetime.utcnow().isoformat(),
    }
    users.append(new_user)
    await write_json("users.json", users)

    token = create_access_token({"sub": user_id, "email": data.email.lower()})
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user_id, name=data.name, email=data.email.lower(), created_at=new_user["created_at"]),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    users = await read_json("users.json")
    user = next((u for u in users if u["email"].lower() == data.email.lower()), None)
    if not user or not check_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user["id"], "email": user["email"]})
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user["id"], name=user["name"], email=user["email"], created_at=user["created_at"]),
    )



@router.get("/me", response_model=UserOut)
async def get_current_user_profile(token_data: dict = Depends(get_current_user)):
    """Return the authenticated user's profile from stored user records."""
    users = await read_json("users.json")
    user = next((u for u in users if u["id"] == token_data["user_id"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(id=user["id"], name=user["name"], email=user["email"], created_at=user["created_at"])

