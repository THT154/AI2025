# app/controllers/teacher_controller.py
"""
Teacher Controller - Adapter giữa UI và Teacher Service
"""

from app.services import TeacherService
from app.utils.exceptions import AppException

class TeacherController:
    """Controller xử lý nghiệp vụ giảng viên"""
    
    def __init__(self, teacher_service: TeacherService):
        self.teacher_service = teacher_service
    
    def get_teacher_info(self, teacher_id: int) -> dict:
        """
        Lấy thông tin giảng viên
        
        Args:
            teacher_id: ID giảng viên
            
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            data = self.teacher_service.get_teacher_info(teacher_id)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'data': None,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': f"Lỗi: {str(e)}"
            }
    
    def get_my_classes(self, teacher_user_id: int) -> dict:
        """
        Lấy danh sách lớp của giảng viên
        
        Args:
            teacher_user_id: user_id của giảng viên
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.teacher_service.get_my_classes(teacher_user_id)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'error': f"Lỗi: {str(e)}"
            }
    
    def create_class(self, teacher_user_id: int, class_code: str, class_name: str,
                    total_sessions: int, credits: int, max_students: int,
                    semester: int, academic_year: str, schedule=None) -> dict:
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
            dict: {'success': bool, 'class_id': int, 'error': str}
        """
        try:
            class_id = self.teacher_service.create_class(
                teacher_user_id, class_code, class_name, total_sessions,
                credits, max_students, semester, academic_year, schedule
            )
            return {
                'success': True,
                'class_id': class_id,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'class_id': None,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'class_id': None,
                'error': f"Lỗi: {str(e)}"
            }
    
    def get_class_students(self, class_id: int) -> dict:
        """
        Lấy danh sách sinh viên trong lớp
        
        Args:
            class_id: ID lớp
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.teacher_service.get_class_students(class_id)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'error': f"Lỗi: {str(e)}"
            }
    
    def get_session_attendance(self, session_id: int) -> dict:
        """
        Lấy danh sách điểm danh của buổi học
        
        Args:
            session_id: ID buổi học
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.teacher_service.get_session_attendance(session_id)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'error': f"Lỗi: {str(e)}"
            }
    
    def mark_attendance(self, session_id: int, student_id: int, 
                       status: str = 'present', confidence_score=None) -> dict:
        """
        Điểm danh sinh viên
        
        Args:
            session_id: ID buổi học
            student_id: ID sinh viên
            status: Trạng thái (present/absent/late)
            confidence_score: Độ tin cậy (optional)
            
        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            self.teacher_service.mark_attendance(session_id, student_id, status, confidence_score)
            return {
                'success': True,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Lỗi: {str(e)}"
            }
    
    def update_attendance_status(self, attendance_id: int, status: str) -> dict:
        """
        Cập nhật trạng thái điểm danh
        
        Args:
            attendance_id: ID bản ghi điểm danh
            status: Trạng thái mới
            
        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            self.teacher_service.update_attendance_status(attendance_id, status)
            return {
                'success': True,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Lỗi: {str(e)}"
            }
    
    def get_class_statistics(self, class_id: int) -> dict:
        """
        Lấy thống kê lớp học
        
        Args:
            class_id: ID lớp
            
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            data = self.teacher_service.get_class_statistics(class_id)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'data': None,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': f"Lỗi: {str(e)}"
            }
