"""
Tests para OrderCreateController - Archivo consolidado con nombres estándar
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from flask import Flask
from app.controllers.order_create_controller import OrderCreateController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderCreateController:
    """Tests para el controlador de creación de pedidos"""
    
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
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
    
    # Tests de validación de JSON
    def test_post_no_json_data(self, app):
        """Test: POST sin datos JSON"""
        controller = OrderCreateController()
        
        with app.test_request_context():
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Se requiere un cuerpo JSON válido"
    
    def test_post_empty_json_data(self, app):
        """Test: POST con JSON vacío"""
        controller = OrderCreateController()
        
        with app.test_request_context(json={}):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Se requiere un cuerpo JSON"
    
    def test_post_json_data_none(self, app):
        """Test: POST con data=None"""
        controller = OrderCreateController()
        
        with app.test_request_context(json=None):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Se requiere un cuerpo JSON válido"
    
    # Tests de validación de client_id/vendor_id
    def test_post_missing_both_client_and_vendor_id(self, app):
        """Test: POST sin client_id ni vendor_id"""
        controller = OrderCreateController()
        
        order_data = {
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Debe proporcionar al menos 'client_id' o 'vendor_id'"
    
    # Tests de validación de items
    def test_post_missing_items(self, app):
        """Test: POST sin campo items"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z'
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'items' es obligatorio"
    
    def test_post_empty_items_list(self, app):
        """Test: POST con lista de items vacía"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': []
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'items' es obligatorio"
    
    # Tests de validación de total_amount
    def test_post_missing_total_amount(self, app):
        """Test: POST sin total_amount"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'total_amount' es obligatorio"
    
    def test_post_invalid_total_amount_zero(self, app):
        """Test: POST con total_amount cero"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'total_amount' es obligatorio"
    
    def test_post_invalid_total_amount_negative(self, app):
        """Test: POST con total_amount negativo"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': -5.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El 'total_amount' debe ser un número mayor a 0"
    
    # Tests de validación de scheduled_delivery_date
    def test_post_missing_scheduled_delivery_date(self, app):
        """Test: POST sin scheduled_delivery_date"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El campo 'scheduled_delivery_date' es obligatorio"
    
    def test_post_invalid_scheduled_delivery_date_format(self, app):
        """Test: POST con formato de fecha inválido"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': 'invalid-date',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El 'scheduled_delivery_date' debe tener formato ISO 8601 válido"

    def test_post_invalid_item_missing_product_id(self, app):
        """Test: POST con item sin product_id"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El item 1 debe tener un 'product_id'"
    
    def test_post_invalid_item_missing_quantity(self, app):
        """Test: POST con item sin quantity"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El item 1 debe tener una 'quantity' válida mayor a 0"
    
    def test_post_invalid_item_zero_quantity(self, app):
        """Test: POST con item con quantity cero"""
        controller = OrderCreateController()
        
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 0}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "El item 1 debe tener una 'quantity' válida mayor a 0"

    def test_post_missing_client_and_vendor(self, app):
        """Test: POST sin client_id ni vendor_id (línea 38)"""
        controller = OrderCreateController()
        
        order_data = {
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with app.test_request_context(json=order_data):
            response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Debe proporcionar al menos 'client_id' o 'vendor_id'"
