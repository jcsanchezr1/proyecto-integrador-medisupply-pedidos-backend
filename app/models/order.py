"""
Modelo de Pedido
"""
from datetime import datetime
from typing import Optional, List
import uuid
from .base_model import BaseModel
from .db_models import OrderStatus, TruckType
import random


class Order(BaseModel):
    """Modelo de Pedido"""
    
    def __init__(
        self,
        order_number: str,
        client_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        status: str = "Recibido",
        total_amount: float = 0.0,
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
        self.total_amount = total_amount
        self.scheduled_delivery_date = scheduled_delivery_date
        self.assigned_truck = assigned_truck or self._assign_random_truck()
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
        """Valida que tenga al menos cliente o vendedor"""
        if not self.client_id and not self.vendor_id:
            raise ValueError("El pedido debe tener al menos un cliente o vendedor válido")

        if self.client_id:
            try:
                uuid.UUID(self.client_id)
            except ValueError:
                raise ValueError("El client_id debe ser un UUID válido")
        
        if self.vendor_id:
            try:
                uuid.UUID(self.vendor_id)
            except ValueError:
                raise ValueError("El vendor_id debe ser un UUID válido")
    
    def _validate_status(self) -> None:
        """Valida el estado del pedido"""
        valid_statuses = [status.value for status in OrderStatus]
        if self.status not in valid_statuses:
            raise ValueError(f"El estado debe ser uno de: {', '.join(valid_statuses)}")
    
    def _assign_random_truck(self) -> str:
        """Asigna un camión aleatorio al pedido"""
        trucks = [truck.value for truck in TruckType]
        return random.choice(trucks)
    
    def calculate_total_amount(self) -> float:
        """Calcula el monto total del pedido basado en los items"""
        total = 0.0
        for item in self.items:
            total += item.quantity * item.unit_price
        self.total_amount = total
        return total
    
    def to_dict(self) -> dict:
        """Convierte el pedido a diccionario"""
        return {
            'id': getattr(self, 'id', None),
            'order_number': self.order_number,
            'client_id': self.client_id,
            'vendor_id': self.vendor_id,
            'status': self.status,
            'total_amount': self.total_amount,
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
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        microseconds = now.microsecond // 1000
        sequence = str(seconds_since_midnight * 1000 + microseconds)[-5:]
        return f"PED-{date_str}-{sequence}"
