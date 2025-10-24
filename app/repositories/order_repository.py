"""
Repositorio para manejo de pedidos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.db_models import OrderDB, OrderItemDB
from .base_repository import BaseRepository


class OrderRepository(BaseRepository):
    """Repositorio para manejo de pedidos"""
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_all(self) -> List[Order]:
        """Obtiene todos los pedidos"""
        try:
            db_orders = self.session.query(OrderDB).all()
            return [self._db_to_model(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos: {str(e)}")
    
    def get_orders_with_items_by_client(self, client_id: str) -> List[Order]:
        """Obtiene pedidos con items por cliente"""
        try:
            # Validar entrada
            if not client_id:
                raise ValueError("El ID del cliente debe ser válido")
            
            db_orders = self.session.query(OrderDB).filter(OrderDB.client_id == client_id).all()
            return [self._db_to_model_with_items(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos del cliente: {str(e)}")
    
    def get_orders_with_items_by_vendor(self, vendor_id: str) -> List[Order]:
        """Obtiene pedidos con items por vendedor"""
        try:
            # Validar entrada
            if not vendor_id:
                raise ValueError("El ID del vendedor debe ser válido")
            
            db_orders = self.session.query(OrderDB).filter(OrderDB.vendor_id == vendor_id).all()
            return [self._db_to_model_with_items(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos del vendedor: {str(e)}")
    
    def create(self, order: Order) -> Order:
        """Crea un nuevo pedido con sus items"""
        try:
            # Crear el pedido principal
            db_order = OrderDB(
                order_number=order.order_number,
                client_id=order.client_id,
                vendor_id=order.vendor_id,
                status=order.status,
                total_amount=order.total_amount,
                scheduled_delivery_date=order.scheduled_delivery_date,
                assigned_truck=order.assigned_truck
            )
            self.session.add(db_order)
            self.session.flush()
                        
            for item in order.items:
                db_item = OrderItemDB(
                    order_id=db_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                self.session.add(db_item)
            
            self.session.commit()
            self.session.refresh(db_order)

            return self._db_to_model_with_items(db_order)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al crear pedido: {str(e)}")
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Obtiene un pedido por ID"""
        try:
            db_order = self.session.query(OrderDB).filter(OrderDB.id == order_id).first()
            if db_order:
                return self._db_to_model(db_order)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedido: {str(e)}")
    
    def update(self, order: Order) -> Order:
        """Actualiza un pedido"""
        try:
            db_order = self.session.query(OrderDB).filter(OrderDB.id == order.id).first()
            if not db_order:
                raise Exception("Pedido no encontrado")
            
            db_order.order_number = order.order_number
            db_order.client_id = order.client_id
            db_order.vendor_id = order.vendor_id
            db_order.status = order.status
            db_order.total_amount = order.total_amount
            db_order.scheduled_delivery_date = order.scheduled_delivery_date
            db_order.assigned_truck = order.assigned_truck
            
            self.session.commit()
            return self._db_to_model(db_order)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al actualizar pedido: {str(e)}")
    
    def delete(self, order_id: int) -> bool:
        """Elimina un pedido por ID"""
        try:
            db_order = self.session.query(OrderDB).filter(OrderDB.id == order_id).first()
            if not db_order:
                return False
            
            # Eliminar items primero
            self.session.query(OrderItemDB).filter(OrderItemDB.order_id == order_id).delete()
            # Eliminar pedido
            self.session.delete(db_order)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar pedido: {str(e)}")
    
    def delete_all(self) -> int:
        """Elimina todos los pedidos"""
        try:
            # Contar pedidos antes de eliminar
            count = self.session.query(OrderDB).count()
            self.session.query(OrderItemDB).delete()
            self.session.query(OrderDB).delete()
            self.session.commit()
            return count
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
            total_amount=db_order.total_amount,
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
                quantity=db_item.quantity,
                order_id=db_item.order_id
            )
            order.items.append(item)
        
        return order
