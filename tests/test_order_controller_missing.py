"""
Tests para cubrir las líneas faltantes en order_controller.py
"""
import pytest
from unittest.mock import MagicMock, patch
from app import create_app
from app.controllers.order_controller import OrderController, OrderDeleteAllController
from app.exceptions.custom_exceptions import OrderBusinessLogicError


class TestOrderControllerMissing:
    """Tests para cubrir líneas faltantes en OrderController"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.client = self.app.test_client()
    


class TestOrderDeleteAllControllerMissing:
    """Tests para cubrir líneas faltantes en OrderDeleteAllController"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_delete_with_business_logic_error(self):
        """Test: DELETE con OrderBusinessLogicError (línea 98)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderDeleteAllController()
            
            with patch.object(controller.order_service, 'delete_all_orders', side_effect=OrderBusinessLogicError("Error de lógica de negocio")):
                response, status_code = controller.delete()
            
            assert status_code == 500
            assert response["success"] is False
            assert "Error de lógica de negocio" in response["error"]
            assert "Error de lógica de negocio" in response["details"]
    
    def test_delete_with_general_exception(self):
        """Test: DELETE con excepción general (línea 99)"""
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            controller = OrderDeleteAllController()
            
            with patch.object(controller.order_service, 'delete_all_orders', side_effect=Exception("Error general")):
                response, status_code = controller.delete()
            
            assert status_code == 500
            assert response["success"] is False
            assert "Error interno del servidor" in response["error"]
            assert "Error general" in response["details"]
