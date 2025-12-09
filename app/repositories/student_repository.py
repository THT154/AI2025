# app/repositories/student_repository.py
"""
Student Repository - Quản lý truy cập dữ liệu sinh viên
"""

from .base_repository import BaseRepository

class StudentRepository(BaseRepository):
    """Repository cho bảng students"""
    
    def create(self, user_id, student_code, major=None, enrollment_year=None, face_encoding_path=None):
        """
        Tạo hồ sơ sinh viên
        
        Args:
            user_id: ID của user
            student_code: Mã sinh viên
            major: Ngành học (optional)
            enrollment_year: Năm nhập học (optional)
            face_encoding_path: Đường dẫn face encoding (optional)
            
        Returns:
            int: student_id
        """
        query = """
            INSERT INTO students (user_id, student_code, major, enrollment_year, face_encoding_path)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self._execute_query(
            query,
            (user_id, student_code, major, enrollment_year, face_encoding_path)
        )
    
    def get_by_id(self, student_id):
        """
        Lấy sinh viên theo ID
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            dict: Thông tin sinh viên
        """
        query = """
            SELECT s.*, u.full_name, u.email, u.phone, u.gender, u.date_of_birth
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.student_id = %s
        """
        return self._execute_query(query, (student_id,), fetch_one=True)
    
    def get_by_code(self, student_code):
        """
        Lấy sinh viên theo mã
        
        Args:
            student_code: Mã sinh viên
            
        Returns:
            dict: Thông tin sinh viên
        """
        query = """
            SELECT s.*, u.full_name, u.email, u.phone
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.student_code = %s
        """
        return self._execute_query(query, (student_code,), fetch_one=True)
    
    def get_by_user_id(self, user_id):
        """
        Lấy sinh viên theo user_id
        
        Args:
            user_id: ID của user
            
        Returns:
            dict: Thông tin sinh viên
        """
        query = "SELECT * FROM students WHERE user_id = %s"
        return self._execute_query(query, (user_id,), fetch_one=True)
    
    def list_all(self):
        """
        Lấy danh sách tất cả sinh viên
        
        Returns:
            list: Danh sách sinh viên
        """
        query = """
            SELECT s.*, u.full_name, u.email, u.gender, u.date_of_birth
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY s.student_code
        """
        return self._execute_query(query, fetch_all=True)
    
    def list_by_class(self, class_id):
        """
        Lấy danh sách sinh viên trong lớp
        
        Args:
            class_id: ID lớp học
            
        Returns:
            list: Danh sách sinh viên
        """
        query = """
            SELECT s.*, u.full_name, u.email, ce.enrollment_date
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            JOIN class_enrollments ce ON s.student_id = ce.student_id
            WHERE ce.class_id = %s AND ce.status = 'enrolled'
            ORDER BY s.student_code
        """
        return self._execute_query(query, (class_id,), fetch_all=True)
    
    def update(self, student_id, **kwargs):
        """
        Cập nhật thông tin sinh viên
        
        Args:
            student_id: ID sinh viên
            **kwargs: Các field cần update (major, enrollment_year, face_encoding_path)
            
        Returns:
            bool: True nếu thành công
        """
        valid_fields = ['major', 'enrollment_year', 'face_encoding_path', 'face_image']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        query = f"UPDATE students SET {set_clause} WHERE student_id = %s"
        
        self._execute_query(query, list(updates.values()) + [student_id])
        return True
    
    def delete(self, student_id):
        """
        Xóa sinh viên
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            bool: True nếu thành công
        """
        query = "DELETE FROM students WHERE student_id = %s"
        self._execute_query(query, (student_id,))
        return True
    
    def exists_code(self, student_code):
        """
        Kiểm tra mã sinh viên đã tồn tại chưa
        
        Args:
            student_code: Mã sinh viên
            
        Returns:
            bool: True nếu đã tồn tại
        """
        return self._exists('students', 'student_code = %s', (student_code,))
    
    def get_enrolled_classes(self, student_id):
        """
        Lấy danh sách lớp sinh viên đã đăng ký
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            list: Danh sách lớp
        """
        query = """
            SELECT c.*, u.full_name as teacher_name, ce.enrollment_date
            FROM class_enrollments ce
            JOIN classes c ON ce.class_id = c.class_id
            JOIN users u ON c.teacher_id = u.user_id
            WHERE ce.student_id = %s AND ce.status = 'enrolled'
            ORDER BY c.semester DESC, c.class_code
        """
        return self._execute_query(query, (student_id,), fetch_all=True)
    
    def get_approved_classes(self, student_id):
        """
        Lấy danh sách lớp đã được duyệt mà sinh viên đã đăng ký
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            list: Danh sách lớp
        """
        query = """
            SELECT c.*, u.full_name AS teacher_name, ce.enrollment_date
            FROM class_enrollments ce
            JOIN classes c ON ce.class_id = c.class_id
            JOIN users u ON c.teacher_id = u.user_id
            WHERE ce.student_id = %s
            AND ce.status = 'enrolled'
            AND c.status = 'approved'
            ORDER BY c.semester DESC, c.class_code
        """
        return self._execute_query(query, (student_id,), fetch_all=True)
