"""
Tests para los modelos de dominio
"""
import pytest
from datetime import datetime
from app.models.order import Order
from app.models.order_item import OrderItem


class TestOrderModel:
    """Tests para el modelo Order"""
    
    def test_order_creation_basic(self):
        """Test: Crear pedido básico"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )
        
        assert order.order_number == "PED-20240101-00001"
        assert order.client_id == "6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        assert order.vendor_id is None
        assert order.status == "Recibido"
        assert order.total_amount == 0.0
        assert order.assigned_truck is not None
    
    def test_order_creation_with_all_params(self):
        """Test: Crear pedido con todos los parámetros"""
        order = Order(
            order_number="PED-20240101-00002",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8",
            vendor_id="6ba7b816-9dad-11d1-80b4-00c04fd430c8",
            status="En Preparación",
            total_amount=150.0,
            scheduled_delivery_date=datetime(2024, 12, 25, 10, 0, 0),
            assigned_truck="CAM-001"
        )
        
        assert order.order_number == "PED-20240101-00002"
        assert order.client_id == "6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        assert order.vendor_id == "6ba7b816-9dad-11d1-80b4-00c04fd430c8"
        assert order.status == "En Preparación"
        assert order.total_amount == 150.0
        assert order.assigned_truck == "CAM-001"
    
    def test_order_to_dict(self):
        """Test: Conversión a diccionario"""
        order = Order(
            order_number="PED-20240101-00003",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )
        
        order_dict = order.to_dict()
        
        assert isinstance(order_dict, dict)
        assert order_dict['order_number'] == "PED-20240101-00003"
        assert order_dict['client_id'] == "6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        assert 'items' in order_dict
        assert isinstance(order_dict['items'], list)


class TestOrderItemModel:
    """Tests para el modelo OrderItem"""
    
    def test_order_item_creation_basic(self):
        """Test: Crear item básico"""
        order_item = OrderItem(
            product_id=123,
            quantity=1
        )
        
        assert order_item.product_id == 123
        assert order_item.quantity == 1
        assert order_item.order_id is None
    
    def test_order_item_creation_with_all_params(self):
        """Test: Crear item con todos los parámetros"""
        order_item = OrderItem(
            product_id=456,
            quantity=5,
            order_id=1,
            id=1
        )
        
        assert order_item.id == 1
        assert order_item.product_id == 456
        assert order_item.quantity == 5
        assert order_item.order_id == 1
    
    def test_order_item_to_dict(self):
        """Test: Conversión a diccionario"""
        order_item = OrderItem(
            product_id=789,
            quantity=3
        )
        
        item_dict = order_item.to_dict()
        
        assert isinstance(item_dict, dict)
        assert item_dict['product_id'] == 789
        assert item_dict['quantity'] == 3
    
    def test_order_item_has_methods(self):
        """Test: Verificar que OrderItem tiene los métodos necesarios"""
        order_item = OrderItem(
            product_id=123,
            quantity=1
        )
        
        assert hasattr(order_item, 'validate')
        assert hasattr(order_item, 'to_dict')
        assert callable(order_item.validate)
        assert callable(order_item.to_dict)