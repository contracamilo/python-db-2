# Proyecto de Tienda API - Python, MongoDB y FastAPI

Este proyecto es una API de tienda en línea que permite a los usuarios realizar operaciones como visualizar productos, gestionar carritos de compra y completar el proceso de compra. La API está desarrollada en **FastAPI** con una base de datos **MongoDB**.

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
- **MongoDB** (puede ser local o una instancia en la nube)

## Configuración

1. **Instalar dependencias**: Ejecuta el siguiente comando para instalar los paquetes necesarios desde `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar las variables de entorno**: Crea un archivo `.env` en el directorio raíz y define la conexión a MongoDB.

   ```plaintext
   MONGO_URL=mongodb://<usuario>:<contraseña>@<host>:<puerto>/<base_de_datos>
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
│   │   └── cart.py
│   ├── repositories/           # Lógica de negocio
│   │   ├── product_repository.py
│   │   └── cart_repository.py
│   ├── routers/                # Rutas o endpoints
│   │   └── app_router.py
│   ├── database.py             # Configuración de la base de datos
├── .env                        # Variables de entorno
└── main.py                     # Punto de entrada de la API
```

---

## Descripción de los Endpoints

### Productos

- **GET `/products`**: Obtiene todos los productos.
- **GET `/products/{category}`**: Obtiene los productos de una categoría específica.
- **POST `/products`**: Crea un nuevo producto.

### Carrito

- **POST `/cart`**: Agrega un producto al carrito de un usuario autenticado o actualiza la cantidad si ya existe en el carrito.
- **GET `/cart`**: Muestra el contenido del carrito de un usuario autenticado. Los productos en el carrito se proyectan con información completa como nombre, precio y stock.

### Checkout

- **POST `/checkout`**: Finaliza la compra del carrito del usuario autenticado. Este proceso:
   - Verifica el stock de cada producto en el carrito.
   - Actualiza las cantidades de los productos en la base de datos.
   - Vacía el carrito del usuario una vez que la compra es exitosa.

---

## Modelos de Datos

### Modelo `Product`

Representa un producto en la tienda.

```python
class Product(BaseModel):
    id: Optional[str] = None  # Generado por MongoDB
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

### 1. Crear un Producto

**Endpoint**: `POST /products`

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

### 2. Agregar un Producto al Carrito

**Endpoint**: `POST /cart`

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

### 3. Ver el Contenido del Carrito

**Endpoint**: `GET /cart`

**Respuesta**:
```json
{
    "user_id": "user123",
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

### 4. Realizar la Compra (Checkout)

**Endpoint**: `POST /checkout`

**Respuesta**:
```json
{
    "message": "Compra realizada con éxito y carrito vaciado."
}
```

---

## Errores y Mensajes de Respuesta

1. **404 Not Found**:
   - `{"detail": "Carrito no encontrado."}`: El carrito del usuario no existe.
   - `{"detail": "Producto no encontrado."}`: El producto solicitado no existe en la base de datos.

2. **400 Bad Request**:
   - `{"detail": "Stock insuficiente para el producto {nombre_producto}."}`: El stock del producto es insuficiente para la cantidad solicitada.

3. **500 Internal Server Error**:
   - Generalmente se debe a errores en la conexión a la base de datos o problemas de lógica. Se recomienda revisar los logs del servidor para obtener detalles específicos.

---