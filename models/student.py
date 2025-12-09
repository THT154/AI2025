# models/student.py - Model cho Student
from typing import Optional, List, Tuple

class Student:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id: int, student_code: str, major: Optional[str] = None,
               enrollment_year: Optional[int] = None, 
               face_encoding_path: Optional[str] = None) -> Optional[int]:
        """Tạo hồ sơ sinh viên với validation"""
        from utils.validators import Validators
        
        # Validate
        is_valid, msg = Validators.validate_student_code(student_code)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = Validators.check_duplicate_student_code(self.db, student_code)
        if not is_valid:
            raise ValueError(msg)
        
        if enrollment_year:
            is_valid, msg = Validators.validate_year(str(enrollment_year))
            if not is_valid:
                raise ValueError(msg)
        
        cursor = self.db.connection.cursor()
        try:
            query = """
                INSERT INTO students (user_id, student_code, major, enrollment_year, face_encoding_path)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, student_code, major, enrollment_year, face_encoding_path))
            self.db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"✗ Lỗi tạo student: {e}")
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def get_all(self) -> List[dict]:
        """Lấy tất cả sinh viên"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT s.*, u.full_name, u.email, u.gender, u.date_of_birth
                FROM students s
                JOIN users u ON s.user_id = u.user_id
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_by_code(self, student_code: str) -> Optional[dict]:
        """Lấy sinh viên theo mã"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT s.*, u.full_name, u.email
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.student_code = %s
            """
            cursor.execute(query, (student_code,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def get_by_user_id(self, user_id: int) -> Optional[dict]:
        """Lấy sinh viên theo user_id"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM students WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def create_bulk(self, students_data: List[dict]) -> Tuple[int, List[dict]]:
        """Tạo nhiều sinh viên cùng lúc"""
        from models.user import User
        cursor = self.db.connection.cursor()
        created_accounts = []
        success_count = 0
        
        try:
            for student in students_data:
                username = student['student_code'].lower()
                password = student['student_code']
                email = f"{student['student_code']}@student.edu.vn"
                
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    continue
                
                password_hash = User.hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, full_name, gender, date_of_birth)
                    VALUES (%s, %s, %s, 'student', %s, %s, %s)
                """, (username, email, password_hash, student['full_name'], 
                    student.get('gender'), student.get('date_of_birth')))
                
                user_id = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO students (user_id, student_code, major, enrollment_year)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, student['student_code'], student.get('major'), student.get('enrollment_year')))
                
                created_accounts.append({
                    'student_code': student['student_code'],
                    'full_name': student['full_name'],
                    'username': username,
                    'password': password,
                    'email': email
                })
                success_count += 1
            
            self.db.connection.commit()
            return success_count, created_accounts
            
        except Exception as e:
            print(f"✗ Lỗi tạo sinh viên hàng loạt: {e}")
            self.db.connection.rollback()
            return 0, []
        finally:
            cursor.close()

    def update(self, student_id: int, **kwargs) -> bool:
        """Cập nhật thông tin sinh viên"""
        cursor = self.db.connection.cursor()
        try:
            valid_fields = ['major', 'enrollment_year', 'face_encoding_path']
            updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
            
            if not updates:
                return False
            
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            query = f"UPDATE students SET {set_clause} WHERE student_id = %s"
            
            cursor.execute(query, list(updates.values()) + [student_id])
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi cập nhật student: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
