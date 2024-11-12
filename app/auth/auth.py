import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database import MongoDBConnection
from app.models.user import User
from bson import ObjectId


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
db_connection = MongoDBConnection()
db = db_connection.get_db()
users_collection = db["users"]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Obtiene el usuario completo a partir del token JWT."""
    user_id = await verify_token(token)

    # Busca el usuario en la base de datos usando el user_id
    user_data = await users_collection.find_one({"_id": ObjectId(user_id)})

    if user_data is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Convierte el documento de MongoDB a un objeto User
    return User(
        id=str(user_data["_id"]),
        name=user_data["name"],
        email=user_data["email"],
        hashed_password=user_data["hashed_password"]
    )
