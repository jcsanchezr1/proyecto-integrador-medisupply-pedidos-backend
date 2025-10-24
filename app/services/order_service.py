"""
Servicio para lógica de negocio de pedidos
"""
import logging
from typing import List, Optional
import requests
import os
from ..models.order import Order
from ..models.order_item import OrderItem
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderNotFoundError, OrderValidationError, OrderBusinessLogicError
from .inventory_service import InventoryService
from ..integrations.inventory_integration import InventoryIntegration

logger = logging.getLogger(__name__)


class OrderService:
    """Servicio para lógica de negocio de pedidos"""
    
    def __init__(self, order_repository: OrderRepository):
        logger.info("=== INICIALIZANDO OrderService ===")
        self.order_repository = order_repository
        self.inventory_service = InventoryService()
        self.inventory_integration = InventoryIntegration(self.inventory_service)
    
    def get_orders_by_client(self, client_id: str) -> List[Order]:
        """Obtiene pedidos por ID de cliente"""
        # Validar entrada al inicio
        if not client_id:
            raise OrderValidationError("El ID del cliente es obligatorio")
        
        try:
            orders = self.order_repository.get_orders_with_items_by_client(client_id)
            for order in orders:
                self._enrich_order_items_with_product_info(order)
            return orders
        except ValueError as e:
            raise OrderValidationError(str(e))
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al obtener pedidos del cliente: {str(e)}")
    
    def get_orders_by_vendor(self, vendor_id: str) -> List[Order]:
        """Obtiene pedidos por ID de vendedor"""
        # Validar entrada al inicio
        if not vendor_id:
            raise OrderValidationError("El ID del vendedor es obligatorio")
        
        try:
            orders = self.order_repository.get_orders_with_items_by_vendor(vendor_id)
            for order in orders:
                self._enrich_order_items_with_product_info(order)
            return orders
        except ValueError as e:
            raise OrderValidationError(str(e))
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al obtener pedidos del vendedor: {str(e)}")
    
    def get_all_orders(self) -> List[Order]:
        """Obtiene todos los pedidos"""
        try:
            orders = self.order_repository.get_all()
            for order in orders:
                self._enrich_order_items_with_product_info(order)
            return orders
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al obtener todos los pedidos: {str(e)}")
    
    def delete_all_orders(self) -> bool:
        """Elimina todos los pedidos"""
        try:
            count = self.order_repository.delete_all()
            return count >= 0  # Retorna True si se eliminó al menos 0 pedidos (incluso si no había pedidos)
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al eliminar todos los pedidos: {str(e)}")
    
    def _enrich_order_items_with_product_info(self, order: Order) -> Order:
        """Enriquece los items del pedido con información del producto"""
        logger.info(f"Enriqueciendo {len(order.items)} items del pedido {order.order_number}")
        
        for item in order.items:
            try:
                product_info = self.inventory_service.get_product_by_id(item.product_id)

                item.product_name = product_info.get('name', '')
                item.product_image_url = product_info.get('image_url', '')
                item.unit_price = product_info.get('price', 0.0)
                item.product_sku = product_info.get('sku', '')
                
                logger.debug(f"Item {item.product_id} enriquecido: name='{item.product_name}', sku='{item.product_sku}'")
                    
            except Exception as e:
                logger.warning(f"Error al enriquecer item {item.product_id}: {str(e)}")
                item.product_name = ''
                item.product_image_url = ''
                item.unit_price = 0.0
                item.product_sku = ''
        
        return order
    
    def create_order(self, order_data: dict) -> Order:
        """
        Crea un nuevo pedido con verificación de stock
        
        Args:
            order_data: Datos del pedido con items
            
        Returns:
            Order: Pedido creado
            
        Raises:
            OrderValidationError: Si hay errores de validación
            OrderBusinessLogicError: Si no hay stock suficiente o error en creación
        """
        try:
            logger.info("Iniciando create_order")
            logger.info(f"Creando pedido con {len(order_data.get('items', []))} items")
            
            if not order_data.get('client_id') and not order_data.get('vendor_id'):
                raise OrderValidationError("Debe proporcionar al menos client_id o vendor_id")
            
            if not order_data.get('items') or not isinstance(order_data['items'], list):
                raise OrderValidationError("El pedido debe tener al menos un item")
            
            if len(order_data['items']) == 0:
                raise OrderValidationError("El pedido debe tener al menos un item")
            
            if not order_data.get('total_amount'):
                raise OrderValidationError("El total_amount es obligatorio")
            
            if not isinstance(order_data['total_amount'], (int, float)) or order_data['total_amount'] <= 0:
                raise OrderValidationError("El total_amount debe ser un número mayor a 0")
            
            if not order_data.get('scheduled_delivery_date'):
                raise OrderValidationError("El scheduled_delivery_date es obligatorio")
            
            try:
                from datetime import datetime
                scheduled_date = datetime.fromisoformat(order_data['scheduled_delivery_date'].replace('Z', '+00:00'))
                if scheduled_date.date() < datetime.now().date():
                    raise OrderValidationError("La fecha de entrega no puede ser en el pasado")
            except (ValueError, AttributeError):
                raise OrderValidationError("El scheduled_delivery_date debe tener formato ISO 8601 válido")
            
            order_items = []
            for item_data in order_data['items']:
                if not item_data.get('product_id'):
                    raise OrderValidationError("Cada item debe tener un product_id")
                
                if not item_data.get('quantity') or item_data['quantity'] <= 0:
                    raise OrderValidationError("Cada item debe tener una cantidad válida mayor a 0")
                
                order_items.append({
                    'product_id': item_data['product_id'],
                    'quantity': item_data['quantity']
                })
            
            logger.info(f"Validando disponibilidad de stock para {len(order_items)} productos")
            products_info = self.inventory_integration.verify_products_availability(order_items)
            
            order_number = Order.generate_order_number()
            scheduled_date = datetime.fromisoformat(order_data['scheduled_delivery_date'].replace('Z', '+00:00'))
            
            logger.info(f"Creando Order con total_amount: {order_data['total_amount']}")
            order = Order(
                order_number=order_number,
                client_id=order_data.get('client_id'),
                vendor_id=order_data.get('vendor_id'),
                status="En Preparación",
                total_amount=order_data['total_amount'],
                scheduled_delivery_date=scheduled_date
            )
            logger.info(f"Order creado con total_amount: {order.total_amount}")
            
            for i, item_data in enumerate(order_data['items']):
                order_item = OrderItem(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity']
                )
                
                order.items.append(order_item)
            
            order.validate()
            
            logger.info(f"Iniciando actualización de stock para {len(order_data['items'])} productos")
            self.inventory_integration.update_products_stock_with_compensation(order_items)
            
            logger.info(f"Todos los productos actualizados. Creando pedido {order.order_number}")
            created_order = self.order_repository.create(order)
            logger.info(f"Pedido {order.order_number} creado exitosamente con ID {created_order.id}")
            
            return created_order
            
        except OrderValidationError:
            raise
        except OrderBusinessLogicError:
            raise
        except Exception as e:
            raise OrderBusinessLogicError(f"Error inesperado al crear pedido: {str(e)}")
