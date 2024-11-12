from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # Campo opcional para MongoDB
    name: str
    category: str
    price: float
    stock: int

    class Config:
        populate_by_name = True
