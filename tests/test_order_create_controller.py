"""
Tests para el controlador de creación de pedidos
"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from app.controllers.order_create_controller import OrderCreateController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderCreateController:
    """Tests para OrderCreateController"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.mock_order_service = Mock()
        self.controller = OrderCreateController()
        self.controller.order_service = self.mock_order_service
    
    def test_post_success(self):
        """Test de creación exitosa de pedido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [
                {'product_id': 1, 'quantity': 2},
                {'product_id': 2, 'quantity': 1}
            ]
        }

        mock_order = Mock()
        mock_order.to_dict.return_value = {
            'id': 1,
            'order_number': 'PED-20241221-12345',
            'client_id': order_data['client_id'],
            'vendor_id': order_data['vendor_id'],
            'status': 'En Preparación',
            'total_amount': 150.0,
            'assigned_truck': 'CAM-001-Refrigerado',
            'items': []
        }
        
        self.mock_order_service.create_order.return_value = mock_order
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['message'] == 'Pedido creado exitosamente'
        assert 'data' in response
        self.mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_missing_json(self):
        """Test de error cuando no se proporciona JSON"""
        with self.app.test_request_context():
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'Se requiere un cuerpo JSON' in response['details']
    
    def test_post_missing_both_client_and_vendor_id(self):
        """Test de error cuando faltan tanto client_id como vendor_id"""
        order_data = {
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'al menos' in response['details']
    
    def test_post_only_client_id(self):
        """Test de creación exitosa con solo client_id"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }

        mock_order = Mock()
        mock_order.to_dict.return_value = {
            'id': 1,
            'order_number': 'ORD-2024-001',
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': None,
            'status': 'En Preparación',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2024-12-25T10:00:00Z'
        }
        
        self.mock_order_service.create_order.return_value = mock_order
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['data']['client_id'] == '123e4567-e89b-12d3-a456-426614174000'
        assert response['data']['vendor_id'] is None
        self.mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_only_vendor_id(self):
        """Test de creación exitosa con solo vendor_id"""
        order_data = {
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }

        mock_order = Mock()
        mock_order.to_dict.return_value = {
            'id': 1,
            'order_number': 'ORD-2024-001',
            'client_id': None,
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'status': 'En Preparación',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2024-12-25T10:00:00Z'
        }
        
        self.mock_order_service.create_order.return_value = mock_order
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['data']['client_id'] is None
        assert response['data']['vendor_id'] == '456e7890-e89b-12d3-a456-426614174001'
        self.mock_order_service.create_order.assert_called_once_with(order_data)
    
    def test_post_missing_items(self):
        """Test de error cuando faltan items"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'items' in response['details']
    
    def test_post_missing_total_amount(self):
        """Test de error cuando falta total_amount"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'total_amount' in response['details']
    
    def test_post_invalid_total_amount(self):
        """Test de error cuando total_amount es inválido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'total_amount' in response['details']
    
    def test_post_missing_scheduled_delivery_date(self):
        """Test de error cuando falta scheduled_delivery_date"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'scheduled_delivery_date' in response['details']
    
    def test_post_invalid_scheduled_delivery_date_format(self):
        """Test de error cuando scheduled_delivery_date tiene formato inválido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'scheduled_delivery_date' in response['details']
    
    def test_post_past_scheduled_delivery_date(self):
        """Test de error cuando scheduled_delivery_date es en el pasado"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2020-01-01T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'pasado' in response['details']
    
    def test_post_empty_items(self):
        """Test de error cuando items está vacío"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': []
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'El pedido debe tener al menos un item' in response['details']
    
    def test_post_invalid_item_missing_product_id(self):
        """Test de error cuando un item no tiene product_id"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'quantity': 2}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'product_id' in response['details']
    
    def test_post_invalid_item_invalid_quantity(self):
        """Test de error cuando un item tiene cantidad inválida"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 0}]
        }
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
        assert 'quantity' in response['details']
    
    def test_post_validation_error(self):
        """Test de error de validación del servicio"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        self.mock_order_service.create_order.side_effect = OrderValidationError("Error de validación")
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de validación' in response['error']
    
    def test_post_business_logic_error(self):
        """Test de error de lógica de negocio del servicio"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        self.mock_order_service.create_order.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with self.app.test_request_context(json=order_data):
            response, status_code = self.controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de lógica de negocio' in response['error']
        assert 'Stock insuficiente' in response['details']
    
    def test_post_generic_error(self):
        """Test de error genérico"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
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
