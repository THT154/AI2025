# controllers/student_controller.py - Controller cho sinh viên
from models import ClassModel, Attendance, Student
from typing import List, Optional

class StudentController:
    def __init__(self, db):
        self.db = db
        self.class_model = ClassModel(db)
        self.attendance_model = Attendance(db)
        self.student_model = Student(db)
    
    def get_available_classes(self, semester: int, academic_year: str) -> List[dict]:
        """Lấy danh sách lớp có thể đăng ký"""
        return self.class_model.get_approved_by_period(semester, academic_year)
    
    def enroll_class(self, class_id: int, student_id: int):
        """Đăng ký lớp"""
        success, message = self.class_model.enroll_student(class_id, student_id)
        return success, message
    
    def get_my_classes(self, student_id: int) -> List[dict]:
        """Lấy danh sách lớp đã đăng ký"""
        return self.class_model.get_student_classes(student_id)
    
    def get_attendance_stats(self, student_id: int, 
                           semester: Optional[int] = None,
                           academic_year: Optional[str] = None) -> List[dict]:
        """Lấy thống kê điểm danh"""
        return self.attendance_model.get_stats(student_id, semester, academic_year)
