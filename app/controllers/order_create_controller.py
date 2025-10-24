"""
Controlador para creación de pedidos
"""
import logging
from flask_restful import Resource
from flask import request
from typing import Dict, Any, Tuple
from ..services.order_service import OrderService
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session

logger = logging.getLogger(__name__)


class OrderCreateController(BaseController, Resource):
    """Controlador para creación de pedidos"""
    
    def __init__(self):
        logger.debug("Inicializando OrderCreateController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def post(self) -> Tuple[Dict[str, Any], int]:
        """POST /orders - Crear un nuevo pedido"""
        logger.info("POST /orders/create - Iniciando creacion de pedido")
        try:
            try:
                data = request.get_json()
            except Exception:
                return self.error_response("Error de validación", "Se requiere un cuerpo JSON válido", 422)
            
            if not data:
                return self.error_response("Error de validación", "Se requiere un cuerpo JSON", 422)

            if not data.get('client_id') and not data.get('vendor_id'):
                return self.error_response("Error de validación", "Debe proporcionar al menos 'client_id' o 'vendor_id'", 422)
            
            if 'items' not in data:
                return self.error_response("Error de validación", "El campo 'items' es obligatorio", 422)
            
            if not isinstance(data['items'], list) or len(data['items']) == 0:
                return self.error_response("Error de validación", "El pedido debe tener al menos un item", 422)
            
            if not data.get('total_amount'):
                return self.error_response("Error de validación", "El campo 'total_amount' es obligatorio", 422)
            
            if not isinstance(data['total_amount'], (int, float)) or data['total_amount'] <= 0:
                return self.error_response("Error de validación", "El 'total_amount' debe ser un número mayor a 0", 422)
            
            if not data.get('scheduled_delivery_date'):
                return self.error_response("Error de validación", "El campo 'scheduled_delivery_date' es obligatorio", 422)

            try:
                from datetime import datetime
                scheduled_date = datetime.fromisoformat(data['scheduled_delivery_date'].replace('Z', '+00:00'))

                if scheduled_date < datetime.now(scheduled_date.tzinfo):
                    return self.error_response("Error de validación", "La fecha programada no puede ser en el pasado", 422)
            except (ValueError, AttributeError):
                return self.error_response("Error de validación", "El 'scheduled_delivery_date' debe tener formato ISO 8601 válido", 422)

            for i, item in enumerate(data['items']):
                if not item.get('product_id'):
                    return self.error_response("Error de validación", f"El item {i+1} debe tener un 'product_id'", 422)
                
                if not item.get('quantity') or not isinstance(item['quantity'], (int, float)) or item['quantity'] <= 0:
                    return self.error_response("Error de validación", f"El item {i+1} debe tener una 'quantity' válida mayor a 0", 422)

            logger.debug("Invocando order_service.create_order")
            order = self.order_service.create_order(data)
            
            return self.created_response(
                data=order.to_dict(),
                message="Pedido creado exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 422)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 422)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)
