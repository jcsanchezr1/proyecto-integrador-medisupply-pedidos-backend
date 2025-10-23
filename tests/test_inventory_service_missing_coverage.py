"""
Tests adicionales para InventoryService - cubrir líneas faltantes
"""
import pytest
from unittest.mock import Mock, patch
import requests
from app.services.inventory_service import InventoryService
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestInventoryServiceMissingCoverage:
    """Tests para cubrir las líneas faltantes del InventoryService"""
    
    def setup_method(self):
        """Configuración inicial para cada test"""
        self.inventory_service = InventoryService("http://localhost:8084")
    
    @patch('requests.get')
    def test_check_product_availability_api_success_false(self, mock_get):
        """Test: API retorna success=False"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': False,
            'error': 'Producto no disponible'
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(1, 5)
        
        assert "Error al obtener producto: Producto no disponible" in str(exc_info.value)
    
    @patch('requests.get')
    def test_check_product_availability_generic_exception(self, mock_get):
        """Test: Excepción genérica en check_product_availability"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("Error de procesamiento JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(1, 5)
        
        assert "Error de conexión con el servicio de inventarios: Error de procesamiento JSON" in str(exc_info.value)
    
    @patch('requests.get')
    def test_check_product_availability_order_business_logic_error_re_raise(self, mock_get):
        """Test: Re-lanzar OrderBusinessLogicError"""
        mock_get.side_effect = OrderBusinessLogicError("Error de negocio")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.check_product_availability(1, 5)
        
        assert "Error de negocio" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_api_error_non_200_non_404_non_422(self, mock_put):
        """Test: API retorna status_code diferente a 200, 404, 422"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            'success': False,
            'error': 'Error interno del servidor'
        }
        mock_put.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 2)
        
        assert "Error al actualizar stock: Error interno del servidor" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_api_success_false(self, mock_put):
        """Test: API retorna success=False en update"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': False,
            'error': 'Error en la actualización'
        }
        mock_put.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 2)
        
        assert "Error al actualizar stock: Error en la actualización" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_generic_exception(self, mock_put):
        """Test: Excepción genérica en update_product_stock"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("Error de procesamiento JSON en actualización")
        mock_put.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 2)
        
        assert "Error de conexión con el servicio de inventarios: Error de procesamiento JSON en actualización" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_order_business_logic_error_re_raise(self, mock_put):
        """Test: Re-lanzar OrderBusinessLogicError en update"""
        mock_put.side_effect = OrderBusinessLogicError("Error de negocio en actualización")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 2)
        
        assert "Error de negocio en actualización" in str(exc_info.value)
    
    @patch('requests.put')
    def test_update_product_stock_api_error_without_error_field(self, mock_put):
        """Test: API retorna error sin campo 'error'"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            'success': False,
            'message': 'Error interno'
        }
        mock_put.return_value = mock_response
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            self.inventory_service.update_product_stock(1, 2)
        
        assert "Error al actualizar stock: Error desconocido" in str(exc_info.value)
