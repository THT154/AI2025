# models/class_model.py - Model cho Class
from typing import Optional, List, Tuple, Any
import json

class ClassModel:
    def __init__(self, db):
        self.db = db
    
    def create(self, class_code: str, class_name: str, teacher_id: int, 
               total_sessions: int, credits: int, max_students: int, 
               semester: int, academic_year: str, 
               schedule: Optional[dict] = None) -> Optional[int]:
        """Tạo lớp học mới"""
        cursor = self.db.connection.cursor()
        try:
            schedule_json = json.dumps(schedule) if schedule else None
            query = """
                INSERT INTO classes (class_code, class_name, teacher_id, total_sessions,
                                   credits, max_students, semester, academic_year, schedule)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (class_code, class_name, teacher_id, total_sessions,
                                   credits, max_students, semester, academic_year, schedule_json))
            self.db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"✗ Lỗi tạo lớp: {e}")
            self.db.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def get_by_teacher(self, teacher_id: int) -> List[dict]:
        """Lấy lớp theo giảng viên"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM classes WHERE teacher_id = %s"
            cursor.execute(query, (teacher_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_for_approval(self, semester: Optional[int] = None, 
                        academic_year: Optional[str] = None) -> List[dict]:
        """Lấy lớp cần duyệt"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, u.full_name as teacher_name
                FROM classes c
                JOIN users u ON c.teacher_id = u.user_id
                WHERE 1=1
            """
            params: List[Any] = []
            if semester is not None:
                query += " AND c.semester = %s"
                params.append(semester)
            if academic_year is not None:
                query += " AND c.academic_year = %s"
                params.append(academic_year)
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def approve(self, class_id: int) -> bool:
        """Duyệt lớp"""
        cursor = self.db.connection.cursor()
        try:
            query = "UPDATE classes SET status = 'approved' WHERE class_id = %s"
            cursor.execute(query, (class_id,))
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi duyệt lớp: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def reject(self, class_id: int) -> bool:
        """Từ chối lớp"""
        cursor = self.db.connection.cursor()
        try:
            query = "UPDATE classes SET status = 'rejected' WHERE class_id = %s"
            cursor.execute(query, (class_id,))
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi từ chối lớp: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def enroll_student(self, class_id: int, student_id: int) -> Tuple[bool, str]:
        """Đăng ký sinh viên vào lớp với validation đầy đủ"""
        from models.validation import ValidationRules
        validator = ValidationRules(self.db)
        
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            # 1. Kiểm tra lớp tồn tại
            cursor.execute("""
                SELECT max_students, status, credits, semester, academic_year 
                FROM classes WHERE class_id = %s
            """, (class_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Lớp không tồn tại"
            
            max_students = result['max_students']
            status = result['status']
            credits = result['credits']
            semester = result['semester']
            academic_year = result['academic_year']
            
            # 2. Kiểm tra lớp đã được duyệt
            if status != 'approved':
                return False, "Lớp chưa được duyệt"
            
            # 3. Kiểm tra đã đăng ký chưa
            is_valid, msg = validator.check_duplicate_enrollment(student_id, class_id)
            if not is_valid:
                return False, msg
            
            # 4. Kiểm tra khung giờ đăng ký
            is_valid, msg = validator.check_registration_period()
            if not is_valid:
                return False, msg
            
            # 5. Kiểm tra trùng lịch học
            is_valid, msg = validator.check_schedule_conflict(student_id, class_id)
            if not is_valid:
                return False, msg
            
            # 6. Kiểm tra giới hạn tín chỉ
            is_valid, msg = validator.check_credit_limit(student_id, credits, semester, academic_year)
            if not is_valid:
                return False, msg
            
            # 7. Kiểm tra lớp đã đầy
            cursor.execute("""
                SELECT COUNT(*) FROM class_enrollments 
                WHERE class_id = %s AND status = 'enrolled'
            """, (class_id,))
            current_count = cursor.fetchone()['COUNT(*)']
            
            if current_count >= max_students:
                return False, f"Lớp đã đầy ({current_count}/{max_students})"
            
            # 8. Đăng ký
            query = "INSERT INTO class_enrollments (class_id, student_id) VALUES (%s, %s)"
            cursor.execute(query, (class_id, student_id))
            self.db.connection.commit()
            return True, f"Đăng ký thành công! {msg}"
            
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Lỗi: {e}"
        finally:
            cursor.close()
    
    def get_student_classes(self, student_id: int) -> List[dict]:
        """Lấy lớp của sinh viên"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, u.full_name as teacher_name, ce.enrollment_date
                FROM class_enrollments ce
                JOIN classes c ON ce.class_id = c.class_id
                JOIN users u ON c.teacher_id = u.user_id
                WHERE ce.student_id = %s AND ce.status = 'enrolled' AND c.status = 'approved'
            """
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_approved_by_period(self, semester: int, academic_year: str) -> List[dict]:
        """Lấy lớp đã duyệt theo kỳ"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, u.full_name as teacher_name
                FROM classes c
                JOIN users u ON c.teacher_id = u.user_id
                WHERE c.status = 'approved' AND c.semester = %s AND c.academic_year = %s
            """
            cursor.execute(query, (semester, academic_year))
            return cursor.fetchall()
        finally:
            cursor.close()
