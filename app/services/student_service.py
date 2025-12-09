# app/services/student_service.py
"""
Student Service - Xử lý logic nghiệp vụ sinh viên
"""

from app.repositories import StudentRepository, ClassRepository, AttendanceRepository
from app.utils.exceptions import ValidationException, NotFoundException, BusinessRuleException

class StudentService:
    """Service xử lý nghiệp vụ sinh viên"""
    
    def __init__(self, student_repo: StudentRepository, class_repo: ClassRepository, 
                 attendance_repo: AttendanceRepository):
        self.student_repo = student_repo
        self.class_repo = class_repo
        self.attendance_repo = attendance_repo
    
    def get_student_info(self, student_id: int) -> dict:
        """
        Lấy thông tin sinh viên
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            dict: Thông tin sinh viên
            
        Raises:
            NotFoundException: Nếu không tìm thấy
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundException("Không tìm thấy sinh viên")
        return student
    
    def get_enrolled_classes(self, student_id: int) -> list:
        """
        Lấy danh sách lớp đã đăng ký
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            list: Danh sách lớp
        """
        return self.student_repo.get_enrolled_classes(student_id)
    
    def get_approved_classes(self, student_id: int) -> list:
        """
        Lấy danh sách lớp đã được duyệt
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            list: Danh sách lớp đã duyệt
        """
        return self.student_repo.get_approved_classes(student_id)
    
    def register_class(self, student_id: int, class_id: int) -> tuple:
        """
        Đăng ký lớp học
        
        Args:
            student_id: ID sinh viên
            class_id: ID lớp
            
        Returns:
            tuple: (success: bool, message: str)
            
        Raises:
            NotFoundException: Nếu không tìm thấy lớp
            BusinessRuleException: Nếu vi phạm quy tắc đăng ký
        """
        # Validate student exists
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundException("Không tìm thấy sinh viên")
        
        # Register through class repository (has business logic)
        success, message = self.class_repo.enroll_student(class_id, student_id)
        
        if not success:
            raise BusinessRuleException(message)
        
        return success, message
    
    def get_attendance_history(self, student_id: int, class_id=None) -> list:
        """
        Lấy lịch sử điểm danh
        
        Args:
            student_id: ID sinh viên
            class_id: ID lớp (optional)
            
        Returns:
            list: Lịch sử điểm danh
        """
        return self.attendance_repo.get_by_student(student_id, class_id)
    
    def get_attendance_statistics(self, student_id: int, class_id=None) -> dict:
        """
        Lấy thống kê điểm danh
        
        Args:
            student_id: ID sinh viên
            class_id: ID lớp (optional)
            
        Returns:
            dict: Thống kê (present, absent, late, total, percentage)
        """
        stats = self.attendance_repo.get_statistics(student_id, class_id)
        
        if not stats or stats['total'] == 0:
            return {
                'total': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'percentage': 0.0
            }
        
        # Calculate percentage
        percentage = (stats['present'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        return {
            'total': stats['total'],
            'present': stats['present'],
            'absent': stats['absent'],
            'late': stats['late'],
            'percentage': round(percentage, 2)
        }
    
    def get_class_details(self, class_id: int) -> dict:
        """
        Lấy chi tiết lớp học
        
        Args:
            class_id: ID lớp
            
        Returns:
            dict: Thông tin lớp
            
        Raises:
            NotFoundException: Nếu không tìm thấy
        """
        class_info = self.class_repo.get_by_id(class_id)
        if not class_info:
            raise NotFoundException("Không tìm thấy lớp học")
        
        # Add enrollment count
        class_info['current_students'] = self.class_repo.get_enrollment_count(class_id)
        
        return class_info
    
    def list_available_classes(self, semester: int, academic_year: str) -> list:
        """
        Lấy danh sách lớp có thể đăng ký
        
        Args:
            semester: Học kỳ
            academic_year: Năm học
            
        Returns:
            list: Danh sách lớp đã được duyệt
        """
        classes = self.class_repo.list_approved(semester, academic_year)
        
        # Add enrollment info
        for cls in classes:
            cls['current_students'] = self.class_repo.get_enrollment_count(cls['class_id'])
            cls['is_full'] = cls['current_students'] >= cls['max_students']
        
        return classes
