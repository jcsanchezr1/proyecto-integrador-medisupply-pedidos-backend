from flask import request
from flask_restful import Resource
from ..services.order_service import OrderService
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session


class OrderTruckController(BaseController):
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def get(self):
        assigned_truck = request.args.get('assigned_truck', type=str, default=None)
        scheduled_delivery_date = request.args.get('scheduled_delivery_date', type=str, default=None)
        
        try:
            orders = self.order_service.get_orders_by_truck_and_date(assigned_truck, scheduled_delivery_date)
            
            enriched_orders = []
            for order in orders:
                enriched_order = self.order_service._enrich_order_items_with_product_info(order)
                enriched_orders.append(enriched_order)
            
            if not enriched_orders:
                filter_msg = []
                if assigned_truck:
                    filter_msg.append(f"camión {assigned_truck}")
                if scheduled_delivery_date:
                    filter_msg.append(f"fecha {scheduled_delivery_date}")
                
                message = "No hay pedidos"
                if filter_msg:
                    message += f" para {' y '.join(filter_msg)}"
                else:
                    message += " en el sistema"
                
                return self.success_response(
                    data=[],
                    message=message
                )
            
            message = "Pedidos obtenidos exitosamente"
            if assigned_truck or scheduled_delivery_date:
                filter_msg = []
                if assigned_truck:
                    filter_msg.append(f"camión {assigned_truck}")
                if scheduled_delivery_date:
                    filter_msg.append(f"fecha {scheduled_delivery_date}")
                message += f" (filtrados por: {', '.join(filter_msg)})"
            
            return self.success_response(
                data=[order.to_dict() for order in enriched_orders],
                message=message
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)

