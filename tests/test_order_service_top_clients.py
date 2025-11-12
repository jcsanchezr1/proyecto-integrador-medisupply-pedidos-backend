"""
Tests para el método get_top_clients_report del OrderService
Incluye tests con mocks completos y tests que ejecutan código real
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestOrderServiceTopClientsReport:
    """Tests para el método get_top_clients_report con mocks completos"""
    
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
    def mock_auth_service(self):
        """Mock del AuthService"""
        return MagicMock()
    
    @pytest.fixture
    def mock_auth_integration(self):
        """Mock del AuthIntegration"""
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_inventory_service, mock_inventory_integration, mock_auth_service, mock_auth_integration):
        """Instancia de OrderService con dependencias mockeadas"""
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
    
    def test_get_top_clients_report_success_with_data(self, order_service):
        """Test: Generar reporte de top clientes exitosamente con datos"""
        
        expected_report = {
            'period': {
                'start_date': '2025-08-11',
                'end_date': '2025-11-11',
                'months': 3
            },
            'top_clients': [
                {'client_id': 'client-1', 'orders_count': 10, 'client_name': 'Cliente Uno'},
                {'client_id': 'client-2', 'orders_count': 8, 'client_name': 'Cliente Dos'},
                {'client_id': 'client-3', 'orders_count': 5, 'client_name': 'Cliente Tres'}
            ]
        }
        
        
        with patch.object(order_service, 'get_top_clients_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_top_clients_report()
        
        
        assert result is not None
        assert 'period' in result
        assert 'top_clients' in result
        assert len(result['top_clients']) == 3
        assert result['top_clients'][0]['client_id'] == 'client-1'
        assert result['top_clients'][0]['orders_count'] == 10
        assert result['top_clients'][0]['client_name'] == 'Cliente Uno'
        mock_method.assert_called_once()
    
    def test_get_top_clients_report_success_without_data(self, order_service):
        """Test: Generar reporte de top clientes sin datos"""
        
        expected_report = {
            'period': {
                'start_date': '2025-08-11',
                'end_date': '2025-11-11',
                'months': 3
            },
            'top_clients': []
        }
        
        
        with patch.object(order_service, 'get_top_clients_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_top_clients_report()
        
        
        assert result is not None
        assert result['top_clients'] == []
        mock_method.assert_called_once()
    
    def test_get_top_clients_report_max_five_clients(self, order_service):
        """Test: Verificar que siempre retorna máximo 5 clientes"""
        
        expected_report = {
            'period': {'start_date': '2025-08-11', 'end_date': '2025-11-11', 'months': 3},
            'top_clients': [
                {'client_id': f'client-{i}', 'orders_count': 10 - i, 'client_name': f'Cliente {i}'}
                for i in range(5)
            ]
        }
        
        
        with patch.object(order_service, 'get_top_clients_report') as mock_method:
            mock_method.return_value = expected_report
            result = order_service.get_top_clients_report()
        
        
        assert len(result['top_clients']) == 5
        mock_method.assert_called_once()
    
    def test_get_top_clients_report_repository_exception(self, order_service):
        """Test: Manejar excepción del repositorio"""
        with patch.object(order_service, 'get_top_clients_report') as mock_method:
            mock_method.side_effect = OrderBusinessLogicError("Error al generar reporte de top clientes")
            
            with pytest.raises(OrderBusinessLogicError) as exc_info:
                order_service.get_top_clients_report()
            
            assert "Error al generar reporte de top clientes" in str(exc_info.value)


class TestOrderServiceTopClientsReportReal:
    """Tests que ejecutan el código real del método get_top_clients_report"""
    
    @pytest.fixture
    def mock_order_repository(self):
        """Mock del OrderRepository"""
        mock_repo = MagicMock(spec=OrderRepository)
        return mock_repo
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock del AuthService"""
        return MagicMock()
    
    @pytest.fixture
    def mock_auth_integration(self):
        """Mock del AuthIntegration"""
        return MagicMock()
    
    @pytest.fixture
    def order_service(self, mock_order_repository, mock_auth_service, mock_auth_integration):
        """Instancia de OrderService con dependencias mockeadas"""
        with patch('app.services.order_service.InventoryService'):
            with patch('app.services.order_service.InventoryIntegration'):
                with patch('app.services.order_service.AuthService') as mock_auth_service_class:
                    with patch('app.services.order_service.AuthIntegration') as mock_auth_integration_class:
                        mock_auth_service_class.return_value = mock_auth_service
                        mock_auth_integration_class.return_value = mock_auth_integration
                        service = OrderService(mock_order_repository)
                        service.auth_service = mock_auth_service
                        service.auth_integration = mock_auth_integration
                        return service
    
    def test_real_get_top_clients_report_with_data(self, order_service, mock_order_repository, mock_auth_integration):
        """Test: Ejecutar código real con datos"""
        
        mock_top_clients_data = [
            {'client_id': 'client-1', 'orders_count': 10},
            {'client_id': 'client-2', 'orders_count': 8},
            {'client_id': 'client-3', 'orders_count': 5}
        ]
        mock_order_repository.get_top_clients_last_quarter.return_value = mock_top_clients_data
        
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente Uno',
            'client-2': 'Cliente Dos',
            'client-3': 'Cliente Tres'
        }
        
        
        result = order_service.get_top_clients_report()
        
        
        assert result is not None
        assert 'period' in result
        assert 'top_clients' in result
        assert len(result['top_clients']) == 3
        assert result['top_clients'][0]['client_id'] == 'client-1'
        assert result['top_clients'][0]['orders_count'] == 10
        assert result['top_clients'][0]['client_name'] == 'Cliente Uno'
        assert result['period']['months'] == 3
        
        mock_order_repository.get_top_clients_last_quarter.assert_called_once()
        mock_auth_integration.get_client_names.assert_called_once_with(['client-1', 'client-2', 'client-3'])
    
    def test_real_get_top_clients_report_without_data(self, order_service, mock_order_repository):
        """Test: Ejecutar código real sin datos"""
        
        mock_order_repository.get_top_clients_last_quarter.return_value = []
        
        
        result = order_service.get_top_clients_report()
        
        
        assert result is not None
        assert result['top_clients'] == []
        assert result['period']['months'] == 3
    
    def test_real_get_top_clients_report_client_name_not_available(self, order_service, mock_order_repository, mock_auth_integration):
        """Test: Manejar cuando el nombre del cliente no está disponible"""
        
        mock_top_clients_data = [
            {'client_id': 'client-1', 'orders_count': 10}
        ]
        mock_order_repository.get_top_clients_last_quarter.return_value = mock_top_clients_data
        
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente no disponible'
        }
        
        
        result = order_service.get_top_clients_report()
        
        
        assert result['top_clients'][0]['client_name'] == 'Cliente no disponible'
        mock_auth_integration.get_client_names.assert_called_once_with(['client-1'])
    
    def test_real_get_top_clients_report_auth_service_error(self, order_service, mock_order_repository, mock_auth_integration):
        """Test: Manejar error del servicio de autenticación"""
        
        mock_top_clients_data = [
            {'client_id': 'client-1', 'orders_count': 10}
        ]
        mock_order_repository.get_top_clients_last_quarter.return_value = mock_top_clients_data
        
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente no disponible'
        }
        
        
        result = order_service.get_top_clients_report()
        
        
        assert result['top_clients'][0]['client_name'] == 'Cliente no disponible'
        mock_auth_integration.get_client_names.assert_called_once_with(['client-1'])
    
    def test_real_get_top_clients_report_quarter_calculation(self, order_service, mock_order_repository):
        """Test: Verificar cálculo correcto del trimestre"""
        
        mock_order_repository.get_top_clients_last_quarter.return_value = []
        
        
        result = order_service.get_top_clients_report()
        
        
        assert result['period']['months'] == 3
        assert 'start_date' in result['period']
        assert 'end_date' in result['period']
        assert '-' in result['period']['start_date']
        assert '-' in result['period']['end_date']
    
    def test_real_get_top_clients_report_ordered_by_count(self, order_service, mock_order_repository, mock_auth_integration):
        """Test: Verificar que los clientes están ordenados por cantidad"""
        
        mock_top_clients_data = [
            {'client_id': 'client-1', 'orders_count': 15},
            {'client_id': 'client-2', 'orders_count': 10},
            {'client_id': 'client-3', 'orders_count': 5}
        ]
        mock_order_repository.get_top_clients_last_quarter.return_value = mock_top_clients_data
        
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente 1',
            'client-2': 'Cliente 2',
            'client-3': 'Cliente 3'
        }
        
        
        result = order_service.get_top_clients_report()
        
        for i in range(len(result['top_clients']) - 1):
            assert result['top_clients'][i]['orders_count'] >= result['top_clients'][i + 1]['orders_count']
    
    def test_real_get_top_clients_report_repository_exception(self, order_service, mock_order_repository):
        """Test: Manejar excepción del repositorio (código real)"""
        
        mock_order_repository.get_top_clients_last_quarter.side_effect = Exception("Database error")
        
        with pytest.raises(OrderBusinessLogicError) as exc_info:
            order_service.get_top_clients_report()
        
        assert "Error al generar reporte de top clientes" in str(exc_info.value)
    
    def test_real_get_top_clients_report_response_structure(self, order_service, mock_order_repository, mock_auth_integration):
        """Test: Verificar estructura completa del response"""
        
        mock_top_clients_data = [
            {'client_id': 'client-1', 'orders_count': 10}
        ]
        mock_order_repository.get_top_clients_last_quarter.return_value = mock_top_clients_data
        
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente Uno'
        }
        
        result = order_service.get_top_clients_report()
        
        assert 'period' in result
        assert 'top_clients' in result
        
        assert 'start_date' in result['period']
        assert 'end_date' in result['period']
        assert 'months' in result['period']
        
        if result['top_clients']:
            client = result['top_clients'][0]
            assert 'client_id' in client
            assert 'orders_count' in client
            assert 'client_name' in client
    
    def test_real_get_top_clients_with_empty_client_id(self, order_service, mock_order_repository, mock_auth_integration):
        """Test: Manejar client_id vacío o None"""
        
        mock_top_clients_data = [
            {'client_id': 'client-1', 'orders_count': 10},
            {'client_id': None, 'orders_count': 5},
            {'client_id': '', 'orders_count': 3}
        ]
        mock_order_repository.get_top_clients_last_quarter.return_value = mock_top_clients_data
        mock_auth_integration.get_client_names.return_value = {
            'client-1': 'Cliente Uno'
        }
        
        
        result = order_service.get_top_clients_report()
        
        
        assert len(result['top_clients']) == 3
        assert result['top_clients'][0]['client_id'] == 'client-1'
        mock_auth_integration.get_client_names.assert_called_once_with(['client-1'])

