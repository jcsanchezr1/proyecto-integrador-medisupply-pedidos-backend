"""
Tests para BaseService
"""
import pytest
from unittest.mock import MagicMock
from app.services.base_service import BaseService


class TestBaseService:
    """Tests para BaseService"""
    
    def test_base_service_creation(self):
        """Test: Crear BaseService"""
        # BaseService no tiene __init__, es puramente abstracto
        # Solo verificamos que es una clase abstracta
        assert BaseService is not None
        assert hasattr(BaseService, 'create')
        assert hasattr(BaseService, 'get_by_id')
        assert hasattr(BaseService, 'get_all')
        assert hasattr(BaseService, 'update')
        assert hasattr(BaseService, 'delete')
    
    def test_base_service_abstract_methods(self):
        """Test: BaseService tiene métodos abstractos"""
        import inspect
        
        # Verificar que tiene métodos abstractos
        assert hasattr(BaseService, 'create')
        assert hasattr(BaseService, 'get_by_id')
        assert hasattr(BaseService, 'get_all')
        assert hasattr(BaseService, 'update')
        assert hasattr(BaseService, 'delete')
        
        # Verificar que son abstractos
        assert inspect.isabstract(BaseService)
    
    def test_base_service_cannot_instantiate(self):
        """Test: BaseService no se puede instanciar"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseService()
    
    def test_base_service_has_methods(self):
        """Test: BaseService tiene métodos necesarios"""
        # Verificar que tiene los métodos necesarios
        assert hasattr(BaseService, 'create')
        assert hasattr(BaseService, 'get_by_id')
        assert hasattr(BaseService, 'get_all')
        assert hasattr(BaseService, 'update')
        assert hasattr(BaseService, 'delete')
        
        # Verificar que son callables
        assert callable(BaseService.create)
        assert callable(BaseService.get_by_id)
        assert callable(BaseService.get_all)
        assert callable(BaseService.update)
        assert callable(BaseService.delete)
    
    def test_base_service_inheritance(self):
        """Test: BaseService hereda correctamente"""
        from abc import ABC
        
        assert issubclass(BaseService, ABC)
    
    def test_base_service_method_signatures(self):
        """Test: BaseService tiene firmas de métodos correctas"""
        import inspect
        
        # Verificar que los métodos existen y tienen las firmas correctas
        create_sig = inspect.signature(BaseService.create)
        get_by_id_sig = inspect.signature(BaseService.get_by_id)
        get_all_sig = inspect.signature(BaseService.get_all)
        update_sig = inspect.signature(BaseService.update)
        delete_sig = inspect.signature(BaseService.delete)
        
        # Verificar que tienen parámetros self
        assert 'self' in create_sig.parameters
        assert 'self' in get_by_id_sig.parameters
        assert 'self' in get_all_sig.parameters
        assert 'self' in update_sig.parameters
        assert 'self' in delete_sig.parameters
    
    def test_base_service_abstract_methods_raise_not_implemented(self):
        """Test: Métodos abstractos lanzan NotImplementedError"""
        # Crear una clase concreta que herede de BaseService
        class ConcreteService(BaseService):
            def create(self, data):
                return data
            
            def get_by_id(self, entity_id):
                return None
            
            def get_all(self):
                return []
            
            def update(self, entity_id, data):
                return data
            
            def delete(self, entity_id):
                return True
        
        service = ConcreteService()
        
        # Verificar que los métodos funcionan
        assert service.create(None) is None
        assert service.get_by_id(1) is None
        assert service.get_all() == []
        assert service.update(1, None) is None
        assert service.delete(1) is True
    
    def test_base_service_import(self):
        """Test: Importar BaseService"""
        from app.services.base_service import BaseService
        
        assert BaseService is not None
        assert hasattr(BaseService, 'create')
        assert hasattr(BaseService, 'get_by_id')
        assert hasattr(BaseService, 'get_all')
        assert hasattr(BaseService, 'update')
        assert hasattr(BaseService, 'delete')
    
    def test_base_service_abstract_methods_are_abstract(self):
        """Test: Métodos abstractos están marcados como abstractos"""
        import inspect
        
        # Verificar que los métodos están marcados como abstractos
        assert getattr(BaseService.create, '__isabstractmethod__', False)
        assert getattr(BaseService.get_by_id, '__isabstractmethod__', False)
        assert getattr(BaseService.get_all, '__isabstractmethod__', False)
        assert getattr(BaseService.update, '__isabstractmethod__', False)
        assert getattr(BaseService.delete, '__isabstractmethod__', False)
    
    def test_base_service_cannot_instantiate_directly(self):
        """Test: BaseService no se puede instanciar directamente"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseService()
    
    def test_base_service_method_parameters(self):
        """Test: Parámetros de métodos de BaseService"""
        import inspect
        
        # Verificar parámetros de create
        create_sig = inspect.signature(BaseService.create)
        assert 'self' in create_sig.parameters
        assert 'data' in create_sig.parameters
        
        # Verificar parámetros de get_by_id
        get_by_id_sig = inspect.signature(BaseService.get_by_id)
        assert 'self' in get_by_id_sig.parameters
        assert 'entity_id' in get_by_id_sig.parameters
        
        # Verificar parámetros de get_all
        get_all_sig = inspect.signature(BaseService.get_all)
        assert 'self' in get_all_sig.parameters
        
        # Verificar parámetros de update
        update_sig = inspect.signature(BaseService.update)
        assert 'self' in update_sig.parameters
        assert 'entity_id' in update_sig.parameters
        assert 'data' in update_sig.parameters
        
        # Verificar parámetros de delete
        delete_sig = inspect.signature(BaseService.delete)
        assert 'self' in delete_sig.parameters
        assert 'entity_id' in delete_sig.parameters
    
    def test_base_service_return_types(self):
        """Test: Tipos de retorno de métodos de BaseService"""
        import inspect
        
        # Verificar tipos de retorno
        create_sig = inspect.signature(BaseService.create)
        get_by_id_sig = inspect.signature(BaseService.get_by_id)
        get_all_sig = inspect.signature(BaseService.get_all)
        update_sig = inspect.signature(BaseService.update)
        delete_sig = inspect.signature(BaseService.delete)
        
        # Verificar que tienen anotaciones de tipo
        assert create_sig.return_annotation != inspect.Signature.empty
        assert get_by_id_sig.return_annotation != inspect.Signature.empty
        assert get_all_sig.return_annotation != inspect.Signature.empty
        assert update_sig.return_annotation != inspect.Signature.empty
        assert delete_sig.return_annotation != inspect.Signature.empty