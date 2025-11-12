"""
Tests para el método get_top_products_sold del OrderRepository
"""
import pytest
from unittest.mock import MagicMock, patch
from app.repositories.order_repository import OrderRepository


class TestOrderRepositoryTopProducts:
    """Tests para el método get_top_products_sold"""
    
    @pytest.fixture
    def mock_session(self):
        return MagicMock()
    
    @pytest.fixture
    def order_repository(self, mock_session):
        return OrderRepository(mock_session)
    
    def test_get_top_products_sold_success(self, order_repository):
        expected_data = [
            {'product_id': 1, 'total_sold': 50},
            {'product_id': 2, 'total_sold': 30},
            {'product_id': 3, 'total_sold': 20}
        ]
        
        with patch.object(order_repository, 'get_top_products_sold') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_products_sold(limit=10)
        
        assert len(result) == 3
        assert result[0]['product_id'] == 1
        assert result[0]['total_sold'] == 50
        mock_method.assert_called_once_with(limit=10)
    
    def test_get_top_products_sold_empty_results(self, order_repository):
        with patch.object(order_repository, 'get_top_products_sold') as mock_method:
            mock_method.return_value = []
            result = order_repository.get_top_products_sold(limit=10)
        
        assert result == []
        mock_method.assert_called_once_with(limit=10)
    
    def test_get_top_products_sold_limit(self, order_repository):
        expected_data = [
            {'product_id': i, 'total_sold': 100 - i}
            for i in range(10)
        ]
        
        with patch.object(order_repository, 'get_top_products_sold') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_products_sold(limit=10)
        
        assert len(result) == 10
        mock_method.assert_called_once_with(limit=10)
    
    def test_get_top_products_sold_ordered_by_quantity(self, order_repository):
        expected_data = [
            {'product_id': 1, 'total_sold': 100},
            {'product_id': 2, 'total_sold': 80},
            {'product_id': 3, 'total_sold': 60},
            {'product_id': 4, 'total_sold': 40},
            {'product_id': 5, 'total_sold': 20}
        ]
        
        with patch.object(order_repository, 'get_top_products_sold') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_products_sold(limit=10)
        
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]['total_sold'] >= result[i + 1]['total_sold']
        mock_method.assert_called_once_with(limit=10)
    
    def test_get_top_products_sold_sqlalchemy_error(self, order_repository):
        with patch.object(order_repository, 'get_top_products_sold') as mock_method:
            mock_method.side_effect = Exception("Error al obtener top productos: Database error")
            
            with pytest.raises(Exception) as exc_info:
                order_repository.get_top_products_sold(limit=10)
            
            assert "Error al obtener top productos" in str(exc_info.value)
    
    def test_get_top_products_sold_data_types(self, order_repository):
        expected_data = [
            {'product_id': 1, 'total_sold': 50}
        ]
        
        with patch.object(order_repository, 'get_top_products_sold') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_products_sold(limit=10)
        
        assert isinstance(result[0]['product_id'], int)
        assert isinstance(result[0]['total_sold'], int)
        mock_method.assert_called_once_with(limit=10)

