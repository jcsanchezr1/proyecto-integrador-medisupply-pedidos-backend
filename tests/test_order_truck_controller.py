import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from app import create_app
from app.controllers.order_truck_controller import OrderTruckController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderTruckController:
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_missing_assigned_truck(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderTruckController()
            
            with self.app.test_request_context('/orders/by-truck?scheduled_delivery_date=2025-12-25'):
                from flask import request
                response, status_code = controller.get()
                
                assert status_code == 400
                assert 'assigned_truck' in response['error'].lower() or 'obligatorio' in response['details'].lower()
    
    def test_get_missing_scheduled_delivery_date(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderTruckController()
            
            with self.app.test_request_context('/orders/by-truck?assigned_truck=CAM-001'):
                from flask import request
                response, status_code = controller.get()
                
                assert status_code == 400
                assert 'scheduled_delivery_date' in response['error'].lower() or 'obligatorio' in response['details'].lower()
    
    def test_get_success_with_orders(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_order = Mock()
                    mock_order.to_dict.return_value = {
                        'id': 1,
                        'order_number': 'PED-001',
                        'assigned_truck': 'CAM-001'
                    }
                    mock_order.items = []
                    mock_service.get_orders_by_truck_and_date.return_value = [mock_order]
                    mock_service._enrich_order_items_with_product_info.return_value = mock_order
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTruckController()
                    
                    with self.app.test_request_context('/orders/by-truck?assigned_truck=CAM-001&scheduled_delivery_date=2025-12-25'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert len(response['data']) == 1
    
    def test_get_success_no_orders(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_truck_and_date.return_value = []
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTruckController()
                    
                    with self.app.test_request_context('/orders/by-truck?assigned_truck=CAM-001&scheduled_delivery_date=2025-12-25'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['data'] == []
                        assert 'No hay pedidos' in response['message']
    
    def test_get_validation_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_truck_and_date.side_effect = OrderValidationError("Error de validación")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTruckController()
                    
                    with self.app.test_request_context('/orders/by-truck?assigned_truck=CAM-001&scheduled_delivery_date=2025-12-25'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert 'validación' in response['error'].lower()
    
    def test_get_business_logic_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderTruckController()
            
            with self.app.test_request_context('/orders/by-truck?assigned_truck=CAM-001&scheduled_delivery_date=2025-12-25'):
                with patch.object(controller.order_service, 'get_orders_by_truck_and_date', side_effect=OrderBusinessLogicError("Error de negocio")):
                    response, status_code = controller.get()
                    
                    assert status_code == 500
                    assert 'negocio' in response['error'].lower()
    
    def test_get_exception(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_truck_and_date.side_effect = Exception("Error inesperado")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTruckController()
                    
                    with self.app.test_request_context('/orders/by-truck?assigned_truck=CAM-001&scheduled_delivery_date=2025-12-25'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert 'Error' in response['error']

