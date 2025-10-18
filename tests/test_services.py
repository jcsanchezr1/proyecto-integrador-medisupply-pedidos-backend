"""
Tests para el servicio de pedidos
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.services.order_service import OrderService
from app.models.order import Order
from app.models.order_item import OrderItem
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderService:
    """Tests para OrderService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del OrderRepository"""
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_repository):
        """Instancia de OrderService con repository mockeado"""
        return OrderService(order_repository=mock_repository)
    
    @pytest.fixture
    def sample_order(self):
        """Pedido de muestra para testing"""
        order = Order(
            order_number="PED-20241201-00001",
            client_id=123,
            vendor_id=456,
            status="RECIBIDO",
            scheduled_delivery_date=datetime.utcnow() + timedelta(days=1),
            assigned_truck="TRUCK-001"
        )
        return order
    
    @pytest.fixture
    def sample_order_item(self):
        """Item de pedido de muestra para testing"""
        order_item = OrderItem(
            product_id=123,
            product_name="Producto Test",
            quantity=5,
            unit_price=100.0,
            order_id=1
        )
        return order_item
    
    def test_get_orders_by_client_success(self, order_service, mock_repository, sample_order):
        """Test: Obtener pedidos por cliente exitosamente"""
        mock_repository.get_orders_with_items_by_client.return_value = [sample_order]
        
        result = order_service.get_orders_by_client(123)
        
        assert len(result) == 1
        assert isinstance(result[0], Order)
        assert result[0].client_id == 123
        mock_repository.get_orders_with_items_by_client.assert_called_once_with(123)
    
    def test_get_orders_by_client_empty(self, order_service, mock_repository):
        """Test: Obtener pedidos por cliente cuando no hay pedidos"""
        mock_repository.get_orders_with_items_by_client.return_value = []
        
        result = order_service.get_orders_by_client(123)
        
        assert result == []
        mock_repository.get_orders_with_items_by_client.assert_called_once_with(123)
    
    def test_get_orders_by_client_validation_error(self, order_service):
        """Test: Error de validación en get_orders_by_client"""
        with pytest.raises(OrderValidationError, match="El ID del cliente es obligatorio"):
            order_service.get_orders_by_client(None)
    
    def test_get_orders_by_client_invalid_id(self, order_service):
        """Test: ID de cliente inválido en get_orders_by_client"""
        with pytest.raises(OrderValidationError, match="El ID del cliente es obligatorio"):
            order_service.get_orders_by_client(0)
    
    def test_get_orders_by_vendor_success(self, order_service, mock_repository, sample_order):
        """Test: Obtener pedidos por vendedor exitosamente"""
        mock_repository.get_orders_with_items_by_vendor.return_value = [sample_order]
        
        result = order_service.get_orders_by_vendor(456)
        
        assert len(result) == 1
        assert isinstance(result[0], Order)
        assert result[0].vendor_id == 456
        mock_repository.get_orders_with_items_by_vendor.assert_called_once_with(456)
    
    def test_get_orders_by_vendor_empty(self, order_service, mock_repository):
        """Test: Obtener pedidos por vendedor cuando no hay pedidos"""
        mock_repository.get_orders_with_items_by_vendor.return_value = []
        
        result = order_service.get_orders_by_vendor(456)
        
        assert result == []
        mock_repository.get_orders_with_items_by_vendor.assert_called_once_with(456)
    
    def test_get_orders_by_vendor_validation_error(self, order_service):
        """Test: Error de validación en get_orders_by_vendor"""
        with pytest.raises(OrderValidationError, match="El ID del vendedor es obligatorio"):
            order_service.get_orders_by_vendor(None)
    
    def test_get_orders_by_vendor_invalid_id(self, order_service):
        """Test: ID de vendedor inválido en get_orders_by_vendor"""
        with pytest.raises(OrderValidationError, match="El ID del vendedor es obligatorio"):
            order_service.get_orders_by_vendor(0)
    
    def test_delete_all_orders_success(self, order_service, mock_repository):
        """Test: Eliminar todos los pedidos exitosamente"""
        mock_repository.delete_all.return_value = 5
        
        result = order_service.delete_all_orders()
        
        assert result == True
        mock_repository.delete_all.assert_called_once()
    
    def test_delete_all_orders_empty(self, order_service, mock_repository):
        """Test: Eliminar todos los pedidos cuando no hay pedidos"""
        mock_repository.delete_all.return_value = 0
        
        result = order_service.delete_all_orders()
        
        assert result == True
        mock_repository.delete_all.assert_called_once()
    
    def test_delete_all_orders_database_error(self, order_service, mock_repository):
        """Test: Error de base de datos en delete_all_orders"""
        mock_repository.delete_all.side_effect = Exception("Database error")
        
        with pytest.raises(OrderBusinessLogicError, match="Error al eliminar todos los pedidos"):
            order_service.delete_all_orders()
    
    @patch('app.services.order_service.requests.get')
    def test_enrich_order_items_with_product_info_success(self, mock_requests_get, order_service, sample_order, sample_order_item):
        """Test: Enriquecer items con información del producto exitosamente"""
        # Mock de respuesta del servicio de inventarios
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'id': 123,
                'name': 'Producto Test',
                'photo_url': 'https://example.com/test.jpg',
                'price': 100.0
            }
        }
        mock_requests_get.return_value = mock_response
        
        sample_order.items = [sample_order_item]
        
        order_service._enrich_order_items_with_product_info(sample_order)
        
        # Verificar que se hizo la llamada HTTP
        mock_requests_get.assert_called_once()
        
        # Verificar que se asignaron los valores
        assert sample_order_item.product_name == 'Producto Test'
        assert sample_order_item.product_image_url == 'https://example.com/test.jpg'
        assert sample_order_item.unit_price == 100.0
    
    @patch('app.services.order_service.requests.get')
    def test_enrich_order_items_with_product_info_not_found(self, mock_requests_get, order_service, sample_order, sample_order_item):
        """Test: Enriquecer items cuando el producto no se encuentra"""
        # Mock de respuesta 404 del servicio de inventarios
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        
        sample_order.items = [sample_order_item]
        
        order_service._enrich_order_items_with_product_info(sample_order)
        
        # Verificar que se hizo la llamada HTTP
        mock_requests_get.assert_called_once()
        
        # Verificar que se asignaron valores None
        assert sample_order_item.product_name is None
        assert sample_order_item.product_image_url is None
        assert sample_order_item.unit_price is None
    
    @patch('app.services.order_service.requests.get')
    def test_enrich_order_items_with_product_info_network_error(self, mock_requests_get, order_service, sample_order, sample_order_item):
        """Test: Enriquecer items cuando hay error de red"""
        # Mock de excepción de red
        mock_requests_get.side_effect = Exception("Network error")
        
        sample_order.items = [sample_order_item]
        
        order_service._enrich_order_items_with_product_info(sample_order)
        
        # Verificar que se hizo la llamada HTTP
        mock_requests_get.assert_called_once()
        
        # Verificar que se asignaron valores None por el error
        assert sample_order_item.product_name is None
        assert sample_order_item.product_image_url is None
        assert sample_order_item.unit_price is None
    
    @patch('app.services.order_service.requests.get')
    def test_enrich_order_items_with_product_info_invalid_json(self, mock_requests_get, order_service, sample_order, sample_order_item):
        """Test: Enriquecer items cuando la respuesta JSON es inválida"""
        # Mock de respuesta con JSON inválido
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_requests_get.return_value = mock_response
        
        sample_order.items = [sample_order_item]
        
        order_service._enrich_order_items_with_product_info(sample_order)
        
        # Verificar que se hizo la llamada HTTP
        mock_requests_get.assert_called_once()
        
        # Verificar que se asignaron valores None por el error
        assert sample_order_item.product_name is None
        assert sample_order_item.product_image_url is None
        assert sample_order_item.unit_price is None
    
    def test_enrich_order_items_with_product_info_no_items(self, order_service, sample_order):
        """Test: Enriquecer items cuando no hay items"""
        sample_order.items = []
        
        # No debería lanzar excepción
        order_service._enrich_order_items_with_product_info(sample_order)
        
        # No se debería hacer ninguna llamada HTTP
        assert True  # Si llegamos aquí, no hubo excepción
    
    def test_get_orders_by_client_repository_error(self, order_service, mock_repository):
        """Test: Error del repositorio en get_orders_by_client"""
        mock_repository.get_orders_with_items_by_client.side_effect = Exception("Repository error")
        
        with pytest.raises(Exception, match="Error al obtener pedidos del cliente"):
            order_service.get_orders_by_client(123)
    
    def test_get_orders_by_vendor_repository_error(self, order_service, mock_repository):
        """Test: Error del repositorio en get_orders_by_vendor"""
        mock_repository.get_orders_with_items_by_vendor.side_effect = Exception("Repository error")
        
        with pytest.raises(Exception, match="Error al obtener pedidos del vendedor"):
            order_service.get_orders_by_vendor(456)
