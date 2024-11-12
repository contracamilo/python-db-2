from fastapi import HTTPException
from app.models.cart import Cart, CartItem
from bson import ObjectId


class CartRepository:
    def __init__(self, db):
        self.collection = db["carts"]
        self.products_collection = db["products"]

    async def get_cart(self, user_id: str) -> Cart:
        """Obtiene el carrito de un usuario específico con los detalles de los productos."""
        cart_data = await self.collection.find_one({"user_id": user_id})
        if not cart_data:
            return Cart(user_id=user_id, items=[])

        # Traer detalles del producto para cada item en el carrito
        items_with_details = []
        for item in cart_data.get("items", []):
            product_data = await self.products_collection.find_one({"_id": ObjectId(item["product_id"])})
            if not product_data:
                continue  # Ignorar productos que ya no existen
            items_with_details.append(
                CartItem(
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    name=product_data.get("name"),
                    price=product_data.get("price"),
                    category=product_data.get("category")
                )
            )

        return Cart(user_id=user_id, items=items_with_details)

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
