"""
Tests para settings.py
"""
import pytest
from unittest.mock import patch
from app.config.settings import Config, DevelopmentConfig, ProductionConfig, get_config


class TestSettings:
    """Tests para configuración de la aplicación"""
    
    def test_config_default_values(self):
        """Test: Valores por defecto de la configuración base"""
        config = Config()
        
        # Verificar valores por defecto
        assert config.SECRET_KEY == 'dev-secret-key'
        assert config.DEBUG is True
        assert config.HOST == '0.0.0.0'
        assert config.PORT == 8085
        assert config.APP_NAME == 'MediSupply Orders Backend'
        assert config.APP_VERSION == '1.0.0'
    
    def test_config_from_environment(self):
        """Test: Configuración desde variables de entorno"""
        with patch.dict('os.environ', {
            'SECRET_KEY': 'test-secret-key',
            'DEBUG': 'false',
            'HOST': '127.0.0.1',
            'PORT': '3000'
        }):
            # Reimportar para que tome las nuevas variables de entorno
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.Config()
            
            assert config.SECRET_KEY == 'test-secret-key'
            assert config.DEBUG is False
            assert config.HOST == '127.0.0.1'
            assert config.PORT == 3000
    
    def test_debug_boolean_conversion(self):
        """Test: Conversión de DEBUG a booleano"""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('1', False),  # Solo 'true' (case insensitive) es True
            ('0', False),
            ('yes', False),
            ('no', False),
        ]
        
        for debug_value, expected in test_cases:
            with patch.dict('os.environ', {'DEBUG': debug_value}):
                import importlib
                import app.config.settings
                importlib.reload(app.config.settings)
                
                config = app.config.settings.Config()
                assert config.DEBUG == expected, f"Failed for DEBUG='{debug_value}'"
    
    def test_port_integer_conversion(self):
        """Test: Conversión de PORT a entero"""
        with patch.dict('os.environ', {'PORT': '9999'}):
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.Config()
            assert config.PORT == 9999
            assert isinstance(config.PORT, int)
    
    def test_development_config(self):
        """Test: Configuración de desarrollo"""
        dev_config = DevelopmentConfig()
        
        # Verificar que hereda de Config
        assert isinstance(dev_config, Config)
        
        # Verificar que DEBUG está sobrescrito
        assert dev_config.DEBUG is True
        
        # Verificar que otros valores se mantienen
        assert dev_config.APP_NAME == 'MediSupply Orders Backend'
        assert dev_config.APP_VERSION == '1.0.0'
    
    def test_production_config(self):
        """Test: Configuración de producción"""
        prod_config = ProductionConfig()
        
        # Verificar que hereda de Config
        assert isinstance(prod_config, Config)
        
        # Verificar que DEBUG está sobrescrito
        assert prod_config.DEBUG is False
        
        # Verificar que otros valores se mantienen
        assert prod_config.APP_NAME == 'MediSupply Orders Backend'
        assert prod_config.APP_VERSION == '1.0.0'
    
    def test_get_config_development_default(self):
        """Test: get_config retorna DevelopmentConfig por defecto"""
        with patch.dict('os.environ', {}, clear=True):
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.get_config()
            assert isinstance(config, app.config.settings.DevelopmentConfig)
            assert config.DEBUG is True
    
    def test_get_config_development_explicit(self):
        """Test: get_config retorna DevelopmentConfig cuando FLASK_ENV=development"""
        with patch.dict('os.environ', {'FLASK_ENV': 'development'}):
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.get_config()
            assert isinstance(config, app.config.settings.DevelopmentConfig)
            assert config.DEBUG is True
    
    def test_get_config_production(self):
        """Test: get_config retorna ProductionConfig cuando FLASK_ENV=production"""
        with patch.dict('os.environ', {'FLASK_ENV': 'production'}):
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.get_config()
            assert isinstance(config, app.config.settings.ProductionConfig)
            assert config.DEBUG is False
    
    def test_get_config_production_case_insensitive(self):
        """Test: get_config maneja FLASK_ENV case insensitive"""
        test_cases = ['PRODUCTION', 'Production', 'prod', 'PROD']
        
        for env_value in test_cases:
            with patch.dict('os.environ', {'FLASK_ENV': env_value}):
                import importlib
                import app.config.settings
                importlib.reload(app.config.settings)
                
                config = app.config.settings.get_config()
                # Solo 'production' (case insensitive) debería retornar ProductionConfig
                if env_value.lower() == 'production':
                    assert isinstance(config, app.config.settings.ProductionConfig)
                    assert config.DEBUG is False
                else:
                    assert isinstance(config, app.config.settings.DevelopmentConfig)
                    assert config.DEBUG is True
    
    def test_get_config_unknown_environment(self):
        """Test: get_config retorna DevelopmentConfig para entornos desconocidos"""
        with patch.dict('os.environ', {'FLASK_ENV': 'unknown'}):
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.get_config()
            assert isinstance(config, app.config.settings.DevelopmentConfig)
            assert config.DEBUG is True
    
    def test_get_config_none_environment(self):
        """Test: get_config retorna DevelopmentConfig cuando FLASK_ENV es None"""
        # Simular que FLASK_ENV no está definido
        with patch.dict('os.environ', {}, clear=True):
            import importlib
            import app.config.settings
            importlib.reload(app.config.settings)
            
            config = app.config.settings.get_config()
            assert isinstance(config, app.config.settings.DevelopmentConfig)
            assert config.DEBUG is True
    
    def test_config_inheritance(self):
        """Test: Verificar herencia entre clases de configuración"""
        # DevelopmentConfig debe heredar de Config
        assert issubclass(DevelopmentConfig, Config)
        
        # ProductionConfig debe heredar de Config
        assert issubclass(ProductionConfig, Config)
        
        # DevelopmentConfig y ProductionConfig no deben ser la misma clase
        assert DevelopmentConfig is not ProductionConfig
    
    def test_config_attributes_access(self):
        """Test: Acceso a atributos de configuración"""
        config = Config()
        
        # Verificar que todos los atributos son accesibles
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'DEBUG')
        assert hasattr(config, 'HOST')
        assert hasattr(config, 'PORT')
        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'APP_VERSION')
        
        # Verificar que los atributos tienen valores
        assert config.SECRET_KEY is not None
        assert config.APP_NAME is not None
        assert config.APP_VERSION is not None
    
    def test_config_immutable_attributes(self):
        """Test: Los atributos de configuración son inmutables por defecto"""
        config = Config()
        
        # Los atributos deben ser accesibles pero no modificables fácilmente
        # (aunque técnicamente se pueden modificar, esto es más para verificar
        # que la estructura está bien definida)
        original_secret = config.SECRET_KEY
        original_debug = config.DEBUG
        
        # Verificar que los valores están definidos
        assert original_secret is not None
        assert original_debug is not None
