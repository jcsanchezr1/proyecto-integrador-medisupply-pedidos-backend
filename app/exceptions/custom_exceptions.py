"""
Excepciones personalizadas del sistema de pedidos
"""


class OrdersException(Exception):
    """Excepción base para el sistema de pedidos"""
    pass


class OrderNotFoundError(OrdersException):
    """Excepción cuando no se encuentra un pedido"""
    pass


class OrderValidationError(OrdersException):
    """Excepción de validación de pedido"""
    pass


class OrderBusinessLogicError(OrdersException):
    """Excepción de lógica de negocio de pedidos"""
    pass
