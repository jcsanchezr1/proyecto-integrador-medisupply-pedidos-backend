"""
Modelo de Item del Pedido
"""
from typing import Optional
from .base_model import BaseModel


class OrderItem(BaseModel):
    """Modelo de Item del Pedido"""
    
    def __init__(
        self,
        product_id: int,
        quantity: int = 1,
        order_id: Optional[int] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.order_id = order_id
    
    def validate(self) -> None:
        """Valida los datos del item del pedido"""
        self._validate_product_id()
        self._validate_quantity()
    
    def _validate_product_id(self) -> None:
        """Valida el ID del producto"""
        if not self.product_id or self.product_id <= 0:
            raise ValueError("El ID del producto es obligatorio y debe ser mayor a 0")
    
    def _validate_quantity(self) -> None:
        """Valida la cantidad"""
        if not self.quantity or self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
    
    def to_dict(self) -> dict:
        """Convierte el item del pedido a diccionario"""
        return {
            'id': getattr(self, 'id', None),
            'product_id': self.product_id,
            'quantity': self.quantity,
            'order_id': self.order_id
        }
