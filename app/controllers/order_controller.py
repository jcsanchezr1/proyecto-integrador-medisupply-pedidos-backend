"""
Controlador para manejo de pedidos
"""
from flask_restful import Resource, reqparse
from typing import List
from ..services.order_service import OrderService
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderNotFoundError, OrderValidationError, OrderBusinessLogicError
from .base_controller import BaseController


class OrderController(BaseController):
    """Controlador para pedidos"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    def get(self):
        """Obtiene pedidos por cliente o vendedor"""
        from flask import request
        
        # Obtener parámetros de query
        client_id = request.args.get('client_id', type=int)
        vendor_id = request.args.get('vendor_id', type=int)
        
        try:
            # Validar que se proporcione al menos uno de los IDs
            if not client_id and not vendor_id:
                return self.error_response(
                    "Error de validación",
                    "Debe proporcionar client_id o vendor_id",
                    400
                )
            
            # Obtener pedidos según el tipo de usuario
            if client_id:
                orders = self.order_service.get_orders_by_client(client_id)
            elif vendor_id:
                orders = self.order_service.get_orders_by_vendor(vendor_id)
            else:
                orders = []
            
            # Enriquecer items con información del producto
            enriched_orders = []
            for order in orders:
                enriched_order = self.order_service._enrich_order_items_with_product_info(order)
                enriched_orders.append(enriched_order)
            
            if not enriched_orders:
                return self.success_response(
                    data=[],
                    message="No tienes entregas programadas en este momento"
                )
            
            return self.success_response(
                data=[order.to_dict() for order in enriched_orders],
                message="Pedidos obtenidos exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class OrderDeleteAllController(BaseController):
    """Controlador para eliminar todos los pedidos"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    def delete(self):
        """Elimina todos los pedidos"""
        try:
            success = self.order_service.delete_all_orders()
            
            if success:
                return self.success_response(
                    message="Todos los pedidos han sido eliminados exitosamente"
                )
            else:
                return self.error_response(
                    "Error al eliminar pedidos",
                    "No se pudieron eliminar todos los pedidos",
                    500
                )
                
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)
