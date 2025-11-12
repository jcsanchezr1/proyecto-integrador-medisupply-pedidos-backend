"""
Servicio para comunicación con el servicio de autenticación
"""
import os
import logging
import requests
from typing import Dict, Optional

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

