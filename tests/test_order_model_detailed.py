"""
Tests extendidos para el modelo Order
"""
import pytest
from datetime import datetime
from app.models.order import Order
from app.models.db_models import OrderStatus


class TestOrderModelExtended:
    """Tests extendidos para Order"""
    
    def test_validate_order_number_empty(self):
        """Test: Validación de número de pedido vacío"""
        order = Order(
            order_number="",
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="El número de pedido es obligatorio"):
            order.validate()
    
    def test_validate_order_number_none(self):
        """Test: Validación de número de pedido None"""
        order = Order(
            order_number=None,
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="El número de pedido es obligatorio"):
            order.validate()
    
    def test_validate_order_number_wrong_prefix(self):
        """Test: Validación de número de pedido con prefijo incorrecto"""
        order = Order(
            order_number="ORD-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="El número de pedido debe comenzar con 'PED-'"):
            order.validate()
    
    def test_validate_order_number_wrong_format(self):
        """Test: Validación de número de pedido con formato incorrecto"""
        order = Order(
            order_number="PED-20240101",
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="El número de pedido debe tener el formato PED-YYYYMMDD-XXXXX"):
            order.validate()
    
    def test_validate_order_number_invalid_date(self):
        """Test: Validación de número de pedido con fecha inválida"""
        order = Order(
            order_number="PED-20240230-00001",
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="La fecha en el número de pedido debe ser válida"):
            order.validate()
    
    def test_validate_order_number_invalid_sequence(self):
        """Test: Validación de número de pedido con secuencia inválida"""
        order = Order(
            order_number="PED-20240101-ABC",
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="La secuencia del pedido debe ser de 5 dígitos"):
            order.validate()
    
    def test_validate_order_number_short_sequence(self):
        """Test: Validación de número de pedido con secuencia corta"""
        order = Order(
            order_number="PED-20240101-123",
            client_id=1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="La secuencia del pedido debe ser de 5 dígitos"):
            order.validate()
    
    def test_validate_client_id_zero(self):
        """Test: Validación de client_id cero"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=0,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="El pedido debe tener un cliente válido"):
            order.validate()
    
    def test_validate_client_id_negative(self):
        """Test: Validación de client_id negativo"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=-1,
            vendor_id=1
        )
        
        with pytest.raises(ValueError, match="El pedido debe tener un cliente válido"):
            order.validate()
    
    def test_validate_vendor_id_zero(self):
        """Test: Validación de vendor_id cero"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=0
        )
        
        with pytest.raises(ValueError, match="El pedido debe tener un vendedor válido"):
            order.validate()
    
    def test_validate_vendor_id_negative(self):
        """Test: Validación de vendor_id negativo"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=-1
        )
        
        with pytest.raises(ValueError, match="El pedido debe tener un vendedor válido"):
            order.validate()
    
    def test_validate_status_invalid(self):
        """Test: Validación de estado inválido"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1,
            status="INVALID_STATUS"
        )
        
        with pytest.raises(ValueError, match="El estado debe ser uno de:"):
            order.validate()
    
    def test_to_dict_with_scheduled_delivery_date(self):
        """Test: to_dict con scheduled_delivery_date"""
        delivery_date = datetime(2024, 1, 5)
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1,
            scheduled_delivery_date=delivery_date
        )
        
        result = order.to_dict()
        
        assert result["scheduled_delivery_date"] == delivery_date.isoformat()
    
    def test_to_dict_without_scheduled_delivery_date(self):
        """Test: to_dict sin scheduled_delivery_date"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        result = order.to_dict()
        
        assert result["scheduled_delivery_date"] is None
    
    def test_to_dict_with_assigned_truck(self):
        """Test: to_dict con assigned_truck"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1,
            assigned_truck="TRUCK001"
        )
        
        result = order.to_dict()
        
        assert result["assigned_truck"] == "TRUCK001"
    
    def test_to_dict_without_assigned_truck(self):
        """Test: to_dict sin assigned_truck"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        result = order.to_dict()
        
        assert result["assigned_truck"] is None
    
    def test_to_dict_with_items(self):
        """Test: to_dict con items"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        # Mock items
        mock_item = type('MockItem', (), {
            'to_dict': lambda self: {'id': 1, 'product_id': 101, 'quantity': 2}
        })()
        
        order.items = [mock_item]
        
        result = order.to_dict()
        
        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == 1
    
    def test_to_dict_without_items(self):
        """Test: to_dict sin items"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        result = order.to_dict()
        
        assert result["items"] == []
    
    def test_generate_order_number(self):
        """Test: Generación de número de pedido"""
        order_number = Order.generate_order_number()
        
        assert order_number.startswith("PED-")
        assert len(order_number) == 18  # PED-YYYYMMDD-HHMMS (puede ser 18 si incluye segundos)
        assert order_number.count("-") == 2
    
    def test_generate_order_number_format(self):
        """Test: Formato de número de pedido generado"""
        order_number = Order.generate_order_number()
        
        parts = order_number.split("-")
        assert len(parts) == 3
        assert parts[0] == "PED"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 5  # HHMMS
    
    def test_validate_success(self):
        """Test: Validación exitosa"""
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1,
            status="Recibido"
        )
        
        # No debe lanzar excepción
        order.validate()
    
    def test_validate_with_all_statuses(self):
        """Test: Validación con todos los estados válidos"""
        for status in OrderStatus:
            order = Order(
                order_number="PED-20240101-00001",
                client_id=1,
                vendor_id=1,
                status=status.value
            )
            
            # No debe lanzar excepción
            order.validate()
