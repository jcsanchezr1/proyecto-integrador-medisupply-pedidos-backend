"""
Tests para OrderTopClientsController
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app import create_app
from app.controllers.order_report_controller import OrderTopClientsController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderTopClientsController:
    """Tests para OrderTopClientsController"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_top_clients_success(self):
        """Test: Obtener top clientes exitosamente"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2025-08-11',
                            'end_date': '2025-11-11',
                            'months': 3
                        },
                        'top_clients': [
                            {
                                'client_id': 'client-1',
                                'orders_count': 10,
                                'client_name': 'Cliente Uno'
                            },
                            {
                                'client_id': 'client-2',
                                'orders_count': 8,
                                'client_name': 'Cliente Dos'
                            }
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['message'] == "Reporte de top clientes generado exitosamente"
                        assert response['data'] == mock_report_data
                        assert len(response['data']['top_clients']) == 2
                        
                        mock_service.get_top_clients_report.assert_called_once()
    
    def test_get_top_clients_empty_data(self):
        """Test: Obtener top clientes sin datos"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2025-08-11',
                            'end_date': '2025-11-11',
                            'months': 3
                        },
                        'top_clients': []
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert "No hay clientes con pedidos" in response['message']
                        assert response['data']['top_clients'] == []
    
    def test_get_top_clients_business_logic_error(self):
        """Test: Error de lógica de negocio al generar reporte"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.side_effect = OrderBusinessLogicError(
                        "Error al generar reporte de top clientes"
                    )
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
                        assert "Error de lógica de negocio" in response['error']
                        assert "Error al generar reporte de top clientes" in response['details']
    
    def test_get_top_clients_generic_exception(self):
        """Test: Excepción genérica al generar reporte"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.side_effect = Exception("Unexpected error")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
                        assert "Error interno del servidor" in response['error']
                        assert "Unexpected error" in response['details']
    
    def test_get_top_clients_response_structure(self):
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
                            'start_date': '2025-08-11',
                            'end_date': '2025-11-11',
                            'months': 3
                        },
                        'top_clients': [
                            {
                                'client_id': 'client-1',
                                'orders_count': 10,
                                'client_name': 'Cliente Uno'
                            }
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert 'success' in response
                        assert 'message' in response
                        assert 'data' in response
                        
                        data = response['data']
                        assert 'period' in data
                        assert 'top_clients' in data
                        
                        assert 'start_date' in data['period']
                        assert 'end_date' in data['period']
                        assert 'months' in data['period']
                        
                        if data['top_clients']:
                            client = data['top_clients'][0]
                            assert 'client_id' in client
                            assert 'orders_count' in client
                            assert 'client_name' in client
    
    def test_get_top_clients_max_five_clients(self):
        """Test: Verificar que retorna máximo 5 clientes"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    # Generar 5 clientes
                    top_clients = []
                    for i in range(5):
                        top_clients.append({
                            'client_id': f'client-{i+1}',
                            'orders_count': 10 - i,
                            'client_name': f'Cliente {i+1}'
                        })
                    
                    mock_report_data = {
                        'period': {
                            'start_date': '2025-08-11',
                            'end_date': '2025-11-11',
                            'months': 3
                        },
                        'top_clients': top_clients
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert len(response['data']['top_clients']) == 5
    
    def test_get_top_clients_validation_error(self):
        """Test: Error de validación al generar reporte"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_top_clients_report.side_effect = OrderValidationError(
                        "Error de validación en reporte"
                    )
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopClientsController()
                    
                    with self.app.test_request_context('/orders/reports/top-clients'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
                        assert "Error de validación" in response['error']
                        assert "Error de validación en reporte" in response['details']

