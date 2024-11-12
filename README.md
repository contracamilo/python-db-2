# Proyecto de Tienda Backend API - FastAPI, MongoDB, JWT

Este proyecto es una API para una tienda en línea que permite a los usuarios realizar varias operaciones, como la visualización de productos, gestión de carritos de compra personalizados, autenticación de usuarios con tokens JWT, y la finalización de compras. La API está desarrollada en **FastAPI** y utiliza **MongoDB** para el almacenamiento de datos.

## Tabla de Contenidos

1. [Requerimientos](#requerimientos)
2. [Configuración](#configuración)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Descripción de los Endpoints](#descripción-de-los-endpoints)
5. [Modelos de Datos](#modelos-de-datos)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Errores y Mensajes de Respuesta](#errores-y-mensajes-de-respuesta)

---

## Requerimientos

- **Python 3.9+**
- **FastAPI**
- **Motor** para operaciones asíncronas con MongoDB
- **MongoDB** (puede ser local o en la nube)
- **Pydantic v2** para la validación de modelos
- **Email Validator** para la validación de correos electrónicos en los modelos de usuario
- **JWT** para la autenticación de usuarios

## Configuración

1. **Instalar dependencias**: Ejecuta el siguiente comando para instalar los paquetes necesarios desde `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar las variables de entorno**: Crea un archivo `.env` en el directorio raíz y define la conexión a MongoDB, la clave secreta para los JWT, y la configuración del token.

   ```plaintext
   MONGO_URL=mongodb://<usuario>:<contraseña>@<host>:<puerto>/<base_de_datos>
   SECRET_KEY=tu_clave_secreta_para_jwt
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Iniciar la API**: Usa `uvicorn` para iniciar el servidor de desarrollo de FastAPI.

   ```bash
   uvicorn main:app --reload
   ```

4. **Documentación interactiva**: Accede a la documentación de la API en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Estructura del Proyecto

```plaintext
Proyecto/
├── app/
│   ├── models/                 # Modelos de datos
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── user.py
│   ├── repositories/           # Lógica de negocio
│   │   ├── product_repository.py
│   │   ├── cart_repository.py
│   │   └── user_repository.py
│   ├── routers/                # Rutas o endpoints
│   │   └── app_router.py
│   ├── auth/                   # Funciones de autenticación
│   │   └── auth.py
│   ├── database.py             # Configuración de la base de datos
├── .env                        # Variables de entorno
└── main.py                     # Punto de entrada de la API
```

---

## Descripción de los Endpoints

### Usuarios

- **POST `/register`**: Registro de un nuevo usuario.
- **POST `/login`**: Autenticación de usuario. Devuelve un token JWT que permite al usuario acceder a los endpoints protegidos.

### Productos

- **GET `/products`**: Obtiene todos los productos.
- **GET `/products/{category}`**: Obtiene los productos de una categoría específica.
- **POST `/products`**: Crea un nuevo producto (requiere autenticación).

### Carrito

- **POST `/cart`**: Agrega o actualiza un producto en el carrito de un usuario específico (requiere autenticación).
- **GET `/cart`**: Muestra el contenido del carrito del usuario autenticado.

### Checkout

- **POST `/checkout`**: Finaliza la compra, verifica el stock de cada producto, actualiza el inventario y vacía el carrito del usuario autenticado.

---

## Modelos de Datos

### Modelo `User`

Representa a un usuario registrado en la tienda.

```python
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    hashed_password: str
```

### Modelo `Product`

Representa un producto en la tienda.

```python
class Product(BaseModel):
    id: Optional[str] = None
    name: str
    category: str
    price: float
    stock: int
```

### Modelo `CartItem`

Representa un ítem en el carrito de un usuario.

```python
class CartItem(BaseModel):
    product_id: str
    quantity: int
```

### Modelo `Cart`

Representa el carrito completo de un usuario.

```python
class Cart(BaseModel):
    user_id: str
    items: List[CartItem]
```

---

## Ejemplos de Uso

### 1. Registro de Usuario

**Endpoint**: `POST /register`

**Body**:
```json
{
    "name": "John Doe",
    "email": "johndoe@example.com",
    "password": "password123"
}
```

**Respuesta**:
```json
{
    "message": "Usuario registrado exitosamente"
}
```

### 2. Inicio de Sesión

**Endpoint**: `POST /login`

**Body**:
```json
{
    "email": "johndoe@example.com",
    "password": "password123"
}
```

**Respuesta**:
```json
{
    "access_token": "<token_jwt>",
    "token_type": "bearer",
    "user_id": "<user_id>"
}
```

### 3. Crear un Producto

**Endpoint**: `POST /products` (requiere autenticación)

**Body**:
```json
{
    "name": "Teclado Mecánico",
    "category": "Electronics",
    "price": 120.00,
    "stock": 50
}
```

**Respuesta**:
```json
{
    "id": "generated_object_id",
    "name": "Teclado Mecánico",
    "category": "Electronics",
    "price": 120.00,
    "stock": 50
}
```

### 4. Agregar un Producto al Carrito

**Endpoint**: `POST /cart` (requiere autenticación)

**Body**:
```json
{
    "product_id": "product_object_id_here",
    "quantity": 2
}
```

**Respuesta**:
```json
{
    "message": "Producto agregado o actualizado en el carrito"
}
```

### 5. Ver el Contenido del Carrito

**Endpoint**: `GET /cart` (requiere autenticación)

**Respuesta**:
```json
{
    "user_id": "<user_id>",
    "items": [
        {
            "product_id": "product_object_id_here",
            "name": "Teclado Mecánico",
            "category": "Electronics",
            "price": 120.00,
            "quantity": 2
        }
    ]
}
```

### 6. Realizar la Compra

**Endpoint**: `POST /checkout` (requiere autenticación)

**Respuesta**:
```json
{
    "message": "Compra realizada exitosamente"
}
```

---

## Errores y Mensajes de Respuesta

1. **401 Unauthorized**:
   - `{"detail": "Email o contraseña incorrectos"}`: Credenciales inválidas en el login.
   - `{"detail": "No autenticado"}`: Intento de acceder a un endpoint protegido sin un token JWT válido.

2. **404 Not Found**:
   - `{"detail": "Carrito no encontrado."}`: El carrito del usuario no existe.
   - `{"detail": "Producto no encontrado."}`: El producto solicitado no existe en la base de datos.

3. **400 Bad Request**:
   - `{"detail": "Stock insuficiente para la cantidad solicitada."}`: El stock del producto es insuficiente para la cantidad solicitada.

4. **500 Internal Server Error**:
   - Generalmente se debe a errores en la conexión a la base de datos o problemas de lógica. Se recomienda revisar los logs del servidor para obtener detalles específicos.

---

