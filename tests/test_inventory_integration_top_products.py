"""
Tests para el método get_product_names de InventoryIntegration
"""
import pytest
from unittest.mock import MagicMock
from app.integrations.inventory_integration import InventoryIntegration


class TestInventoryIntegrationProductNames:
    """Tests para get_product_names"""
    
    @pytest.fixture
    def mock_inventory_service(self):
        return MagicMock()
    
    @pytest.fixture
    def inventory_integration(self, mock_inventory_service):
        return InventoryIntegration(mock_inventory_service)
    
    def test_get_product_names_success(self, inventory_integration, mock_inventory_service):
        product_ids = [1, 2, 3]
        mock_inventory_service.get_product_by_id.side_effect = [
            {'name': 'Producto Uno'},
            {'name': 'Producto Dos'},
            {'name': 'Producto Tres'}
        ]
        
        result = inventory_integration.get_product_names(product_ids)
        
        assert result == {
            1: 'Producto Uno',
            2: 'Producto Dos',
            3: 'Producto Tres'
        }
        assert mock_inventory_service.get_product_by_id.call_count == 3
    
    def test_get_product_names_empty_list(self, inventory_integration, mock_inventory_service):
        product_ids = []
        
        result = inventory_integration.get_product_names(product_ids)
        
        assert result == {}
        mock_inventory_service.get_product_by_id.assert_not_called()
    
    def test_get_product_names_with_unavailable(self, inventory_integration, mock_inventory_service):
        product_ids = [1, 2]
        mock_inventory_service.get_product_by_id.side_effect = [
            {'name': 'Producto Uno'},
            {'name': ''}
        ]
        
        result = inventory_integration.get_product_names(product_ids)
        
        assert result[1] == 'Producto Uno'
        assert result[2] == 'Producto no disponible'
    
    def test_get_product_names_with_none_name(self, inventory_integration, mock_inventory_service):
        product_ids = [1]
        mock_inventory_service.get_product_by_id.return_value = {'name': None}
        
        result = inventory_integration.get_product_names(product_ids)
        
        assert result[1] == 'Producto no disponible'
    
    def test_get_product_names_with_empty_product_id(self, inventory_integration, mock_inventory_service):
        product_ids = [1, None, 0, 2]
        
        mock_inventory_service.get_product_by_id.side_effect = [
            {'name': 'Producto Uno'},
            {'name': 'Producto Dos'}
        ]
        
        result = inventory_integration.get_product_names(product_ids)
        
        assert 1 in result
        assert 2 in result
        assert None not in result
        assert 0 not in result
        assert mock_inventory_service.get_product_by_id.call_count == 2

