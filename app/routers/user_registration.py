from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from database.create_database import get_db
from models.validation import UserCreate, UserResponse, validate_avatar
from crud.create_users import create_user

router = APIRouter()


@router.post("/api/clients/create")
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    email: EmailStr = Form(...),
    gender: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    avatar: UploadFile = File(None), session: AsyncSession=Depends(get_db)):

    user = UserCreate(
        username=username,
        password=password,
        email=email,
        gender=gender,
        first_name=first_name,
        last_name=last_name
    )

    errors = await validate_avatar(avatar)

    if errors:
        raise HTTPException(status_code=400, detail=f"{errors}")
    
    username, email = await create_user(user, avatar, session)
    return UserResponse(
        username=username,
        email=email,
        message="Пользователь успешно зарегистрирован"
    )