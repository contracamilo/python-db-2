import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError

# Cargar las variables de entorno
load_dotenv()


class MongoDBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            mongo_url = os.getenv("MONGODB_URI")  # Cambiado para coincidir con tu .env
            cls._instance.client = AsyncIOMotorClient(mongo_url)
            cls._instance.db = cls._instance.client[os.getenv("DATABASE_NAME")]

            # Probar la conexión
            try:
                cls._instance.client.admin.command('ping')
                print("Conexión a MongoDB Atlas exitosa.")
            except ServerSelectionTimeoutError as err:
                print(f"Error de conexión: {err}")
                cls._instance = None  # Resetear la instancia para evitar problemas

            # Verificar y crear las colecciones si no existen
            cls._instance.ensure_collections()
        return cls._instance

    def get_db(self):
        return self.db

    async def ensure_collections(self):
        """Verifica y crea las colecciones necesarias."""
        existing_collections = await self.db.list_collection_names()

        # Crear colección "products" si no existe
        if "products" not in existing_collections:
            await self.db.create_collection("products")
            print("Colección 'products' creada.")

        # Crear colección "carts" si no existe
        if "carts" not in existing_collections:
            await self.db.create_collection("carts")
            print("Colección 'carts' creada.")

        # Crear índices en las colecciones
        await self.db.products.create_index("category")
        await self.db.carts.create_index("user_id")
        print("Índices creados en 'products' y 'carts'.")
