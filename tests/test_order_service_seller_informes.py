"""
Tests para los métodos de informes por vendedor del OrderService
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.exceptions.custom_exceptions import OrderBusinessLogicError
from app.models.db_models import OrderStatus


class TestOrderServiceSellerStatusSummary:
    """Tests para el método get_seller_status_summary con mocks completos"""
    
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
    
    def test_get_seller_status_summary_success_with_data(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'summary': {
                'total_orders': 10,
                'total_amount': 50000.0
            },
            'status_summary': [
                {'status': 'Recibido', 'count': 2, 'percentage': 20.0, 'total_amount': 10000.0},
                {'status': 'En Preparación', 'count': 3, 'percentage': 30.0, 'total_amount': 15000.0},
                {'status': 'En Tránsito', 'count': 2, 'percentage': 20.0, 'total_amount': 10000.0},
                {'status': 'Entregado', 'count': 3, 'percentage': 30.0, 'total_amount': 15000.0},
                {'status': 'Devuelto', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0}
            ]
        }
        
        with patch.object(order_service, 'get_seller_status_summary') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_status_summary('seller-123')
        
        assert result is not None
        assert result['seller_id'] == 'seller-123'
        assert result['summary']['total_orders'] == 10
        assert len(result['status_summary']) == 5
        mock_method.assert_called_once_with('seller-123')
    
    def test_get_seller_status_summary_success_without_data(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'summary': {
                'total_orders': 0,
                'total_amount': 0.0
            },
            'status_summary': [
                {'status': 'Recibido', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'En Preparación', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'En Tránsito', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'Entregado', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'Devuelto', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0}
            ]
        }
        
        with patch.object(order_service, 'get_seller_status_summary') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_status_summary('seller-123')
        
        assert result['summary']['total_orders'] == 0
        assert all(item['count'] == 0 for item in result['status_summary'])
        mock_method.assert_called_once_with('seller-123')
    
    def test_get_seller_status_summary_all_statuses_present(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'summary': {'total_orders': 0, 'total_amount': 0.0},
            'status_summary': [
                {'status': 'Recibido', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'En Preparación', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'En Tránsito', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'Entregado', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0},
                {'status': 'Devuelto', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0}
            ]
        }
        
        with patch.object(order_service, 'get_seller_status_summary') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_status_summary('seller-123')
        
        statuses = [item['status'] for item in result['status_summary']]
        assert 'Recibido' in statuses
        assert 'En Preparación' in statuses
        assert 'En Tránsito' in statuses
        assert 'Entregado' in statuses
        assert 'Devuelto' in statuses
        assert len(statuses) == 5
    
    def test_get_seller_status_summary_repository_exception(self, order_service):
        with patch.object(order_service, 'get_seller_status_summary') as mock_method:
            mock_method.side_effect = OrderBusinessLogicError("Error al generar informe de estados por vendedor")
            
            with pytest.raises(OrderBusinessLogicError) as exc_info:
                order_service.get_seller_status_summary('seller-123')
            
            assert "Error al generar informe de estados por vendedor" in str(exc_info.value)


class TestOrderServiceSellerStatusSummaryReal:
    """Tests que ejecutan el código real del método get_seller_status_summary"""
    
    @pytest.fixture
    def mock_order_repository(self):
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_auth_integration):
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                with patch('app.services.order_service.AuthService'):
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_real_get_seller_status_summary_with_data(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1', 'client-2']
        
        mock_status_data = [
            {'status': 'Recibido', 'count': 2, 'total_amount': 10000.0},
            {'status': 'En Preparación', 'count': 3, 'total_amount': 15000.0},
            {'status': 'Entregado', 'count': 1, 'total_amount': 5000.0}
        ]
        mock_order_repository.get_orders_status_summary_by_client_ids.return_value = mock_status_data
        
        result = order_service.get_seller_status_summary('seller-123')
        
        assert result is not None
        assert result['seller_id'] == 'seller-123'
        assert result['summary']['total_orders'] == 6
        assert result['summary']['total_amount'] == 30000.0
        assert len(result['status_summary']) == 5
        
        received_statuses = [item['status'] for item in result['status_summary']]
        assert 'Recibido' in received_statuses
        assert 'En Preparación' in received_statuses
        assert 'En Tránsito' in received_statuses
        assert 'Entregado' in received_statuses
        assert 'Devuelto' in received_statuses
        
        recibido_item = next(item for item in result['status_summary'] if item['status'] == 'Recibido')
        assert recibido_item['count'] == 2
        assert recibido_item['percentage'] == 33.33
        
        mock_auth_integration.get_assigned_clients.assert_called_once_with('seller-123')
        mock_order_repository.get_orders_status_summary_by_client_ids.assert_called_once_with(['client-1', 'client-2'])
    
    def test_real_get_seller_status_summary_without_clients(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = []
        
        result = order_service.get_seller_status_summary('seller-123')
        
        assert result['seller_id'] == 'seller-123'
        assert result['summary']['total_orders'] == 0
        assert result['summary']['total_amount'] == 0.0
        assert len(result['status_summary']) == 5
        
        for item in result['status_summary']:
            assert item['count'] == 0
            assert item['percentage'] == 0.0
            assert item['total_amount'] == 0.0
        
        mock_auth_integration.get_assigned_clients.assert_called_once_with('seller-123')
        mock_order_repository.get_orders_status_summary_by_client_ids.assert_not_called()
    
    def test_real_get_seller_status_summary_percentages_sum_to_100(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        
        mock_status_data = [
            {'status': 'Recibido', 'count': 5, 'total_amount': 25000.0},
            {'status': 'En Preparación', 'count': 3, 'total_amount': 15000.0},
            {'status': 'Entregado', 'count': 2, 'total_amount': 10000.0}
        ]
        mock_order_repository.get_orders_status_summary_by_client_ids.return_value = mock_status_data
        
        result = order_service.get_seller_status_summary('seller-123')
        
        total_percentage = sum(item['percentage'] for item in result['status_summary'])
        assert abs(total_percentage - 100.0) < 0.01
    
    def test_real_get_seller_status_summary_all_statuses_with_zero(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        
        mock_status_data = [
            {'status': 'Recibido', 'count': 10, 'total_amount': 50000.0}
        ]
        mock_order_repository.get_orders_status_summary_by_client_ids.return_value = mock_status_data
        
        result = order_service.get_seller_status_summary('seller-123')
        
        assert len(result['status_summary']) == 5
        
        recibido = next(item for item in result['status_summary'] if item['status'] == 'Recibido')
        assert recibido['count'] == 10
        assert recibido['percentage'] == 100.0
        
        otros = [item for item in result['status_summary'] if item['status'] != 'Recibido']
        for item in otros:
            assert item['count'] == 0
            assert item['percentage'] == 0.0
    
    def test_real_get_seller_status_summary_repository_exception(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_orders_status_summary_by_client_ids.side_effect = Exception("Database error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_seller_status_summary('seller-123')
        
        assert "Error al generar informe de estados por vendedor" in str(exc_info.value)
    
    def test_real_get_seller_status_summary_auth_integration_exception(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.side_effect = Exception("Auth service error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_seller_status_summary('seller-123')
        
        assert "Error al generar informe de estados por vendedor" in str(exc_info.value)


class TestOrderServiceSellerClientsSummary:
    """Tests para el método get_seller_clients_summary con mocks completos"""
    
    @pytest.fixture
    def mock_order_repository(self):
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_auth_integration):
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                with patch('app.services.order_service.AuthService'):
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_get_seller_clients_summary_success_with_data(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'summary': {
                'total_clients': 2,
                'total_orders': 10,
                'total_amount': 50000.0
            },
            'clients': [
                {'client_id': 'client-1', 'client_name': 'Cliente Uno', 'orders_count': 6, 'total_amount': 30000.0, 'average_order_amount': 5000.0},
                {'client_id': 'client-2', 'client_name': 'Cliente Dos', 'orders_count': 4, 'total_amount': 20000.0, 'average_order_amount': 5000.0}
            ],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 2,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False,
                'next_page': None,
                'prev_page': None
            }
        }
        
        with patch.object(order_service, 'get_seller_clients_summary') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_clients_summary('seller-123', 1, 10)
        
        assert result is not None
        assert result['seller_id'] == 'seller-123'
        assert len(result['clients']) == 2
        assert result['pagination']['total'] == 2
        mock_method.assert_called_once_with('seller-123', 1, 10)
    
    def test_get_seller_clients_summary_success_without_data(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'summary': {
                'total_clients': 0,
                'total_orders': 0,
                'total_amount': 0.0
            },
            'clients': [],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 0,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False,
                'next_page': None,
                'prev_page': None
            }
        }
        
        with patch.object(order_service, 'get_seller_clients_summary') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_clients_summary('seller-123')
        
        assert result['clients'] == []
        assert result['summary']['total_clients'] == 0
        mock_method.assert_called_once()
    
    def test_get_seller_clients_summary_pagination(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'summary': {'total_clients': 15, 'total_orders': 30, 'total_amount': 150000.0},
            'clients': [],
            'pagination': {
                'page': 2,
                'per_page': 10,
                'total': 15,
                'total_pages': 2,
                'has_next': True,
                'has_prev': True,
                'next_page': 3,
                'prev_page': 1
            }
        }
        
        with patch.object(order_service, 'get_seller_clients_summary') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_clients_summary('seller-123', 2, 10)
        
        assert result['pagination']['page'] == 2
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_prev'] is True
        mock_method.assert_called_once_with('seller-123', 2, 10)
    
    def test_get_seller_clients_summary_repository_exception(self, order_service):
        with patch.object(order_service, 'get_seller_clients_summary') as mock_method:
            mock_method.side_effect = OrderBusinessLogicError("Error al generar informe de clientes por vendedor")
            
            with pytest.raises(OrderBusinessLogicError) as exc_info:
                order_service.get_seller_clients_summary('seller-123')
            
            assert "Error al generar informe de clientes por vendedor" in str(exc_info.value)


class TestOrderServiceSellerClientsSummaryReal:
    """Tests que ejecutan el código real del método get_seller_clients_summary"""
    
    @pytest.fixture
    def mock_order_repository(self):
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_auth_integration):
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                with patch('app.services.order_service.AuthService'):
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_real_get_seller_clients_summary_with_data(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1', 'client-2']
        
        mock_clients_data = [
            {'client_id': 'client-1', 'orders_count': 6, 'total_amount': 30000.0, 'average_order_amount': 5000.0},
            {'client_id': 'client-2', 'orders_count': 4, 'total_amount': 20000.0, 'average_order_amount': 5000.0}
        ]
        mock_order_repository.get_clients_summary_by_client_ids.return_value = (mock_clients_data, 2)
        
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente Uno',
            'client-2': 'Cliente Dos'
        }
        
        result = order_service.get_seller_clients_summary('seller-123', 1, 10)
        
        assert result is not None
        assert result['seller_id'] == 'seller-123'
        assert result['summary']['total_clients'] == 2
        assert result['summary']['total_orders'] == 10
        assert result['summary']['total_amount'] == 50000.0
        assert len(result['clients']) == 2
        assert result['clients'][0]['client_name'] == 'Cliente Uno'
        assert result['pagination']['total'] == 2
        assert result['pagination']['has_next'] is False
        
        mock_auth_integration.get_assigned_clients.assert_called_once_with('seller-123')
        mock_order_repository.get_clients_summary_by_client_ids.assert_called_once_with(['client-1', 'client-2'], 10, 0)
        mock_auth_integration.get_client_names.assert_called_once_with(['client-1', 'client-2'])
    
    def test_real_get_seller_clients_summary_without_clients(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = []
        
        result = order_service.get_seller_clients_summary('seller-123')
        
        assert result['seller_id'] == 'seller-123'
        assert result['summary']['total_clients'] == 0
        assert result['summary']['total_orders'] == 0
        assert result['summary']['total_amount'] == 0.0
        assert result['clients'] == []
        assert result['pagination']['total'] == 0
        assert result['pagination']['has_next'] is False
        assert result['pagination']['has_prev'] is False
        
        mock_auth_integration.get_assigned_clients.assert_called_once_with('seller-123')
        mock_order_repository.get_clients_summary_by_client_ids.assert_not_called()
    
    def test_real_get_seller_clients_summary_pagination_next_page(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1', 'client-2', 'client-3']
        
        mock_clients_data = [
            {'client_id': 'client-2', 'orders_count': 4, 'total_amount': 20000.0, 'average_order_amount': 5000.0}
        ]
        mock_order_repository.get_clients_summary_by_client_ids.return_value = (mock_clients_data, 3)
        
        mock_auth_integration.get_client_names.return_value = {
            'client-2': 'Cliente Dos'
        }
        
        result = order_service.get_seller_clients_summary('seller-123', 2, 1)
        
        assert result['pagination']['page'] == 2
        assert result['pagination']['per_page'] == 1
        assert result['pagination']['total'] == 3
        assert result['pagination']['total_pages'] == 3
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_prev'] is True
        assert result['pagination']['next_page'] == 3
        assert result['pagination']['prev_page'] == 1
        
        mock_order_repository.get_clients_summary_by_client_ids.assert_called_once_with(['client-1', 'client-2', 'client-3'], 1, 1)
    
    def test_real_get_seller_clients_summary_client_name_not_available(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        
        mock_clients_data = [
            {'client_id': 'client-1', 'orders_count': 5, 'total_amount': 25000.0, 'average_order_amount': 5000.0}
        ]
        mock_order_repository.get_clients_summary_by_client_ids.return_value = (mock_clients_data, 1)
        
        mock_auth_integration.get_client_names.return_value = {}
        
        result = order_service.get_seller_clients_summary('seller-123')
        
        assert result['clients'][0]['client_name'] == 'Cliente no disponible'
    
    def test_real_get_seller_clients_summary_repository_exception(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_clients_summary_by_client_ids.side_effect = Exception("Database error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_seller_clients_summary('seller-123')
        
        assert "Error al generar informe de clientes por vendedor" in str(exc_info.value)
    
    def test_real_get_seller_clients_summary_auth_integration_exception(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.side_effect = Exception("Auth service error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_seller_clients_summary('seller-123')
        
        assert "Error al generar informe de clientes por vendedor" in str(exc_info.value)


class TestOrderServiceSellerMonthlyReport:
    """Tests para el método get_seller_monthly_report con mocks completos"""
    
    @pytest.fixture
    def mock_order_repository(self):
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_auth_integration):
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                with patch('app.services.order_service.AuthService'):
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_get_seller_monthly_report_success_with_data(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'period': {
                'start_date': '2024-12-01',
                'end_date': '2025-11-14',
                'months': 12
            },
            'summary': {
                'total_orders': 8,
                'total_amount': 4000000.0
            },
            'monthly_data': [
                {'year': 2025, 'month': 11, 'month_name': 'noviembre', 'month_short': 'nov', 'label': 'nov-2025', 'orders_count': 8, 'total_amount': 4000000.0}
            ] + [
                {'year': 2025, 'month': i, 'month_name': 'mes', 'month_short': 'mes', 'label': 'mes-2025', 'orders_count': 0, 'total_amount': 0.0}
                for i in range(10, 0, -1)
            ] + [
                {'year': 2024, 'month': 12, 'month_name': 'diciembre', 'month_short': 'dic', 'label': 'dic-2024', 'orders_count': 0, 'total_amount': 0.0}
            ]
        }
        
        with patch.object(order_service, 'get_seller_monthly_report') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_monthly_report('seller-123')
        
        assert result is not None
        assert result['seller_id'] == 'seller-123'
        assert result['period']['months'] == 12
        assert len(result['monthly_data']) == 12
        mock_method.assert_called_once_with('seller-123')
    
    def test_get_seller_monthly_report_success_without_data(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'period': {'start_date': '2024-12-01', 'end_date': '2025-11-14', 'months': 12},
            'summary': {'total_orders': 0, 'total_amount': 0.0},
            'monthly_data': [
                {'year': 2025, 'month': i, 'month_name': 'mes', 'month_short': 'mes', 'label': 'mes-2025', 'orders_count': 0, 'total_amount': 0.0}
                for i in range(12, 0, -1)
            ]
        }
        
        with patch.object(order_service, 'get_seller_monthly_report') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_monthly_report('seller-123')
        
        assert result['summary']['total_orders'] == 0
        assert all(m['orders_count'] == 0 for m in result['monthly_data'])
        mock_method.assert_called_once_with('seller-123')
    
    def test_get_seller_monthly_report_twelve_months(self, order_service):
        expected_result = {
            'seller_id': 'seller-123',
            'period': {'start_date': '2024-12-01', 'end_date': '2025-11-14', 'months': 12},
            'summary': {'total_orders': 0, 'total_amount': 0.0},
            'monthly_data': [
                {'year': 2025, 'month': i, 'month_name': 'mes', 'month_short': 'mes', 'label': 'mes-2025', 'orders_count': 0, 'total_amount': 0.0}
                for i in range(12, 0, -1)
            ]
        }
        
        with patch.object(order_service, 'get_seller_monthly_report') as mock_method:
            mock_method.return_value = expected_result
            result = order_service.get_seller_monthly_report('seller-123')
        
        assert len(result['monthly_data']) == 12
        mock_method.assert_called_once_with('seller-123')
    
    def test_get_seller_monthly_report_repository_exception(self, order_service):
        with patch.object(order_service, 'get_seller_monthly_report') as mock_method:
            mock_method.side_effect = OrderBusinessLogicError("Error al generar informe mensual por vendedor")
            
            with pytest.raises(OrderBusinessLogicError) as exc_info:
                order_service.get_seller_monthly_report('seller-123')
            
            assert "Error al generar informe mensual por vendedor" in str(exc_info.value)


class TestOrderServiceSellerMonthlyReportReal:
    """Tests que ejecutan el código real del método get_seller_monthly_report"""
    
    @pytest.fixture
    def mock_order_repository(self):
        return MagicMock(spec=OrderRepository)
    
    @pytest.fixture
    def mock_auth_integration(self):
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_auth_integration):
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                with patch('app.services.order_service.AuthService'):
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_real_get_seller_monthly_report_with_data(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        mock_monthly_data = [
            {'year': current_year, 'month': current_month, 'orders_count': 5, 'total_amount': 2000.0}
        ]
        mock_order_repository.get_orders_monthly_summary_by_client_ids.return_value = mock_monthly_data
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        assert result is not None
        assert result['seller_id'] == 'seller-123'
        assert result['period']['months'] == 12
        assert len(result['monthly_data']) == 12
        assert result['summary']['total_orders'] == 5
        assert result['summary']['total_amount'] == 2000.0
        
        first_month = result['monthly_data'][0]
        assert first_month['year'] == current_year
        assert first_month['month'] == current_month
        assert first_month['orders_count'] == 5
        
        mock_auth_integration.get_assigned_clients.assert_called_once_with('seller-123')
        assert mock_order_repository.get_orders_monthly_summary_by_client_ids.called
    
    def test_real_get_seller_monthly_report_without_clients(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = []
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        assert result['seller_id'] == 'seller-123'
        assert result['period']['months'] == 12
        assert len(result['monthly_data']) == 12
        assert result['summary']['total_orders'] == 0
        assert result['summary']['total_amount'] == 0.0
        
        for month_data in result['monthly_data']:
            assert month_data['orders_count'] == 0
            assert month_data['total_amount'] == 0.0
        
        mock_auth_integration.get_assigned_clients.assert_called_once_with('seller-123')
        mock_order_repository.get_orders_monthly_summary_by_client_ids.assert_not_called()
    
    def test_real_get_seller_monthly_report_all_months_present(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_orders_monthly_summary_by_client_ids.return_value = []
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        assert len(result['monthly_data']) == 12
        
        for month_data in result['monthly_data']:
            assert 'year' in month_data
            assert 'month' in month_data
            assert 'month_name' in month_data
            assert 'month_short' in month_data
            assert 'label' in month_data
            assert 'orders_count' in month_data
            assert 'total_amount' in month_data
    
    def test_real_get_seller_monthly_report_ordered_from_current(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_orders_monthly_summary_by_client_ids.return_value = []
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        monthly_data = result['monthly_data']
        current_date = datetime.now()
        
        first_month = monthly_data[0]
        assert first_month['year'] == current_date.year
        assert first_month['month'] == current_date.month
        
        for i in range(1, len(monthly_data)):
            current = monthly_data[i - 1]
            previous = monthly_data[i]
            current_value = current['year'] * 12 + current['month']
            previous_value = previous['year'] * 12 + previous['month']
            assert previous_value == current_value - 1
    
    def test_real_get_seller_monthly_report_spanish_month_names(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_orders_monthly_summary_by_client_ids.return_value = []
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        spanish_months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                         'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        spanish_months_short = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
                               'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
        
        for month_data in result['monthly_data']:
            assert month_data['month_name'] in spanish_months
            assert month_data['month_short'] in spanish_months_short
    
    def test_real_get_seller_monthly_report_label_format(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_orders_monthly_summary_by_client_ids.return_value = []
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        for month_data in result['monthly_data']:
            assert '-' in month_data['label']
            parts = month_data['label'].split('-')
            assert len(parts) == 2
            assert month_data['label'] == f"{month_data['month_short']}-{month_data['year']}"
    
    def test_real_get_seller_monthly_report_repository_exception(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        mock_order_repository.get_orders_monthly_summary_by_client_ids.side_effect = Exception("Database error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_seller_monthly_report('seller-123')
        
        assert "Error al generar informe mensual por vendedor" in str(exc_info.value)
    
    def test_real_get_seller_monthly_report_auth_integration_exception(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.side_effect = Exception("Auth service error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_seller_monthly_report('seller-123')
        
        assert "Error al generar informe mensual por vendedor" in str(exc_info.value)
    
    def test_real_get_seller_monthly_report_multiple_months_with_data(self, order_service, mock_order_repository, mock_auth_integration):
        mock_auth_integration.get_assigned_clients.return_value = ['client-1']
        
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        mock_monthly_data = [
            {'year': current_year, 'month': current_month, 'orders_count': 5, 'total_amount': 2000.0},
            {'year': current_year, 'month': current_month - 1 if current_month > 1 else 12, 'orders_count': 3, 'total_amount': 1500.0}
        ]
        mock_order_repository.get_orders_monthly_summary_by_client_ids.return_value = mock_monthly_data
        
        result = order_service.get_seller_monthly_report('seller-123')
        
        assert result['summary']['total_orders'] == 8
        assert result['summary']['total_amount'] == 3500.0
        
        months_with_data = [m for m in result['monthly_data'] if m['orders_count'] > 0]
        assert len(months_with_data) >= 1

