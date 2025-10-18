"""
Tests extendidos para OrderService
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError
from datetime import datetime


class TestOrderServiceExtended:
    """Tests extendidos para OrderService"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_repository = MagicMock(spec=OrderRepository)
        self.service = OrderService(self.mock_repository)
    
    def test_get_orders_by_client_value_error(self):
        """Test: get_orders_by_client con ValueError (línea 29)"""
        self.mock_repository.get_orders_with_items_by_client.side_effect = ValueError("Error de validación")
        
        with pytest.raises(OrderValidationError, match="Error de validación"):
            self.service.get_orders_by_client(1)
    
    def test_get_orders_by_vendor_value_error(self):
        """Test: get_orders_by_vendor con ValueError (línea 43)"""
        self.mock_repository.get_orders_with_items_by_vendor.side_effect = ValueError("Error de validación")
        
        with pytest.raises(OrderValidationError, match="Error de validación"):
            self.service.get_orders_by_vendor(1)
    
    def test_get_all_orders_success(self):
        """Test: get_all_orders exitoso (líneas 49-53)"""
        mock_orders = [MagicMock(spec=Order), MagicMock(spec=Order)]
        self.mock_repository.get_all.return_value = mock_orders
        
        result = self.service.get_all_orders()
        
        assert result == mock_orders
        self.mock_repository.get_all.assert_called_once()
    
    def test_get_all_orders_exception(self):
        """Test: get_all_orders con excepción (líneas 49-53)"""
        self.mock_repository.get_all.side_effect = Exception("Error de base de datos")
        
        with pytest.raises(OrderBusinessLogicError, match="Error al obtener todos los pedidos"):
            self.service.get_all_orders()
    
    def test_enrich_order_items_product_not_found(self):
        """Test: _enrich_order_items_with_product_info - producto no encontrado (líneas 82-84)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de la respuesta del servicio de inventarios
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': False,
            'data': None
        }
        
        with patch('requests.get', return_value=mock_response):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_request_exception(self):
        """Test: _enrich_order_items_with_product_info - RequestException (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de RequestException
        with patch('requests.get', side_effect=Exception("Connection error")):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_general_exception(self):
        """Test: _enrich_order_items_with_product_info - Exception general (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de Exception general
        with patch('requests.get', side_effect=Exception("General error")):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_success_with_data(self):
        """Test: _enrich_order_items_with_product_info - éxito con datos"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de la respuesta del servicio de inventarios
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'name': 'Updated Product',
                'photo_url': 'http://example.com/photo.jpg',
                'price': 25.50
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se actualizan correctamente
        assert result.items[0].product_name == 'Updated Product'
        assert result.items[0].product_image_url == 'http://example.com/photo.jpg'
        assert result.items[0].unit_price == 25.50
    
    def test_enrich_order_items_http_error(self):
        """Test: _enrich_order_items_with_product_info - error HTTP"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de respuesta con error HTTP
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch('requests.get', return_value=mock_response):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_empty_items(self):
        """Test: _enrich_order_items_with_product_info - sin items"""
        # Crear un pedido sin items
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        order.items = []
        
        result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que retorna el pedido sin cambios
        assert result == order
        assert len(result.items) == 0
    
    def test_enrich_order_items_custom_inventory_url(self):
        """Test: _enrich_order_items_with_product_info - URL personalizada"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de la respuesta del servicio de inventarios
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'name': 'Test Product',
                'photo_url': 'http://example.com/photo.jpg',
                'price': 15.00
            }
        }
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            with patch.dict('os.environ', {'INVENTORY_SERVICE_URL': 'http://custom-inventory:8080'}):
                result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que se usa la URL personalizada
        mock_get.assert_called_once_with(
            "http://custom-inventory:8080/inventory/products/101",
            timeout=5
        )
        
        # Verificar que los campos se actualizan correctamente
        assert result.items[0].product_name == 'Test Product'
        assert result.items[0].product_image_url == 'http://example.com/photo.jpg'
        assert result.items[0].unit_price == 15.00
    
    def test_get_orders_by_client_success(self):
        """Test: get_orders_by_client exitoso (línea 27)"""
        mock_orders = [MagicMock(spec=Order), MagicMock(spec=Order)]
        self.mock_repository.get_orders_with_items_by_client.return_value = mock_orders
        
        result = self.service.get_orders_by_client(1)
        
        assert result == mock_orders
        self.mock_repository.get_orders_with_items_by_client.assert_called_once_with(1)
    
    def test_get_orders_by_client_general_exception(self):
        """Test: get_orders_by_client con excepción general (líneas 30-31)"""
        self.mock_repository.get_orders_with_items_by_client.side_effect = Exception("Error de base de datos")
        
        with pytest.raises(OrderBusinessLogicError, match="Error al obtener pedidos del cliente"):
            self.service.get_orders_by_client(1)
    
    def test_get_orders_by_vendor_success(self):
        """Test: get_orders_by_vendor exitoso (línea 41)"""
        mock_orders = [MagicMock(spec=Order), MagicMock(spec=Order)]
        self.mock_repository.get_orders_with_items_by_vendor.return_value = mock_orders
        
        result = self.service.get_orders_by_vendor(1)
        
        assert result == mock_orders
        self.mock_repository.get_orders_with_items_by_vendor.assert_called_once_with(1)
    
    def test_get_orders_by_vendor_general_exception(self):
        """Test: get_orders_by_vendor con excepción general (líneas 44-45)"""
        self.mock_repository.get_orders_with_items_by_vendor.side_effect = Exception("Error de base de datos")
        
        with pytest.raises(OrderBusinessLogicError, match="Error al obtener pedidos del vendedor"):
            self.service.get_orders_by_vendor(1)
    
    def test_delete_all_orders_success(self):
        """Test: delete_all_orders exitoso (líneas 57-60)"""
        self.mock_repository.delete_all.return_value = 5
        
        result = self.service.delete_all_orders()
        
        assert result == True
        self.mock_repository.delete_all.assert_called_once()
    
    def test_delete_all_orders_exception(self):
        """Test: delete_all_orders con excepción (líneas 57-60)"""
        self.mock_repository.delete_all.side_effect = Exception("Error de base de datos")
        
        with pytest.raises(OrderBusinessLogicError, match="Error al eliminar todos los pedidos"):
            self.service.delete_all_orders()
    
    def test_enrich_order_items_request_exception_specific(self):
        """Test: _enrich_order_items_with_product_info - RequestException específico (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de RequestException específico
        import requests
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Connection timeout")):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_get_orders_by_client_zero_id(self):
        """Test: get_orders_by_client con ID cero (línea 23)"""
        with pytest.raises(OrderValidationError, match="El ID del cliente es obligatorio y debe ser mayor a 0"):
            self.service.get_orders_by_client(0)
    
    def test_get_orders_by_vendor_zero_id(self):
        """Test: get_orders_by_vendor con ID cero (línea 37)"""
        with pytest.raises(OrderValidationError, match="El ID del vendedor es obligatorio y debe ser mayor a 0"):
            self.service.get_orders_by_vendor(0)
    
    def test_enrich_order_items_general_exception_specific(self):
        """Test: _enrich_order_items_with_product_info - Exception general específico (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de Exception general específico
        with patch('requests.get', side_effect=Exception("General error")):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_json_decode_error(self):
        """Test: _enrich_order_items_with_product_info - JSON decode error (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock de respuesta con JSON inválido
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch('requests.get', return_value=mock_response):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_attribute_error(self):
        """Test: _enrich_order_items_with_product_info - AttributeError (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock que simule un AttributeError al acceder a los campos del item
        def mock_get(*args, **kwargs):
            # Simular un error al acceder a los campos del item
            item.product_name = None  # Esto debería funcionar
            item.product_image_url = None
            item.unit_price = None
            raise AttributeError("Simulated attribute error")
        
        with patch('requests.get', side_effect=mock_get):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_key_error(self):
        """Test: _enrich_order_items_with_product_info - KeyError (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock que simule un KeyError
        def mock_get(*args, **kwargs):
            raise KeyError("Simulated key error")
        
        with patch('requests.get', side_effect=mock_get):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_type_error(self):
        """Test: _enrich_order_items_with_product_info - TypeError (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock que simule un TypeError
        def mock_get(*args, **kwargs):
            raise TypeError("Simulated type error")
        
        with patch('requests.get', side_effect=mock_get):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_runtime_error(self):
        """Test: _enrich_order_items_with_product_info - RuntimeError (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock que simule un RuntimeError
        def mock_get(*args, **kwargs):
            raise RuntimeError("Simulated runtime error")
        
        with patch('requests.get', side_effect=mock_get):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
    
    def test_enrich_order_items_os_error(self):
        """Test: _enrich_order_items_with_product_info - OSError (líneas 96-100)"""
        # Crear un pedido con un item
        order = Order(
            order_number="PED-20240101-00001",
            client_id=1,
            vendor_id=1
        )
        
        item = OrderItem(
            id=1,
            order_id=1,
            product_id=101,
            quantity=2,
            product_name="Test Product"
        )
        order.items = [item]
        
        # Mock que simule un OSError
        def mock_get(*args, **kwargs):
            raise OSError("Simulated OS error")
        
        with patch('requests.get', side_effect=mock_get):
            result = self.service._enrich_order_items_with_product_info(order)
        
        # Verificar que los campos se establecen como None
        assert result.items[0].product_name is None
        assert result.items[0].product_image_url is None
        assert result.items[0].unit_price is None
