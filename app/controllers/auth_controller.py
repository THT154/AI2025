# app/controllers/auth_controller.py
"""
Auth Controller - Adapter giữa UI và Auth Service
"""

from app.services import AuthService
from app.utils.exceptions import AppException

class AuthController:
    """Controller xử lý authentication"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def login(self, username: str, password: str) -> dict:
        """
        Xử lý đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
            
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            result = self.auth_service.login(username, password)
            return {
                'success': True,
                'data': result,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'data': None,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': f"Lỗi không xác định: {str(e)}"
            }
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """
        Xử lý đổi mật khẩu
        
        Args:
            user_id: ID user
            old_password: Mật khẩu cũ
            new_password: Mật khẩu mới
            
        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            self.auth_service.change_password(user_id, old_password, new_password)
            return {
                'success': True,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Lỗi không xác định: {str(e)}"
            }
    
    def reset_password(self, user_id: int, new_password: str) -> dict:
        """
        Xử lý reset mật khẩu (admin)
        
        Args:
            user_id: ID user
            new_password: Mật khẩu mới
            
        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            self.auth_service.reset_password(user_id, new_password)
            return {
                'success': True,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Lỗi không xác định: {str(e)}"
            }
