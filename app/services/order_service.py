"""
Servicio para lógica de negocio de pedidos
"""
from typing import List, Optional
import requests
import os
from ..models.order import Order
from ..models.order_item import OrderItem
from ..repositories.order_repository import OrderRepository
from ..exceptions.custom_exceptions import OrderNotFoundError, OrderValidationError, OrderBusinessLogicError


class OrderService:
    """Servicio para lógica de negocio de pedidos"""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def get_orders_by_client(self, client_id: int) -> List[Order]:
        """Obtiene pedidos por ID de cliente"""
        # Validar entrada al inicio
        if not client_id or client_id <= 0:
            raise OrderValidationError("El ID del cliente es obligatorio y debe ser mayor a 0")
        
        try:
            orders = self.order_repository.get_orders_with_items_by_client(client_id)
            return orders
        except ValueError as e:
            raise OrderValidationError(str(e))
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al obtener pedidos del cliente: {str(e)}")
    
    def get_orders_by_vendor(self, vendor_id: int) -> List[Order]:
        """Obtiene pedidos por ID de vendedor"""
        # Validar entrada al inicio
        if not vendor_id or vendor_id <= 0:
            raise OrderValidationError("El ID del vendedor es obligatorio y debe ser mayor a 0")
        
        try:
            orders = self.order_repository.get_orders_with_items_by_vendor(vendor_id)
            return orders
        except ValueError as e:
            raise OrderValidationError(str(e))
        except Exception as e:
            raise OrderBusinessLogicError(f"Error al obtener pedidos del vendedor: {str(e)}")
    
    def get_all_orders(self) -> List[Order]:
        """Obtiene todos los pedidos"""
        try:
            orders = self.order_repository.get_all()
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
        # URL del servicio de inventarios
        inventory_service_url = os.getenv('INVENTORY_SERVICE_URL', 'http://host.docker.internal:8084')
        
        for item in order.items:
            try:
                # Consultar información del producto en el servicio de inventarios
                response = requests.get(f"{inventory_service_url}/inventory/products/{item.product_id}", timeout=5)
                
                if response.status_code == 200:
                    product_data = response.json()
                    if product_data.get('success') and product_data.get('data'):
                        # Producto encontrado exitosamente
                        product = product_data['data']
                        item.product_name = product.get('name')
                        item.product_image_url = product.get('photo_url')
                        item.unit_price = product.get('price')
                    else:
                        # Producto no encontrado en inventario - dejar campos como null
                        item.product_name = None
                        item.product_image_url = None
                        item.unit_price = None
                else:
                    # Error en la consulta - dejar campos como null
                    item.product_name = None
                    item.product_image_url = None
                    item.unit_price = None
                    
            except requests.exceptions.RequestException:
                # Error de conexión - dejar campos como null
                item.product_name = None
                item.product_image_url = None
                item.unit_price = None
            except Exception:
                # Cualquier otro error - dejar campos como null
                item.product_name = None
                item.product_image_url = None
                item.unit_price = None
        
        return order
