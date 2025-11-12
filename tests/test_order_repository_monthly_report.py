"""
Tests para el método get_monthly_summary del OrderRepository
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime, date
from app.repositories.order_repository import OrderRepository
from sqlalchemy.exc import SQLAlchemyError


class TestOrderRepositoryMonthlySummary:
    """Tests para el método get_monthly_summary"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock de la sesión de SQLAlchemy"""
        return MagicMock()
    
    @pytest.fixture
    def order_repository(self, mock_session):
        """Instancia de OrderRepository con sesión mockeada"""
        return OrderRepository(mock_session)
    
    def test_get_monthly_summary_success(self, order_repository):
        """Test: Obtener resumen mensual exitosamente"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'year': 2025, 'month': 1, 'orders_count': 5, 'total_amount': 1500.50},
            {'year': 2025, 'month': 2, 'orders_count': 3, 'total_amount': 800.75}
        ]

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_monthly_summary(start_date, end_date)

        assert len(result) == 2
        assert result[0]['year'] == 2025
        assert result[0]['month'] == 1
        assert result[0]['orders_count'] == 5
        assert result[0]['total_amount'] == 1500.50
        
        assert result[1]['year'] == 2025
        assert result[1]['month'] == 2
        assert result[1]['orders_count'] == 3
        assert result[1]['total_amount'] == 800.75
        
        mock_method.assert_called_once_with(start_date, end_date)
    
    def test_get_monthly_summary_empty_results(self, order_repository):
        """Test: Resumen mensual sin resultados"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.return_value = []
            result = order_repository.get_monthly_summary(start_date, end_date)

        assert result == []
        mock_method.assert_called_once_with(start_date, end_date)
    
    def test_get_monthly_summary_with_null_values(self, order_repository):
        """Test: Resumen mensual con valores nulos convertidos a 0"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'year': 2025, 'month': 3, 'orders_count': 0, 'total_amount': 0.0}
        ]

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_monthly_summary(start_date, end_date)

        assert len(result) == 1
        assert result[0]['orders_count'] == 0
        assert result[0]['total_amount'] == 0.0
        mock_method.assert_called_once_with(start_date, end_date)
    
    def test_get_monthly_summary_sqlalchemy_error(self, order_repository):
        """Test: Error de SQLAlchemy al obtener resumen mensual"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.side_effect = Exception("Error al obtener resumen mensual de pedidos: Database error")
            
            with pytest.raises(Exception) as exc_info:
                order_repository.get_monthly_summary(start_date, end_date)
            
            assert "Error al obtener resumen mensual de pedidos" in str(exc_info.value)
    
    def test_get_monthly_summary_multiple_months(self, order_repository):
        """Test: Resumen mensual con múltiples meses"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)

        expected_data = []
        for month in range(1, 13):
            expected_data.append({
                'year': 2025,
                'month': month,
                'orders_count': month * 2,
                'total_amount': month * 1000.0
            })

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_monthly_summary(start_date, end_date)

        assert len(result) == 12
        for i, monthly_data in enumerate(result):
            assert monthly_data['month'] == i + 1
            assert monthly_data['orders_count'] == (i + 1) * 2
            assert monthly_data['total_amount'] == (i + 1) * 1000.0
        
        mock_method.assert_called_once_with(start_date, end_date)
    
    def test_get_monthly_summary_year_transition(self, order_repository):
        """Test: Resumen mensual con transición de año"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'year': 2024, 'month': 12, 'orders_count': 5, 'total_amount': 2500.0},
            {'year': 2025, 'month': 1, 'orders_count': 8, 'total_amount': 3200.0}
        ]

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_monthly_summary(start_date, end_date)

        assert len(result) == 2
        assert result[0]['year'] == 2024
        assert result[0]['month'] == 12
        assert result[1]['year'] == 2025
        assert result[1]['month'] == 1
        
        mock_method.assert_called_once_with(start_date, end_date)
    
    def test_get_monthly_summary_data_types(self, order_repository):
        """Test: Verificar tipos de datos correctos"""
        start_date = datetime(2024, 11, 11)
        end_date = datetime(2025, 11, 11)
        
        expected_data = [
            {'year': 2025, 'month': 5, 'orders_count': 10, 'total_amount': 5000.50}
        ]

        with patch.object(order_repository, 'get_monthly_summary') as mock_method:
            mock_method.return_value = expected_data
            result = order_repository.get_monthly_summary(start_date, end_date)

        assert isinstance(result[0]['year'], int)
        assert isinstance(result[0]['month'], int)
        assert isinstance(result[0]['orders_count'], int)
        assert isinstance(result[0]['total_amount'], float)
        
        mock_method.assert_called_once_with(start_date, end_date)
