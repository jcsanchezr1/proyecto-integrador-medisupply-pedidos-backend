"""
Tests completos para OrderCreateController
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from app.controllers.order_create_controller import OrderCreateController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderCreateControllerComplete:
    """Tests completos para OrderCreateController"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = Flask(__name__)
        
        with patch('app.controllers.order_create_controller.SessionLocal') as mock_session_local:
            with patch('app.controllers.order_create_controller.OrderRepository') as mock_repo_class:
                with patch('app.controllers.order_create_controller.OrderService') as mock_service_class:
                    mock_session = Mock()
                    mock_session_local.return_value = mock_session
                    
                    self.mock_order_repository = Mock()
                    mock_repo_class.return_value = self.mock_order_repository
                    
                    self.mock_order_service = Mock()
                    mock_service_class.return_value = self.mock_order_service
                    
                    self.controller = OrderCreateController()
    
    def test_post_success_with_client_and_vendor(self):
        """Test de creación exitosa con cliente y vendedor"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        mock_order = Mock()
        mock_order.to_dict.return_value = {'id': 1, 'order_number': 'PED-001'}
        self.mock_order_service.create_order.return_value = mock_order
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert 'Pedido creado exitosamente' in response['message']
        self.mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_success_with_only_client(self):
        """Test de creación exitosa solo con cliente"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 100.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 1}]
        }
        
        mock_order = Mock()
        mock_order.to_dict.return_value = {'id': 2, 'order_number': 'PED-002'}
        self.mock_order_service.create_order.return_value = mock_order
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 201
        assert response['success'] is True
    
    def test_post_success_with_only_vendor(self):
        """Test de creación exitosa solo con vendedor"""
        order_data = {
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 200.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 2, 'quantity': 3}]
        }
        
        mock_order = Mock()
        mock_order.to_dict.return_value = {'id': 3, 'order_number': 'PED-003'}
        self.mock_order_service.create_order.return_value = mock_order
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 201
        assert response['success'] is True
    
    def test_post_missing_json_body(self):
        """Test de error cuando falta el cuerpo JSON"""
        with self.app.test_request_context():
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'Se requiere un cuerpo JSON válido' in response['details']
    
    def test_post_empty_json_body(self):
        """Test de error cuando el cuerpo JSON está vacío"""
        with self.app.test_request_context(json=None):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'Se requiere un cuerpo JSON' in response['details']
    
    def test_post_missing_both_client_and_vendor(self):
        """Test de error cuando faltan cliente y vendedor"""
        order_data = {
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'Debe proporcionar al menos' in response['details']
    
    def test_post_missing_items(self):
        """Test de error cuando faltan items"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z'
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El campo \'items\' es obligatorio' in response['details']
    
    def test_post_empty_items_list(self):
        """Test de error cuando la lista de items está vacía"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': []
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El pedido debe tener al menos un item' in response['details']
    
    def test_post_missing_total_amount(self):
        """Test de error cuando falta total_amount"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El campo \'total_amount\' es obligatorio' in response['details']
    
    def test_post_invalid_total_amount_zero(self):
        """Test de error cuando total_amount es cero"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El \'total_amount\' debe ser un número mayor a 0' in response['details']
    
    def test_post_invalid_total_amount_negative(self):
        """Test de error cuando total_amount es negativo"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': -50.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El \'total_amount\' debe ser un número mayor a 0' in response['details']
    
    def test_post_missing_scheduled_delivery_date(self):
        """Test de error cuando falta scheduled_delivery_date"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El campo \'scheduled_delivery_date\' es obligatorio' in response['details']
    
    def test_post_invalid_scheduled_delivery_date_format(self):
        """Test de error cuando scheduled_delivery_date tiene formato inválido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'formato ISO 8601 válido' in response['details']
    
    def test_post_invalid_item_missing_product_id(self):
        """Test de error cuando un item no tiene product_id"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El item 1 debe tener un \'product_id\'' in response['details']
    
    def test_post_invalid_item_invalid_quantity(self):
        """Test de error cuando un item tiene cantidad inválida"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 0}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'El item 1 debe tener una \'quantity\' válida mayor a 0' in response['details']
    
    def test_post_validation_error_from_service(self):
        """Test de error de validación del servicio"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        self.mock_order_service.create_order.side_effect = OrderValidationError("Error de validación del servicio")
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'Error de validación del servicio' in response['details']
    
    def test_post_business_logic_error_from_service(self):
        """Test de error de lógica de negocio del servicio"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        self.mock_order_service.create_order.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Stock insuficiente' in response['details']
    
    def test_post_generic_exception_from_service(self):
        """Test de excepción genérica del servicio"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        self.mock_order_service.create_order.side_effect = Exception("Error inesperado")
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 500
        assert response['success'] is False
        assert 'Error interno del servidor' in response['error']
