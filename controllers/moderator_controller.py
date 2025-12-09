# controllers/moderator_controller.py - Controller cho kiểm duyệt viên
from models import ClassModel, Student, Teacher
from typing import List, Optional, Tuple

class ModeratorController:
    def __init__(self, db):
        self.db = db
        self.class_model = ClassModel(db)
        self.student_model = Student(db)
        self.teacher_model = Teacher(db)
    
    def get_pending_classes(self, semester: Optional[int] = None,
                           academic_year: Optional[str] = None) -> List[dict]:
        """Lấy danh sách lớp chờ duyệt"""
        return self.class_model.get_for_approval(semester, academic_year)
    
    def approve_class(self, class_id: int):
        """Duyệt lớp"""
        success = self.class_model.approve(class_id)
        if success:
            return True, "Duyệt lớp thành công"
        return False, "Duyệt lớp thất bại"
    
    def reject_class(self, class_id: int):
        """Từ chối lớp"""
        success = self.class_model.reject(class_id)
        if success:
            return True, "Từ chối lớp thành công"
        return False, "Từ chối lớp thất bại"
    
    def create_students_bulk(self, students_data: List[dict]) -> Tuple[int, List[dict]]:
        """Tạo nhiều sinh viên"""
        return self.student_model.create_bulk(students_data)
    
    def create_teachers_bulk(self, teachers_data: List[dict]) -> Tuple[int, List[dict]]:
        """Tạo nhiều giảng viên"""
        return self.teacher_model.create_bulk(teachers_data)
    
    def get_all_students(self) -> List[dict]:
        """Lấy tất cả sinh viên"""
        return self.student_model.get_all()
    
    def get_all_teachers(self) -> List[dict]:
        """Lấy tất cả giảng viên"""
        return self.teacher_model.get_all()
    
    def set_registration_period(self, start_datetime, end_datetime, 
                               semester: int, academic_year: str):
        """Thiết lập khung giờ đăng ký"""
        success = self.db.save_registration_period(
            start_datetime, end_datetime, semester, academic_year
        )
        if success:
            return True, "Thiết lập khung giờ thành công"
        return False, "Thiết lập khung giờ thất bại"
