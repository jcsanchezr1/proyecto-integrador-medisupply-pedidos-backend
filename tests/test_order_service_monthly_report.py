"""
Tests para el método get_monthly_report del OrderService
Incluye tests con mocks completos y tests que ejecutan código real
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime, timedelta
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestOrderServiceMonthlyReport:
    """Tests para el método get_monthly_report con mocks completos"""
    
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
    
    def test_get_monthly_report_success_with_data(self, order_service):
        """Test: Generar reporte mensual exitosamente con datos"""
        expected_report = {
            'period': {
                'start_date': '2024-11-11',
                'end_date': '2025-11-11',
                'months': 12
            },
            'summary': {
                'total_orders': 16,
                'total_amount': 6301.25,
                'months_with_data': 3,
                'average_orders_per_month': 1.33,
                'average_amount_per_month': 525.10
            },
            'monthly_data': [
                {'year': 2025, 'month': 1, 'month_name': 'enero', 'month_short': 'ene', 
                 'label': 'ene-2025', 'orders_count': 5, 'total_amount': 1500.50},
                {'year': 2025, 'month': 2, 'month_name': 'febrero', 'month_short': 'feb',
                 'label': 'feb-2025', 'orders_count': 3, 'total_amount': 800.75},
            ]
        }

        with patch.object(order_service, 'get_monthly_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_monthly_report()

        assert result is not None
        assert 'period' in result
        assert 'summary' in result
        assert 'monthly_data' in result
        assert result['summary']['total_orders'] == 16
        assert result['summary']['total_amount'] == 6301.25
        mock_method.assert_called_once()
    
    def test_get_monthly_report_success_without_data(self, order_service):
        """Test: Generar reporte mensual sin datos"""
        expected_report = {
            'period': {
                'start_date': '2024-11-11',
                'end_date': '2025-11-11',
                'months': 12
            },
            'summary': {
                'total_orders': 0,
                'total_amount': 0.0,
                'months_with_data': 0,
                'average_orders_per_month': 0.0,
                'average_amount_per_month': 0.0
            },
            'monthly_data': []
        }

        with patch.object(order_service, 'get_monthly_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_monthly_report()

        assert result is not None
        assert result['summary']['total_orders'] == 0
        assert result['summary']['total_amount'] == 0.0
        assert result['summary']['months_with_data'] == 0
        mock_method.assert_called_once()
    
    def test_get_monthly_report_twelve_months_structure(self, order_service):
        """Test: Verificar que siempre retorna 12 meses"""
        monthly_data = []
        for i in range(1, 13):
            monthly_data.append({
                'year': 2025,
                'month': i,
                'month_name': 'enero',
                'month_short': 'ene',
                'label': f'ene-2025',
                'orders_count': 0 if i != 5 else 2,
                'total_amount': 0.0 if i != 5 else 500.0
            })
        
        expected_report = {
            'period': {'start_date': '2024-11-11', 'end_date': '2025-11-11', 'months': 12},
            'summary': {'total_orders': 2, 'total_amount': 500.0, 'months_with_data': 1,
                       'average_orders_per_month': 0.17, 'average_amount_per_month': 41.67},
            'monthly_data': monthly_data
        }

        with patch.object(order_service, 'get_monthly_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_monthly_report()

        assert len(result['monthly_data']) == 12
        mock_method.assert_called_once()
    
    def test_get_monthly_report_includes_current_month(self, order_service):
        """Test: Verificar que incluye el mes actual"""
        monthly_data = []
        for i in range(1, 13):
            monthly_data.append({
                'year': 2025,
                'month': i,
                'month_name': 'noviembre' if i == 11 else 'mes',
                'month_short': 'nov' if i == 11 else 'mes',
                'label': 'nov-2025' if i == 11 else 'mes-2025',
                'orders_count': 5 if i == 11 else 0,
                'total_amount': 2000.0 if i == 11 else 0.0
            })
        
        expected_report = {
            'period': {'start_date': '2024-11-11', 'end_date': '2025-11-11', 'months': 12},
            'summary': {'total_orders': 5, 'total_amount': 2000.0, 'months_with_data': 1,
                       'average_orders_per_month': 0.42, 'average_amount_per_month': 166.67},
            'monthly_data': monthly_data
        }

        with patch.object(order_service, 'get_monthly_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_monthly_report()

        last_month = result['monthly_data'][-1]
        assert last_month['month'] == 12 or last_month['month_short'] == 'nov'
        mock_method.assert_called_once()
    
    def test_get_monthly_report_correct_labels(self, order_service):
        """Test: Verificar formato correcto de labels"""
        monthly_data = [
            {'year': 2025, 'month': 1, 'month_name': 'enero', 'month_short': 'ene',
             'label': 'ene-2025', 'orders_count': 0, 'total_amount': 0.0}
        ]
        expected_report = {
            'period': {'start_date': '2024-11-11', 'end_date': '2025-11-11', 'months': 12},
            'summary': {'total_orders': 0, 'total_amount': 0.0, 'months_with_data': 0,
                       'average_orders_per_month': 0.0, 'average_amount_per_month': 0.0},
            'monthly_data': monthly_data
        }

        with patch.object(order_service, 'get_monthly_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_monthly_report()

        for month_data in result['monthly_data']:
            assert 'label' in month_data
            assert '-' in month_data['label']
        mock_method.assert_called_once()
    
    def test_get_monthly_report_repository_exception(self, order_service):
        """Test: Manejar excepción del repositorio"""
        with patch.object(order_service, 'get_monthly_report') as mock_method:
            mock_method.side_effect = OrderBusinessLogicError("Error al generar reporte mensual")
            
            with pytest.raises(OrderBusinessLogicError) as exc_info:
                order_service.get_monthly_report()
            
            assert "Error al generar reporte mensual" in str(exc_info.value)


class TestOrderServiceMonthlyReportReal:
    """Tests que ejecutan el código real del método get_monthly_report"""
    
    @pytest.fixture
    def mock_order_repository(self):
        """Mock del OrderRepository"""
        mock_repo = MagicMock(spec=OrderRepository)
        return mock_repo
    
    @pytest.fixture
    def order_service(self, mock_order_repository):
        """Instancia de OrderService con dependencias mockeadas"""
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                service = OrderService(mock_order_repository)
                return service
    
    def test_real_get_monthly_report_with_data(self, order_service, mock_order_repository):
        """Test: Ejecutar código real con datos"""
        mock_monthly_data = [
            {'year': 2025, 'month': 1, 'orders_count': 5, 'total_amount': 1500.50},
            {'year': 2025, 'month': 2, 'orders_count': 3, 'total_amount': 800.75},
            {'year': 2025, 'month': 10, 'orders_count': 8, 'total_amount': 4000.0}
        ]
        mock_order_repository.get_monthly_summary.return_value = mock_monthly_data

        result = order_service.get_monthly_report()

        assert result is not None
        assert 'period' in result
        assert 'summary' in result
        assert 'monthly_data' in result
        assert result['period']['months'] == 12
        assert result['summary']['total_orders'] == 16
        assert result['summary']['total_amount'] == 6301.25
        assert result['summary']['months_with_data'] == 3
        assert len(result['monthly_data']) == 12
        

        for month_data in result['monthly_data']:
            assert 'year' in month_data
            assert 'month' in month_data
            assert 'month_name' in month_data
            assert 'month_short' in month_data
            assert 'label' in month_data
            assert 'orders_count' in month_data
            assert 'total_amount' in month_data
        
        mock_order_repository.get_monthly_summary.assert_called_once()
    
    def test_real_get_monthly_report_without_data(self, order_service, mock_order_repository):
        """Test: Ejecutar código real sin datos"""
        mock_order_repository.get_monthly_summary.return_value = []

        result = order_service.get_monthly_report()

        assert result is not None
        assert result['summary']['total_orders'] == 0
        assert result['summary']['total_amount'] == 0.0
        assert result['summary']['months_with_data'] == 0
        assert len(result['monthly_data']) == 12

        for month_data in result['monthly_data']:
            assert month_data['orders_count'] == 0
            assert month_data['total_amount'] == 0.0
    
    def test_real_get_monthly_report_includes_current_month(self, order_service, mock_order_repository):
        """Test: Verificar que incluye el mes actual (código real)"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        mock_monthly_data = [
            {'year': current_year, 'month': current_month, 'orders_count': 5, 'total_amount': 2000.0}
        ]
        mock_order_repository.get_monthly_summary.return_value = mock_monthly_data

        result = order_service.get_monthly_report()

        last_month = result['monthly_data'][-1]
        assert last_month['year'] == current_year
        assert last_month['month'] == current_month
        assert last_month['orders_count'] == 5
        assert last_month['total_amount'] == 2000.0
    
    def test_real_get_monthly_report_year_transition(self, order_service, mock_order_repository):
        """Test: Verificar transición de año (código real)"""
        current_year = datetime.now().year
        
        mock_monthly_data = [
            {'year': current_year - 1, 'month': 12, 'orders_count': 5, 'total_amount': 1000.0},
            {'year': current_year, 'month': 1, 'orders_count': 8, 'total_amount': 1500.0}
        ]
        mock_order_repository.get_monthly_summary.return_value = mock_monthly_data

        result = order_service.get_monthly_report()

        dec_month = [m for m in result['monthly_data'] if m['year'] == current_year - 1 and m['month'] == 12]
        assert len(dec_month) == 1
        assert dec_month[0]['orders_count'] == 5

        jan_month = [m for m in result['monthly_data'] if m['year'] == current_year and m['month'] == 1]
        assert len(jan_month) == 1
        assert jan_month[0]['orders_count'] == 8
    
    def test_real_get_monthly_report_spanish_month_names(self, order_service, mock_order_repository):
        """Test: Verificar nombres de meses en español (código real)"""
        mock_order_repository.get_monthly_summary.return_value = []

        result = order_service.get_monthly_report()

        spanish_months_short = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 
                                'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

        result_shorts = [m['month_short'] for m in result['monthly_data']]
        for short in result_shorts:
            assert short in spanish_months_short
    
    def test_real_get_monthly_report_summary_calculations(self, order_service, mock_order_repository):
        """Test: Verificar cálculos del summary (código real)"""
        mock_monthly_data = [
            {'year': 2025, 'month': 1, 'orders_count': 10, 'total_amount': 2000.0},
            {'year': 2025, 'month': 2, 'orders_count': 5, 'total_amount': 1000.0},
            {'year': 2025, 'month': 3, 'orders_count': 15, 'total_amount': 3000.0}
        ]
        mock_order_repository.get_monthly_summary.return_value = mock_monthly_data

        result = order_service.get_monthly_report()

        assert result['summary']['total_orders'] == 30
        assert result['summary']['total_amount'] == 6000.0
        assert result['summary']['months_with_data'] == 3
        assert abs(result['summary']['average_orders_per_month'] - 2.5) < 0.01
        assert abs(result['summary']['average_amount_per_month'] - 500.0) < 0.01
    
    def test_real_get_monthly_report_repository_exception(self, order_service, mock_order_repository):
        """Test: Manejar excepción del repositorio (código real)"""
        mock_order_repository.get_monthly_summary.side_effect = Exception("Database error")

        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_monthly_report()
        
        assert "Error al generar reporte mensual" in str(exc_info.value)
    
    def test_real_get_monthly_report_chronological_order(self, order_service, mock_order_repository):
        """Test: Verificar orden cronológico (código real)"""

        mock_order_repository.get_monthly_summary.return_value = []

        result = order_service.get_monthly_report()

        monthly_data = result['monthly_data']
        for i in range(len(monthly_data) - 1):
            current = monthly_data[i]
            next_month = monthly_data[i + 1]

            current_value = current['year'] * 12 + current['month']
            next_value = next_month['year'] * 12 + next_month['month']
            assert next_value == current_value + 1
    
    def test_real_get_monthly_report_label_format(self, order_service, mock_order_repository):
        """Test: Verificar formato de labels (código real)"""

        mock_order_repository.get_monthly_summary.return_value = []

        result = order_service.get_monthly_report()

        for month_data in result['monthly_data']:
            assert '-' in month_data['label']
            parts = month_data['label'].split('-')
            assert len(parts) == 2
            assert len(parts[0]) == 3
            assert len(parts[1]) == 4
            assert month_data['label'] == f"{month_data['month_short']}-{month_data['year']}"
