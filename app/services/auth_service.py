# app/services/auth_service.py
"""
Auth Service - Xử lý logic đăng nhập và xác thực
"""

from app.repositories import UserRepository, StudentRepository, TeacherRepository
from app.utils.exceptions import AuthenticationException, ValidationException

class AuthService:
    """Service xử lý authentication và authorization"""
    
    def __init__(self, user_repo: UserRepository, student_repo: StudentRepository, teacher_repo: TeacherRepository):
        self.user_repo = user_repo
        self.student_repo = student_repo
        self.teacher_repo = teacher_repo
    
    def login(self, username: str, password: str) -> dict:
        """
        Đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu
            
        Returns:
            dict: Thông tin user với role_info
            
        Raises:
            AuthenticationException: Nếu đăng nhập thất bại
        """
        if not username or not password:
            raise ValidationException("Username và password không được để trống")
        
        user = self.user_repo.authenticate(username, password)
        
        if not user:
            raise AuthenticationException("Tên đăng nhập hoặc mật khẩu không đúng")
        
        # Lấy thông tin role-specific
        role_info = None
        if user['role'] == 'student':
            role_info = self.student_repo.get_by_user_id(user['user_id'])
        elif user['role'] == 'teacher':
            role_info = self.teacher_repo.get_by_user_id(user['user_id'])
        
        return {
            'user': user,
            'role_info': role_info,
            'first_login': user.get('first_login', False)
        }
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Đổi mật khẩu
        
        Args:
            user_id: ID user
            old_password: Mật khẩu cũ
            new_password: Mật khẩu mới
            
        Returns:
            bool: True nếu thành công
            
        Raises:
            AuthenticationException: Nếu mật khẩu cũ không đúng
            ValidationException: Nếu mật khẩu mới không hợp lệ
        """
        # Validate new password
        if not new_password or len(new_password) < 6:
            raise ValidationException("Mật khẩu mới phải có ít nhất 6 ký tự")
        
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationException("User không tồn tại")
        
        # Verify old password
        if not self.user_repo.verify_password(old_password, user['password_hash']):
            raise AuthenticationException("Mật khẩu cũ không đúng")
        
        # Update password
        return self.user_repo.update_password(user_id, new_password)
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """
        Reset mật khẩu (dành cho admin)
        
        Args:
            user_id: ID user
            new_password: Mật khẩu mới
            
        Returns:
            bool: True nếu thành công
            
        Raises:
            ValidationException: Nếu mật khẩu không hợp lệ
        """
        if not new_password or len(new_password) < 6:
            raise ValidationException("Mật khẩu mới phải có ít nhất 6 ký tự")
        
        return self.user_repo.update_password(user_id, new_password)
    
    def check_permission(self, user: dict, required_role: str) -> bool:
        """
        Kiểm tra quyền truy cập
        
        Args:
            user: Thông tin user
            required_role: Role yêu cầu
            
        Returns:
            bool: True nếu có quyền
        """
        if not user:
            return False
        
        # Moderator có tất cả quyền
        if user['role'] == 'moderator':
            return True
        
        return user['role'] == required_role
