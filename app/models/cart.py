from pydantic import BaseModel, Field
from typing import Optional, List


class CartItem(BaseModel):
    product_id: str
    quantity: int
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class Cart(BaseModel):
    user_id: str
    items: List[CartItem]
