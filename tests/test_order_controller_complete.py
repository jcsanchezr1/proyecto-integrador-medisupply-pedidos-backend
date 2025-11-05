"""
Tests finales para order_controller.py usando Flask test client
"""
import pytest
from unittest.mock import MagicMock, patch
from app import create_app
from app.controllers.order_controller import OrderController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderControllerFinal:
    """Tests finales para OrderController usando Flask test client"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_with_neither_client_nor_vendor_id(self):
        """Test: GET sin client_id ni vendor_id (línea 44)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderController()
            
            # Usar Flask test client para crear contexto de request
            with self.app.test_request_context('/orders'):
                from flask import request
                # Mock request.args.get para que retorne None para ambos
                with patch.object(request, 'args') as mock_args:
                    mock_args.get.side_effect = lambda key, type=None: None
                    
                    response, status_code = controller.get()
                    
                    assert status_code == 400
                    assert response["success"] is False
                    assert "Error de validación" in response["error"]
                    assert "Debe proporcionar client_id o vendor_id" in response["details"]
    
    def test_get_with_empty_orders_list(self):
        """Test: GET con lista vacía de pedidos (línea 53)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    
                    # Configurar mocks
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_client.return_value = []
                    mock_service_class.return_value = mock_service

                    controller = OrderController()

                    with self.app.test_request_context('/orders'):
                        from flask import request
                        with patch.object(request, 'args') as mock_args:
                            mock_args.get.side_effect = lambda key, type=None: "f1c2ce13-6623-4f42-a70b-9caadb7b8cbf" if key == 'client_id' else None

                            response, status_code = controller.get()

                    assert status_code == 200
                    assert response["success"] is True
                    assert response["data"] == []
                    assert "No tienes entregas programadas en este momento" in response["message"]
    
    def test_get_with_order_business_logic_error(self):
        """Test: GET con OrderBusinessLogicError (línea 66)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    
                    # Configurar mocks
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_client.side_effect = OrderBusinessLogicError("Error de lógica de negocio")
                    mock_service_class.return_value = mock_service

                    controller = OrderController()

                    with self.app.test_request_context('/orders'):
                        from flask import request
                        with patch.object(request, 'args') as mock_args:
                            mock_args.get.side_effect = lambda key, type=None: "f1c2ce13-6623-4f42-a70b-9caadb7b8cbf" if key == 'client_id' else None

                            response, status_code = controller.get()

                    assert status_code == 500
                    assert response["success"] is False
                    assert "Error de lógica de negocio" in response["error"]
    
    def test_get_with_client_id_success(self):
        """Test: GET con client_id exitoso"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    
                    # Configurar mocks
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_order = MagicMock()
                    mock_order.to_dict.return_value = {"id": 1, "order_number": "PED-001"}
                    mock_service.get_orders_by_client.return_value = [mock_order]
                    mock_service._enrich_order_items_with_product_info.return_value = mock_order
                    mock_service_class.return_value = mock_service

                    controller = OrderController()

                    with self.app.test_request_context('/orders'):
                        from flask import request
                        with patch.object(request, 'args') as mock_args:
                            mock_args.get.side_effect = lambda key, type=None: "f1c2ce13-6623-4f42-a70b-9caadb7b8cbf" if key == 'client_id' else None

                            response, status_code = controller.get()

                    assert status_code == 200
                    assert response["success"] is True
                    assert len(response["data"]) == 1
                    assert response["data"][0]["id"] == 1
                    assert "Pedidos obtenidos exitosamente" in response["message"]
    
    def test_get_with_vendor_id_success(self):
        """Test: GET con vendor_id exitoso"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    
                    # Configurar mocks
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_order = MagicMock()
                    mock_order.to_dict.return_value = {"id": 2, "order_number": "PED-002"}
                    mock_service.get_orders_by_vendor.return_value = [mock_order]
                    mock_service._enrich_order_items_with_product_info.return_value = mock_order
                    mock_service_class.return_value = mock_service

                    controller = OrderController()

                    with self.app.test_request_context('/orders'):
                        from flask import request
                        with patch.object(request, 'args') as mock_args:
                            mock_args.get.side_effect = lambda key, type=None: "df3bdc3f-7783-4c1e-981a-8060b114dfb2" if key == 'vendor_id' else None

                            response, status_code = controller.get()

                    assert status_code == 200
                    assert response["success"] is True
                    assert len(response["data"]) == 1
                    assert response["data"][0]["id"] == 2
                    assert "Pedidos obtenidos exitosamente" in response["message"]
    
    def test_get_with_validation_error(self):
        """Test: GET con OrderValidationError"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    
                    # Configurar mocks
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_client.side_effect = OrderValidationError("Error de validación")
                    mock_service_class.return_value = mock_service

                    controller = OrderController()

                    with self.app.test_request_context('/orders'):
                        from flask import request
                        with patch.object(request, 'args') as mock_args:
                            mock_args.get.side_effect = lambda key, type=None: "f1c2ce13-6623-4f42-a70b-9caadb7b8cbf" if key == 'client_id' else None

                            response, status_code = controller.get()

                    assert status_code == 400
                    assert response["success"] is False
                    assert "Error de validación" in response["error"]
                    assert "Error de validación" in response["details"]
    
    def test_get_with_general_exception(self):
        """Test: GET con excepción general"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    
                    # Configurar mocks
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_orders_by_client.side_effect = Exception("Error general")
                    mock_service_class.return_value = mock_service

                    controller = OrderController()

                    with self.app.test_request_context('/orders'):
                        from flask import request
                        with patch.object(request, 'args') as mock_args:
                            mock_args.get.side_effect = lambda key, type=None: "f1c2ce13-6623-4f42-a70b-9caadb7b8cbf" if key == 'client_id' else None

                            response, status_code = controller.get()

                    assert status_code == 500
                    assert response["success"] is False
                    assert "Error interno del servidor" in response["error"]
                    assert "Error general" in response["details"]
    
    def test_get_with_invalid_client_id_uuid(self):
        """Test: GET con client_id UUID inválido (líneas 45-46)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderController()
            
            with self.app.test_request_context('/orders?client_id=invalid-uuid'):
                from flask import request
                response, status_code = controller.get()
                
                assert status_code == 400
                assert response["success"] is False
                assert "Error de validación" in response["error"]
                assert "UUID válido" in response["details"]
    
    def test_get_with_invalid_vendor_id_uuid(self):
        """Test: GET con vendor_id UUID inválido (líneas 55-56)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderController()
            
            with self.app.test_request_context('/orders?vendor_id=invalid-uuid'):
                from flask import request
                response, status_code = controller.get()
                
                assert status_code == 400
                assert response["success"] is False
                assert "Error de validación" in response["error"]
                assert "UUID válido" in response["details"]
    