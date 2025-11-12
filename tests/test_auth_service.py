"""
Tests para AuthService
"""
import pytest
from unittest.mock import MagicMock, patch
import requests
from app.services.auth_service import AuthService


class TestAuthService:
    """Tests para AuthService"""
    
    @pytest.fixture
    def auth_service(self):
        """Instancia de AuthService"""
        with patch.dict('os.environ', {'AUTH_SERVICE_URL': 'http://test-auth:8080'}):
            return AuthService()
    
    def test_get_user_by_id_success(self, auth_service):
        """Test: Obtener usuario exitosamente"""
        user_id = 'user-123'
        expected_user = {'id': 'user-123', 'name': 'Usuario Test'}
        
        with patch('app.services.auth_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': {'user': expected_user}
            }
            mock_get.return_value = mock_response

            result = auth_service.get_user_by_id(user_id)

        assert result == expected_user
        mock_get.assert_called_once_with(f"http://test-auth:8080/auth/user/{user_id}", timeout=5)
    
    def test_get_user_by_id_not_found(self, auth_service):
        """Test: Usuario no encontrado"""

        user_id = 'user-123'
        
        with patch('app.services.auth_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = auth_service.get_user_by_id(user_id)

        assert result is None
    
    def test_get_user_by_id_request_exception(self, auth_service):
        """Test: Excepción de requests"""

        user_id = 'user-123'
        
        with patch('app.services.auth_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Connection error")

            result = auth_service.get_user_by_id(user_id)

        assert result is None
    
    def test_get_user_by_id_generic_exception(self, auth_service):
        """Test: Excepción genérica"""
        user_id = 'user-123'
        
        with patch('app.services.auth_service.requests.get') as mock_get:
            mock_get.side_effect = ValueError("Unexpected error")
            

            result = auth_service.get_user_by_id(user_id)
        

        assert result is None
    
    def test_get_user_by_id_flat_data(self, auth_service):
        """Test: Usuario viene directo en data (no en data.user)"""

        user_id = 'user-123'
        expected_user = {'id': 'user-123', 'name': 'Usuario Test'}
        
        with patch('app.services.auth_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': expected_user
            }
            mock_get.return_value = mock_response
            

            result = auth_service.get_user_by_id(user_id)
        

        assert result == expected_user
    
    def test_get_user_by_id_not_dict(self, auth_service):
        """Test: Usuario no es un diccionario"""

        user_id = 'user-123'
        
        with patch('app.services.auth_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': {'user': 'not-a-dict'}
            }
            mock_get.return_value = mock_response
            

            result = auth_service.get_user_by_id(user_id)
        

        assert result is None
    
    def test_get_user_name_success(self, auth_service):
        """Test: Obtener nombre de usuario exitosamente"""

        user_id = 'user-123'
        
        with patch.object(auth_service, 'get_user_by_id') as mock_get_user:
            mock_get_user.return_value = {'id': 'user-123', 'name': 'Usuario Test'}
            

            result = auth_service.get_user_name(user_id)
        

        assert result == 'Usuario Test'
    
    def test_get_user_name_not_found(self, auth_service):
        """Test: Nombre cuando usuario no encontrado"""

        user_id = 'user-123'
        
        with patch.object(auth_service, 'get_user_by_id') as mock_get_user:
            mock_get_user.return_value = None
            

            result = auth_service.get_user_name(user_id)
        

        assert result == 'Usuario no disponible'
    
    def test_get_user_name_no_name_field(self, auth_service):
        """Test: Nombre cuando usuario no tiene campo name"""

        user_id = 'user-123'
        
        with patch.object(auth_service, 'get_user_by_id') as mock_get_user:
            mock_get_user.return_value = {'id': 'user-123'}
            

            result = auth_service.get_user_name(user_id)
        

        assert result == 'Usuario no disponible'
    
    def test_get_users_by_ids_success(self, auth_service):
        """Test: Obtener múltiples usuarios exitosamente"""

        user_ids = ['user-1', 'user-2', 'user-3']
        
        with patch.object(auth_service, 'get_user_name') as mock_get_name:
            mock_get_name.side_effect = ['Usuario 1', 'Usuario 2', 'Usuario 3']
            

            result = auth_service.get_users_by_ids(user_ids)
        

        assert len(result) == 3
        assert result['user-1'] == 'Usuario 1'
        assert result['user-2'] == 'Usuario 2'
        assert result['user-3'] == 'Usuario 3'
    
    def test_get_users_by_ids_with_empty(self, auth_service):
        """Test: Obtener usuarios filtrando IDs vacíos"""

        user_ids = ['user-1', None, '', 'user-2']
        
        with patch.object(auth_service, 'get_user_name') as mock_get_name:
            mock_get_name.side_effect = ['Usuario 1', 'Usuario 2']
            

            result = auth_service.get_users_by_ids(user_ids)
        

        assert len(result) == 2
        assert 'user-1' in result
        assert 'user-2' in result
        assert None not in result
        assert '' not in result

