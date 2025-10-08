"""
Repositorio para manejo de pedidos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.db_models import OrderDB, OrderItemDB


class OrderRepository:
    """Repositorio para manejo de pedidos"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_all(self) -> List[Order]:
        """Obtiene todos los pedidos"""
        try:
            db_orders = self.session.query(OrderDB).all()
            return [self._db_to_model(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos: {str(e)}")
    
    def get_orders_with_items_by_client(self, client_id: int) -> List[Order]:
        """Obtiene pedidos con items por cliente"""
        try:
            # Validar entrada
            if not client_id or client_id <= 0:
                raise ValueError("El ID del cliente debe ser mayor a 0")
            
            db_orders = self.session.query(OrderDB).filter(OrderDB.client_id == client_id).all()
            return [self._db_to_model_with_items(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos del cliente: {str(e)}")
    
    def get_orders_with_items_by_vendor(self, vendor_id: int) -> List[Order]:
        """Obtiene pedidos con items por vendedor"""
        try:
            # Validar entrada
            if not vendor_id or vendor_id <= 0:
                raise ValueError("El ID del vendedor debe ser mayor a 0")
            
            db_orders = self.session.query(OrderDB).filter(OrderDB.vendor_id == vendor_id).all()
            return [self._db_to_model_with_items(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos del vendedor: {str(e)}")
    
    def delete_all(self) -> bool:
        """Elimina todos los pedidos"""
        try:
            self.session.query(OrderItemDB).delete()
            self.session.query(OrderDB).delete()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar todos los pedidos: {str(e)}")
    
    def _db_to_model(self, db_order: OrderDB) -> Order:
        """Convierte modelo de BD a modelo de dominio"""
        order = Order(
            id=db_order.id,
            order_number=db_order.order_number,
            client_id=db_order.client_id,
            vendor_id=db_order.vendor_id,
            status=db_order.status.value if hasattr(db_order.status, 'value') else str(db_order.status),
            scheduled_delivery_date=db_order.scheduled_delivery_date,
            assigned_truck=db_order.assigned_truck,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at
        )
        return order
    
    def _db_to_model_with_items(self, db_order: OrderDB) -> Order:
        """Convierte modelo de BD a modelo de dominio con items"""
        order = self._db_to_model(db_order)
        
        # Agregar items del pedido
        for db_item in db_order.items:
            item = OrderItem(
                id=db_item.id,
                product_id=db_item.product_id,
                product_name=None,  # TODO: Consultar del servicio de inventarios
                product_image_url=None,  # TODO: Consultar del servicio de inventarios
                quantity=db_item.quantity,
                unit_price=None,  # TODO: Consultar del servicio de inventarios
                order_id=db_item.order_id
            )
            order.items.append(item)
        
        return order
