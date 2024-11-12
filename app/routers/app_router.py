from fastapi import APIRouter, Query, HTTPException, Depends, status
from app.auth.auth import create_access_token, verify_token, get_current_user
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.user import User, UserCreate, UserLogin
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.database import MongoDBConnection
from datetime import timedelta
from passlib.context import CryptContext

from app.repositories.user_repository import UserRepository

router = APIRouter()

# Obtener la conexión de la base de datos y repositorios`
db = MongoDBConnection().get_db()
product_repo = ProductRepository(db)
cart_repo = CartRepository(db)
user_repo = UserRepository(db)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    existing_user = await user_repo.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado.")

    hashed_password = pwd_context.hash(user_data.password)
    user = User(name=user_data.name, email=user_data.email, hashed_password=hashed_password)
    new_user = await user_repo.create_user(user)
    return new_user


@router.get("/products", response_model=list[Product])
async def get_all_products():
    """Endpoint para obtener todos los productos."""
    try:
        products = await product_repo.get_all_products()
        return products
    except Exception as e:
        # Captura el error y devuelve un mensaje detallado
        raise HTTPException(status_code=500, detail="Error al obtener productos: " + str(e))


@router.get("/products/{category}", response_model=list[Product])
async def get_products_by_category(category: str):
    """Endpoint para obtener productos por categoría."""
    try:
        products = await product_repo.get_products_by_category(category)

        if not products:
            raise HTTPException(status_code=404, detail="No se encontraron productos en esta categoría.")
        return products
    except Exception as e:
        print("Error en get_products_by_category:", e)  # Log de error
        raise HTTPException(status_code=500, detail="Error interno del servidor: " + str(e))


@router.post("/cart")
async def add_to_cart(item: CartItem, current_user: User = Depends(get_current_user)):
    """
    Endpoint para agregar o actualizar un producto en el carrito del usuario autenticado.
    """
    user_id = current_user.id  # Extraído del token JWT

    # Verificar si el producto existe y tiene suficiente stock
    product = await product_repo.get_product_by_id(item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Stock insuficiente para la cantidad solicitada.")

    # Llamar a `add_to_cart` del repositorio con `user_id` y `item` ya instanciado como `CartItem`
    await cart_repo.add_to_cart(user_id=user_id, item=item)

    # Actualizar el stock del producto en la base de datos después de agregarlo al carrito
    await product_repo.update_stock(item.product_id, -item.quantity)

    return {"message": "Producto agregado o actualizado en el carrito"}


@router.get("/cart", response_model=Cart)
async def get_user_cart(current_user: User = Depends(get_current_user)):
    """Endpoint para ver el contenido del carrito de un usuario con detalles de los productos."""
    user_id = current_user.id
    cart = await cart_repo.get_cart(user_id)
    if not cart.items:
        raise HTTPException(status_code=404, detail="Carrito vacío o no encontrado.")
    return cart


@router.post("/checkout")
async def checkout(user_id: str = Depends(verify_token)):
    """Endpoint para finalizar la compra."""
    try:
        # Procesa el checkout y maneja el stock de productos
        result = await cart_repo.checkout(user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor: " + str(e))


@router.post("/products", response_model=Product)
async def create_product(product: Product):
    """Endpoint para crear un nuevo producto en la tienda."""
    try:
        new_product = await product_repo.create_product(product)
        return new_product
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear el producto: " + str(e))


@router.post("/login")
async def login(user_data: UserLogin):
    # Verificar si el usuario existe
    user = await user_repo.get_user_by_email(user_data.email)
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar el token de acceso JWT
    access_token_expires = timedelta(minutes=60)  # Expira en 30 minutos
    access_token = create_access_token(data={"sub": user.id}, expires_delta=access_token_expires)

    # Devolver el token de acceso y el ID del usuario
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }
