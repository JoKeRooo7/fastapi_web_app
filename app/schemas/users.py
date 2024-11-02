from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    username: str = Field(..., description="Уникальное имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя (не менее 8 символов)")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    gender: str = Field(..., description="Пол пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя (не менее 8 символов)")


class UserMatchSchema(BaseModel):
    current_id: int = Field(..., description="id текущего пользователя")
    other_id: int  = Field(..., description="id другого пользователя")
    

class UserResponseSchema(BaseModel):
    email: str 
    username: str 
    message: str 

