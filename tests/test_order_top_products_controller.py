"""
Tests para OrderTopProductsController
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app import create_app
from app.controllers.order_report_controller import OrderTopProductsController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderTopProductsController:
    """Tests para OrderTopProductsController"""
    
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_top_products_success(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'top_products': [
                            {
                                'product_id': 1,
                                'total_sold': 100,
                                'product_name': 'Producto Uno'
                            },
                            {
                                'product_id': 2,
                                'total_sold': 80,
                                'product_name': 'Producto Dos'
                            }
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['message'] == "Reporte de top productos generado exitosamente"
                        assert response['data'] == mock_report_data
                        assert len(response['data']['top_products']) == 2
                        
                        mock_service.get_top_products_report.assert_called_once()
    
    def test_get_top_products_empty_data(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'top_products': []
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert "No hay productos vendidos" in response['message']
                        assert response['data']['top_products'] == []
    
    def test_get_top_products_business_logic_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.side_effect = OrderBusinessLogicError(
                        "Error al generar reporte de top productos"
                    )
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
                        assert "Error de lógica de negocio" in response['error']
                        assert "Error al generar reporte de top productos" in response['details']
    
    def test_get_top_products_generic_exception(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.side_effect = Exception("Unexpected error")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
                        assert "Error interno del servidor" in response['error']
                        assert "Unexpected error" in response['details']
    
    def test_get_top_products_response_structure(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'top_products': [
                            {
                                'product_id': 1,
                                'total_sold': 100,
                                'product_name': 'Producto Uno'
                            }
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert 'success' in response
                        assert 'message' in response
                        assert 'data' in response
                        
                        data = response['data']
                        assert 'top_products' in data
                        
                        if data['top_products']:
                            product = data['top_products'][0]
                            assert 'product_id' in product
                            assert 'total_sold' in product
                            assert 'product_name' in product
    
    def test_get_top_products_max_ten_products(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    top_products = []
                    for i in range(10):
                        top_products.append({
                            'product_id': i + 1,
                            'total_sold': 100 - i,
                            'product_name': f'Producto {i + 1}'
                        })
                    
                    mock_report_data = {
                        'top_products': top_products
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert len(response['data']['top_products']) == 10
    
    def test_get_top_products_validation_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_top_products_report.side_effect = OrderValidationError(
                        "Error de validación en reporte"
                    )
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderTopProductsController()
                    
                    with self.app.test_request_context('/orders/reports/top-products'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
                        assert "Error de validación" in response['error']
                        assert "Error de validación en reporte" in response['details']

