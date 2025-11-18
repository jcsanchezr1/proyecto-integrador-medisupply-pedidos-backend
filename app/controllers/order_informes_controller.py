"""
Controlador para informes de pedidos por vendedor
"""
import uuid
from flask import request
from flask_restful import Resource
from ..services.order_service import OrderService
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session


class OrderSellerStatusSummaryController(BaseController):
    """Controlador para informe de estados por vendedor"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def get(self):
        """
        Obtiene el resumen de pedidos por estado para los clientes asignados a un vendedor
        
        Query params:
            seller_id (requerido): UUID del vendedor
            
        Returns:
            JSON con datos de estados estructurados para gráfica de dona
        """
        try:
            seller_id = request.args.get('seller_id', type=str)
            
            if not seller_id:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'seller_id' es obligatorio",
                    400
                )
            
            try:
                uuid.UUID(seller_id)
            except ValueError:
                return self.error_response(
                    "Error de validación",
                    "El 'seller_id' debe ser un UUID válido",
                    400
                )
            
            report_data = self.order_service.get_seller_status_summary(seller_id)
            
            return self.success_response(
                data=report_data,
                message="Informe de estados generado exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class OrderSellerClientsSummaryController(BaseController):
    """Controlador para informe de clientes por vendedor"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def get(self):
        """
        Obtiene el resumen de pedidos por cliente para los clientes asignados a un vendedor
        
        Query params:
            seller_id (requerido): UUID del vendedor
            page (opcional): Número de página (default: 1)
            per_page (opcional): Elementos por página (default: 10, max: 100)
            
        Returns:
            JSON con datos de clientes estructurados para tabla con paginación
        """
        try:
            seller_id = request.args.get('seller_id', type=str)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            if not seller_id:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'seller_id' es obligatorio",
                    400
                )
            
            try:
                uuid.UUID(seller_id)
            except ValueError:
                return self.error_response(
                    "Error de validación",
                    "El 'seller_id' debe ser un UUID válido",
                    400
                )
            
            if page < 1:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'page' debe ser mayor a 0",
                    400
                )
            
            if per_page < 1 or per_page > 100:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'per_page' debe estar entre 1 y 100",
                    400
                )
            
            report_data = self.order_service.get_seller_clients_summary(seller_id, page, per_page)
            
            return self.success_response(
                data=report_data,
                message="Informe de clientes generado exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)


class OrderSellerMonthlyController(BaseController):
    """Controlador para informe mensual por vendedor"""
    
    def __init__(self):
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.order_repository = OrderRepository(session)
        self.order_service = OrderService(self.order_repository)
    
    @auto_close_session
    def get(self):
        """
        Obtiene el reporte mensual de pedidos para los clientes asignados a un vendedor
        
        Query params:
            seller_id (requerido): UUID del vendedor
            
        Returns:
            JSON con datos mensuales estructurados para gráficas
        """
        try:
            seller_id = request.args.get('seller_id', type=str)
            
            if not seller_id:
                return self.error_response(
                    "Error de validación",
                    "El parámetro 'seller_id' es obligatorio",
                    400
                )
            
            try:
                uuid.UUID(seller_id)
            except ValueError:
                return self.error_response(
                    "Error de validación",
                    "El 'seller_id' debe ser un UUID válido",
                    400
                )
            
            report_data = self.order_service.get_seller_monthly_report(seller_id)
            
            return self.success_response(
                data=report_data,
                message="Informe mensual generado exitosamente"
            )
            
        except OrderValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except OrderBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)



