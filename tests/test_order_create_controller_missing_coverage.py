"""
Tests adicionales para OrderCreateController - cubrir líneas faltantes
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from app.controllers.order_create_controller import OrderCreateController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderCreateControllerMissingCoverage:
    """Tests para cubrir las líneas faltantes del OrderCreateController"""
    
    @pytest.fixture
    def mock_order_service(self):
        """Mock del OrderService"""
        return MagicMock()
    
    @pytest.fixture
    def mock_order_repository(self):
        """Mock del OrderRepository"""
        return MagicMock()
    
    @pytest.fixture
    def order_create_controller(self, mock_order_service, mock_order_repository):
        """Instancia de OrderCreateController con dependencias mockeadas"""
        with patch('app.controllers.order_create_controller.OrderRepository') as mock_repo_class:
            with patch('app.controllers.order_create_controller.OrderService') as mock_service_class:
                mock_repo_class.return_value = mock_order_repository
                mock_service_class.return_value = mock_order_service
                
                controller = OrderCreateController()
                controller.order_service = mock_order_service
                return controller
    
    @pytest.fixture
    def app(self):
        """Instancia de la aplicación Flask"""
        from app import create_app
        return create_app()
    
    def test_post_empty_json_data_none(self, order_create_controller, app):
        """Test: POST con data=None (línea 35)"""
        with app.test_request_context(json=None):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Se requiere un cuerpo JSON válido"
    
    def test_post_empty_items_list(self, order_create_controller, app):
        """Test: POST con lista de items vacía (línea 44)"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': []  # Lista vacía
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'items' es obligatorio"
    
    def test_post_successful_order_creation(self, order_create_controller, mock_order_service, app):
        """Test: Creación exitosa de pedido (líneas 71-77)"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }

        mock_order = MagicMock()
        mock_order.to_dict.return_value = {'id': 1, 'order_number': 'PED-001'}
        mock_order_service.create_order.return_value = mock_order
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['message'] == "Pedido creado exitosamente"
        assert response['data'] == {'id': 1, 'order_number': 'PED-001'}
        mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_order_validation_error(self, order_create_controller, mock_order_service, app):
        """Test: Error de validación del servicio (línea 79-80)"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        mock_order_service.create_order.side_effect = OrderValidationError("Error de validación del servicio")
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Error de validación del servicio"
    
    def test_post_order_business_logic_error(self, order_create_controller, mock_order_service, app):
        """Test: Error de lógica de negocio del servicio (línea 81-82)"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        mock_order_service.create_order.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
        assert response['details'] == "Stock insuficiente"
    
    def test_post_generic_exception(self, order_create_controller, mock_order_service, app):
        """Test: Excepción genérica del servicio (línea 83-84)"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        mock_order_service.create_order.side_effect = Exception("Error inesperado")
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error interno del servidor"
        assert response['details'] == "Error inesperado"
