from pydantic import BaseModel
from typing import List


class CartItem(BaseModel):
    product_id: str
    quantity: int


class Cart(BaseModel):
    user_id: str
    items: List[CartItem]
