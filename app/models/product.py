from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # Campo opcional para MongoDB
    name: str
    category: str
    price: float
    stock: int

    class Config:
        allow_population_by_field_name = True  # Permitir que el campo `id` mapee a `_id`
