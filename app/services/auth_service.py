"""
Servicio para comunicación con el servicio de autenticación
"""
import os
import logging
import requests
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class AuthService:
    """Servicio para comunicación con autenticación"""
    
    def __init__(self, auth_base_url: str = None):
        self.base_url = auth_base_url or os.getenv(
            'AUTH_SERVICE_URL', 
            'http://autenticador:8080'
        )
        logger.info(f"AuthService inicializado con URL: {self.base_url}")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Obtiene información de un usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con información del usuario o None si no se encuentra
        """
        try:
            response = requests.get(
                f"{self.base_url}/auth/user/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('data', {}).get('user') or data.get('data', {})
                if isinstance(user, dict):
                    return user
                return None
            else:
                logger.warning(f"Usuario {user_id} no encontrado (status: {response.status_code})")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error obteniendo usuario {user_id}: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error inesperado obteniendo usuario {user_id}: {str(e)}")
            return None
    
    def get_user_name(self, user_id: str) -> str:
        """
        Obtiene el nombre de un usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Nombre del usuario o 'Usuario no disponible' si no se encuentra
        """
        user = self.get_user_by_id(user_id)
        if user and isinstance(user, dict):
            return user.get('name', 'Usuario no disponible')
        return 'Usuario no disponible'
    
    def get_users_by_ids(self, user_ids: list) -> Dict[str, str]:
        """
        Obtiene los nombres de múltiples usuarios por sus IDs
        
        Args:
            user_ids: Lista de IDs de usuarios
            
        Returns:
            Diccionario {user_id: user_name}
        """
        user_names = {}
        for user_id in user_ids:
            if not user_id:
                continue
            user_names[user_id] = self.get_user_name(user_id)
        return user_names
    
    def get_assigned_clients(self, seller_id: str) -> List[str]:
        """
        Obtiene la lista de client_id asignados a un vendedor
        
        Args:
            seller_id: ID del vendedor
            
        Returns:
            Lista de client_id asignados
        """
        try:
            response = requests.get(
                f"{self.base_url}/auth/assigned-clients/{seller_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                assigned_clients_data = data.get('data', {}).get('assigned_clients', [])
                client_ids = [client.get('id') for client in assigned_clients_data if client.get('id')]
                logger.info(f"Client IDs obtenidos para vendedor {seller_id}: {client_ids}")
                return client_ids
            else:
                logger.warning(f"Vendedor {seller_id} no encontrado o sin clientes asignados (status: {response.status_code})")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión obteniendo clientes asignados para vendedor {seller_id}: {str(e)}")
            logger.exception(e)
            return []
        except Exception as e:
            logger.error(f"Error inesperado obteniendo clientes asignados para vendedor {seller_id}: {str(e)}")
            logger.exception(e)
            return []

