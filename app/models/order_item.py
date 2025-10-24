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

        self.product_name: Optional[str] = None
        self.product_image_url: Optional[str] = None
        self.unit_price: Optional[float] = None
        self.product_sku: Optional[str] = None
    
    def validate(self) -> None:
        """Valida los datos del item del pedido"""
        self._validate_product_id()
        self._validate_quantity()
        # unit_price se valida solo si está presente
        if self.unit_price is not None:
            self._validate_unit_price()
    
    def _validate_product_id(self) -> None:
        """Valida el ID del producto"""
        if not self.product_id or self.product_id <= 0:
            raise ValueError("El ID del producto es obligatorio y debe ser mayor a 0")
    
    def _validate_quantity(self) -> None:
        """Valida la cantidad"""
        if not self.quantity or self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
    
    def _validate_unit_price(self) -> None:
        """Valida el precio unitario"""
        if self.unit_price < 0:
            raise ValueError("El precio unitario no puede ser negativo")
    
    def to_dict(self) -> dict:
        """Convierte el item del pedido a diccionario"""
        return {
            'id': getattr(self, 'id', None),
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_image_url': self.product_image_url,
            'product_sku': self.product_sku,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'order_id': self.order_id
        }
    
    def get_total_price(self) -> Optional[float]:
        """Calcula el precio total del item"""
        if self.unit_price is None:
            return None
        return self.quantity * self.unit_price
