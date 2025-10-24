"""
Tests para el modelo OrderItem
"""
import pytest
from app.models.order_item import OrderItem


class TestOrderItem:
    """Tests para el modelo OrderItem"""
    
    @pytest.fixture
    def valid_order_item_data(self):
        """Datos válidos para crear un item de pedido"""
        return {
            'product_id': 123,
            'quantity': 5,
            'order_id': 1
        }
    
    def test_create_order_item_with_valid_data(self, valid_order_item_data):
        """Test: Crear item de pedido con datos válidos"""
        order_item = OrderItem(**valid_order_item_data)
        
        assert order_item.product_id == 123
        assert order_item.quantity == 5
        assert order_item.order_id == 1
    
    def test_create_order_item_with_minimal_data(self):
        """Test: Crear item de pedido con datos mínimos"""
        order_item = OrderItem(
            product_id=456,
            quantity=1
        )
        
        assert order_item.product_id == 456
        assert order_item.quantity == 1
        assert order_item.order_id is None
    
    def test_create_order_item_with_all_parameters(self):
        """Test: Crear item de pedido con todos los parámetros"""
        order_item = OrderItem(
            product_id=789,
            quantity=3,
            order_id=2,
            id=1
        )
        
        assert order_item.id == 1
        assert order_item.product_id == 789
        assert order_item.quantity == 3
        assert order_item.order_id == 2
    
    def test_to_dict(self, valid_order_item_data):
        """Test: Conversión a diccionario"""
        order_item = OrderItem(**valid_order_item_data)
        item_dict = order_item.to_dict()
        
        assert isinstance(item_dict, dict)
        assert item_dict['product_id'] == 123
        assert item_dict['quantity'] == 5
        assert item_dict['order_id'] == 1
    
    def test_validate_product_id_valid(self, valid_order_item_data):
        """Test: Validar product_id válido"""
        order_item = OrderItem(**valid_order_item_data)
        order_item.validate()
        
        assert order_item.product_id == 123
    
    def test_validate_product_id_invalid(self):
        """Test: Validar product_id inválido"""
        order_item = OrderItem(
            order_id=1,
            product_id=0,
            quantity=5
        )
        
        with pytest.raises(ValueError, match="El ID del producto es obligatorio y debe ser mayor a 0"):
            order_item.validate()
    
    def test_validate_quantity_valid(self, valid_order_item_data):
        """Test: Validar quantity válido"""
        order_item = OrderItem(**valid_order_item_data)
        order_item.validate()
        
        assert order_item.quantity == 5
    
    def test_validate_quantity_invalid(self):
        """Test: Validar quantity inválido"""
        order_item = OrderItem(
            order_id=1,
            product_id=123,
            quantity=0
        )
        
        with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
            order_item.validate()