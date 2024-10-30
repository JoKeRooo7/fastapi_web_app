import io
from pydantic import BaseModel, EmailStr, Field
from PIL import Image


class UserCreate(BaseModel):
    username: str = Field(..., description="Уникальное имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя (не менее 8 символов)")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    gender: str = Field(..., description="Пол пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")


class UserResponse(BaseModel):
    email: str
    username: str
    message: str


async def validate_avatar(avatar):
    if not (avatar.filename.endswith('.jpeg') or avatar.filename.endswith('.jpg') or avatar.filename.endswith('.png')):
        return "Неверный формат"
    try:
        contents = await avatar.read()
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception as e:
        return "Некорректное изображение"
    finally:
        await avatar.seek(0)
    return None