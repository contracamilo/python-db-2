from app.models.product import Product
from bson import ObjectId
from fastapi import HTTPException


class ProductRepository:
    def __init__(self, db):
        self.collection = db["products"]

    async def get_all_products(self):
        products_cursor = self.collection.find()
        products = await products_cursor.to_list(length=None)

        for product in products:
            if "_id" in product and isinstance(product["_id"], ObjectId):
                product["_id"] = str(product["_id"])

        return [Product(**product) for product in products]

    async def get_products_by_category(self, category: str):
        products = await self.collection.find({"category": category}).to_list(length=100)
        for product in products:
            product["_id"] = str(product["_id"])
        return products

    async def update_stock(self, product_id: str, quantity: int):
        product = await self.collection.find_one({"_id": ObjectId(product_id)})

        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        if product["stock"] < quantity:
            raise HTTPException(status_code=400, detail="Stock insuficiente para este producto.")

        result = await self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"stock": -quantity}}
        )
        return result.modified_count > 0

    async def create_product(self, product: Product):
        # Primero, intentamos buscar el producto por `nombre`
        existing_product_by_name = await self.collection.find_one({"name": product.name})

        # Luego, si tiene `product.id`, buscamos específicamente por `_id`
        existing_product_by_id = None
        if product.id:
            try:
                existing_product_by_id = await self.collection.find_one({"_id": ObjectId(product.id)})
            except Exception as e:
                raise HTTPException(status_code=400, detail="ID de producto inválido.")

        # Verificamos si encontramos el producto por nombre o por ID
        if existing_product_by_id:
            # Si existe por ID, incrementamos el stock
            await self.collection.update_one(
                {"_id": existing_product_by_id["_id"]},
                {"$inc": {"stock": 1}}
            )
            existing_product_by_id["stock"] += 1
            existing_product_by_id["_id"] = str(existing_product_by_id["_id"])
            return Product(**existing_product_by_id)

        elif existing_product_by_name:
            # Si existe solo por nombre, también incrementamos el stock
            await self.collection.update_one(
                {"_id": existing_product_by_name["_id"]},
                {"$inc": {"stock": 1}}
            )
            existing_product_by_name["stock"] += 1
            existing_product_by_name["_id"] = str(existing_product_by_name["_id"])
            return Product(**existing_product_by_name)

        # Si no existe por ID ni por nombre, insertamos un nuevo producto
        product_data = product.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(product_data)
        product_data["_id"] = str(result.inserted_id)
        return Product(**product_data)

    async def get_product_by_id(self, product_id: str):
        try:
            product = await self.collection.find_one({"_id": ObjectId(product_id)})
            if product:
                product["_id"] = str(product["_id"])
                return Product(**product)
            else:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error al obtener el producto.")
