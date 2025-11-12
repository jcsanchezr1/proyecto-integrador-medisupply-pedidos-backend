"""
Integración con el microservicio de Inventarios
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class InventoryIntegration:
    """Integración para operaciones con el microservicio de Inventarios"""
    
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service
    
    def verify_products_availability(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica la disponibilidad de múltiples productos
        
        Args:
            items: Lista de items con product_id y quantity
            
        Returns:
            Lista con información de productos disponibles
            
        Raises:
            OrderBusinessLogicError: Si algún producto no está disponible
        """
        logger.info(f"Verificando disponibilidad de {len(items)} productos")
        return self.inventory_service.check_multiple_products_availability(items)
    
    def update_products_stock_with_compensation(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Actualiza el stock de productos con compensación automática
        
        Args:
            items: Lista de items con product_id y quantity
            
        Returns:
            Lista de productos actualizados exitosamente
            
        Raises:
            OrderBusinessLogicError: Si hay error en la actualización
        """
        logger.info(f"Actualizando stock para {len(items)} productos con compensación")
        successfully_updated_items = []
        
        try:
            for i, item in enumerate(items):
                product_id = item['product_id']
                quantity = item['quantity']
                
                logger.info(f"Procesando producto {i+1}/{len(items)}: ID={product_id}, Cantidad={quantity}")
                self.inventory_service.update_product_stock(product_id, quantity)
                
                successfully_updated_items.append({
                    'product_id': product_id,
                    'quantity': quantity
                })
                logger.info(f"Producto {product_id} actualizado exitosamente")
            
            logger.info(f"Todos los productos actualizados exitosamente")
            return successfully_updated_items
            
        except Exception as e:
            logger.error(f"Error actualizando stock: {str(e)}")
            logger.info(f"Iniciando compensación para {len(successfully_updated_items)} productos")
            
            for item in successfully_updated_items:
                try:
                    logger.info(f"Compensando producto {item['product_id']} con cantidad {item['quantity']}")
                    self.inventory_service._make_request(
                        "PUT", 
                        f"/products/{item['product_id']}/stock", 
                        json={
                            "operation": "add",
                            "quantity": item['quantity'],
                            "reason": "compensation"
                        }
                    )
                    logger.info(f"Producto {item['product_id']} compensado exitosamente")
                except Exception as compensation_error:
                    logger.error(f"Error compensando producto {item['product_id']}: {compensation_error}")
            
            logger.error(f"Compensación completada. Re-lanzando error original: {str(e)}")
            raise e
    
    def get_product_names(self, product_ids: List[int]) -> Dict[int, str]:
        """
        Obtiene los nombres de múltiples productos por sus IDs
        
        Args:
            product_ids: Lista de IDs de productos
            
        Returns:
            Diccionario {product_id: product_name}
            Si un producto no se encuentra, se retorna 'Producto no disponible'
        """
        logger.info(f"Obteniendo nombres para {len(product_ids)} productos")
        product_names = {}
        for product_id in product_ids:
            if not product_id:
                continue
            product_info = self.inventory_service.get_product_by_id(product_id)
            product_names[product_id] = product_info.get('name', 'Producto no disponible') or 'Producto no disponible'
        return product_names