"""
Tests para mejorar coverage del InventoryIntegration
"""
import pytest
from unittest.mock import MagicMock, patch
from app.integrations.inventory_integration import InventoryIntegration
from app.services.inventory_service import InventoryService
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestInventoryIntegrationCoverage:
    """Tests para mejorar coverage del InventoryIntegration"""
    
    @pytest.fixture
    def mock_inventory_service(self):
        """Mock del InventoryService"""
        return MagicMock(spec=InventoryService)
    
    @pytest.fixture
    def inventory_integration(self, mock_inventory_service):
        """Instancia de InventoryIntegration con servicio mockeado"""
        return InventoryIntegration(mock_inventory_service)
    
    def test_verify_products_availability_success(self, inventory_integration, mock_inventory_service):
        """Test: Verificación exitosa de disponibilidad de productos"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        expected_products = [
            {'id': 1, 'name': 'Producto 1', 'quantity': 5},
            {'id': 2, 'name': 'Producto 2', 'quantity': 3}
        ]
        
        mock_inventory_service.check_multiple_products_availability.return_value = expected_products
        
        result = inventory_integration.verify_products_availability(items)
        
        assert result == expected_products
        mock_inventory_service.check_multiple_products_availability.assert_called_once_with(items)
    
    def test_verify_products_availability_error(self, inventory_integration, mock_inventory_service):
        """Test: Error en verificación de disponibilidad"""
        items = [{'product_id': 1, 'quantity': 10}]
        
        mock_inventory_service.check_multiple_products_availability.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            inventory_integration.verify_products_availability(items)
        
        assert str(exc_info.value) == "Stock insuficiente"
        mock_inventory_service.check_multiple_products_availability.assert_called_once_with(items)
    
    def test_update_products_stock_with_compensation_success(self, inventory_integration, mock_inventory_service):
        """Test: Actualización exitosa de stock con compensación"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]

        mock_inventory_service.update_product_stock.return_value = None
        inventory_integration.update_products_stock_with_compensation(items)
        
        assert mock_inventory_service.update_product_stock.call_count == 2
        mock_inventory_service.update_product_stock.assert_any_call(1, 2)
        mock_inventory_service.update_product_stock.assert_any_call(2, 1)
    
    def test_update_products_stock_with_compensation_partial_failure(self, inventory_integration, mock_inventory_service):
        """Test: Actualización con fallo parcial y compensación exitosa"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]

        def side_effect(product_id, quantity):
            if product_id == 1:
                return None
            else:
                raise OrderBusinessLogicError("Stock insuficiente")
        
        mock_inventory_service.update_product_stock.side_effect = side_effect
        mock_inventory_service._make_request = MagicMock()
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            inventory_integration.update_products_stock_with_compensation(items)
        
        assert str(exc_info.value) == "Stock insuficiente"

        mock_inventory_service._make_request.assert_called_once_with(
            "PUT", 
            "/products/1/stock", 
            json={
                "operation": "add",
                "quantity": 2,
                "reason": "compensation"
            }
        )
    
    def test_update_products_stock_with_compensation_compensation_failure(self, inventory_integration, mock_inventory_service):
        """Test: Fallo en la compensación"""
        items = [{'product_id': 1, 'quantity': 2}]
        mock_inventory_service.update_product_stock.side_effect = OrderBusinessLogicError("Stock insuficiente")

        def mock_make_request(*args, **kwargs):
            raise Exception("Error de compensación")
        
        mock_inventory_service._make_request = mock_make_request
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            inventory_integration.update_products_stock_with_compensation(items)
        
        assert str(exc_info.value) == "Stock insuficiente"
    
    def test_update_products_stock_with_compensation_multiple_items_partial_failure(self, inventory_integration, mock_inventory_service):
        """Test: Múltiples items con fallo parcial y compensación"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1},
            {'product_id': 3, 'quantity': 3}
        ]
        
        # Primeros dos productos exitosos, tercero falla
        def side_effect(product_id, quantity):
            if product_id in [1, 2]:
                return None  # Éxito
            else:
                raise OrderBusinessLogicError("Stock insuficiente")
        
        mock_inventory_service.update_product_stock.side_effect = side_effect
        mock_inventory_service._make_request = MagicMock()
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            inventory_integration.update_products_stock_with_compensation(items)
        
        assert str(exc_info.value) == "Stock insuficiente"
        assert mock_inventory_service._make_request.call_count == 2

        calls = mock_inventory_service._make_request.call_args_list
        assert calls[0][0] == ("PUT", "/products/1/stock")
        assert calls[0][1]["json"] == {"operation": "add", "quantity": 2, "reason": "compensation"}
        assert calls[1][0] == ("PUT", "/products/2/stock")
        assert calls[1][1]["json"] == {"operation": "add", "quantity": 1, "reason": "compensation"}
