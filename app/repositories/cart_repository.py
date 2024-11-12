from fastapi import HTTPException
from bson import ObjectId
from app.models.cart import CartItem, Cart


class CartRepository:
    def __init__(self, db):
        self.collection = db["carts"]
        self.products_collection = db["products"]

    async def get_cart(self, user_id: str) -> Cart:
        """Obtiene el carrito de un usuario específico con los detalles de los productos."""
        cart_data = await self.collection.find_one({"user_id": user_id})
        if not cart_data:
            # Retornar un carrito vacío si no existe en la base de datos
            return Cart(user_id=user_id, items=[])

        # Si el carrito existe, procesamos los items con detalles del producto
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
        """Añade un producto al carrito de un usuario o actualiza la cantidad si ya existe, sin agregar detalles innecesarios."""
        cart = await self.get_cart(user_id)
        item_found = False

        # Actualizar la cantidad si el producto ya existe en el carrito
        for existing_item in cart.items:
            if existing_item.product_id == item.product_id:
                existing_item.quantity += item.quantity
                item_found = True
                break

        # Si el producto no está en el carrito, agrégalo solo con product_id y quantity
        if not item_found:
            cart.items.append(CartItem(product_id=item.product_id, quantity=item.quantity))

        # Guardar el carrito en la base de datos con solo product_id y quantity en cada item
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": [{"product_id": item.product_id, "quantity": item.quantity} for item in cart.items]}},
            upsert=True
        )

    async def checkout(self, user_id: str):
        """Realiza el checkout, reduce el stock de cada producto en el carrito según la cantidad y luego vacía el carrito."""
        # Obtener el carrito del usuario
        cart = await self.get_cart(user_id)

        if not cart.items:
            raise HTTPException(status_code=400, detail="El carrito está vacío.")

        # Procesar cada producto en el carrito
        for item in cart.items:
            product_id = ObjectId(item.product_id)
            # Buscar el producto en la colección de productos usando _id
            product = await self.products_collection.find_one({"_id": product_id})
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto con ID {item.product_id} no encontrado.")

            # Verificar si hay stock suficiente para la cantidad solicitada
            if product["stock"] < item.quantity:
                raise HTTPException(status_code=400,
                                    detail=f"Stock insuficiente para el producto con ID {item.product_id}.")

            # Reducir el stock del producto en la cantidad especificada en el carrito
            update_result = await self.products_collection.update_one(
                {"_id": product_id},
                {"$inc": {"stock": -item.quantity}}
            )

            # Verificar si la reducción de stock fue exitosa
            if update_result.modified_count == 0:
                raise HTTPException(status_code=500,
                                    detail=f"No se pudo actualizar el stock del producto con ID {item.product_id}.")

        # Limpiar el carrito después de un checkout exitoso
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"items": []}}
        )

        return {"message": "Compra realizada con éxito y carrito vaciado."}

    async def clear_cart(self, user_id: str):
        """Limpia el carrito de un usuario específico."""
        await self.collection.delete_one({"user_id": user_id})
