from app.models.user import User
from pymongo import ReturnDocument
from bson import ObjectId
from typing import Optional


class UserRepository:
    def __init__(self, db):
        self.collection = db["users"]

    async def create_user(self, user: User):
        # Insertar usuario y devolver el documento completo con `_id` como string
        user_data = user.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return User(**user_data)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            user_data["_id"] = str(user_data["_id"])
            return User(**user_data)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data["_id"] = str(user_data["_id"])
            return User(**user_data)
        return None
