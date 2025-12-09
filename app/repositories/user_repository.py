# app/repositories/user_repository.py
"""
User Repository - Quản lý truy cập dữ liệu người dùng
"""

from .base_repository import BaseRepository
import hashlib

class UserRepository(BaseRepository):
    """Repository cho bảng users"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password với SHA256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password"""
        return UserRepository.hash_password(password) == hashed
    
    def create(self, username: str, email: str, password: str, role: str,
               full_name: str, gender=None, date_of_birth=None, phone=None):
        """
        Tạo user mới
        
        Args:
            username: Tên đăng nhập
            email: Email
            password: Mật khẩu (plain text)
            role: Vai trò (teacher/student/moderator)
            full_name: Họ tên đầy đủ
            gender: Giới tính (optional)
            date_of_birth: Ngày sinh (optional)
            phone: Số điện thoại (optional)
            
        Returns:
            int: user_id của user mới tạo
        """
        password_hash = self.hash_password(password)
        query = """
            INSERT INTO users (username, email, phone, password_hash, role, full_name, gender, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self._execute_query(
            query,
            (username, email, phone, password_hash, role, full_name, gender, date_of_birth)
        )
    
    def get_by_id(self, user_id):
        """
        Lấy user theo ID
        
        Args:
            user_id: ID của user
            
        Returns:
            dict: Thông tin user hoặc None
        """
        query = "SELECT * FROM users WHERE user_id = %s"
        return self._execute_query(query, (user_id,), fetch_one=True)
    
    def get_by_username(self, username):
        """
        Lấy user theo username
        
        Args:
            username: Tên đăng nhập
            
        Returns:
            dict: Thông tin user hoặc None
        """
        query = "SELECT * FROM users WHERE username = %s"
        return self._execute_query(query, (username,), fetch_one=True)
    
    def get_by_email(self, email):
        """
        Lấy user theo email
        
        Args:
            email: Email
            
        Returns:
            dict: Thông tin user hoặc None
        """
        query = "SELECT * FROM users WHERE email = %s"
        return self._execute_query(query, (email,), fetch_one=True)
    
    def authenticate(self, username, password):
        """
        Xác thực đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu (plain text)
            
        Returns:
            dict: Thông tin user nếu đúng, None nếu sai
        """
        user = self.get_by_username(username)
        if user and self.verify_password(password, user['password_hash']):
            return user
        return None
    
    def update(self, user_id, **kwargs):
        """
        Cập nhật thông tin user
        
        Args:
            user_id: ID của user
            **kwargs: Các field cần update (full_name, email, phone, gender, date_of_birth)
            
        Returns:
            bool: True nếu thành công
        """
        valid_fields = ['full_name', 'email', 'phone', 'gender', 'date_of_birth']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
        
        self._execute_query(query, list(updates.values()) + [user_id])
        return True
    
    def update_password(self, user_id, new_password):
        """
        Cập nhật mật khẩu
        
        Args:
            user_id: ID của user
            new_password: Mật khẩu mới (plain text)
            
        Returns:
            bool: True nếu thành công
        """
        password_hash = self.hash_password(new_password)
        query = "UPDATE users SET password_hash = %s, first_login = FALSE WHERE user_id = %s"
        self._execute_query(query, (password_hash, user_id))
        return True
    
    def delete(self, user_id):
        """
        Xóa user (cascade sẽ xóa student/teacher)
        
        Args:
            user_id: ID của user
            
        Returns:
            bool: True nếu thành công
        """
        query = "DELETE FROM users WHERE user_id = %s"
        self._execute_query(query, (user_id,))
        return True
    
    def list_by_role(self, role):
        """
        Lấy danh sách users theo role
        
        Args:
            role: Vai trò (teacher/student/moderator)
            
        Returns:
            list: Danh sách users
        """
        query = "SELECT * FROM users WHERE role = %s ORDER BY created_at DESC"
        return self._execute_query(query, (role,), fetch_all=True)
    
    def exists_username(self, username):
        """
        Kiểm tra username đã tồn tại chưa
        
        Args:
            username: Tên đăng nhập
            
        Returns:
            bool: True nếu đã tồn tại
        """
        return self._exists('users', 'username = %s', (username,))
    
    def exists_email(self, email):
        """
        Kiểm tra email đã tồn tại chưa
        
        Args:
            email: Email
            
        Returns:
            bool: True nếu đã tồn tại
        """
        return self._exists('users', 'email = %s', (email,))
    
    def exists_phone(self, phone):
        """
        Kiểm tra phone đã tồn tại chưa
        
        Args:
            phone: Số điện thoại
            
        Returns:
            bool: True nếu đã tồn tại
        """
        if not phone:
            return False
        return self._exists('users', 'phone = %s', (phone,))
