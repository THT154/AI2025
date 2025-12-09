# models/teacher.py - Model cho Teacher
from typing import Optional, List, Tuple

class Teacher:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id: int, teacher_code: str, 
               department: Optional[str] = None) -> Optional[int]:
        """Tạo hồ sơ giảng viên với validation"""
        from utils.validators import Validators
        
        # Validate
        is_valid, msg = Validators.validate_teacher_code(teacher_code)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = Validators.check_duplicate_teacher_code(self.db, teacher_code)
        if not is_valid:
            raise ValueError(msg)
        
        cursor = self.db.connection.cursor()
        try:
            query = """
                INSERT INTO teachers (user_id, teacher_code, department)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, teacher_code, department))
            self.db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"✗ Lỗi tạo teacher: {e}")
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def get_all(self) -> List[dict]:
        """Lấy tất cả giảng viên"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT t.*, u.full_name, u.email, u.gender, u.date_of_birth
                FROM teachers t
                JOIN users u ON t.user_id = u.user_id
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_by_user_id(self, user_id: int) -> Optional[dict]:
        """Lấy giảng viên theo user_id"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM teachers WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def create_bulk(self, teachers_data: List[dict]) -> Tuple[int, List[dict]]:
        """Tạo nhiều giảng viên cùng lúc"""
        from models.user import User
        cursor = self.db.connection.cursor()
        created_accounts = []
        success_count = 0
        
        try:
            for teacher in teachers_data:
                teacher_code = teacher.get('teacher_code') or teacher.get('code')
                if not teacher_code:
                    continue
                
                username = teacher_code.lower()
                password = teacher_code
                email = f"{teacher_code}@faculty.edu.vn"
                
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    continue
                
                password_hash = User.hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, full_name, gender, date_of_birth)
                    VALUES (%s, %s, %s, 'teacher', %s, %s, %s)
                """, (username, email, password_hash, teacher['full_name'], 
                    teacher.get('gender'), teacher.get('date_of_birth')))
                
                user_id = cursor.lastrowid
                
                department = teacher.get('department') or teacher.get('major')
                
                cursor.execute("""
                    INSERT INTO teachers (user_id, teacher_code, department)
                    VALUES (%s, %s, %s)
                """, (user_id, teacher_code, department))
                
                created_accounts.append({
                    'teacher_code': teacher_code,
                    'full_name': teacher['full_name'],
                    'username': username,
                    'password': password,
                    'email': email
                })
                success_count += 1
            
            self.db.connection.commit()
            return success_count, created_accounts
            
        except Exception as e:
            print(f"✗ Lỗi tạo giảng viên hàng loạt: {e}")
            self.db.connection.rollback()
            return 0, []
        finally:
            cursor.close()

    def update(self, teacher_id: int, **kwargs) -> bool:
        """Cập nhật thông tin giảng viên"""
        cursor = self.db.connection.cursor()
        try:
            valid_fields = ['department']
            updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
            
            if not updates:
                return False
            
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            query = f"UPDATE teachers SET {set_clause} WHERE teacher_id = %s"
            
            cursor.execute(query, list(updates.values()) + [teacher_id])
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi cập nhật teacher: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
