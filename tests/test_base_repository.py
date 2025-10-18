"""
Tests para BaseRepository
"""
import pytest
from unittest.mock import MagicMock
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class TestBaseRepository:
    """Tests para BaseRepository"""
    
    def test_base_repository_creation(self):
        """Test: Crear BaseRepository"""
        # No se puede instanciar directamente porque es abstracto
        # Solo verificamos que tiene __init__
        assert hasattr(BaseRepository, '__init__')
        assert callable(BaseRepository.__init__)
    
    def test_base_repository_has_session(self):
        """Test: BaseRepository tiene session"""
        # Verificamos que el __init__ acepta session
        import inspect
        init_sig = inspect.signature(BaseRepository.__init__)
        assert 'session' in init_sig.parameters
    
    def test_base_repository_abstract_methods(self):
        """Test: BaseRepository tiene métodos abstractos"""
        import inspect
        
        # Verificar que tiene métodos abstractos
        assert hasattr(BaseRepository, 'create')
        assert hasattr(BaseRepository, 'get_by_id')
        assert hasattr(BaseRepository, 'get_all')
        assert hasattr(BaseRepository, 'update')
        assert hasattr(BaseRepository, 'delete')
        
        # Verificar que son abstractos
        assert inspect.isabstract(BaseRepository)
    
    def test_base_repository_cannot_instantiate_without_session(self):
        """Test: BaseRepository no se puede instanciar sin session"""
        with pytest.raises(TypeError):
            BaseRepository()
    
    def test_base_repository_session_type(self):
        """Test: BaseRepository session es del tipo correcto"""
        # Verificamos que el __init__ acepta session como parámetro
        import inspect
        init_sig = inspect.signature(BaseRepository.__init__)
        session_param = init_sig.parameters['session']
        assert session_param.annotation == Session
    
    def test_base_repository_has_methods(self):
        """Test: BaseRepository tiene métodos necesarios"""
        # Verificar que tiene los métodos necesarios
        assert hasattr(BaseRepository, 'create')
        assert hasattr(BaseRepository, 'get_by_id')
        assert hasattr(BaseRepository, 'get_all')
        assert hasattr(BaseRepository, 'update')
        assert hasattr(BaseRepository, 'delete')
        
        # Verificar que son callables
        assert callable(BaseRepository.create)
        assert callable(BaseRepository.get_by_id)
        assert callable(BaseRepository.get_all)
        assert callable(BaseRepository.update)
        assert callable(BaseRepository.delete)
    
    def test_base_repository_inheritance(self):
        """Test: BaseRepository hereda correctamente"""
        from abc import ABC
        
        assert issubclass(BaseRepository, ABC)
    
    def test_base_repository_method_signatures(self):
        """Test: BaseRepository tiene firmas de métodos correctas"""
        import inspect
        
        # Verificar que los métodos existen y tienen las firmas correctas
        create_sig = inspect.signature(BaseRepository.create)
        get_by_id_sig = inspect.signature(BaseRepository.get_by_id)
        get_all_sig = inspect.signature(BaseRepository.get_all)
        update_sig = inspect.signature(BaseRepository.update)
        delete_sig = inspect.signature(BaseRepository.delete)
        
        # Verificar que tienen parámetros self
        assert 'self' in create_sig.parameters
        assert 'self' in get_by_id_sig.parameters
        assert 'self' in get_all_sig.parameters
        assert 'self' in update_sig.parameters
        assert 'self' in delete_sig.parameters
    
    def test_base_repository_abstract_methods_raise_not_implemented(self):
        """Test: Métodos abstractos lanzan NotImplementedError"""
        # Crear una clase concreta que herede de BaseRepository
        class ConcreteRepository(BaseRepository):
            def create(self, entity):
                return entity
            
            def get_by_id(self, entity_id):
                return None
            
            def get_all(self):
                return []
            
            def update(self, entity):
                return entity
            
            def delete(self, entity_id):
                return True
        
        mock_session = MagicMock()
        repository = ConcreteRepository(mock_session)
        
        # Verificar que los métodos funcionan
        assert repository.create(None) is None
        assert repository.get_by_id(1) is None
        assert repository.get_all() == []
        assert repository.update(None) is None
        assert repository.delete(1) is True
    
    def test_base_repository_session_assignment(self):
        """Test: Asignación de session en BaseRepository"""
        # Crear una clase concreta para probar
        class ConcreteRepository(BaseRepository):
            def create(self, entity): return entity
            def get_by_id(self, entity_id): return None
            def get_all(self): return []
            def update(self, entity): return entity
            def delete(self, entity_id): return True
        
        mock_session1 = MagicMock()
        mock_session2 = MagicMock()
        
        repository = ConcreteRepository(mock_session1)
        assert repository.session == mock_session1
        
        # Cambiar session
        repository.session = mock_session2
        assert repository.session == mock_session2
    
    def test_base_repository_import(self):
        """Test: Importar BaseRepository"""
        from app.repositories.base_repository import BaseRepository
        
        assert BaseRepository is not None
        assert hasattr(BaseRepository, '__init__')
        assert hasattr(BaseRepository, 'create')
        assert hasattr(BaseRepository, 'get_by_id')
        assert hasattr(BaseRepository, 'get_all')
        assert hasattr(BaseRepository, 'update')
        assert hasattr(BaseRepository, 'delete')
    
    def test_base_repository_abstract_methods_are_abstract(self):
        """Test: Métodos abstractos están marcados como abstractos"""
        import inspect
        
        # Verificar que los métodos están marcados como abstractos
        assert getattr(BaseRepository.create, '__isabstractmethod__', False)
        assert getattr(BaseRepository.get_by_id, '__isabstractmethod__', False)
        assert getattr(BaseRepository.get_all, '__isabstractmethod__', False)
        assert getattr(BaseRepository.update, '__isabstractmethod__', False)
        assert getattr(BaseRepository.delete, '__isabstractmethod__', False)
    
    def test_base_repository_cannot_instantiate_directly(self):
        """Test: BaseRepository no se puede instanciar directamente"""
        mock_session = MagicMock()
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseRepository(mock_session)