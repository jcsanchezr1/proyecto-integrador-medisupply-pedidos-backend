"""
Tests básicos para excepciones - Enfoque simple
"""
import pytest
from app.exceptions.custom_exceptions import (
    OrdersException, 
    OrderNotFoundError, 
    OrderValidationError, 
    OrderBusinessLogicError
)


class TestOrdersException:
    """Tests para OrdersException"""
    
    def test_orders_exception_creation(self):
        """Test: Crear OrdersException"""
        error = OrdersException("Mensaje de error")
        
        assert str(error) == "Mensaje de error"
        assert isinstance(error, Exception)
    
    def test_orders_exception_inheritance(self):
        """Test: OrdersException hereda de Exception"""
        error = OrdersException("Mensaje de error")
        
        assert isinstance(error, Exception)
    
    def test_orders_exception_with_empty_message(self):
        """Test: OrdersException con mensaje vacío"""
        error = OrdersException("")
        
        assert str(error) == ""
        assert isinstance(error, Exception)


class TestOrderNotFoundError:
    """Tests para OrderNotFoundError"""
    
    def test_order_not_found_error_creation(self):
        """Test: Crear OrderNotFoundError"""
        error = OrderNotFoundError("Pedido no encontrado")
        
        assert str(error) == "Pedido no encontrado"
        assert isinstance(error, OrdersException)
        assert isinstance(error, Exception)
    
    def test_order_not_found_error_inheritance(self):
        """Test: OrderNotFoundError hereda de OrdersException"""
        error = OrderNotFoundError("Pedido no encontrado")
        
        assert isinstance(error, OrdersException)
        assert isinstance(error, Exception)
    
    def test_order_not_found_error_with_different_message(self):
        """Test: OrderNotFoundError con mensaje diferente"""
        error = OrderNotFoundError("No se encontró el pedido con ID 123")
        
        assert str(error) == "No se encontró el pedido con ID 123"
        assert isinstance(error, OrdersException)


class TestOrderValidationError:
    """Tests para OrderValidationError"""
    
    def test_order_validation_error_creation(self):
        """Test: Crear OrderValidationError"""
        error = OrderValidationError("Error de validación")
        
        assert str(error) == "Error de validación"
        assert isinstance(error, OrdersException)
        assert isinstance(error, Exception)
    
    def test_order_validation_error_inheritance(self):
        """Test: OrderValidationError hereda de OrdersException"""
        error = OrderValidationError("Error de validación")
        
        assert isinstance(error, OrdersException)
        assert isinstance(error, Exception)
    
    def test_order_validation_error_with_specific_message(self):
        """Test: OrderValidationError con mensaje específico"""
        error = OrderValidationError("El client_id es requerido")
        
        assert str(error) == "El client_id es requerido"
        assert isinstance(error, OrdersException)


class TestOrderBusinessLogicError:
    """Tests para OrderBusinessLogicError"""
    
    def test_order_business_logic_error_creation(self):
        """Test: Crear OrderBusinessLogicError"""
        error = OrderBusinessLogicError("Error de lógica de negocio")
        
        assert str(error) == "Error de lógica de negocio"
        assert isinstance(error, OrdersException)
        assert isinstance(error, Exception)
    
    def test_order_business_logic_error_inheritance(self):
        """Test: OrderBusinessLogicError hereda de OrdersException"""
        error = OrderBusinessLogicError("Error de lógica de negocio")
        
        assert isinstance(error, OrdersException)
        assert isinstance(error, Exception)
    
    def test_order_business_logic_error_with_specific_message(self):
        """Test: OrderBusinessLogicError con mensaje específico"""
        error = OrderBusinessLogicError("No se puede eliminar un pedido en tránsito")
        
        assert str(error) == "No se puede eliminar un pedido en tránsito"
        assert isinstance(error, OrdersException)


class TestExceptionsModule:
    """Tests para el módulo de excepciones"""
    
    def test_exceptions_module_import(self):
        """Test: Importar módulo de excepciones"""
        from app.exceptions import custom_exceptions
        
        assert custom_exceptions is not None
        assert hasattr(custom_exceptions, 'OrdersException')
        assert hasattr(custom_exceptions, 'OrderNotFoundError')
        assert hasattr(custom_exceptions, 'OrderValidationError')
        assert hasattr(custom_exceptions, 'OrderBusinessLogicError')
    
    def test_exceptions_module_init(self):
        """Test: Importar __init__ de excepciones"""
        from app.exceptions import __init__
        
        assert __init__ is not None
    
    def test_all_exceptions_are_exception_subclass(self):
        """Test: Todas las excepciones heredan de Exception"""
        exceptions = [
            OrdersException,
            OrderNotFoundError,
            OrderValidationError,
            OrderBusinessLogicError
        ]
        
        for exception_class in exceptions:
            assert issubclass(exception_class, Exception)
    
    def test_specific_exceptions_inherit_from_orders_exception(self):
        """Test: Excepciones específicas heredan de OrdersException"""
        specific_exceptions = [
            OrderNotFoundError,
            OrderValidationError,
            OrderBusinessLogicError
        ]
        
        for exception_class in specific_exceptions:
            assert issubclass(exception_class, OrdersException)
