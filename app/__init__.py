"""
Aplicación principal del sistema de pedidos MediSupply
"""
import os
import logging
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app():
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Configurar CORS
    cors = CORS(app)
    
    # Inicializar base de datos
    from .config.database import create_tables
    create_tables()
    
    # Configurar rutas
    configure_routes(app)
    
    return app


def configure_routes(app):
    """Configura las rutas de la aplicación"""
    from .controllers.health_controller import HealthCheckView
    from .controllers.order_controller import OrderController, OrderDeleteAllController
    from .controllers.order_create_controller import OrderCreateController
    from .controllers.order_truck_controller import OrderTruckController
    from .controllers.order_report_controller import OrderMonthlyReportController, OrderTopClientsController, OrderTopProductsController
    from .controllers.order_informes_controller import OrderSellerStatusSummaryController, OrderSellerClientsSummaryController, OrderSellerMonthlyController
    
    api = Api(app)
    
    # Health check endpoint
    api.add_resource(HealthCheckView, '/orders/ping')
    
    # Order endpoints
    api.add_resource(OrderCreateController, '/orders/create')
    api.add_resource(OrderController, '/orders')
    api.add_resource(OrderDeleteAllController, '/orders/delete-all')
    api.add_resource(OrderTruckController, '/orders/by-truck')
    
    # Report endpoints
    api.add_resource(OrderMonthlyReportController, '/orders/reports/monthly')
    api.add_resource(OrderTopClientsController, '/orders/reports/top-clients')
    api.add_resource(OrderTopProductsController, '/orders/reports/top-products')
    
    # Informes por vendedor endpoints
    api.add_resource(OrderSellerStatusSummaryController, '/orders/informes/seller/status-summary')
    api.add_resource(OrderSellerClientsSummaryController, '/orders/informes/seller/clients-summary')
    api.add_resource(OrderSellerMonthlyController, '/orders/informes/seller/monthly')
