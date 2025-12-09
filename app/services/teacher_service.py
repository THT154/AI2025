# app/services/teacher_service.py
"""
Teacher Service - Xử lý logic nghiệp vụ giảng viên
"""

from app.repositories import TeacherRepository, ClassRepository, StudentRepository, AttendanceRepository
from app.utils.exceptions import ValidationException, NotFoundException, BusinessRuleException

class TeacherService:
    """Service xử lý nghiệp vụ giảng viên"""
    
    def __init__(self, teacher_repo: TeacherRepository, class_repo: ClassRepository,
                 student_repo: StudentRepository, attendance_repo: AttendanceRepository):
        self.teacher_repo = teacher_repo
        self.class_repo = class_repo
        self.student_repo = student_repo
        self.attendance_repo = attendance_repo
    
    def get_teacher_info(self, teacher_id: int) -> dict:
        """
        Lấy thông tin giảng viên
        
        Args:
            teacher_id: ID giảng viên
            
        Returns:
            dict: Thông tin giảng viên
            
        Raises:
            NotFoundException: Nếu không tìm thấy
        """
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise NotFoundException("Không tìm thấy giảng viên")
        return teacher
    
    def get_my_classes(self, teacher_user_id: int) -> list:
        """
        Lấy danh sách lớp của giảng viên
        
        Args:
            teacher_user_id: user_id của giảng viên
            
        Returns:
            list: Danh sách lớp
        """
        classes = self.class_repo.list_by_teacher(teacher_user_id)
        
        # Add enrollment count
        for cls in classes:
            cls['current_students'] = self.class_repo.get_enrollment_count(cls['class_id'])
        
        return classes
    
    def create_class(self, teacher_user_id: int, class_code: str, class_name: str,
                    total_sessions: int, credits: int, max_students: int,
                    semester: int, academic_year: str, schedule=None) -> int:
        """
        Tạo lớp học mới
        
        Args:
            teacher_user_id: user_id của giảng viên
            class_code: Mã lớp
            class_name: Tên lớp
            total_sessions: Tổng số buổi
            credits: Số tín chỉ
            max_students: Số sinh viên tối đa
            semester: Học kỳ
            academic_year: Năm học
            schedule: Lịch học (optional)
            
        Returns:
            int: class_id
            
        Raises:
            ValidationException: Nếu dữ liệu không hợp lệ
        """
        # Validate
        if not class_code or not class_name:
            raise ValidationException("Mã lớp và tên lớp không được để trống")
        
        if total_sessions <= 0 or credits <= 0 or max_students <= 0:
            raise ValidationException("Số buổi, tín chỉ và số sinh viên phải lớn hơn 0")
        
        # Create class
        class_id = self.class_repo.create(
            class_code, class_name, teacher_user_id, total_sessions,
            credits, max_students, semester, academic_year, schedule
        )
        
        return class_id
    
    def get_class_students(self, class_id: int) -> list:
        """
        Lấy danh sách sinh viên trong lớp
        
        Args:
            class_id: ID lớp
            
        Returns:
            list: Danh sách sinh viên
        """
        return self.student_repo.list_by_class(class_id)
    
    def get_session_attendance(self, session_id: int) -> list:
        """
        Lấy danh sách điểm danh của buổi học
        
        Args:
            session_id: ID buổi học
            
        Returns:
            list: Danh sách điểm danh
        """
        return self.attendance_repo.get_by_session(session_id)
    
    def mark_attendance(self, session_id: int, student_id: int, 
                       status: str = 'present', confidence_score=None) -> bool:
        """
        Điểm danh sinh viên
        
        Args:
            session_id: ID buổi học
            student_id: ID sinh viên
            status: Trạng thái (present/absent/late)
            confidence_score: Độ tin cậy (optional)
            
        Returns:
            bool: True nếu thành công
            
        Raises:
            ValidationException: Nếu status không hợp lệ
        """
        valid_statuses = ['present', 'absent', 'late']
        if status not in valid_statuses:
            raise ValidationException(f"Status phải là một trong: {', '.join(valid_statuses)}")
        
        # Check if already marked
        if self.attendance_repo.exists(session_id, student_id):
            # Update existing
            return self.attendance_repo.update_status(session_id, student_id, status)
        
        # Mark new
        self.attendance_repo.mark(session_id, student_id, status, confidence_score)
        return True
    
    def update_attendance_status(self, attendance_id: int, status: str) -> bool:
        """
        Cập nhật trạng thái điểm danh
        
        Args:
            attendance_id: ID bản ghi điểm danh
            status: Trạng thái mới
            
        Returns:
            bool: True nếu thành công
            
        Raises:
            ValidationException: Nếu status không hợp lệ
        """
        valid_statuses = ['present', 'absent', 'late']
        if status not in valid_statuses:
            raise ValidationException(f"Status phải là một trong: {', '.join(valid_statuses)}")
        
        return self.attendance_repo.update_status(attendance_id, status)
    
    def get_class_statistics(self, class_id: int) -> dict:
        """
        Lấy thống kê lớp học
        
        Args:
            class_id: ID lớp
            
        Returns:
            dict: Thống kê (total_students, total_sessions, avg_attendance)
        """
        class_info = self.class_repo.get_by_id(class_id)
        if not class_info:
            raise NotFoundException("Không tìm thấy lớp học")
        
        total_students = self.class_repo.get_enrollment_count(class_id)
        
        # TODO: Calculate total sessions and avg attendance from sessions table
        # For now, return basic info
        return {
            'class_id': class_id,
            'class_name': class_info['class_name'],
            'total_students': total_students,
            'max_students': class_info['max_students'],
            'total_sessions': class_info['total_sessions']
        }
