"""
Modelo de Pedido
"""
from datetime import datetime
from typing import Optional, List
from .base_model import BaseModel
from .db_models import OrderStatus


class Order(BaseModel):
    """Modelo de Pedido"""
    
    def __init__(
        self,
        order_number: str,
        client_id: int,
        vendor_id: int,
        status: str = "Recibido",
        scheduled_delivery_date: Optional[datetime] = None,
        assigned_truck: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.order_number = order_number
        self.client_id = client_id
        self.vendor_id = vendor_id
        self.status = status
        self.scheduled_delivery_date = scheduled_delivery_date
        self.assigned_truck = assigned_truck
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.items: List['OrderItem'] = []
    
    def validate(self) -> None:
        """Valida los datos del pedido"""
        self._validate_order_number()
        self._validate_client_and_vendor()
        self._validate_status()
    
    def _validate_order_number(self) -> None:
        """Valida el número de pedido"""
        if not self.order_number:
            raise ValueError("El número de pedido es obligatorio")
        
        # Validar formato PED-YYYYMMDD-XXXXX
        if not self.order_number.startswith("PED-"):
            raise ValueError("El número de pedido debe comenzar con 'PED-'")
        
        parts = self.order_number.split("-")
        if len(parts) != 3:
            raise ValueError("El número de pedido debe tener el formato PED-YYYYMMDD-XXXXX")
        
        # Validar fecha en el formato YYYYMMDD
        try:
            datetime.strptime(parts[1], "%Y%m%d")
        except ValueError:
            raise ValueError("La fecha en el número de pedido debe ser válida (YYYYMMDD)")
        
        # Validar secuencia de 5 dígitos
        if not parts[2].isdigit() or len(parts[2]) != 5:
            raise ValueError("La secuencia del pedido debe ser de 5 dígitos")
    
    def _validate_client_and_vendor(self) -> None:
        """Valida que tenga cliente y vendedor"""
        if not self.client_id or self.client_id <= 0:
            raise ValueError("El pedido debe tener un cliente válido")
        if not self.vendor_id or self.vendor_id <= 0:
            raise ValueError("El pedido debe tener un vendedor válido")
    
    def _validate_status(self) -> None:
        """Valida el estado del pedido"""
        valid_statuses = [status.value for status in OrderStatus]
        if self.status not in valid_statuses:
            raise ValueError(f"El estado debe ser uno de: {', '.join(valid_statuses)}")
    
    def to_dict(self) -> dict:
        """Convierte el pedido a diccionario"""
        return {
            'id': getattr(self, 'id', None),
            'order_number': self.order_number,
            'client_id': self.client_id,
            'vendor_id': self.vendor_id,
            'status': self.status,
            'scheduled_delivery_date': self.scheduled_delivery_date.isoformat() if self.scheduled_delivery_date else None,
            'assigned_truck': self.assigned_truck,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items] if self.items else []
        }
    
    @staticmethod
    def generate_order_number() -> str:
        """Genera un número de pedido único"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        # Generar secuencia de 5 dígitos (simplificado)
        sequence = now.strftime("%H%M%S")[:5]
        return f"PED-{date_str}-{sequence}"
