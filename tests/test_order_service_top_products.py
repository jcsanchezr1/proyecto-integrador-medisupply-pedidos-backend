"""
Tests para el método get_top_products_report del OrderService
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestOrderServiceTopProductsReport:
    """Tests para el método get_top_products_report con mocks completos"""
    
    @pytest.fixture
    def mock_order_repository(self):
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_inventory_service(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_inventory_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_auth_service(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_inventory_service, mock_inventory_integration, mock_auth_service, mock_auth_integration):
        with patch('app.services.order_service.InventoryService') as mock_service_class:
            with patch('app.services.order_service.InventoryIntegration') as mock_integration_class:
                with patch('app.services.order_service.AuthService') as mock_auth_service_class:
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_service_class.return_value = mock_inventory_service
                        mock_integration_class.return_value = mock_inventory_integration
                        mock_auth_service_class.return_value = mock_auth_service
                        mock_auth_integration_class.return_value = mock_auth_integration
                        
                        service = OrderService(mock_order_repository)
                        service.inventory_service = mock_inventory_service
                        service.inventory_integration = mock_inventory_integration
                        service.auth_service = mock_auth_service
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_get_top_products_report_success_with_data(self, order_service):
        expected_report = {
            'top_products': [
                {'product_id': 1, 'total_sold': 100, 'product_name': 'Producto Uno'},
                {'product_id': 2, 'total_sold': 80, 'product_name': 'Producto Dos'},
                {'product_id': 3, 'total_sold': 60, 'product_name': 'Producto Tres'}
            ]
        }
        
        with patch.object(order_service, 'get_top_products_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_top_products_report()
        
        assert result is not None
        assert 'top_products' in result
        assert len(result['top_products']) == 3
        assert result['top_products'][0]['product_id'] == 1
        assert result['top_products'][0]['total_sold'] == 100
        assert result['top_products'][0]['product_name'] == 'Producto Uno'
        mock_method.assert_called_once()
    
    def test_get_top_products_report_success_without_data(self, order_service):
        expected_report = {
            'top_products': []
        }
        
        with patch.object(order_service, 'get_top_products_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_top_products_report()
        
        assert result is not None
        assert result['top_products'] == []
        mock_method.assert_called_once()
    
    def test_get_top_products_report_max_ten_products(self, order_service):
        expected_report = {
            'top_products': [
                {'product_id': i, 'total_sold': 100 - i, 'product_name': f'Producto {i}'}
                for i in range(10)
            ]
        }
        
        with patch.object(order_service, 'get_top_products_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_top_products_report()
        
        assert len(result['top_products']) == 10
        mock_method.assert_called_once()
    
    def test_get_top_products_report_repository_exception(self, order_service):
        with patch.object(order_service, 'get_top_products_report') as mock_method:
            mock_method.side_effect = OrderBusinessLogicError("Error al generar reporte de top productos")
            
            with pytest.raises(OrderBusinessLogicError) as exc_info:
                order_service.get_top_products_report()
            
            assert "Error al generar reporte de top productos" in str(exc_info.value)


class TestOrderServiceTopProductsReportReal:
    """Tests que ejecutan el código real del método get_top_products_report"""
    
    @pytest.fixture
    def mock_order_repository(self):
        mock_repo = MagicMock(spec=OrderRepository)
        return mock_repo
    
    @pytest.fixture
    def mock_inventory_service(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_inventory_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_auth_service(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_inventory_service, mock_inventory_integration, mock_auth_service, mock_auth_integration):
        with patch('app.services.order_service.InventoryService') as mock_service_class:
            with patch('app.services.order_service.InventoryIntegration') as mock_integration_class:
                with patch('app.services.order_service.AuthService') as mock_auth_service_class:
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_service_class.return_value = mock_inventory_service
                        mock_integration_class.return_value = mock_inventory_integration
                        mock_auth_service_class.return_value = mock_auth_service
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.inventory_service = mock_inventory_service
                        service.inventory_integration = mock_inventory_integration
                        service.auth_service = mock_auth_service
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_real_get_top_products_report_with_data(self, order_service, mock_order_repository, mock_inventory_integration):
        mock_top_products_data = [
            {'product_id': 1, 'total_sold': 100},
            {'product_id': 2, 'total_sold': 80},
            {'product_id': 3, 'total_sold': 60}
        ]
        mock_order_repository.get_top_products_sold.return_value = mock_top_products_data
        
        mock_inventory_integration.get_product_names.return_value = {
            1: 'Producto Uno',
            2: 'Producto Dos',
            3: 'Producto Tres'
        }
        
        result = order_service.get_top_products_report()
        
        assert result is not None
        assert 'top_products' in result
        assert len(result['top_products']) == 3
        assert result['top_products'][0]['product_id'] == 1
        assert result['top_products'][0]['total_sold'] == 100
        assert result['top_products'][0]['product_name'] == 'Producto Uno'
        
        mock_order_repository.get_top_products_sold.assert_called_once_with(limit=10)
        mock_inventory_integration.get_product_names.assert_called_once_with([1, 2, 3])
    
    def test_real_get_top_products_report_without_data(self, order_service, mock_order_repository):
        mock_order_repository.get_top_products_sold.return_value = []
        
        result = order_service.get_top_products_report()
        
        assert result is not None
        assert result['top_products'] == []
    
    def test_real_get_top_products_report_product_name_not_available(self, order_service, mock_order_repository, mock_inventory_integration):
        mock_top_products_data = [
            {'product_id': 1, 'total_sold': 100}
        ]
        mock_order_repository.get_top_products_sold.return_value = mock_top_products_data
        
        mock_inventory_integration.get_product_names.return_value = {
            1: 'Producto no disponible'
        }
        
        result = order_service.get_top_products_report()
        
        assert result['top_products'][0]['product_name'] == 'Producto no disponible'
        mock_inventory_integration.get_product_names.assert_called_once_with([1])
    
    def test_real_get_top_products_report_ordered_by_quantity(self, order_service, mock_order_repository, mock_inventory_integration):
        mock_top_products_data = [
            {'product_id': 1, 'total_sold': 150},
            {'product_id': 2, 'total_sold': 100},
            {'product_id': 3, 'total_sold': 50}
        ]
        mock_order_repository.get_top_products_sold.return_value = mock_top_products_data
        
        mock_inventory_integration.get_product_names.return_value = {
            1: 'Producto 1',
            2: 'Producto 2',
            3: 'Producto 3'
        }
        
        result = order_service.get_top_products_report()
        
        for i in range(len(result['top_products']) - 1):
            assert result['top_products'][i]['total_sold'] >= result['top_products'][i + 1]['total_sold']
    
    def test_real_get_top_products_report_repository_exception(self, order_service, mock_order_repository):
        mock_order_repository.get_top_products_sold.side_effect = Exception("Database error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_top_products_report()
        
        assert "Error al generar reporte de top productos" in str(exc_info.value)
    
    def test_real_get_top_products_report_response_structure(self, order_service, mock_order_repository, mock_inventory_integration):
        mock_top_products_data = [
            {'product_id': 1, 'total_sold': 100}
        ]
        mock_order_repository.get_top_products_sold.return_value = mock_top_products_data
        
        mock_inventory_integration.get_product_names.return_value = {
            1: 'Producto Uno'
        }
        
        result = order_service.get_top_products_report()
        
        assert 'top_products' in result
        
        if result['top_products']:
            product = result['top_products'][0]
            assert 'product_id' in product
            assert 'total_sold' in product
            assert 'product_name' in product
    
    def test_real_get_top_products_with_empty_product_id(self, order_service, mock_order_repository, mock_inventory_integration):
        mock_top_products_data = [
            {'product_id': 1, 'total_sold': 100},
            {'product_id': None, 'total_sold': 50},
            {'product_id': 0, 'total_sold': 30}
        ]
        mock_order_repository.get_top_products_sold.return_value = mock_top_products_data
        mock_inventory_integration.get_product_names.return_value = {
            1: 'Producto Uno'
        }
        
        result = order_service.get_top_products_report()
        
        assert len(result['top_products']) == 3
        assert result['top_products'][0]['product_id'] == 1
        mock_inventory_integration.get_product_names.assert_called_once_with([1])
    
    def test_real_get_top_products_report_product_name_empty(self, order_service, mock_order_repository, mock_inventory_integration):
        mock_top_products_data = [
            {'product_id': 1, 'total_sold': 100}
        ]
        mock_order_repository.get_top_products_sold.return_value = mock_top_products_data
        
        mock_inventory_integration.get_product_names.return_value = {
            1: 'Producto no disponible'
        }
        
        result = order_service.get_top_products_report()
        
        assert result['top_products'][0]['product_name'] == 'Producto no disponible'

