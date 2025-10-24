"""
Servicio para comunicación con el servicio de inventarios
"""
import os
import logging
import requests
from typing import Dict, List, Tuple
from ..exceptions.custom_exceptions import OrderBusinessLogicError

logger = logging.getLogger(__name__)


class InventoryService:
    """Servicio para comunicación con inventarios"""
    
    def __init__(self, inventory_base_url: str = None):
        # Usar variable de entorno o URL por defecto
        self.base_url = inventory_base_url or os.getenv(
            'INVENTORY_SERVICE_URL', 
            'http://medisupply-inventarios:8080'
        )
        logger.info(f"InventoryService inicializado con URL: {self.base_url}")
    
    def check_product_availability(self, product_id: int, required_quantity: int) -> Dict:
        """
        Verifica si un producto tiene stock suficiente
        
        Args:
            product_id: ID del producto
            required_quantity: Cantidad requerida
            
        Returns:
            Dict con información del producto y stock disponible
            
        Raises:
            OrderBusinessLogicError: Si el producto no existe o no hay stock suficiente
        """
        try:
            response = requests.get(f"{self.base_url}/inventory/products/{product_id}")
            
            if response.status_code == 404:
                raise OrderBusinessLogicError(f"Producto con ID {product_id} no encontrado en inventario")
            
            if response.status_code != 200:
                raise OrderBusinessLogicError(f"Error al consultar producto: {response.status_code}")
            
            product_data = response.json()
            if not product_data.get('success'):
                raise OrderBusinessLogicError(f"Error al obtener producto: {product_data.get('error')}")
            
            product_info = product_data['data']
            available_quantity = product_info['quantity']
            
            if available_quantity < required_quantity:
                raise OrderBusinessLogicError(
                    f"Stock insuficiente para el producto {product_info['name']} "
                    f"(SKU: {product_info['sku']}). Disponible: {available_quantity}, "
                    f"Requerido: {required_quantity}"
                )
            
            return {
                'product_id': product_id,
                'sku': product_info['sku'],
                'name': product_info['name'],
                'price': product_info['price'],
                'available_quantity': available_quantity,
                'required_quantity': required_quantity
            }
            
        except requests.exceptions.RequestException as e:
            raise OrderBusinessLogicError(f"Error de conexión con el servicio de inventarios: {str(e)}")
        except OrderBusinessLogicError:
            raise
        except Exception as e:
            raise OrderBusinessLogicError(f"Error inesperado al verificar stock: {str(e)}")
    
    def update_product_stock(self, product_id: int, quantity: int) -> Dict:
        """
        Actualiza el stock de un producto (resta la cantidad)
        
        Args:
            product_id: ID del producto
            quantity: Cantidad a restar
            
        Returns:
            Dict con información de la actualización
            
        Raises:
            OrderBusinessLogicError: Si hay error en la actualización
        """
        try:
            payload = {
                "operation": "subtract",
                "quantity": quantity,
                "reason": "order_fulfillment"
            }
            
            response = requests.put(
                f"{self.base_url}/inventory/products/{product_id}/stock",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 404:
                raise OrderBusinessLogicError(f"Producto con ID {product_id} no encontrado")
            
            if response.status_code == 422:
                error_data = response.json()
                raise OrderBusinessLogicError(f"Stock insuficiente: {error_data.get('details', 'Error desconocido')}")
            
            if response.status_code != 200:
                error_data = response.json()
                raise OrderBusinessLogicError(f"Error al actualizar stock: {error_data.get('error', 'Error desconocido')}")
            
            update_data = response.json()
            if not update_data.get('success'):
                raise OrderBusinessLogicError(f"Error al actualizar stock: {update_data.get('error')}")
            
            return update_data['data']
            
        except requests.exceptions.RequestException as e:
            raise OrderBusinessLogicError(f"Error de conexión con el servicio de inventarios: {str(e)}")
        except OrderBusinessLogicError:
            raise
        except Exception as e:
            raise OrderBusinessLogicError(f"Error inesperado al actualizar stock: {str(e)}")
    
    def check_multiple_products_availability(self, order_items: List[Dict]) -> List[Dict]:
        """
        Verifica la disponibilidad de múltiples productos
        
        Args:
            order_items: Lista de items con product_id y quantity
            
        Returns:
            Lista con información de cada producto
            
        Raises:
            OrderBusinessLogicError: Si algún producto no está disponible
        """
        products_info = []
        
        for item in order_items:
            product_info = self.check_product_availability(
                item['product_id'], 
                item['quantity']
            )
            products_info.append(product_info)
        
        return products_info
    
    def update_multiple_products_stock(self, order_items: List[Dict]) -> List[Dict]:
        """
        Actualiza el stock de múltiples productos
        
        Args:
            order_items: Lista de items con product_id y quantity
            
        Returns:
            Lista con información de cada actualización
        """
        updates_info = []
        
        for item in order_items:
            update_info = self.update_product_stock(
                item['product_id'], 
                item['quantity']
            )
            updates_info.append(update_info)
        
        return updates_info
