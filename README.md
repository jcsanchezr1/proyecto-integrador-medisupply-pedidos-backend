# MediSupply Orders Backend

Sistema de gestión de pedidos para MediSupply.

## Descripción

Este servicio se encarga de la gestión de pedidos en el sistema MediSupply, incluyendo la creación, consulta, actualización y seguimiento de pedidos.

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
│   │   └── health_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base_model.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── base_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── base_service.py
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
3. Configurar variables de entorno
4. Ejecutar: `python app.py`

## Endpoints

- `GET /orders/ping` - Health check del servicio

## Desarrollo

El servicio corre en el puerto 8085 por defecto.

## Docker

```bash
docker build -t medisupply-pedidos-backend .
docker run -p 8085:8080 medisupply-pedidos-backend
```