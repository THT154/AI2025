# controllers/auth_controller.py - Controller xử lý xác thực
from models import User

class AuthController:
    def __init__(self, db):
        self.db = db
        self.user_model = User(db)
    
    def login(self, username: str, password: str):
        """Xử lý đăng nhập"""
        if not username or not password:
            return None, "Vui lòng nhập đầy đủ thông tin"
        
        user = self.user_model.authenticate(username, password)
        if user:
            return user, "Đăng nhập thành công"
        return None, "Tên đăng nhập hoặc mật khẩu không đúng"
    
    def register(self, username: str, email: str, password: str, 
                role: str, full_name: str, **kwargs):
        """Xử lý đăng ký"""
        if not all([username, email, password, role, full_name]):
            return None, "Vui lòng nhập đầy đủ thông tin"
        
        user_id = self.user_model.create(
            username, email, password, role, full_name,
            kwargs.get('gender'), kwargs.get('date_of_birth')
        )
        
        if user_id:
            return user_id, "Đăng ký thành công"
        return None, "Đăng ký thất bại"
