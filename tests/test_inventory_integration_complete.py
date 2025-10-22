"""
Tests completos para InventoryIntegration
"""
import pytest
from unittest.mock import Mock, patch
from app.integrations.inventory_integration import InventoryIntegration
from app.services.inventory_service import InventoryService
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestInventoryIntegrationComplete:
    """Tests completos para InventoryIntegration"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_inventory_service = Mock(spec=InventoryService)
        self.integration = InventoryIntegration(self.mock_inventory_service)
    
    def test_verify_products_availability_success(self):
        """Test de verificación exitosa de disponibilidad de productos"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        expected_products = [
            {'id': 1, 'name': 'Producto 1', 'quantity': 5},
            {'id': 2, 'name': 'Producto 2', 'quantity': 3}
        ]
        
        self.mock_inventory_service.check_multiple_products_availability.return_value = expected_products
        
        result = self.integration.verify_products_availability(items)
        
        assert result == expected_products
        self.mock_inventory_service.check_multiple_products_availability.assert_called_once_with(items)
    
    def test_verify_products_availability_product_not_found(self):
        """Test de error cuando un producto no se encuentra"""
        items = [{'product_id': 999, 'quantity': 2}]
        
        self.mock_inventory_service.check_multiple_products_availability.side_effect = OrderBusinessLogicError("Producto no encontrado")
        
        with pytest.raises(OrderBusinessLogicError, match="Producto no encontrado"):
            self.integration.verify_products_availability(items)
    
    def test_verify_products_availability_insufficient_stock(self):
        """Test de error cuando no hay stock suficiente"""
        items = [{'product_id': 1, 'quantity': 100}]
        
        self.mock_inventory_service.check_multiple_products_availability.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with pytest.raises(OrderBusinessLogicError, match="Stock insuficiente"):
            self.integration.verify_products_availability(items)
    
    def test_update_products_stock_with_compensation_success(self):
        """Test de actualización exitosa de stock con compensación"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        self.mock_inventory_service.update_product_stock.return_value = None
        
        self.integration.update_products_stock_with_compensation(items)
        
        assert self.mock_inventory_service.update_product_stock.call_count == 2
        self.mock_inventory_service.update_product_stock.assert_any_call(1, 2)
        self.mock_inventory_service.update_product_stock.assert_any_call(2, 1)
    
    def test_update_products_stock_with_compensation_first_product_fails(self):
        """Test de fallo en el primer producto con compensación"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        self.mock_inventory_service.update_product_stock.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with pytest.raises(OrderBusinessLogicError, match="Stock insuficiente"):
            self.integration.update_products_stock_with_compensation(items)
        
        self.mock_inventory_service.update_product_stock.assert_called_once_with(1, 2)
    
    def test_update_products_stock_with_compensation_second_product_fails(self):
        """Test de fallo en el segundo producto con compensación del primero"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        def side_effect(product_id, quantity):
            if product_id == 1:
                return None
            else:
                raise OrderBusinessLogicError("Stock insuficiente")
        
        self.mock_inventory_service.update_product_stock.side_effect = side_effect
        
        with patch.object(self.mock_inventory_service, '_make_request') as mock_request:
            with pytest.raises(OrderBusinessLogicError, match="Stock insuficiente"):
                self.integration.update_products_stock_with_compensation(items)
            
            mock_request.assert_called_once_with(
                "PUT", 
                "/products/1/stock", 
                json={
                    "operation": "add",
                    "quantity": 2,
                    "reason": "compensation"
                }
            )
    
    def test_update_products_stock_with_compensation_third_product_fails(self):
        """Test de fallo en el tercer producto con compensación de los anteriores"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1},
            {'product_id': 3, 'quantity': 3}
        ]
        
        def side_effect(product_id, quantity):
            if product_id == 3:
                raise OrderBusinessLogicError("Stock insuficiente")
            return None
        
        self.mock_inventory_service.update_product_stock.side_effect = side_effect
        
        with patch.object(self.mock_inventory_service, '_make_request') as mock_request:
            with pytest.raises(OrderBusinessLogicError, match="Stock insuficiente"):
                self.integration.update_products_stock_with_compensation(items)
            
            assert mock_request.call_count == 2
            mock_request.assert_any_call(
                "PUT", 
                "/products/1/stock", 
                json={
                    "operation": "add",
                    "quantity": 2,
                    "reason": "compensation"
                }
            )
            mock_request.assert_any_call(
                "PUT", 
                "/products/2/stock", 
                json={
                    "operation": "add",
                    "quantity": 1,
                    "reason": "compensation"
                }
            )
    
    def test_update_products_stock_with_compensation_compensation_fails(self):
        """Test de fallo en la compensación"""
        items = [{'product_id': 1, 'quantity': 2}]
        
        self.mock_inventory_service.update_product_stock.side_effect = OrderBusinessLogicError("Stock insuficiente")
        
        with patch.object(self.mock_inventory_service, '_make_request', side_effect=Exception("Error de compensación")):
            with pytest.raises(OrderBusinessLogicError, match="Stock insuficiente"):
                self.integration.update_products_stock_with_compensation(items)
    
    def test_update_products_stock_with_compensation_multiple_compensation_failures(self):
        """Test de múltiples fallos en la compensación"""
        items = [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
        
        def update_side_effect(product_id, quantity):
            if product_id == 2:
                raise OrderBusinessLogicError("Stock insuficiente")
            return None
        
        self.mock_inventory_service.update_product_stock.side_effect = update_side_effect
        
        def compensation_side_effect(method, endpoint, **kwargs):
            raise Exception("Error de compensación")
        
        with patch.object(self.mock_inventory_service, '_make_request', side_effect=compensation_side_effect):
            with pytest.raises(OrderBusinessLogicError, match="Stock insuficiente"):
                self.integration.update_products_stock_with_compensation(items)
    
    def test_update_products_stock_with_compensation_empty_items(self):
        """Test de actualización con lista vacía de items"""
        items = []
        
        self.integration.update_products_stock_with_compensation(items)
        
        self.mock_inventory_service.update_product_stock.assert_not_called()
    
    def test_update_products_stock_with_compensation_single_item_success(self):
        """Test de actualización exitosa con un solo item"""
        items = [{'product_id': 1, 'quantity': 5}]
        
        self.mock_inventory_service.update_product_stock.return_value = None
        
        self.integration.update_products_stock_with_compensation(items)
        
        self.mock_inventory_service.update_product_stock.assert_called_once_with(1, 5)
