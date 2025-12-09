# app/controllers/student_controller.py
"""
Student Controller - Adapter giữa UI và Student Service
"""

from app.services import StudentService
from app.utils.exceptions import AppException

class StudentController:
    """Controller xử lý nghiệp vụ sinh viên"""
    
    def __init__(self, student_service: StudentService):
        self.student_service = student_service
    
    def get_student_info(self, student_id: int) -> dict:
        """
        Lấy thông tin sinh viên
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            data = self.student_service.get_student_info(student_id)
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
    
    def get_enrolled_classes(self, student_id: int) -> dict:
        """
        Lấy danh sách lớp đã đăng ký
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.student_service.get_enrolled_classes(student_id)
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
    
    def get_approved_classes(self, student_id: int) -> dict:
        """
        Lấy danh sách lớp đã được duyệt
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.student_service.get_approved_classes(student_id)
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
    
    def register_class(self, student_id: int, class_id: int) -> dict:
        """
        Đăng ký lớp học
        
        Args:
            student_id: ID sinh viên
            class_id: ID lớp
            
        Returns:
            dict: {'success': bool, 'message': str, 'error': str}
        """
        try:
            success, message = self.student_service.register_class(student_id, class_id)
            return {
                'success': success,
                'message': message,
                'error': None
            }
        except AppException as e:
            return {
                'success': False,
                'message': None,
                'error': e.message
            }
        except Exception as e:
            return {
                'success': False,
                'message': None,
                'error': f"Lỗi: {str(e)}"
            }
    
    def get_attendance_history(self, student_id: int, class_id=None) -> dict:
        """
        Lấy lịch sử điểm danh
        
        Args:
            student_id: ID sinh viên
            class_id: ID lớp (optional)
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.student_service.get_attendance_history(student_id, class_id)
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
    
    def get_attendance_statistics(self, student_id: int, class_id=None) -> dict:
        """
        Lấy thống kê điểm danh
        
        Args:
            student_id: ID sinh viên
            class_id: ID lớp (optional)
            
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            data = self.student_service.get_attendance_statistics(student_id, class_id)
            return {
                'success': True,
                'data': data,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': f"Lỗi: {str(e)}"
            }
    
    def get_class_details(self, class_id: int) -> dict:
        """
        Lấy chi tiết lớp học
        
        Args:
            class_id: ID lớp
            
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            data = self.student_service.get_class_details(class_id)
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
    
    def list_available_classes(self, semester: int, academic_year: str) -> dict:
        """
        Lấy danh sách lớp có thể đăng ký
        
        Args:
            semester: Học kỳ
            academic_year: Năm học
            
        Returns:
            dict: {'success': bool, 'data': list, 'error': str}
        """
        try:
            data = self.student_service.list_available_classes(semester, academic_year)
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
