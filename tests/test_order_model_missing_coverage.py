"""
Tests adicionales para Order model - cubrir líneas faltantes
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from app.models.order import Order
from app.models.order_item import OrderItem


class TestOrderModelMissingCoverage:
    """Tests para cubrir las líneas faltantes del modelo Order"""
    
    def test_validate_no_client_no_vendor(self):
        """Test: Validación cuando no hay client_id ni vendor_id"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=None,
            vendor_id=None
        )
        
        with pytest.raises(ValueError, match="El pedido debe tener al menos un cliente o vendedor válido"):
            order.validate()
    
    def test_calculate_total_amount_with_items(self):
        """Test: Calcular monto total con items"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )

        mock_item1 = MagicMock()
        mock_item1.quantity = 2
        mock_item1.unit_price = 10.0
        
        mock_item2 = MagicMock()
        mock_item2.quantity = 3
        mock_item2.unit_price = 15.0
        
        order.items = [mock_item1, mock_item2]
        total = order.calculate_total_amount()

        assert total == 65.0
        assert order.total_amount == 65.0
    
    def test_calculate_total_amount_no_items(self):
        """Test: Calcular monto total sin items"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )
        
        order.items = []
        
        total = order.calculate_total_amount()
        
        assert total == 0.0
        assert order.total_amount == 0.0
    
    def test_calculate_total_amount_single_item(self):
        """Test: Calcular monto total con un solo item"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )
        
        # Crear mock item
        mock_item = MagicMock()
        mock_item.quantity = 5
        mock_item.unit_price = 20.0
        
        order.items = [mock_item]
        
        total = order.calculate_total_amount()
        assert total == 100.0
        assert order.total_amount == 100.0
    
    def test_calculate_total_amount_zero_quantity(self):
        """Test: Calcular monto total con cantidad cero"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )
        
        # Crear mock item con cantidad cero
        mock_item = MagicMock()
        mock_item.quantity = 0
        mock_item.unit_price = 10.0
        
        order.items = [mock_item]
        
        total = order.calculate_total_amount()

        assert total == 0.0
        assert order.total_amount == 0.0
    
    def test_calculate_total_amount_zero_price(self):
        """Test: Calcular monto total con precio cero"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id="6ba7b815-9dad-11d1-80b4-00c04fd430c8"
        )

        mock_item = MagicMock()
        mock_item.quantity = 3
        mock_item.unit_price = 0.0
        
        order.items = [mock_item]
        
        total = order.calculate_total_amount()

        assert total == 0.0
        assert order.total_amount == 0.0
