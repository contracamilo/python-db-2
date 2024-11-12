from fastapi import HTTPException
from app.models.cart import Cart, CartItem
from bson import ObjectId


class CartRepository:
    def __init__(self, db):
        self.collection = db["carts"]

    async def get_cart(self, user_id: str) -> Cart:
        """Obtiene el carrito de un usuario específico."""
        cart_data = await self.collection.find_one({"user_id": user_id})
        if cart_data:
            # Convertir el carrito a un objeto Cart
            return Cart(**cart_data)
        return Cart(user_id=user_id, items=[])

    async def add_to_cart(self, user_id: str, item: CartItem):
        """Añade un producto al carrito de un usuario o actualiza la cantidad si ya existe."""
        cart = await self.get_cart(user_id)
        item_found = False

        # Actualiza la cantidad si el producto ya existe en el carrito
        for existing_item in cart.items:
            if existing_item.product_id == item.product_id:
                existing_item.quantity += item.quantity
                item_found = True
                break

        # Si el producto no está en el carrito, agrégalo
        if not item_found:
            cart.items.append(item)

        # Guarda el carrito en la base de datos
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [item.dict() for item in cart.items]}},
            upsert=True  # Crea el documento si no existe
        )

    async def clear_cart(self, user_id: str):
        """Limpia el carrito de un usuario específico."""
        await self.collection.delete_one({"user_id": user_id})
