# app/repositories/class_repository.py
"""
Class Repository - Quản lý truy cập dữ liệu lớp học
"""

from .base_repository import BaseRepository
import json

class ClassRepository(BaseRepository):
    """Repository cho bảng classes"""
    
    def create(self, class_code, class_name, teacher_id, total_sessions, credits,
               max_students, semester, academic_year, schedule=None):
        """
        Tạo lớp học mới
        
        Args:
            class_code: Mã lớp
            class_name: Tên lớp
            teacher_id: ID giảng viên (user_id)
            total_sessions: Tổng số buổi học
            credits: Số tín chỉ
            max_students: Số sinh viên tối đa
            semester: Học kỳ
            academic_year: Năm học
            schedule: Lịch học (dict, optional)
            
        Returns:
            int: class_id
        """
        schedule_json = json.dumps(schedule) if schedule else None
        query = """
            INSERT INTO classes (class_code, class_name, teacher_id, total_sessions,
                               credits, max_students, semester, academic_year, schedule)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self._execute_query(
            query,
            (class_code, class_name, teacher_id, total_sessions,
             credits, max_students, semester, academic_year, schedule_json)
        )
    
    def get_by_id(self, class_id):
        """
        Lấy lớp học theo ID
        
        Args:
            class_id: ID lớp học
            
        Returns:
            dict: Thông tin lớp học
        """
        query = """
            SELECT c.*, u.full_name as teacher_name
            FROM classes c
            JOIN users u ON c.teacher_id = u.user_id
            WHERE c.class_id = %s
        """
        return self._execute_query(query, (class_id,), fetch_one=True)
    
    def get_by_code(self, class_code):
        """
        Lấy lớp học theo mã
        
        Args:
            class_code: Mã lớp
            
        Returns:
            dict: Thông tin lớp học
        """
        query = """
            SELECT c.*, u.full_name as teacher_name
            FROM classes c
            JOIN users u ON c.teacher_id = u.user_id
            WHERE c.class_code = %s
        """
        return self._execute_query(query, (class_code,), fetch_one=True)
    
    def list_by_teacher(self, teacher_id):
        """
        Lấy danh sách lớp của giảng viên
        
        Args:
            teacher_id: ID giảng viên (user_id)
            
        Returns:
            list: Danh sách lớp
        """
        query = "SELECT * FROM classes WHERE teacher_id = %s ORDER BY semester DESC, class_code"
        return self._execute_query(query, (teacher_id,), fetch_all=True)
    
    def list_for_approval(self, semester=None, academic_year=None):
        """
        Lấy danh sách lớp cần duyệt
        
        Args:
            semester: Học kỳ (optional)
            academic_year: Năm học (optional)
            
        Returns:
            list: Danh sách lớp
        """
        query = """
            SELECT c.*, u.full_name as teacher_name
            FROM classes c
            JOIN users u ON c.teacher_id = u.user_id
            WHERE 1=1
        """
        params = []
        
        if semester is not None:
            query += " AND c.semester = %s"
            params.append(semester)
        
        if academic_year is not None:
            query += " AND c.academic_year = %s"
            params.append(academic_year)
        
        query += " ORDER BY c.created_at DESC"
        
        return self._execute_query(query, tuple(params), fetch_all=True)
    
    def list_approved(self, semester=None, academic_year=None):
        """
        Lấy danh sách lớp đã được duyệt
        
        Args:
            semester: Học kỳ (optional)
            academic_year: Năm học (optional)
            
        Returns:
            list: Danh sách lớp
        """
        query = """
            SELECT c.*, u.full_name as teacher_name
            FROM classes c
            JOIN users u ON c.teacher_id = u.user_id
            WHERE c.status = 'approved'
        """
        params = []
        
        if semester is not None:
            query += " AND c.semester = %s"
            params.append(semester)
        
        if academic_year is not None:
            query += " AND c.academic_year = %s"
            params.append(academic_year)
        
        query += " ORDER BY c.class_code"
        
        return self._execute_query(query, tuple(params), fetch_all=True)
    
    def update_status(self, class_id, status):
        """
        Cập nhật trạng thái lớp
        
        Args:
            class_id: ID lớp
            status: Trạng thái mới (pending/approved/rejected)
            
        Returns:
            bool: True nếu thành công
        """
        query = "UPDATE classes SET status = %s WHERE class_id = %s"
        self._execute_query(query, (status, class_id))
        return True
    
    def approve(self, class_id):
        """
        Duyệt lớp
        
        Args:
            class_id: ID lớp
            
        Returns:
            bool: True nếu thành công
        """
        return self.update_status(class_id, 'approved')
    
    def reject(self, class_id):
        """
        Từ chối lớp
        
        Args:
            class_id: ID lớp
            
        Returns:
            bool: True nếu thành công
        """
        return self.update_status(class_id, 'rejected')
    
    def update(self, class_id, **kwargs):
        """
        Cập nhật thông tin lớp
        
        Args:
            class_id: ID lớp
            **kwargs: Các field cần update
            
        Returns:
            bool: True nếu thành công
        """
        valid_fields = ['class_name', 'total_sessions', 'credits', 'max_students', 'schedule']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            return False
        
        # Convert schedule to JSON if present
        if 'schedule' in updates:
            updates['schedule'] = json.dumps(updates['schedule'])
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        query = f"UPDATE classes SET {set_clause} WHERE class_id = %s"
        
        self._execute_query(query, list(updates.values()) + [class_id])
        return True
    
    def delete(self, class_id):
        """
        Xóa lớp
        
        Args:
            class_id: ID lớp
            
        Returns:
            bool: True nếu thành công
        """
        query = "DELETE FROM classes WHERE class_id = %s"
        self._execute_query(query, (class_id,))
        return True
    
    def get_enrollment_count(self, class_id):
        """
        Đếm số sinh viên đã đăng ký
        
        Args:
            class_id: ID lớp
            
        Returns:
            int: Số sinh viên
        """
        query = """
            SELECT COUNT(*) as count FROM class_enrollments 
            WHERE class_id = %s AND status = 'enrolled'
        """
        result = self._execute_query(query, (class_id,), fetch_one=True)
        return result['count'] if result else 0
    
    def is_full(self, class_id):
        """
        Kiểm tra lớp đã đầy chưa
        
        Args:
            class_id: ID lớp
            
        Returns:
            bool: True nếu đã đầy
        """
        query = "SELECT max_students FROM classes WHERE class_id = %s"
        class_info = self._execute_query(query, (class_id,), fetch_one=True)
        
        if not class_info:
            return True
        
        current_count = self.get_enrollment_count(class_id)
        return current_count >= class_info['max_students']
    
    def enroll_student(self, class_id, student_id):
        """
        Đăng ký sinh viên vào lớp
        
        Args:
            class_id: ID lớp
            student_id: ID sinh viên
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if class exists and is approved
        class_info = self.get_by_id(class_id)
        if not class_info:
            return False, "Lớp không tồn tại"
        
        if class_info['status'] != 'approved':
            return False, "Lớp chưa được duyệt"
        
        # Check if class is full
        if self.is_full(class_id):
            return False, "Lớp đã đầy"
        
        # Check if already enrolled
        if self._exists('class_enrollments', 
                       'class_id = %s AND student_id = %s', 
                       (class_id, student_id)):
            return False, "Đã đăng ký lớp này rồi"
        
        # Enroll
        query = "INSERT INTO class_enrollments (class_id, student_id) VALUES (%s, %s)"
        self._execute_query(query, (class_id, student_id))
        return True, "Đăng ký thành công"
    
    def drop_student(self, class_id, student_id):
        """
        Hủy đăng ký sinh viên khỏi lớp
        
        Args:
            class_id: ID lớp
            student_id: ID sinh viên
            
        Returns:
            bool: True nếu thành công
        """
        query = """
            UPDATE class_enrollments 
            SET status = 'dropped' 
            WHERE class_id = %s AND student_id = %s
        """
        self._execute_query(query, (class_id, student_id))
        return True
