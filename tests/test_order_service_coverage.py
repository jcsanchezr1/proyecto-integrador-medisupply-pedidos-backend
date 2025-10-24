"""
Tests para mejorar coverage del OrderService
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderServiceCoverage:
    """Tests para mejorar coverage del OrderService"""
    
    @pytest.fixture
    def mock_order_repository(self):
        """Mock del OrderRepository"""
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_inventory_service(self):
        """Mock del InventoryService"""
        return MagicMock()
    
    @pytest.fixture
    def mock_inventory_integration(self):
        """Mock del InventoryIntegration"""
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_inventory_service, mock_inventory_integration):
        """Instancia de OrderService con dependencias mockeadas"""
        with patch('app.services.order_service.InventoryService') as mock_service_class:
            with patch('app.services.order_service.InventoryIntegration') as mock_integration_class:
                mock_service_class.return_value = mock_inventory_service
                mock_integration_class.return_value = mock_inventory_integration
                
                service = OrderService(mock_order_repository)
                service.inventory_service = mock_inventory_service
                service.inventory_integration = mock_inventory_integration
                return service
    
    @pytest.fixture
    def valid_order_data(self):
        """Datos válidos para crear un pedido"""
        return {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'vendor_id': '456e7890-e89b-12d3-a456-426614174001',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
    
    def test_create_order_success(self, order_service, mock_order_repository, mock_inventory_integration, valid_order_data):
        """Test: Creación exitosa de pedido"""
        mock_products = [{'id': 1, 'name': 'Producto 1', 'quantity': 5}]
        mock_inventory_integration.verify_products_availability.return_value = mock_products

        mock_inventory_integration.update_products_stock_with_compensation.return_value = None

        mock_order = MagicMock()
        mock_order.to_dict.return_value = {'id': 1, 'order_number': 'PED-001'}
        mock_order_repository.create.return_value = mock_order
        
        result = order_service.create_order(valid_order_data)
        
        assert result == mock_order
        mock_inventory_integration.verify_products_availability.assert_called_once()
        mock_inventory_integration.update_products_stock_with_compensation.assert_called_once()
        mock_order_repository.create.assert_called_once()
    
    def test_create_order_missing_client_and_vendor(self, order_service):
        """Test: Error cuando faltan client_id y vendor_id"""
        order_data = {
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "Debe proporcionar al menos client_id o vendor_id" in str(exc_info.value)
    
    def test_create_order_missing_items(self, order_service):
        """Test: Error cuando faltan items"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z'
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "El pedido debe tener al menos un item" in str(exc_info.value)
    
    def test_create_order_empty_items(self, order_service):
        """Test: Error cuando items está vacío"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': []
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "El pedido debe tener al menos un item" in str(exc_info.value)
    
    def test_create_order_missing_total_amount(self, order_service):
        """Test: Error cuando falta total_amount"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "El total_amount es obligatorio" in str(exc_info.value)
    
    def test_create_order_invalid_total_amount(self, order_service):
        """Test: Error cuando total_amount es inválido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': -5.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "El total_amount debe ser un número mayor a 0" in str(exc_info.value)
    
    def test_create_order_missing_scheduled_delivery_date(self, order_service):
        """Test: Error cuando falta scheduled_delivery_date"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "El scheduled_delivery_date es obligatorio" in str(exc_info.value)
    
    def test_create_order_invalid_date_format(self, order_service):
        """Test: Error cuando el formato de fecha es inválido"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': 'invalid-date',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "El scheduled_delivery_date debe tener formato ISO 8601 válido" in str(exc_info.value)
    
    def test_create_order_past_date(self, order_service):
        """Test: Error cuando la fecha es en el pasado"""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': past_date,
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "La fecha de entrega no puede ser en el pasado" in str(exc_info.value)
    
    def test_create_order_invalid_item_missing_product_id(self, order_service):
        """Test: Error cuando un item no tiene product_id"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'quantity': 2}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "Cada item debe tener un product_id" in str(exc_info.value)
    
    def test_create_order_invalid_item_missing_quantity(self, order_service):
        """Test: Error cuando un item no tiene quantity"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "Cada item debe tener una cantidad válida mayor a 0" in str(exc_info.value)
    
    def test_create_order_invalid_item_zero_quantity(self, order_service):
        """Test: Error cuando un item tiene quantity cero"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 0}]
        }
        
        with pytest.raises(OrderValidationError) as exc_info:
            order_service.create_order(order_data)
        
        assert "Cada item debe tener una cantidad válida mayor a 0" in str(exc_info.value)
    
    def test_create_order_stock_verification_error(self, order_service, mock_inventory_integration):
        """Test: Error en verificación de stock"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }
        
        mock_inventory_integration.verify_products_availability.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.create_order(order_data)
        
        assert str(exc_info.value) == "Stock insuficiente"
    
    def test_create_order_stock_update_error(self, order_service, mock_inventory_integration):
        """Test: Error en actualización de stock"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }

        mock_products = [{'id': 1, 'name': 'Producto 1', 'quantity': 5}]
        mock_inventory_integration.verify_products_availability.return_value = mock_products
        mock_inventory_integration.update_products_stock_with_compensation.side_effect = OrderBusinessLogicError("Error actualizando stock")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.create_order(order_data)
        
        assert str(exc_info.value) == "Error actualizando stock"
    
    def test_create_order_repository_error(self, order_service, mock_order_repository, mock_inventory_integration):
        """Test: Error en el repositorio"""
        order_data = {
            'client_id': '123e4567-e89b-12d3-a456-426614174000',
            'total_amount': 150.0,
            'scheduled_delivery_date': '2025-12-25T10:00:00Z',
            'items': [{'product_id': 1, 'quantity': 2}]
        }

        mock_products = [{'id': 1, 'name': 'Producto 1', 'quantity': 5}]
        mock_inventory_integration.verify_products_availability.return_value = mock_products
        mock_inventory_integration.update_products_stock_with_compensation.return_value = None
        mock_order_repository.create.side_effect = Exception("Error de base de datos")
        
        with pytest.raises(Exception) as exc_info:
            order_service.create_order(order_data)
        
        assert str(exc_info.value) == "Error inesperado al crear pedido: Error de base de datos"