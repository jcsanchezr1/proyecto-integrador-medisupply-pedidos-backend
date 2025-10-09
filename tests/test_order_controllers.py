"""
Tests corregidos para OrderController
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from app.controllers.order_controller import OrderController, OrderDeleteAllController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderControllerFixed:
    """Tests corregidos para OrderController"""
    
    def test_order_controller_creation(self):
        """Test: Crear OrderController"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderController()
                    
                    assert controller is not None
                    assert hasattr(controller, 'get')
                    assert hasattr(controller, 'order_service')
                    assert hasattr(controller, 'order_repository')
    
    def test_order_controller_has_get_method(self):
        """Test: OrderController tiene método get"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderController()
                    
                    assert hasattr(controller, 'get')
                    assert callable(controller.get)
    
    def test_get_method_with_client_id(self):
        """Test: GET con client_id"""
        app = Flask(__name__)
        
        with app.test_request_context('/orders?client_id=123'):
            with patch('app.config.database.SessionLocal') as mock_session_local:
                mock_session = MagicMock()
                mock_session_local.return_value = mock_session
                
                with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_order = MagicMock()
                        mock_order.to_dict.return_value = {'id': 1, 'client_id': 123}
                        mock_service.get_orders_by_client.return_value = [mock_order]
                        mock_service_class.return_value = mock_service
                        
                        controller = OrderController()
                        result = controller.get()
                        
                        assert result[1] == 200  # status_code
                        assert 'data' in result[0]
                        assert len(result[0]['data']) == 1
                        mock_service.get_orders_by_client.assert_called_once_with(123)
    
    def test_get_method_with_vendor_id(self):
        """Test: GET con vendor_id"""
        app = Flask(__name__)
        
        with app.test_request_context('/orders?vendor_id=456'):
            with patch('app.config.database.SessionLocal') as mock_session_local:
                mock_session = MagicMock()
                mock_session_local.return_value = mock_session
                
                with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_order = MagicMock()
                        mock_order.to_dict.return_value = {'id': 1, 'vendor_id': 456}
                        mock_service.get_orders_by_vendor.return_value = [mock_order]
                        mock_service_class.return_value = mock_service
                        
                        controller = OrderController()
                        result = controller.get()
                        
                        assert result[1] == 200  # status_code
                        assert 'data' in result[0]
                        assert len(result[0]['data']) == 1
                        mock_service.get_orders_by_vendor.assert_called_once_with(456)
    
    def test_get_method_without_parameters(self):
        """Test: GET sin parámetros"""
        app = Flask(__name__)
        
        with app.test_request_context('/orders'):
            with patch('app.config.database.SessionLocal') as mock_session_local:
                mock_session = MagicMock()
                mock_session_local.return_value = mock_session
                
                with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_service_class.return_value = mock_service
                        
                        controller = OrderController()
                        result = controller.get()
                        
                        assert result[1] == 400  # status_code - error de validación
                        assert 'error' in result[0]
    
    def test_get_method_with_both_parameters(self):
        """Test: GET con ambos parámetros (usa client_id)"""
        app = Flask(__name__)
        
        with app.test_request_context('/orders?client_id=123&vendor_id=456'):
            with patch('app.config.database.SessionLocal') as mock_session_local:
                mock_session = MagicMock()
                mock_session_local.return_value = mock_session
                
                with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_order = MagicMock()
                        mock_order.to_dict.return_value = {'id': 1, 'client_id': 123}
                        mock_service.get_orders_by_client.return_value = [mock_order]
                        mock_service_class.return_value = mock_service
                        
                        controller = OrderController()
                        result = controller.get()
                        
                        assert result[1] == 200  # status_code - éxito con client_id
                        assert 'data' in result[0]
                        assert len(result[0]['data']) == 1
                        mock_service.get_orders_by_client.assert_called_once_with(123)
    
    def test_get_method_service_exception(self):
        """Test: GET con excepción del servicio"""
        app = Flask(__name__)
        
        with app.test_request_context('/orders?client_id=123'):
            with patch('app.config.database.SessionLocal') as mock_session_local:
                mock_session = MagicMock()
                mock_session_local.return_value = mock_session
                
                with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_service.get_orders_by_client.side_effect = Exception("Database error")
                        mock_service_class.return_value = mock_service
                        
                        controller = OrderController()
                        result = controller.get()
                        
                        assert result[1] == 500  # status_code - error interno
                        assert 'error' in result[0]
    
    def test_get_method_validation_error(self):
        """Test: GET con error de validación"""
        app = Flask(__name__)
        
        with app.test_request_context('/orders?client_id=123'):
            with patch('app.config.database.SessionLocal') as mock_session_local:
                mock_session = MagicMock()
                mock_session_local.return_value = mock_session
                
                with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                        mock_service = MagicMock()
                        mock_service.get_orders_by_client.side_effect = OrderValidationError("client_id es requerido")
                        mock_service_class.return_value = mock_service
                        
                        controller = OrderController()
                        result = controller.get()
                        
                        assert result[1] == 400  # status_code - error de validación
                        assert 'error' in result[0]


class TestOrderDeleteAllControllerFixed:
    """Tests corregidos para OrderDeleteAllController"""
    
    def test_delete_all_controller_creation(self):
        """Test: Crear OrderDeleteAllController"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderDeleteAllController()
                    
                    assert controller is not None
                    assert hasattr(controller, 'delete')
                    assert hasattr(controller, 'order_service')
                    assert hasattr(controller, 'order_repository')
    
    def test_delete_all_controller_has_delete_method(self):
        """Test: OrderDeleteAllController tiene método delete"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderDeleteAllController()
                    
                    assert hasattr(controller, 'delete')
                    assert callable(controller.delete)
    
    def test_delete_method_success(self):
        """Test: DELETE exitoso"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service.delete_all_orders.return_value = 5  # Truthy value
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderDeleteAllController()
                    result = controller.delete()
                    
                    assert result[1] == 200  # status_code - éxito
                    assert 'message' in result[0]
                    mock_service.delete_all_orders.assert_called_once()
    
    def test_delete_method_empty(self):
        """Test: DELETE cuando no hay pedidos"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service.delete_all_orders.return_value = 0  # Falsy value
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderDeleteAllController()
                    result = controller.delete()
                    
                    assert result[1] == 500  # status_code - error cuando no hay pedidos
                    assert 'error' in result[0]
                    mock_service.delete_all_orders.assert_called_once()
    
    def test_delete_method_service_exception(self):
        """Test: DELETE con excepción del servicio"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.controllers.order_controller.OrderRepository') as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                
                with patch('app.controllers.order_controller.OrderService') as mock_service_class:
                    mock_service = MagicMock()
                    mock_service.delete_all_orders.side_effect = OrderBusinessLogicError("Error de lógica")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderDeleteAllController()
                    result = controller.delete()
                    
                    assert result[1] == 500  # status_code - error de lógica de negocio
                    assert 'error' in result[0]
                    mock_service.delete_all_orders.assert_called_once()
