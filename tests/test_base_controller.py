"""
Tests para base_controller.py
"""
import pytest
from app.controllers.base_controller import BaseController


class TestBaseController:
    """Tests para BaseController"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.controller = BaseController()
    
    def test_success_response_with_data(self):
        """Test: Respuesta exitosa con datos"""
        data = {"id": 1, "name": "Test"}
        message = "Operación completada"
        
        response, status_code = self.controller.success_response(data, message)
        
        assert status_code == 200
        assert response["success"] is True
        assert response["message"] == message
        assert response["data"] == data
    
    def test_success_response_without_data(self):
        """Test: Respuesta exitosa sin datos"""
        message = "Operación completada"
        
        response, status_code = self.controller.success_response(message=message)
        
        assert status_code == 200
        assert response["success"] is True
        assert response["message"] == message
        assert "data" not in response
    
    def test_success_response_default_message(self):
        """Test: Respuesta exitosa con mensaje por defecto"""
        data = {"id": 1, "name": "Test"}
        
        response, status_code = self.controller.success_response(data)
        
        assert status_code == 200
        assert response["success"] is True
        assert response["message"] == "Operación exitosa"
        assert response["data"] == data
    
    def test_success_response_no_data_no_message(self):
        """Test: Respuesta exitosa sin datos ni mensaje personalizado"""
        response, status_code = self.controller.success_response()
        
        assert status_code == 200
        assert response["success"] is True
        assert response["message"] == "Operación exitosa"
        assert "data" not in response
    
    def test_error_response_basic(self):
        """Test: Respuesta de error básica"""
        message = "Error de validación"
        
        response, status_code = self.controller.error_response(message)
        
        assert status_code == 400
        assert response["success"] is False
        assert response["error"] == message
        assert "details" not in response
    
    def test_error_response_with_details(self):
        """Test: Respuesta de error con detalles"""
        message = "Error de validación"
        details = "El campo 'email' es requerido"
        status_code = 422
        
        response, status_code = self.controller.error_response(message, details, status_code)
        
        assert status_code == 422
        assert response["success"] is False
        assert response["error"] == message
        assert response["details"] == details
    
    def test_error_response_custom_status_code(self):
        """Test: Respuesta de error con código de estado personalizado"""
        message = "Recurso no encontrado"
        status_code = 404
        
        response, status_code = self.controller.error_response(message, status_code=status_code)
        
        assert status_code == 404
        assert response["success"] is False
        assert response["error"] == message
        assert "details" not in response
    
    def test_created_response_with_data(self):
        """Test: Respuesta de creación exitosa con datos"""
        data = {"id": 1, "name": "Nuevo recurso"}
        message = "Recurso creado correctamente"
        
        response, status_code = self.controller.created_response(data, message)
        
        assert status_code == 201
        assert response["success"] is True
        assert response["message"] == message
        assert response["data"] == data
    
    def test_created_response_without_data(self):
        """Test: Respuesta de creación exitosa sin datos"""
        message = "Recurso creado correctamente"
        
        response, status_code = self.controller.created_response(None, message)
        
        assert status_code == 201
        assert response["success"] is True
        assert response["message"] == message
        assert "data" not in response
    
    def test_created_response_default_message(self):
        """Test: Respuesta de creación exitosa con mensaje por defecto"""
        data = {"id": 1, "name": "Nuevo recurso"}
        
        response, status_code = self.controller.created_response(data)
        
        assert status_code == 201
        assert response["success"] is True
        assert response["message"] == "Recurso creado exitosamente"
        assert response["data"] == data
    
    def test_created_response_no_data_default_message(self):
        """Test: Respuesta de creación exitosa sin datos y mensaje por defecto"""
        response, status_code = self.controller.created_response(None)
        
        assert status_code == 201
        assert response["success"] is True
        assert response["message"] == "Recurso creado exitosamente"
        assert "data" not in response
    
    def test_created_response_with_empty_data(self):
        """Test: Respuesta de creación exitosa con datos vacíos"""
        data = {}
        message = "Recurso creado sin datos"
        
        response, status_code = self.controller.created_response(data, message)
        
        assert status_code == 201
        assert response["success"] is True
        assert response["message"] == message
        assert response["data"] == data
    
    def test_created_response_with_falsy_data(self):
        """Test: Respuesta de creación exitosa con datos falsy (0, False, '')"""
        test_cases = [0, False, "", [], {}]
        
        for data in test_cases:
            response, status_code = self.controller.created_response(data)
            
            assert status_code == 201
            assert response["success"] is True
            assert response["message"] == "Recurso creado exitosamente"
            # Los datos falsy pero no None deben incluirse
            if data is not None:
                assert response["data"] == data
    
    def test_created_response_with_none_data(self):
        """Test: Respuesta de creación exitosa con datos None"""
        response, status_code = self.controller.created_response(None)
        
        assert status_code == 201
        assert response["success"] is True
        assert response["message"] == "Recurso creado exitosamente"
        assert "data" not in response
    
    def test_response_types(self):
        """Test: Verificar tipos de retorno de los métodos"""
        # Success response
        response, status_code = self.controller.success_response()
        assert isinstance(response, dict)
        assert isinstance(status_code, int)
        
        # Error response
        response, status_code = self.controller.error_response("Error")
        assert isinstance(response, dict)
        assert isinstance(status_code, int)
        
        # Created response
        response, status_code = self.controller.created_response({"id": 1})
        assert isinstance(response, dict)
        assert isinstance(status_code, int)
    
    def test_response_structure_consistency(self):
        """Test: Verificar consistencia en la estructura de respuestas"""
        # Success response
        response, _ = self.controller.success_response({"test": "data"})
        assert "success" in response
        assert "message" in response
        assert "data" in response
        
        # Error response
        response, _ = self.controller.error_response("Error", "Details")
        assert "success" in response
        assert "error" in response
        assert "details" in response
        
        # Created response
        response, _ = self.controller.created_response({"test": "data"})
        assert "success" in response
        assert "message" in response
        assert "data" in response
    
    def test_controller_inheritance(self):
        """Test: Verificar que BaseController hereda de Resource"""
        from flask_restful import Resource
        
        assert isinstance(self.controller, Resource)
        assert issubclass(BaseController, Resource)
    
    def test_controller_methods_exist(self):
        """Test: Verificar que todos los métodos existen"""
        assert hasattr(self.controller, 'success_response')
        assert hasattr(self.controller, 'error_response')
        assert hasattr(self.controller, 'created_response')
        
        # Verificar que son métodos callables
        assert callable(self.controller.success_response)
        assert callable(self.controller.error_response)
        assert callable(self.controller.created_response)
