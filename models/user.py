# models/user.py - Model cho User
import hashlib
from typing import Optional

class User:
    def __init__(self, db):
        self.db = db
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return User.hash_password(password) == hashed
    
    def create(self, username: str, email: str, password: str, role: str,
               full_name: str, gender: Optional[str] = None, 
               date_of_birth: Optional[str] = None, phone: Optional[str] = None) -> Optional[int]:
        """Tạo user mới với validation"""
        from utils.validators import Validators
        
        # Validate
        is_valid, msg = Validators.validate_email(email)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = Validators.validate_phone(phone)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = Validators.validate_full_name(full_name)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = Validators.validate_date(date_of_birth)
        if not is_valid:
            raise ValueError(msg)
        
        # Check duplicates
        is_valid, msg = Validators.check_duplicate_email(self.db, email)
        if not is_valid:
            raise ValueError(msg)
        
        is_valid, msg = Validators.check_duplicate_phone(self.db, phone)
        if not is_valid:
            raise ValueError(msg)
        
        cursor = self.db.connection.cursor()
        try:
            password_hash = self.hash_password(password)
            query = """
                INSERT INTO users (username, email, phone, password_hash, role, full_name, gender, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (username, email, phone, password_hash, role, full_name, gender, date_of_birth))
            self.db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"✗ Lỗi tạo user: {e}")
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Xác thực đăng nhập"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            if user and self.verify_password(password, user['password_hash']):
                return user
            return None
        except Exception as e:
            print(f"✗ Lỗi đăng nhập: {e}")
            return None
        finally:
            cursor.close()
    
    def get_by_id(self, user_id: int) -> Optional[dict]:
        """Lấy user theo ID"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def update(self, user_id: int, **kwargs) -> bool:
        """Cập nhật thông tin user với validation"""
        from utils.validators import Validators
        
        # Validate trước khi update
        if 'email' in kwargs:
            is_valid, msg = Validators.validate_email(kwargs['email'])
            if not is_valid:
                raise ValueError(msg)
            is_valid, msg = Validators.check_duplicate_email(self.db, kwargs['email'], user_id)
            if not is_valid:
                raise ValueError(msg)
        
        if 'phone' in kwargs:
            is_valid, msg = Validators.validate_phone(kwargs['phone'])
            if not is_valid:
                raise ValueError(msg)
            is_valid, msg = Validators.check_duplicate_phone(self.db, kwargs['phone'], user_id)
            if not is_valid:
                raise ValueError(msg)
        
        if 'full_name' in kwargs:
            is_valid, msg = Validators.validate_full_name(kwargs['full_name'])
            if not is_valid:
                raise ValueError(msg)
        
        if 'date_of_birth' in kwargs:
            is_valid, msg = Validators.validate_date(kwargs['date_of_birth'])
            if not is_valid:
                raise ValueError(msg)
        
        cursor = self.db.connection.cursor()
        try:
            # Lọc các field hợp lệ
            valid_fields = ['full_name', 'email', 'phone', 'gender', 'date_of_birth']
            updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
            
            if not updates:
                return False
            
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
            
            cursor.execute(query, list(updates.values()) + [user_id])
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi cập nhật user: {e}")
            self.db.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def delete(self, user_id: int) -> bool:
        """Xóa user (cascade sẽ xóa student/teacher)"""
        cursor = self.db.connection.cursor()
        try:
            query = "DELETE FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi xóa user: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset mật khẩu"""
        cursor = self.db.connection.cursor()
        try:
            password_hash = self.hash_password(new_password)
            query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
            cursor.execute(query, (password_hash, user_id))
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi reset password: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
