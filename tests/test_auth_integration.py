"""
Tests para AuthIntegration
"""
import pytest
from unittest.mock import MagicMock
from app.integrations.auth_integration import AuthIntegration


class TestAuthIntegration:
    """Tests para AuthIntegration"""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock del AuthService"""
        return MagicMock()
    
    @pytest.fixture
    def auth_integration(self, mock_auth_service):
        """Instancia de AuthIntegration"""
        return AuthIntegration(mock_auth_service)
    
    def test_get_client_names_success(self, auth_integration, mock_auth_service):
        """Test: Obtener nombres de clientes exitosamente"""
        client_ids = ['client-1', 'client-2', 'client-3']
        expected_names = {
            'client-1': 'Cliente Uno',
            'client-2': 'Cliente Dos',
            'client-3': 'Cliente Tres'
        }
        mock_auth_service.get_users_by_ids.return_value = expected_names

        result = auth_integration.get_client_names(client_ids)

        assert result == expected_names
        mock_auth_service.get_users_by_ids.assert_called_once_with(client_ids)
    
    def test_get_client_names_empty_list(self, auth_integration, mock_auth_service):
        """Test: Obtener nombres con lista vacía"""

        client_ids = []
        mock_auth_service.get_users_by_ids.return_value = {}

        result = auth_integration.get_client_names(client_ids)

        assert result == {}
        mock_auth_service.get_users_by_ids.assert_called_once_with([])
    
    def test_get_client_names_with_unavailable(self, auth_integration, mock_auth_service):
        """Test: Obtener nombres cuando algunos no están disponibles"""

        client_ids = ['client-1', 'client-2']
        expected_names = {
            'client-1': 'Cliente Uno',
            'client-2': 'Cliente no disponible'
        }
        mock_auth_service.get_users_by_ids.return_value = expected_names

        result = auth_integration.get_client_names(client_ids)

        assert result == expected_names
        assert result['client-2'] == 'Cliente no disponible'

