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
    
    def get_orders_by_truck_and_date(self, assigned_truck: str = None, scheduled_delivery_date = None) -> List[Order]:
        """Obtiene pedidos por camión y fecha de entrega (parámetros opcionales)"""
        try:
            from datetime import date as date_type
            from sqlalchemy import func
            
            query = self.session.query(OrderDB)
            
            if assigned_truck:
                query = query.filter(OrderDB.assigned_truck == assigned_truck)
            
            if scheduled_delivery_date:
                if isinstance(scheduled_delivery_date, str):
                    from datetime import datetime
                    scheduled_delivery_date = datetime.fromisoformat(scheduled_delivery_date.replace('Z', '+00:00')).date()
                query = query.filter(func.date(OrderDB.scheduled_delivery_date) == scheduled_delivery_date)
            
            db_orders = query.all()
            
            return [self._db_to_model_with_items(db_order) for db_order in db_orders]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pedidos por camión y fecha: {str(e)}")
    
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
    
    def get_monthly_summary(self, start_date, end_date) -> List[dict]:
        """
        Obtiene un resumen de pedidos agrupados por mes en un rango de fechas
        
        Args:
            start_date: Fecha inicial del rango
            end_date: Fecha final del rango
            
        Returns:
            Lista de diccionarios con año, mes, cantidad de pedidos y monto total
        """
        try:
            from sqlalchemy import func, extract
            
            # Consultar pedidos agrupados por año y mes
            results = self.session.query(
                extract('year', OrderDB.created_at).label('year'),
                extract('month', OrderDB.created_at).label('month'),
                func.count(OrderDB.id).label('orders_count'),
                func.sum(OrderDB.total_amount).label('total_amount')
            ).filter(
                OrderDB.created_at >= start_date,
                OrderDB.created_at <= end_date
            ).group_by(
                extract('year', OrderDB.created_at),
                extract('month', OrderDB.created_at)
            ).order_by(
                extract('year', OrderDB.created_at),
                extract('month', OrderDB.created_at)
            ).all()
            
            monthly_data = []
            for result in results:
                monthly_data.append({
                    'year': int(result.year),
                    'month': int(result.month),
                    'orders_count': result.orders_count or 0,
                    'total_amount': float(result.total_amount or 0)
                })
            
            return monthly_data
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener resumen mensual de pedidos: {str(e)}")
    
    def get_top_clients_last_quarter(self, start_date, end_date, limit: int = 5) -> List[dict]:
        """
        Obtiene los clientes con más pedidos en un rango de fechas
        
        Args:
            start_date: Fecha inicial del rango
            end_date: Fecha final del rango
            limit: Número máximo de clientes a retornar (default: 5)
            
        Returns:
            Lista de diccionarios con client_id y orders_count
        """
        try:
            from sqlalchemy import func

            results = self.session.query(
                OrderDB.client_id.label('client_id'),
                func.count(OrderDB.id).label('orders_count')
            ).filter(
                OrderDB.created_at >= start_date,
                OrderDB.created_at <= end_date,
                OrderDB.client_id.isnot(None)
            ).group_by(
                OrderDB.client_id
            ).order_by(
                func.count(OrderDB.id).desc()
            ).limit(limit).all()
            
            top_clients = []
            for result in results:
                top_clients.append({
                    'client_id': result.client_id,
                    'orders_count': result.orders_count or 0
                })
            
            return top_clients
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener top clientes: {str(e)}")
    
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
