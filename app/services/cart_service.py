from app.models.cart import Cart
from app.repositories.product_repository import ProductRepository


class CartService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def add_to_cart(self, cart: Cart):
        # Lógica para agregar al carrito y verificar disponibilidad
        for item in cart.items:
            product = await self.product_repo.get_product_by_id(item.product_id)
            if product.stock < item.quantity:
                raise ValueError("Stock insuficiente para el producto.")
        # Actualizar inventario
        for item in cart.items:
            await self.product_repo.update_stock(item.product_id, item.quantity)
