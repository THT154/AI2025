# controllers/teacher_controller.py - Controller cho giảng viên
from models import ClassModel, Attendance, Teacher
from typing import Optional, List

class TeacherController:
    def __init__(self, db):
        self.db = db
        self.class_model = ClassModel(db)
        self.attendance_model = Attendance(db)
        self.teacher_model = Teacher(db)
    
    def create_class(self, class_code: str, class_name: str, teacher_id: int,
                    total_sessions: int, credits: int, max_students: int,
                    semester: int, academic_year: str, schedule: Optional[dict] = None):
        """Tạo lớp học mới với validation"""
        from models.validation import ValidationRules
        
        # Validate đầu vào
        if not all([class_code, class_name, teacher_id, total_sessions, credits, max_students, semester, academic_year]):
            return None, "Vui lòng nhập đầy đủ thông tin"
        
        # Validate business rules
        validator = ValidationRules(self.db)
        is_valid, message = validator.validate_class_creation(
            class_code, teacher_id, total_sessions, credits, 
            max_students, schedule or {}, semester, academic_year
        )
        
        if not is_valid:
            return None, message
        
        # Tạo lớp
        class_id = self.class_model.create(
            class_code, class_name, teacher_id, total_sessions,
            credits, max_students, semester, academic_year, schedule
        )
        
        if class_id:
            return class_id, "Tạo lớp thành công"
        return None, "Tạo lớp thất bại"
    
    def get_my_classes(self, teacher_id: int) -> List[dict]:
        """Lấy danh sách lớp của giảng viên"""
        return self.class_model.get_by_teacher(teacher_id)
    
    def create_session(self, class_id: int, session_date: str,
                      session_time: str, session_number: int):
        """Tạo buổi học"""
        session_id = self.attendance_model.create_session(
            class_id, session_date, session_time, session_number
        )
        if session_id:
            return session_id, "Tạo buổi học thành công"
        return None, "Tạo buổi học thất bại"
    
    def mark_attendance(self, session_id: int, student_id: int,
                       status: str = 'present', confidence_score: Optional[float] = None):
        """Điểm danh sinh viên"""
        success = self.attendance_model.mark(session_id, student_id, status, confidence_score)
        if success:
            return True, "Điểm danh thành công"
        return False, "Điểm danh thất bại"
    
    def get_sessions(self, class_id: int) -> List[dict]:
        """Lấy danh sách buổi học"""
        return self.attendance_model.get_session_by_class(class_id)
