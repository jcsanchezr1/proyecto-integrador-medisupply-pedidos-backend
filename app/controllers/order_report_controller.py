"""
Controlador para reportes de pedidos
"""
from flask import request
from flask_restful import Resource
from ..services.order_service import OrderService
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session


class OrderMonthlyReportController(BaseController):
    """Controlador para reporte mensual de pedidos"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def get(self):
        """
        Obtiene el reporte consolidado de pedidos por mes del último año
        
        Returns:
            JSON con datos mensuales estructurados para gráficas:
            - monthly_data: array con datos de cada mes
            - summary: resumen general del período
            - period: rango de fechas del reporte
        """
        try:
            report_data = self.order_service.get_monthly_report()
            
            if not report_data['monthly_data']:
                return self.success_response(
                    data=report_data,
                    message="No hay pedidos en el último año"
                )
            
            return self.success_response(
                data=report_data,
                message="Reporte mensual generado exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class OrderTopClientsController(BaseController):
    """Controlador para reporte de top clientes"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def get(self):
        """
        Obtiene los top 5 clientes con más pedidos en el último trimestre
        
        Returns:
            JSON con:
                - period: rango de fechas del trimestre
                - top_clients: lista con client_id, orders_count y client_name
        """
        try:
            report_data = self.order_service.get_top_clients_report()
            
            if not report_data['top_clients']:
                return self.success_response(
                    data=report_data,
                    message="No hay clientes con pedidos en el último trimestre"
                )
            
            return self.success_response(
                data=report_data,
                message="Reporte de top clientes generado exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)

