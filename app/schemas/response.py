from pydantic import BaseModel, EmailStr, Field
from typing import List
from schemas.users import UserDataSchema

class UserDataResponseSchema(BaseModel):
    email: str 
    username: str 
    message: str 


class UserListDataResponseSchema(BaseModel):
    user_list: List[UserDataSchema]

