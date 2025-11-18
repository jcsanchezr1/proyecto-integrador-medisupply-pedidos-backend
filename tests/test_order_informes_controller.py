"""
Tests para los controladores de informes por vendedor
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app import create_app
from app.controllers.order_informes_controller import OrderSellerStatusSummaryController, OrderSellerClientsSummaryController, OrderSellerMonthlyController
from app.exceptions.custom_exceptions import OrderValidationError, OrderBusinessLogicError


class TestOrderSellerStatusSummaryController:
    """Tests para OrderSellerStatusSummaryController"""
    
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_status_summary_success(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'seller_id': 'seller-123',
                        'summary': {
                            'total_orders': 10,
                            'total_amount': 50000.0
                        },
                        'status_summary': [
                            {'status': 'Recibido', 'count': 2, 'percentage': 20.0, 'total_amount': 10000.0},
                            {'status': 'En Preparación', 'count': 3, 'percentage': 30.0, 'total_amount': 15000.0},
                            {'status': 'En Tránsito', 'count': 2, 'percentage': 20.0, 'total_amount': 10000.0},
                            {'status': 'Entregado', 'count': 3, 'percentage': 30.0, 'total_amount': 15000.0},
                            {'status': 'Devuelto', 'count': 0, 'percentage': 0.0, 'total_amount': 0.0}
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_status_summary.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerStatusSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/status-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['message'] == "Informe de estados generado exitosamente"
                        assert response['data'] == mock_report_data
                        mock_service.get_seller_status_summary.assert_called_once_with('384091e2-2447-43a6-9dd6-e111ef428eb2')
    
    def test_get_status_summary_missing_seller_id(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerStatusSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/status-summary'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
                        assert "seller_id" in response.get('details', '').lower() or "obligatorio" in response.get('details', '').lower()
    
    def test_get_status_summary_invalid_uuid(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerStatusSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/status-summary?seller_id=invalid-uuid'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
                        assert "uuid" in response.get('details', '').lower()
    
    def test_get_status_summary_business_logic_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_status_summary.side_effect = OrderBusinessLogicError("Error de negocio")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerStatusSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/status-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
    
    def test_get_status_summary_general_exception(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_status_summary.side_effect = Exception("Unexpected error")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerStatusSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/status-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False


class TestOrderSellerClientsSummaryController:
    """Tests para OrderSellerClientsSummaryController"""
    
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_clients_summary_success(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'seller_id': 'seller-123',
                        'summary': {
                            'total_clients': 2,
                            'total_orders': 10,
                            'total_amount': 50000.0
                        },
                        'clients': [
                            {'client_id': 'client-1', 'client_name': 'Cliente Uno', 'orders_count': 6, 'total_amount': 30000.0, 'average_order_amount': 5000.0},
                            {'client_id': 'client-2', 'client_name': 'Cliente Dos', 'orders_count': 4, 'total_amount': 20000.0, 'average_order_amount': 5000.0}
                        ],
                        'pagination': {
                            'page': 1,
                            'per_page': 10,
                            'total': 2,
                            'total_pages': 1,
                            'has_next': False,
                            'has_prev': False,
                            'next_page': None,
                            'prev_page': None
                        }
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_clients_summary.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2&page=1&per_page=10'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['message'] == "Informe de clientes generado exitosamente"
                        assert response['data'] == mock_report_data
                        mock_service.get_seller_clients_summary.assert_called_once_with('384091e2-2447-43a6-9dd6-e111ef428eb2', 1, 10)
    
    def test_get_clients_summary_missing_seller_id(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?page=1&per_page=10'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_clients_summary_invalid_uuid(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=invalid&page=1&per_page=10'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_clients_summary_invalid_page(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2&page=0&per_page=10'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_clients_summary_invalid_per_page_too_low(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2&page=1&per_page=0'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_clients_summary_invalid_per_page_too_high(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2&page=1&per_page=101'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_clients_summary_default_pagination(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'seller_id': 'seller-123',
                        'summary': {'total_clients': 0, 'total_orders': 0, 'total_amount': 0.0},
                        'clients': [],
                        'pagination': {'page': 1, 'per_page': 10, 'total': 0, 'total_pages': 0, 'has_next': False, 'has_prev': False, 'next_page': None, 'prev_page': None}
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_clients_summary.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        mock_service.get_seller_clients_summary.assert_called_once_with('384091e2-2447-43a6-9dd6-e111ef428eb2', 1, 10)
    
    def test_get_clients_summary_business_logic_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_clients_summary.side_effect = OrderBusinessLogicError("Error de negocio")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
    
    def test_get_clients_summary_general_exception(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_clients_summary.side_effect = Exception("Unexpected error")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerClientsSummaryController()
                    
                    with self.app.test_request_context('/orders/informes/seller/clients-summary?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False


class TestOrderSellerMonthlyController:
    """Tests para OrderSellerMonthlyController"""
    
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_get_monthly_report_success(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_report_data = {
                        'seller_id': 'seller-123',
                        'period': {
                            'start_date': '2024-12-01',
                            'end_date': '2025-11-14',
                            'months': 12
                        },
                        'summary': {
                            'total_orders': 8,
                            'total_amount': 4000000.0
                        },
                        'monthly_data': [
                            {'year': 2025, 'month': 11, 'month_name': 'noviembre', 'month_short': 'nov', 'label': 'nov-2025', 'orders_count': 8, 'total_amount': 4000000.0}
                        ] + [
                            {'year': 2025, 'month': i, 'month_name': 'mes', 'month_short': 'mes', 'label': 'mes-2025', 'orders_count': 0, 'total_amount': 0.0}
                            for i in range(10, 0, -1)
                        ] + [
                            {'year': 2024, 'month': 12, 'month_name': 'diciembre', 'month_short': 'dic', 'label': 'dic-2024', 'orders_count': 0, 'total_amount': 0.0}
                        ]
                    }
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_monthly_report.return_value = mock_report_data
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerMonthlyController()
                    
                    with self.app.test_request_context('/orders/informes/seller/monthly?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 200
                        assert response['success'] is True
                        assert response['message'] == "Informe mensual generado exitosamente"
                        assert response['data'] == mock_report_data
                        mock_service.get_seller_monthly_report.assert_called_once_with('384091e2-2447-43a6-9dd6-e111ef428eb2')
    
    def test_get_monthly_report_missing_seller_id(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerMonthlyController()
                    
                    with self.app.test_request_context('/orders/informes/seller/monthly'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_monthly_report_invalid_uuid(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerMonthlyController()
                    
                    with self.app.test_request_context('/orders/informes/seller/monthly?seller_id=invalid-uuid'):
                        response, status_code = controller.get()
                        
                        assert status_code == 400
                        assert response['success'] is False
    
    def test_get_monthly_report_business_logic_error(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_monthly_report.side_effect = OrderBusinessLogicError("Error de negocio")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerMonthlyController()
                    
                    with self.app.test_request_context('/orders/informes/seller/monthly?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False
    
    def test_get_monthly_report_general_exception(self):
        with patch('app.config.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            with patch('app.repositories.order_repository.OrderRepository') as mock_repo_class:
                with patch('app.services.order_service.OrderService') as mock_service_class:
                    mock_repo = MagicMock()
                    mock_repo_class.return_value = mock_repo
                    
                    mock_service = MagicMock()
                    mock_service.get_seller_monthly_report.side_effect = Exception("Unexpected error")
                    mock_service_class.return_value = mock_service
                    
                    controller = OrderSellerMonthlyController()
                    
                    with self.app.test_request_context('/orders/informes/seller/monthly?seller_id=384091e2-2447-43a6-9dd6-e111ef428eb2'):
                        response, status_code = controller.get()
                        
                        assert status_code == 500
                        assert response['success'] is False

