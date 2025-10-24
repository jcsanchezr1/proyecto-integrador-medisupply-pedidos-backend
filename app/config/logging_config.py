"""
Configuración centralizada de logging para la aplicación
"""
import logging
import sys
import os


def setup_logging():
    """Configura el sistema de logging para la aplicación"""
    
    # Obtener nivel de log desde variable de entorno
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configurar formato de logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar logging básico
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Logger principal de la aplicación
    logger = logging.getLogger('medisupply.orders')
    logger.setLevel(getattr(logging, log_level))
    
    return logger


def get_logger(name: str):
    """
    Obtiene un logger para un módulo específico
    
    Args:
        name: Nombre del módulo (ej: 'controllers', 'services', 'repositories')
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(f'medisupply.orders.{name}')

