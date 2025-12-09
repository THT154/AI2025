# utils/validators.py - Validation helpers
import re
from datetime import datetime
from typing import Tuple

class Validators:
    """Các hàm validation chung cho toàn hệ thống"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        Returns: (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email không được để trống"
        
        email = email.strip()
        
        # Regex pattern cho email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Email không đúng định dạng (vd: example@domain.com)"
        
        if len(email) > 100:
            return False, "Email quá dài (tối đa 100 ký tự)"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate số điện thoại Việt Nam
        Returns: (is_valid, error_message)
        """
        if not phone or not phone.strip():
            return True, ""  # Phone là optional
        
        phone = phone.strip()
        
        # Loại bỏ khoảng trắng và dấu gạch ngang
        phone_clean = phone.replace(" ", "").replace("-", "")
        
        # Kiểm tra chỉ chứa số
        if not phone_clean.isdigit():
            return False, "Số điện thoại chỉ được chứa chữ số"
        
        # Kiểm tra độ dài (10-11 số cho VN)
        if len(phone_clean) < 10 or len(phone_clean) > 11:
            return False, "Số điện thoại phải có 10-11 chữ số"
        
        # Kiểm tra đầu số hợp lệ (03, 05, 07, 08, 09)
        if not phone_clean.startswith(('03', '05', '07', '08', '09')):
            return False, "Số điện thoại không hợp lệ (phải bắt đầu bằng 03, 05, 07, 08, 09)"
        
        return True, ""
    
    @staticmethod
    def validate_student_code(code: str) -> Tuple[bool, str]:
        """
        Validate mã sinh viên
        Returns: (is_valid, error_message)
        """
        if not code or not code.strip():
            return False, "Mã sinh viên không được để trống"
        
        code = code.strip()
        
        # Kiểm tra độ dài (thường 6-10 ký tự)
        if len(code) < 6 or len(code) > 20:
            return False, "Mã sinh viên phải có 6-20 ký tự"
        
        # Kiểm tra chỉ chứa chữ và số
        if not re.match(r'^[A-Za-z0-9]+$', code):
            return False, "Mã sinh viên chỉ được chứa chữ và số"
        
        return True, ""
    
    @staticmethod
    def validate_teacher_code(code: str) -> Tuple[bool, str]:
        """
        Validate mã giảng viên
        Returns: (is_valid, error_message)
        """
        if not code or not code.strip():
            return False, "Mã giảng viên không được để trống"
        
        code = code.strip()
        
        # Kiểm tra độ dài
        if len(code) < 4 or len(code) > 20:
            return False, "Mã giảng viên phải có 4-20 ký tự"
        
        # Kiểm tra chỉ chứa chữ và số
        if not re.match(r'^[A-Za-z0-9]+$', code):
            return False, "Mã giảng viên chỉ được chứa chữ và số"
        
        return True, ""
    
    @staticmethod
    def validate_full_name(name: str) -> Tuple[bool, str]:
        """
        Validate họ tên
        Returns: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Họ tên không được để trống"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Họ tên quá ngắn (tối thiểu 2 ký tự)"
        
        if len(name) > 100:
            return False, "Họ tên quá dài (tối đa 100 ký tự)"
        
        # Kiểm tra chỉ chứa chữ cái, khoảng trắng và dấu tiếng Việt
        if not re.match(r'^[a-zA-ZÀ-ỹ\s]+$', name):
            return False, "Họ tên chỉ được chứa chữ cái và khoảng trắng"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """
        Validate ngày tháng (YYYY-MM-DD)
        Returns: (is_valid, error_message)
        """
        if not date_str or not date_str.strip():
            return True, ""  # Date là optional
        
        date_str = date_str.strip()
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Kiểm tra không phải ngày tương lai
            if date_obj > datetime.now():
                return False, "Ngày sinh không thể là ngày tương lai"
            
            # Kiểm tra tuổi hợp lý (15-100 tuổi)
            age = (datetime.now() - date_obj).days // 365
            if age < 15:
                return False, "Tuổi phải từ 15 trở lên"
            if age > 100:
                return False, "Tuổi không hợp lệ"
            
            return True, ""
        except ValueError:
            return False, "Ngày sinh không đúng định dạng (YYYY-MM-DD)"
    
    @staticmethod
    def validate_year(year: str) -> Tuple[bool, str]:
        """
        Validate khóa học
        Returns: (is_valid, error_message)
        """
        if not year or not year.strip():
            return True, ""  # Year là optional
        
        year = year.strip()
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            
            if year_int < 2000 or year_int > current_year + 5:
                return False, f"Khóa học phải từ 2000 đến {current_year + 5}"
            
            return True, ""
        except ValueError:
            return False, "Khóa học phải là số"
    
    @staticmethod
    def check_duplicate_email(db, email: str, exclude_user_id: int = None) -> Tuple[bool, str]:
        """
        Kiểm tra email đã tồn tại chưa
        Returns: (is_unique, error_message)
        """
        cursor = db.connection.cursor()
        try:
            if exclude_user_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email = %s AND user_id != %s",
                    (email, exclude_user_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                return False, f"Email '{email}' đã được sử dụng"
            
            return True, ""
        finally:
            cursor.close()
    
    @staticmethod
    def check_duplicate_phone(db, phone: str, exclude_user_id: int = None) -> Tuple[bool, str]:
        """
        Kiểm tra số điện thoại đã tồn tại chưa
        Returns: (is_unique, error_message)
        """
        if not phone or not phone.strip():
            return True, ""  # Phone là optional
        
        cursor = db.connection.cursor()
        try:
            if exclude_user_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE phone = %s AND user_id != %s",
                    (phone, exclude_user_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM users WHERE phone = %s", (phone,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                return False, f"Số điện thoại '{phone}' đã được sử dụng"
            
            return True, ""
        finally:
            cursor.close()
    
    @staticmethod
    def check_duplicate_student_code(db, code: str, exclude_student_id: int = None) -> Tuple[bool, str]:
        """
        Kiểm tra mã sinh viên đã tồn tại chưa
        Returns: (is_unique, error_message)
        """
        cursor = db.connection.cursor()
        try:
            if exclude_student_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM students WHERE student_code = %s AND student_id != %s",
                    (code, exclude_student_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM students WHERE student_code = %s", (code,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                return False, f"Mã sinh viên '{code}' đã tồn tại"
            
            return True, ""
        finally:
            cursor.close()
    
    @staticmethod
    def check_duplicate_teacher_code(db, code: str, exclude_teacher_id: int = None) -> Tuple[bool, str]:
        """
        Kiểm tra mã giảng viên đã tồn tại chưa
        Returns: (is_unique, error_message)
        """
        cursor = db.connection.cursor()
        try:
            if exclude_teacher_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM teachers WHERE teacher_code = %s AND teacher_id != %s",
                    (code, exclude_teacher_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM teachers WHERE teacher_code = %s", (code,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                return False, f"Mã giảng viên '{code}' đã tồn tại"
            
            return True, ""
        finally:
            cursor.close()
