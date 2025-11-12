"""
Tests para OrderMonthlyReportController
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app import create_app
from app.controllers.order_report_controller import OrderMonthlyReportController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderMonthlyReportController:
    """Tests para OrderMonthlyReportController"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_monthly_report_success(self):
        """Test: Obtener reporte mensual exitosamente"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2024-11-11',
                            'end_date': '2025-11-11',
                            'months': 12
                        },
                        'summary': {
                            'total_orders': 50,
                            'total_amount': 25000.50,
                            'months_with_data': 8,
                            'average_orders_per_month': 4.17,
                            'average_amount_per_month': 2083.38
                        },
                        'monthly_data': [
                            {
                                'year': 2024,
                                'month': 12,
                                'month_name': 'diciembre',
                                'month_short': 'dic',
                                'label': 'dic-2024',
                                'orders_count': 5,
                                'total_amount': 2500.0
                            },
                            {
                                'year': 2025,
                                'month': 1,
                                'month_name': 'enero',
                                'month_short': 'ene',
                                'label': 'ene-2025',
                                'orders_count': 8,
                                'total_amount': 4000.0
                            }
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['message'] == "Reporte mensual generado exitosamente"
                        assert response['data'] == mock_report_data
                        
                        mock_service.get_monthly_report.assert_called_once()
    
    def test_get_monthly_report_empty_data(self):
        """Test: Obtener reporte mensual sin datos"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2024-11-11',
                            'end_date': '2025-11-11',
                            'months': 12
                        },
                        'summary': {
                            'total_orders': 0,
                            'total_amount': 0.0,
                            'months_with_data': 0,
                            'average_orders_per_month': 0.0,
                            'average_amount_per_month': 0.0
                        },
                        'monthly_data': [
                            {
                                'year': 2025,
                                'month': i,
                                'month_name': 'enero',
                                'month_short': 'ene',
                                'label': f'ene-2025',
                                'orders_count': 0,
                                'total_amount': 0.0
                            } for i in range(1, 13)
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['data']['summary']['total_orders'] == 0
                        assert response['data']['summary']['total_amount'] == 0.0
    
    def test_get_monthly_report_business_logic_error(self):
        """Test: Error de lógica de negocio al generar reporte"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.side_effect = OrderBusinessLogicError(
                        "Error al generar reporte mensual"
                    )
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
                        assert "Error de lógica de negocio" in response['error']
                        assert "Error al generar reporte mensual" in response['details']
    
    def test_get_monthly_report_generic_exception(self):
        """Test: Excepción genérica al generar reporte"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.side_effect = Exception("Unexpected error")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
                        assert "Error interno del servidor" in response['error']
                        assert "Unexpected error" in response['details']
    
    def test_get_monthly_report_response_structure(self):
        """Test: Verificar estructura completa del response"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2024-11-11',
                            'end_date': '2025-11-11',
                            'months': 12
                        },
                        'summary': {
                            'total_orders': 30,
                            'total_amount': 15000.0,
                            'months_with_data': 6,
                            'average_orders_per_month': 2.5,
                            'average_amount_per_month': 1250.0
                        },
                        'monthly_data': []
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()

                        assert 'success' in response
                        assert 'message' in response
                        assert 'data' in response

                        data = response['data']
                        assert 'period' in data
                        assert 'summary' in data
                        assert 'monthly_data' in data

                        assert 'start_date' in data['period']
                        assert 'end_date' in data['period']
                        assert 'months' in data['period']


                        assert 'total_orders' in data['summary']
                        assert 'total_amount' in data['summary']
                        assert 'months_with_data' in data['summary']
                        assert 'average_orders_per_month' in data['summary']
                        assert 'average_amount_per_month' in data['summary']
    
    def test_get_monthly_report_session_management(self):
        """Test: Verificar manejo de sesión"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {},
                        'summary': {},
                        'monthly_data': []
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()

                        mock_session_local.assert_called()
    
    def test_get_monthly_report_with_twelve_months(self):
        """Test: Verificar que el reporte contiene 12 meses"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    # Generar 12 meses de datos
                    monthly_data = []
                    for i in range(12):
                        monthly_data.append({
                            'year': 2025,
                            'month': i + 1,
                            'month_name': 'enero',
                            'month_short': 'ene',
                            'label': f'ene-2025',
                            'orders_count': i * 2,
                            'total_amount': i * 1000.0
                        })
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2024-11-11',
                            'end_date': '2025-11-11',
                            'months': 12
                        },
                        'summary': {
                            'total_orders': 132,
                            'total_amount': 66000.0,
                            'months_with_data': 11,
                            'average_orders_per_month': 11.0,
                            'average_amount_per_month': 5500.0
                        },
                        'monthly_data': monthly_data
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert len(response['data']['monthly_data']) == 12
                        assert response['data']['period']['months'] == 12
    
    def test_get_monthly_report_validation_error(self):
        """Test: Error de validación al generar reporte"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.side_effect = OrderValidationError(
                        "Error de validación en reporte"
                    )
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
                        assert "Error de validación" in response['error']
                        assert "Error de validación en reporte" in response['details']
    
    def test_get_monthly_report_empty_monthly_data_message(self):
        """Test: Mensaje cuando monthly_data está vacío"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2024-11-11',
                            'end_date': '2025-11-11',
                            'months': 12
                        },
                        'summary': {
                            'total_orders': 0,
                            'total_amount': 0.0,
                            'months_with_data': 0
                        },
                        'monthly_data': []  # Array vacío
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderMonthlyReportController()
                    
                    with self.app.test_request_context('/orders/reports/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert "No hay pedidos en el último año" in response['message']

