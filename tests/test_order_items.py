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
            'product_name': 'Producto Test',
            'product_image_url': 'https://example.com/image.jpg',
            'quantity': 5,
            'unit_price': 100.0,
            'order_id': 1
        }
    
    def test_create_order_item_with_valid_data(self, valid_order_item_data):
        """Test: Crear item de pedido con datos válidos"""
        order_item = OrderItem(**valid_order_item_data)
        
        assert order_item.product_id == 123
        assert order_item.product_name == 'Producto Test'
        assert order_item.product_image_url == 'https://example.com/image.jpg'
        assert order_item.quantity == 5
        assert order_item.unit_price == 100.0
        assert order_item.order_id == 1
        # OrderItem no tiene created_at ni updated_at por defecto
    
    def test_create_order_item_with_minimal_data(self):
        """Test: Crear item de pedido con datos mínimos"""
        order_item = OrderItem(
            product_id=456,
            product_name='Producto Mínimo'
        )
        
        assert order_item.product_id == 456
        assert order_item.product_name == 'Producto Mínimo'
        assert order_item.product_image_url is None
        assert order_item.quantity == 1  # Valor por defecto
        assert order_item.unit_price is None
        assert order_item.order_id is None
    
    def test_create_order_item_with_all_parameters(self):
        """Test: Crear item de pedido con todos los parámetros"""
        order_item = OrderItem(
            product_id=789,
            product_name='Producto Completo',
            product_image_url='https://example.com/complete.jpg',
            quantity=3,
            unit_price=75.5,
            order_id=2,
            id=1
        )
        
        assert order_item.id == 1
        assert order_item.product_id == 789
        assert order_item.product_name == 'Producto Completo'
        assert order_item.product_image_url == 'https://example.com/complete.jpg'
        assert order_item.quantity == 3
        assert order_item.unit_price == 75.5
        assert order_item.order_id == 2
    
    def test_to_dict(self, valid_order_item_data):
        """Test: Conversión a diccionario"""
        order_item = OrderItem(**valid_order_item_data)
        item_dict = order_item.to_dict()
        
        assert isinstance(item_dict, dict)
        assert item_dict['product_id'] == 123
        assert item_dict['product_name'] == 'Producto Test'
        assert item_dict['product_image_url'] == 'https://example.com/image.jpg'
        assert item_dict['quantity'] == 5
        assert item_dict['unit_price'] == 100.0
        assert item_dict['order_id'] == 1
        # OrderItem no tiene created_at ni updated_at por defecto
    
    def test_get_total_price_with_unit_price(self, valid_order_item_data):
        """Test: Calcular precio total con unit_price"""
        order_item = OrderItem(**valid_order_item_data)
        total = order_item.get_total_price()
        
        assert total == 500.0  # 5 * 100.0
    
    def test_get_total_price_without_unit_price(self):
        """Test: Calcular precio total sin unit_price"""
        order_item = OrderItem(
            product_id=123,
            product_name='Producto Test',
            quantity=5
        )
        total = order_item.get_total_price()
        
        assert total is None
    
    def test_validate_product_id_valid(self, valid_order_item_data):
        """Test: Validar product_id válido"""
        order_item = OrderItem(**valid_order_item_data)
        order_item.validate()  # No debe lanzar excepción
    
    def test_validate_product_id_invalid(self):
        """Test: Validar product_id inválido"""
        order_item = OrderItem(
            order_id=1,
            product_id=0,
            product_name="Test Product",
            quantity=5
        )
        with pytest.raises(ValueError, match="El ID del producto es obligatorio y debe ser mayor a 0"):
            order_item._validate_product_id()
    
    def test_validate_product_name_valid(self, valid_order_item_data):
        """Test: Validar product_name válido"""
        order_item = OrderItem(**valid_order_item_data)
        order_item._validate_product_name()  # No debe lanzar excepción
    
    def test_validate_product_name_empty(self):
        """Test: Validar product_name vacío"""
        order_item = OrderItem(
            order_id=1,
            product_id=123,
            product_name="",
            quantity=5
        )
        with pytest.raises(ValueError, match="El nombre del producto es obligatorio y debe tener al menos 2 caracteres"):
            order_item._validate_product_name()
    
    def test_validate_quantity_valid(self, valid_order_item_data):
        """Test: Validar quantity válido"""
        order_item = OrderItem(**valid_order_item_data)
        order_item._validate_quantity()  # No debe lanzar excepción
    
    def test_validate_quantity_invalid(self):
        """Test: Validar quantity inválido"""
        order_item = OrderItem(
            order_id=1,
            product_id=123,
            product_name="Test Product",
            quantity=0
        )
        with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
            order_item._validate_quantity()
    
    def test_validate_unit_price_valid(self, valid_order_item_data):
        """Test: Validar unit_price válido"""
        order_item = OrderItem(**valid_order_item_data)
        order_item._validate_unit_price()  # No debe lanzar excepción
    
    def test_validate_unit_price_invalid(self):
        """Test: Validar unit_price inválido"""
        order_item = OrderItem(
            order_id=1,
            product_id=123,
            product_name="Test Product",
            quantity=5,
            unit_price=-10.0
        )
        with pytest.raises(ValueError, match="El precio unitario no puede ser negativo"):
            order_item._validate_unit_price()
    
    def test_validate_unit_price_none(self):
        """Test: Validar unit_price None (válido)"""
        order_item = OrderItem(
            product_id=123,
            product_name='Producto Test',
            quantity=5,
            unit_price=None
        )
        order_item.validate()  # No debe lanzar excepción
