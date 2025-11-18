"""
Integración con el microservicio de Autenticación
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class AuthIntegration:
    """Integración para operaciones con el microservicio de Autenticación"""
    
    def __init__(self, auth_service):
        self.auth_service = auth_service
    
    def get_client_names(self, client_ids: List[str]) -> Dict[str, str]:
        """
        Obtiene los nombres de múltiples clientes por sus IDs
        
        Args:
            client_ids: Lista de IDs de clientes
            
        Returns:
            Diccionario {client_id: client_name}
            Si un cliente no se encuentra, se retorna 'Cliente no disponible'
        """
        logger.info(f"Obteniendo nombres para {len(client_ids)} clientes")
        return self.auth_service.get_users_by_ids(client_ids)
    
    def get_assigned_clients(self, seller_id: str) -> List[str]:
        """
        Obtiene la lista de client_id asignados a un vendedor
        
        Args:
            seller_id: ID del vendedor
            
        Returns:
            Lista de client_id asignados
        """
        logger.info(f"Obteniendo clientes asignados para vendedor {seller_id}")
        return self.auth_service.get_assigned_clients(seller_id)

