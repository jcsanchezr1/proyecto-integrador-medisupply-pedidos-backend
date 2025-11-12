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
from .auth_service import AuthService
from ..integrations.auth_integration import AuthIntegration

logger = logging.getLogger(__name__)


class OrderService:
    """Servicio para lógica de negocio de pedidos"""
    
    def __init__(self, order_repository: OrderRepository):
        logger.info("=== INICIALIZANDO OrderService ===")
        self.order_repository = order_repository
        self.inventory_service = InventoryService()
        self.inventory_integration = InventoryIntegration(self.inventory_service)
        self.auth_service = AuthService()
        self.auth_integration = AuthIntegration(self.auth_service)
    
    def get_orders_by_client(self, client_id: str) -> List[Order]:
        """Obtiene pedidos por ID de cliente"""
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
    
    def get_orders_by_truck_and_date(self, assigned_truck: str = None, scheduled_delivery_date = None) -> List[Order]:
        """Obtiene pedidos por camión y fecha de entrega (parámetros opcionales)"""
        try:
            orders = self.order_repository.get_orders_by_truck_and_date(assigned_truck, scheduled_delivery_date)
            for order in orders:
                self._enrich_order_items_with_product_info(order)
            return orders
        except ValueError as e:
            raise OrderValidationError(str(e))
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al obtener pedidos por camión y fecha: {str(e)}")
    
    def delete_all_orders(self) -> bool:
        """Elimina todos los pedidos"""
        try:
            count = self.order_repository.delete_all()
            return count >= 0
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
    
    def get_monthly_report(self) -> dict:
        """
        Obtiene el reporte mensual consolidado de pedidos del último año
        
        Returns:
            dict: Estructura optimizada para gráficos en Angular con:
                - period: rango de fechas del reporte
                - summary: resumen total (pedidos, monto, meses con datos)
                - monthly_data: array con datos de cada mes
        """
        try:
            from datetime import datetime, timedelta
            from dateutil.relativedelta import relativedelta
            import calendar

            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            logger.info(f"Generando reporte mensual desde {start_date.date()} hasta {end_date.date()}")

            monthly_raw_data = self.order_repository.get_monthly_summary(start_date, end_date)

            data_by_month = {}
            for item in monthly_raw_data:
                key = f"{item['year']}-{item['month']}"
                data_by_month[key] = item

            monthly_data = []
            current_date = end_date.replace(day=1)
            current_date = current_date - relativedelta(months=11)

            month_names = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            month_names_short = {
                1: "ene", 2: "feb", 3: "mar", 4: "abr",
                5: "may", 6: "jun", 7: "jul", 8: "ago",
                9: "sep", 10: "oct", 11: "nov", 12: "dic"
            }
            
            for i in range(12):
                year = current_date.year
                month = current_date.month
                key = f"{year}-{month}"

                month_data = data_by_month.get(key, {
                    'year': year,
                    'month': month,
                    'orders_count': 0,
                    'total_amount': 0.0
                })

                monthly_data.append({
                    'year': year,
                    'month': month,
                    'month_name': month_names[month],
                    'month_short': month_names_short[month],
                    'label': f"{month_names_short[month]}-{year}",
                    'orders_count': month_data['orders_count'],
                    'total_amount': month_data['total_amount']
                })

                if month == 12:
                    current_date = current_date.replace(year=year+1, month=1)
                else:
                    current_date = current_date.replace(month=month+1)

            total_orders = sum(m['orders_count'] for m in monthly_data)
            total_amount = sum(m['total_amount'] for m in monthly_data)
            months_with_data = sum(1 for m in monthly_data if m['orders_count'] > 0)

            return {
                'period': {
                    'start_date': start_date.date().isoformat(),
                    'end_date': end_date.date().isoformat(),
                    'months': 12
                },
                'summary': {
                    'total_orders': total_orders,
                    'total_amount': round(total_amount, 2),
                    'months_with_data': months_with_data,
                    'average_orders_per_month': round(total_orders / 12, 2),
                    'average_amount_per_month': round(total_amount / 12, 2)
                },
                'monthly_data': monthly_data
            }
            
        except Exception as e:
            logger.error(f"Error al generar reporte mensual: {str(e)}")
            raise OrderBusinessLogicError(f"Error al generar reporte mensual: {str(e)}")
    
    def get_top_clients_report(self) -> dict:
        """
        Obtiene el reporte de los top 5 clientes con más pedidos en el último trimestre
        
        Returns:
            Diccionario con:
                - period: rango de fechas del trimestre
                - top_clients: lista con client_id, orders_count y client_name
        """
        try:
            from datetime import datetime, timedelta
            from dateutil.relativedelta import relativedelta

            end_date = datetime.now()
            start_date = end_date - relativedelta(months=3)
            
            logger.info(f"Generando reporte de top clientes desde {start_date.date()} hasta {end_date.date()}")

            top_clients_data = self.order_repository.get_top_clients_last_quarter(start_date, end_date, limit=5)

            client_ids = [client['client_id'] for client in top_clients_data if client.get('client_id')]
            client_names = self.auth_integration.get_client_names(client_ids)

            top_clients = []
            for client_data in top_clients_data:
                client_id = client_data['client_id']
                top_clients.append({
                    'client_id': client_id,
                    'orders_count': client_data['orders_count'],
                    'client_name': client_names.get(client_id, 'Cliente no disponible')
                })
            
            return {
                'period': {
                    'start_date': start_date.date().isoformat(),
                    'end_date': end_date.date().isoformat(),
                    'months': 3
                },
                'top_clients': top_clients
            }
            
        except Exception as e:
            logger.error(f"Error al generar reporte de top clientes: {str(e)}")
            raise OrderBusinessLogicError(f"Error al generar reporte de top clientes: {str(e)}")
    
    def get_top_products_report(self) -> dict:
        """
        Obtiene el reporte de los top 10 productos más vendidos
        
        Returns:
            Diccionario con:
                - top_products: lista con product_id, total_sold y product_name
        """
        try:
            top_products_data = self.order_repository.get_top_products_sold(limit=10)
            
            product_ids = [product['product_id'] for product in top_products_data if product.get('product_id')]
            product_names = self.inventory_integration.get_product_names(product_ids)
            
            top_products = []
            for product_data in top_products_data:
                product_id = product_data['product_id']
                top_products.append({
                    'product_id': product_id,
                    'total_sold': product_data['total_sold'],
                    'product_name': product_names.get(product_id, 'Producto no disponible')
                })
            
            return {
                'top_products': top_products
            }
            
        except Exception as e:
            logger.error(f"Error al generar reporte de top productos: {str(e)}")
            raise OrderBusinessLogicError(f"Error al generar reporte de top productos: {str(e)}")