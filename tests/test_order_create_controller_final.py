"""
Tests para OrderCreateController siguiendo el patrón exitoso
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from app.controllers.order_create_controller import OrderCreateController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderCreateController:
    """Tests para OrderCreateController siguiendo el patrón exitoso"""
    
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
    
    @pytest.fixture
    def valid_order_data(self):
        """Datos válidos para crear un pedido"""
        return {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
    
    def test_post_success_with_client_and_vendor(self, order_create_controller, mock_order_service, app, valid_order_data):
        """Test: POST exitoso con cliente y vendedor"""
        mock_order = MagicMock()
        mock_order.to_dict.return_value = {'id': 1, 'order_number': 'PED-001'}
        mock_order_service.create_order.return_value = mock_order
        
        with app.test_request_context(json=valid_order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['message'] == "Pedido creado exitosamente"
        assert response['data'] == {'id': 1, 'order_number': 'PED-001'}
        mock_order_service.create_order.assert_called_once_with(valid_order_data)
    
    def test_post_success_with_only_client(self, order_create_controller, mock_order_service, app):
        """Test: POST exitoso solo con cliente"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 100.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 1}]
        }
        
        mock_order = MagicMock()
        mock_order.to_dict.return_value = {'id': 2, 'order_number': 'PED-002'}
        mock_order_service.create_order.return_value = mock_order
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_success_with_only_vendor(self, order_create_controller, mock_order_service, app):
        """Test: POST exitoso solo con vendedor"""
        order_data = {
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 200.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 2, 'quantity': 3}]
        }
        
        mock_order = MagicMock()
        mock_order.to_dict.return_value = {'id': 3, 'order_number': 'PED-003'}
        mock_order_service.create_order.return_value = mock_order
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_no_json_data(self, order_create_controller, app):
        """Test: POST sin datos JSON"""
        with app.test_request_context():
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Se requiere un cuerpo JSON válido"
    
    def test_post_empty_json_data(self, order_create_controller, app):
        """Test: POST con JSON vacío"""
        with app.test_request_context(json=None):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Se requiere un cuerpo JSON válido"
    
    def test_post_missing_both_client_and_vendor_id(self, order_create_controller, app):
        """Test: POST sin client_id ni vendor_id"""
        order_data = {
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Debe proporcionar al menos 'client_id' o 'vendor_id'"
    
    def test_post_missing_items(self, order_create_controller, app):
        """Test: POST sin items"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z'
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'items' es obligatorio"
    
    def test_post_empty_items_list(self, order_create_controller, app):
        """Test: POST con lista de items vacía"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': []
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'items' es obligatorio"
    
    def test_post_missing_total_amount(self, order_create_controller, app):
        """Test: POST sin total_amount"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'total_amount' es obligatorio"
    
    def test_post_invalid_total_amount_zero(self, order_create_controller, app):
        """Test: POST con total_amount cero"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'total_amount' es obligatorio"
    
    def test_post_invalid_total_amount_negative(self, order_create_controller, app):
        """Test: POST con total_amount negativo"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': -50.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El 'total_amount' debe ser un número mayor a 0"
    
    def test_post_missing_scheduled_delivery_date(self, order_create_controller, app):
        """Test: POST sin scheduled_delivery_date"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'scheduled_delivery_date' es obligatorio"
    
    def test_post_invalid_scheduled_delivery_date_format(self, order_create_controller, app):
        """Test: POST con formato de fecha inválido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': 'invalid-date',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El 'scheduled_delivery_date' debe tener formato ISO 8601 válido"
    
    def test_post_invalid_item_missing_product_id(self, order_create_controller, app):
        """Test: POST con item sin product_id"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El item 1 debe tener un 'product_id'"
    
    def test_post_invalid_item_missing_quantity(self, order_create_controller, app):
        """Test: POST con item sin quantity"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El item 1 debe tener una 'quantity' válida mayor a 0"
    
    def test_post_invalid_item_zero_quantity(self, order_create_controller, app):
        """Test: POST con item con quantity cero"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 0}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El item 1 debe tener una 'quantity' válida mayor a 0"
    
    def test_post_validation_error_from_service(self, order_create_controller, mock_order_service, app, valid_order_data):
        """Test: Error de validación del servicio"""
        mock_order_service.create_order.side_effect = OrderValidationError("Error de validación del servicio")
        
        with app.test_request_context(json=valid_order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Error de validación del servicio"
    
    def test_post_business_logic_error_from_service(self, order_create_controller, mock_order_service, app, valid_order_data):
        """Test: Error de lógica de negocio del servicio"""
        mock_order_service.create_order.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with app.test_request_context(json=valid_order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
        assert response['details'] == "Stock insuficiente"
    
    def test_post_generic_exception_from_service(self, order_create_controller, mock_order_service, app, valid_order_data):
        """Test: Excepción genérica del servicio"""
        mock_order_service.create_order.side_effect = Exception("Error inesperado")
        
        with app.test_request_context(json=valid_order_data):
            response, status_code = order_create_controller.post()
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error interno del servidor"
