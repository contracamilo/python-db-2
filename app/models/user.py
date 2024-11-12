from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Optional


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    hashed_password: str

    class Config:
        populate_by_name = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
