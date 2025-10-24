"""
Tests para el servicio de inventario
"""
import pytest
from unittest.mock import Mock, patch
import requests
from app.services.inventory_service import InventoryService
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestInventoryService:
    """Tests para InventoryService"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.inventory_service = InventoryService("http://localhost:8084")
    
    @patch('requests.get')
    def test_check_product_availability_success(self, mock_get):
        """Test de verificación exitosa de disponibilidad"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'id': 1,
                'sku': 'MED-0001',
                'name': 'Producto Test',
                'price': 25.50,
                'quantity': 10
            }
        }
        mock_get.return_value = mock_response
        
        result = self.inventory_service.check_product_availability(1, 5)
        
        assert result['product_id'] == 1
        assert result['sku'] == 'MED-0001'
        assert result['name'] == 'Producto Test'
        assert result['price'] == 25.50
        assert result['available_quantity'] == 10
        assert result['required_quantity'] == 5
    
    @patch('requests.get')
    def test_check_product_availability_product_not_found(self, mock_get):
        """Test de error cuando el producto no existe"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(999, 5)
        
        assert "Producto con ID 999 no encontrado" in str(exc_info.value)
    
    @patch('requests.get')
    def test_check_product_availability_insufficient_stock(self, mock_get):
        """Test de error cuando no hay stock suficiente"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'id': 1,
                'sku': 'MED-0001',
                'name': 'Producto Test',
                'price': 25.50,
                'quantity': 3
            }
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(1, 5)
        
        assert "Stock insuficiente" in str(exc_info.value)
        assert "Disponible: 3" in str(exc_info.value)
        assert "Requerido: 5" in str(exc_info.value)
    
    @patch('requests.get')
    def test_check_product_availability_api_error(self, mock_get):
        """Test de error de API"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(1, 5)
        
        assert "Error al consultar producto: 500" in str(exc_info.value)
    
    @patch('requests.get')
    def test_check_product_availability_connection_error(self, mock_get):
        """Test de error de conexión"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(1, 5)
        
        assert "Error de conexión con el servicio de inventarios" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_success(self, mock_put):
        """Test de actualización exitosa de stock"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'product_id': 1,
                'previous_quantity': 10,
                'new_quantity': 8,
                'operation': 'subtract',
                'quantity_changed': 2
            }
        }
        mock_put.return_value = mock_response
        
        result = self.inventory_service.update_product_stock(1, 2)
        
        assert result['product_id'] == 1
        assert result['previous_quantity'] == 10
        assert result['new_quantity'] == 8
        assert result['operation'] == 'subtract'
        assert result['quantity_changed'] == 2
    
    @patch('requests.put')
    def test_update_product_stock_insufficient_stock(self, mock_put):
        """Test de error cuando no hay stock suficiente para actualizar"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            'success': False,
            'error': 'Error de lógica de negocio',
            'details': 'Stock insuficiente. Disponible: 1, Solicitado: 5'
        }
        mock_put.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 5)
        
        assert "Stock insuficiente" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_product_not_found(self, mock_put):
        """Test de error cuando el producto no existe para actualizar"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_put.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(999, 2)
        
        assert "Producto con ID 999 no encontrado" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_connection_error(self, mock_put):
        """Test de error de conexión en actualización"""
        mock_put.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 2)
        
        assert "Error de conexión con el servicio de inventarios" in str(exc_info.value)
    
    @patch.object(InventoryService, 'check_product_availability')
    def test_check_multiple_products_availability_success(self, mock_check):
        """Test de verificación exitosa de múltiples productos"""
        order_items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        mock_check.side_effect = [
            {'product_id': 1, 'sku': 'MED-0001', 'name': 'Producto 1', 'price': 25.50, 'available_quantity': 10, 'required_quantity': 2},
            {'product_id': 2, 'sku': 'MED-0002', 'name': 'Producto 2', 'price': 15.00, 'available_quantity': 5, 'required_quantity': 1}
        ]
        
        result = self.inventory_service.check_multiple_products_availability(order_items)
        
        assert len(result) == 2
        assert result[0]['product_id'] == 1
        assert result[1]['product_id'] == 2
        assert mock_check.call_count == 2
    
    @patch.object(InventoryService, 'check_product_availability')
    def test_check_multiple_products_availability_error(self, mock_check):
        """Test de error en verificación de múltiples productos"""
        order_items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        mock_check.side_effect = [
            {'product_id': 1, 'sku': 'MED-0001', 'name': 'Producto 1', 'price': 25.50, 'available_quantity': 10, 'required_quantity': 2},
            OrderBusinessLogicError("Stock insuficiente para producto 2")
        ]
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_multiple_products_availability(order_items)
        
        assert "Stock insuficiente para producto 2" in str(exc_info.value)
    
    @patch.object(InventoryService, 'update_product_stock')
    def test_update_multiple_products_stock_success(self, mock_update):
        """Test de actualización exitosa de múltiples productos"""
        order_items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        mock_update.side_effect = [
            {'product_id': 1, 'previous_quantity': 10, 'new_quantity': 8, 'operation': 'subtract', 'quantity_changed': 2},
            {'product_id': 2, 'previous_quantity': 5, 'new_quantity': 4, 'operation': 'subtract', 'quantity_changed': 1}
        ]
        
        result = self.inventory_service.update_multiple_products_stock(order_items)
        
        assert len(result) == 2
        assert result[0]['product_id'] == 1
        assert result[1]['product_id'] == 2
        assert mock_update.call_count == 2
