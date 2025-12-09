# app/repositories/teacher_repository.py
"""
Teacher Repository - Quản lý truy cập dữ liệu giảng viên
"""

from .base_repository import BaseRepository

class TeacherRepository(BaseRepository):
    """Repository cho bảng teachers"""
    
    def create(self, user_id, teacher_code, department=None):
        """
        Tạo hồ sơ giảng viên
        
        Args:
            user_id: ID của user
            teacher_code: Mã giảng viên
            department: Bộ môn (optional)
            
        Returns:
            int: teacher_id
        """
        query = """
            INSERT INTO teachers (user_id, teacher_code, department)
            VALUES (%s, %s, %s)
        """
        return self._execute_query(query, (user_id, teacher_code, department))
    
    def get_by_id(self, teacher_id):
        """
        Lấy giảng viên theo ID
        
        Args:
            teacher_id: ID giảng viên
            
        Returns:
            dict: Thông tin giảng viên
        """
        query = """
            SELECT t.*, u.full_name, u.email, u.phone, u.gender, u.date_of_birth
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.teacher_id = %s
        """
        return self._execute_query(query, (teacher_id,), fetch_one=True)
    
    def get_by_code(self, teacher_code):
        """
        Lấy giảng viên theo mã
        
        Args:
            teacher_code: Mã giảng viên
            
        Returns:
            dict: Thông tin giảng viên
        """
        query = """
            SELECT t.*, u.full_name, u.email, u.phone
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.teacher_code = %s
        """
        return self._execute_query(query, (teacher_code,), fetch_one=True)
    
    def get_by_user_id(self, user_id):
        """
        Lấy giảng viên theo user_id
        
        Args:
            user_id: ID của user
            
        Returns:
            dict: Thông tin giảng viên
        """
        query = "SELECT * FROM teachers WHERE user_id = %s"
        return self._execute_query(query, (user_id,), fetch_one=True)
    
    def list_all(self):
        """
        Lấy danh sách tất cả giảng viên
        
        Returns:
            list: Danh sách giảng viên
        """
        query = """
            SELECT t.*, u.full_name, u.email, u.gender, u.date_of_birth
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            ORDER BY t.teacher_code
        """
        return self._execute_query(query, fetch_all=True)
    
    def update(self, teacher_id, **kwargs):
        """
        Cập nhật thông tin giảng viên
        
        Args:
            teacher_id: ID giảng viên
            **kwargs: Các field cần update (department)
            
        Returns:
            bool: True nếu thành công
        """
        valid_fields = ['department']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        query = f"UPDATE teachers SET {set_clause} WHERE teacher_id = %s"
        
        self._execute_query(query, list(updates.values()) + [teacher_id])
        return True
    
    def delete(self, teacher_id):
        """
        Xóa giảng viên
        
        Args:
            teacher_id: ID giảng viên
            
        Returns:
            bool: True nếu thành công
        """
        query = "DELETE FROM teachers WHERE teacher_id = %s"
        self._execute_query(query, (teacher_id,))
        return True
    
    def exists_code(self, teacher_code):
        """
        Kiểm tra mã giảng viên đã tồn tại chưa
        
        Args:
            teacher_code: Mã giảng viên
            
        Returns:
            bool: True nếu đã tồn tại
        """
        return self._exists('teachers', 'teacher_code = %s', (teacher_code,))
    
    def get_classes(self, teacher_id):
        """
        Lấy danh sách lớp của giảng viên
        
        Args:
            teacher_id: ID giảng viên (user_id)
            
        Returns:
            list: Danh sách lớp
        """
        query = """
            SELECT * FROM classes 
            WHERE teacher_id = %s 
            ORDER BY semester DESC, class_code
        """
        return self._execute_query(query, (teacher_id,), fetch_all=True)
