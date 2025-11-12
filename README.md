# MediSupply Orders Backend

Sistema de gestión de pedidos para MediSupply.

## Descripción

Este servicio se encarga de la gestión de pedidos en el sistema MediSupply, permitiendo a clientes y vendedores consultar las entregas de pedidos programadas con información detallada de fecha, productos, cantidades, estado de preparación y camión asignado.

## Estructura del Proyecto

```
proyecto-integrador-medisupply-pedidos-backend/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── base_controller.py
│   │   ├── health_controller.py
│   │   └── order_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   └── db_models.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   └── order_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   └── order_service.py
│   ├── utils/
│   │   └── __init__.py
│   └── exceptions/
│       ├── __init__.py
│       └── custom_exceptions.py
├── tests/
├── .github/workflows/
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno (ver sección Variables de Entorno)
4. Ejecutar: `python app.py`


## Endpoints

### Health Check
- `GET /orders/ping` - Verifica el estado del servicio
  - **Respuesta**: `"pong"`

### Gestión de Pedidos
- `POST /orders/create` - Crea un nuevo pedido
  - **Cuerpo de la petición**:
    ```json
    {
      "client_id": "123e4567-e89b-12d3-a456-426614174000",
      "total_amount": 150.50,
      "scheduled_delivery_date": "2025-12-25T10:00:00Z",
      "items": [
        {
          "product_id": 1,
          "quantity": 2
        },
        {
          "product_id": 2,
          "quantity": 1
        }
      ]
    }
    ```
  - **Validaciones**:
    - Debe proporcionar al menos `client_id` O `vendor_id`
    - `total_amount` debe ser un número mayor a 0
    - `scheduled_delivery_date` debe tener formato ISO 8601 válido y no ser una fecha pasada
    - `items` debe ser un array con al menos un item
    - Cada item debe tener `product_id` y `quantity` válidos
    - Verifica stock suficiente en el servicio de inventarios
  - **Respuesta exitosa** (201):
    ```json
    {
      "success": true,
      "message": "Pedido creado exitosamente",
      "data": {
        "id": 1,
        "order_number": "PED-20251022-12345",
        "client_id": "123e4567-e89b-12d3-a456-426614174000",
        "vendor_id": null,
        "status": "En Preparación",
        "total_amount": 150.50,
        "scheduled_delivery_date": "2025-12-25T10:00:00Z",
        "assigned_truck": "CAM-001",
        "created_at": "2025-10-22T08:00:00",
        "updated_at": "2025-10-22T08:00:00",
        "items": []
      }
    }
    ```
  - **Errores comunes**:
    - **400**: Campos obligatorios faltantes, formato de fecha inválido, fecha pasada
    - **422**: Stock insuficiente para algún producto

- `GET /orders?client_id={uuid}` - Obtiene pedidos por ID de cliente
- `GET /orders?vendor_id={uuid}` - Obtiene pedidos por ID de vendedor
  - **Parámetros**: 
    - `client_id` (string, opcional): UUID del cliente
    - `vendor_id` (string, opcional): UUID del vendedor
  - **Validación**: Debe proporcionar `client_id` O `vendor_id` (no ambos)
  - **Respuesta exitosa**:
    ```json
    {
      "success": true,
      "message": "Pedidos obtenidos exitosamente",
      "data": [
        {
          "id": 1,
          "order_number": "PED-20241207-12345",
          "client_id": "550e8400-e29b-41d4-a716-446655440000",
          "vendor_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
          "status": "Recibido",
          "scheduled_delivery_date": "2024-12-08T10:00:00",
          "assigned_truck": "TRK-001",
          "created_at": "2024-12-07T08:00:00",
          "updated_at": "2024-12-07T08:00:00",
          "items": [
            {
              "id": 1,
              "product_id": 123,
              "product_name": "Producto Ejemplo",
              "product_image_url": null,
              "quantity": 5,
              "unit_price": 100.0,
              "order_id": 1
            }
          ]
        }
      ]
    }
    ```
  - **Sin pedidos**:
    ```json
    {
      "success": true,
      "message": "No tienes entregas programadas en este momento",
      "data": []
    }
    ```

- `DELETE /orders/delete-all` - Elimina todos los pedidos
  - **Respuesta exitosa**:
    ```json
    {
      "success": true,
      "message": "Todos los pedidos han sido eliminados exitosamente"
    }
    ```

### Estados de Pedido
- **Recibido**: Color azul - entrega planificada pero no iniciada
- **En Preparación**: Color morado - pedido siendo alistado en bodega
- **En Tránsito**: Color naranja - pedido despachado, camión en ruta
- **Entregado**: Color verde - entrega completada
- **Devuelto**: Color rojo - entrega que el cliente devolvió

## Base de Datos

El servicio utiliza PostgreSQL como base de datos. Las tablas se crean automáticamente al iniciar la aplicación.

### Tablas Creadas

#### `orders` - Tabla de Pedidos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER (PK) | Identificador único del pedido |
| `order_number` | VARCHAR(20) | Número de pedido (formato: PED-YYYYMMDD-XXXXX) |
| `client_id` | VARCHAR(36) | UUID del cliente (opcional) |
| `vendor_id` | VARCHAR(36) | UUID del vendedor (opcional) |
| `status` | VARCHAR(50) | Estado del pedido (En Preparación, En Tránsito, Entregado, Devuelto) |
| `total_amount` | FLOAT | Monto total del pedido |
| `scheduled_delivery_date` | TIMESTAMP | Fecha programada de entrega |
| `assigned_truck` | VARCHAR(20) | Camión asignado para la entrega (CAM-001, CAM-002, etc.) |
| `created_at` | TIMESTAMP | Fecha de creación del pedido |
| `updated_at` | TIMESTAMP | Fecha de última actualización |

#### `order_items` - Tabla de Items del Pedido
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER (PK) | Identificador único del item |
| `order_id` | INTEGER (FK) | ID del pedido al que pertenece |
| `product_id` | INTEGER | ID del producto |
| `quantity` | INTEGER | Cantidad solicitada |

**Nota**: Los campos `product_name`, `product_image_url` y `unit_price` se consultan dinámicamente del servicio de inventarios y no se almacenan en la base de datos.

### Relaciones
- Un pedido (`orders`) puede tener múltiples items (`order_items`)
- Un item pertenece a un solo pedido
- Relación: `orders.id` → `order_items.order_id`

## Desarrollo

El servicio corre en el puerto 8085 por defecto (mapeado desde el puerto interno 8080).

### Ejecutar Localmente
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URL="postgresql://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db"

# Ejecutar aplicación
python app.py
```

### Ejecutar con Docker Compose
```bash
# Desde el directorio de infraestructura
cd /path/to/proyecto-integrador-medisupply-infraestructura
docker compose up pedidos
```

## Docker

### Construir Imagen
```bash
docker build -t medisupply-pedidos-backend .
```

### Ejecutar Contenedor
```bash
docker run -p 8085:8080 \
  -e DATABASE_URL="postgresql://medisupply_local_user:medisupply_local_password@host.docker.internal:5432/medisupply_local_db" \
  medisupply-pedidos-backend
```

## Testing

### Health Check
```bash
curl http://localhost:8085/orders/ping
# Respuesta: "pong"
```

### Consultar Pedidos por Cliente
```bash
curl "http://localhost:8085/orders?client_id=1"
```

### Consultar Pedidos por Vendedor
```bash
curl "http://localhost:8085/orders?vendor_id=1"
```

### Eliminar Todos los Pedidos
```bash
curl -X DELETE "http://localhost:8085/orders/delete-all"
```