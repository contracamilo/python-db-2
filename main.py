from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import app_router
from app.database import MongoDBConnection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db_connection = MongoDBConnection()
db = db_connection.get_db()


# Registrar eventos de inicio y apagado
@app.on_event("startup")
async def startup_db_client():
    await db_connection.ensure_collections()


# Registrar rutas
app.include_router(app_router.router)


@app.on_event("shutdown")
async def shutdown_db_client():
    db_connection.client.close()
