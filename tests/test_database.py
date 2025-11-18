"""
Tests para database.py
"""
import pytest
from unittest.mock import MagicMock, patch
from app.config.database import get_db_session, create_tables, engine, SessionLocal


class TestDatabase:
    """Tests para configuración de base de datos"""
    
    def test_get_db_session_success(self):
        """Test: Obtener sesión de base de datos exitosamente"""
        # Mock de la sesión
        mock_session = MagicMock()
        
        # Mock de SessionLocal para que retorne nuestra sesión mockeada
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Obtener el generador
            db_generator = get_db_session()
            
            # Obtener la sesión
            db = next(db_generator)
            
            # Verificar que se creó la sesión
            assert db == mock_session
            mock_session_local.assert_called_once()
    
    def test_get_db_session_with_exception(self):
        """Test: Obtener sesión de base de datos con excepción"""
        # Mock de la sesión que lanza una excepción
        mock_session = MagicMock()
        mock_session.close = MagicMock()
        
        # Simular una excepción al usar la sesión
        def raise_exception():
            raise Exception("Database error")
        
        mock_session.some_method = raise_exception
        
        # Mock de SessionLocal para que retorne nuestra sesión mockeada
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Obtener el generador
            db_generator = get_db_session()
            
            # Obtener la sesión
            db = next(db_generator)
            
            # Verificar que se creó la sesión
            assert db == mock_session
            
            # Simular el uso de la sesión y la excepción
            try:
                db.some_method()
            except Exception:
                pass
            
            # Verificar que se llamó close() en el finally
            # Esto se ejecuta cuando el generador se cierra
            try:
                next(db_generator)
            except StopIteration:
                pass
            
            # Verificar que close fue llamado
            mock_session.close.assert_called_once()
    
    def test_get_db_session_generator_behavior(self):
        """Test: Comportamiento del generador get_db_session"""
        # Mock de la sesión
        mock_session = MagicMock()
        
        # Mock de SessionLocal para que retorne nuestra sesión mockeada
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Obtener el generador
            db_generator = get_db_session()
            
            # Verificar que es un generador
            assert hasattr(db_generator, '__next__')
            
            # Obtener la sesión
            db = next(db_generator)
            assert db == mock_session
            
            # Verificar que el generador se agota después de yield
            with pytest.raises(StopIteration):
                next(db_generator)
    
    def test_get_db_session_close_called_on_exit(self):
        """Test: Verificar que close() se llama al salir del contexto"""
        # Mock de la sesión
        mock_session = MagicMock()
        
        # Mock de SessionLocal para que retorne nuestra sesión mockeada
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Usar el generador en un contexto try-finally
            db_generator = get_db_session()
            
            try:
                db = next(db_generator)
                assert db == mock_session
            finally:
                # Simular el comportamiento del finally
                try:
                    next(db_generator)
                except StopIteration:
                    pass
            
            # Verificar que close fue llamado
            mock_session.close.assert_called_once()
    
    def test_create_tables_success(self):
        """Test: Crear tablas exitosamente"""
        # Mock de Base y engine
        mock_base = MagicMock()
        mock_engine = MagicMock()
        
        with patch('app.config.database.engine', mock_engine), \
             patch('app.models.db_models.Base', mock_base):
            
            # Llamar a create_tables
            create_tables()
            
            # Verificar que se llamó create_all
            mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)
    
    def test_create_tables_with_import_error(self):
        """Test: Crear tablas con error de importación"""
        # Mock para simular error de importación en la importación dinámica
        with patch('builtins.__import__', side_effect=ImportError("Module not found")):
            with pytest.raises(ImportError):
                create_tables()
    
    def test_database_url_from_env(self):
        """Test: URL de base de datos desde variable de entorno"""
        test_url = "postgresql://test_user:test_pass@test_host:5432/test_db"
        
        with patch.dict('os.environ', {'DATABASE_URL': test_url}):
            # Reimportar el módulo para que tome la nueva variable de entorno
            import importlib
            import app.config.database
            importlib.reload(app.config.database)
            
            # Verificar que se usó la URL del entorno
            assert app.config.database.DATABASE_URL == test_url
    
    def test_database_url_default(self):
        """Test: URL de base de datos por defecto"""
        # Asegurar que no hay variable de entorno
        with patch.dict('os.environ', {}, clear=True):
            # Reimportar el módulo para que tome la configuración por defecto
            import importlib
            import app.config.database
            importlib.reload(app.config.database)
            
            # Verificar que se usó la URL por defecto
            expected_url = 'postgresql+psycopg2://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db'
            assert app.config.database.DATABASE_URL == expected_url
    
    def test_engine_creation(self):
        """Test: Creación del engine de SQLAlchemy"""
        # Verificar que el engine se creó correctamente
        assert engine is not None
        assert hasattr(engine, 'execute')
        assert hasattr(engine, 'connect')
    
    def test_session_local_creation(self):
        """Test: Creación de SessionLocal"""
        # Verificar que SessionLocal se creó correctamente
        assert SessionLocal is not None
        assert hasattr(SessionLocal, '__call__')
    
    def test_get_db_session_multiple_calls(self):
        """Test: Múltiples llamadas a get_db_session"""
        # Mock de la sesión
        mock_session = MagicMock()
        
        # Mock de SessionLocal para que retorne nuestra sesión mockeada
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Llamar múltiples veces
            db_generator1 = get_db_session()
            db_generator2 = get_db_session()
            
            # Verificar que son generadores independientes
            db1 = next(db_generator1)
            db2 = next(db_generator2)
            
            assert db1 == mock_session
            assert db2 == mock_session
            
            # Verificar que se crearon dos sesiones separadas
            assert mock_session_local.call_count == 2
    
    def test_auto_close_session_exception_closing_existing(self):
        from app.config.database import auto_close_session
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
                self.order_repository.session = MagicMock()
                self.order_repository.session.close = MagicMock(side_effect=Exception("Error closing"))
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            result = controller.test_method()
            
            assert result == "success"
            controller.order_repository.session.close.assert_called_once()
    
    def test_auto_close_session_exception_in_finally(self):
        from app.config.database import auto_close_session
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session.close = MagicMock(side_effect=Exception("Error in finally"))
            mock_session_local.return_value = mock_session
            
            result = controller.test_method()
            
            assert result == "success"
            mock_session.close.assert_called_once()
    
    def test_auto_close_session_with_mocked_service(self):
        from app.config.database import auto_close_session
        
        class TestController:
            def __init__(self):
                from unittest.mock import Mock
                self.order_service = Mock()
                self.order_service.__class__.__module__ = 'unittest.mock'
                self.order_service.__class__.__name__ = 'Mock'
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        result = controller.test_method()
        
        assert result == "success"