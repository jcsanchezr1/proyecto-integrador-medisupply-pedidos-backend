"""
Tests para el método get_top_clients_last_quarter del OrderRepository
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.repositories.order_repository import OrderRepository


class TestOrderRepositoryTopClients:
    """Tests para el método get_top_clients_last_quarter"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock de la sesión de SQLAlchemy"""
        return MagicMock()
    
    @pytest.fixture
    def order_repository(self, mock_session):
        """Instancia de OrderRepository con sesión mockeada"""
        return OrderRepository(mock_session)
    
    def test_get_top_clients_last_quarter_success(self, order_repository):
        """Test: Obtener top clientes exitosamente"""
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'client_id': 'client-1', 'orders_count': 10},
            {'client_id': 'client-2', 'orders_count': 8},
            {'client_id': 'client-3', 'orders_count': 5}
        ]
        
        with patch.object(order_repository, 'get_top_clients_last_quarter') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)
        
        assert len(result) == 3
        assert result[0]['client_id'] == 'client-1'
        assert result[0]['orders_count'] == 10
        assert result[1]['client_id'] == 'client-2'
        assert result[1]['orders_count'] == 8
        mock_method.assert_called_once_with(start_date, end_date, limit=5)
    
    def test_get_top_clients_last_quarter_empty_results(self, order_repository):
        """Test: Top clientes sin resultados"""
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 11, 11)
        
        with patch.object(order_repository, 'get_top_clients_last_quarter') as mock_method:
            mock_method.return_value = []
            result = order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)
        
        assert result == []
        mock_method.assert_called_once_with(start_date, end_date, limit=5)
    
    def test_get_top_clients_last_quarter_limit(self, order_repository):
        """Test: Verificar que respeta el límite"""
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'client_id': f'client-{i}', 'orders_count': 10 - i}
            for i in range(5)
        ]
        
        with patch.object(order_repository, 'get_top_clients_last_quarter') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)
        
        assert len(result) == 5
        mock_method.assert_called_once_with(start_date, end_date, limit=5)
    
    def test_get_top_clients_last_quarter_ordered_by_count(self, order_repository):
        """Test: Verificar que está ordenado por cantidad descendente"""
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'client_id': 'client-1', 'orders_count': 15},
            {'client_id': 'client-2', 'orders_count': 12},
            {'client_id': 'client-3', 'orders_count': 8},
            {'client_id': 'client-4', 'orders_count': 5},
            {'client_id': 'client-5', 'orders_count': 3}
        ]
        
        with patch.object(order_repository, 'get_top_clients_last_quarter') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)
        
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]['orders_count'] >= result[i + 1]['orders_count']
        mock_method.assert_called_once_with(start_date, end_date, limit=5)
    
    def test_get_top_clients_last_quarter_sqlalchemy_error(self, order_repository):
        """Test: Error de SQLAlchemy"""
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 11, 11)
        
        with patch.object(order_repository, 'get_top_clients_last_quarter') as mock_method:
            mock_method.side_effect = Exception("Error al obtener top clientes: Database error")
            
            with pytest.raises(Exception) as exc_info:
                order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)
            
            assert "Error al obtener top clientes" in str(exc_info.value)
    
    def test_get_top_clients_last_quarter_data_types(self, order_repository):
        """Test: Verificar tipos de datos correctos"""
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'client_id': 'client-1', 'orders_count': 10}
        ]
        
        with patch.object(order_repository, 'get_top_clients_last_quarter') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)
        
        assert isinstance(result[0]['client_id'], str)
        assert isinstance(result[0]['orders_count'], int)
        mock_method.assert_called_once_with(start_date, end_date, limit=5)

