from pydantic import BaseModel
from typing import List, Optional


class CartItem(BaseModel):
    product_id: str
    quantity: int
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


class Cart(BaseModel):
    user_id: str
    items: List[CartItem]
