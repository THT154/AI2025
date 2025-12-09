# database.py - UPDATED VERSION
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
from typing import Optional, Tuple, Any, List


class Database:
    def __init__(self, host: str = 'localhost', user: str = 'root',
                 password: str = '', database: str = 'attendance_db', port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection: Optional[mysql.connector.connection.MySQLConnection] = None

    def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=False
            )
            if self.connection.is_connected():
                print(f"✓ Kết nối MySQL thành công: {self.database} (port={self.port})")
                return True
            return False
        except Error as e:
            print(f"✗ Lỗi kết nối MySQL: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Đã đóng kết nối MySQL")

    def create_database(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ Database '{self.database}' đã sẵn sàng")
            cursor.close()
            conn.close()
        except Error as e:
            print(f"✗ Lỗi tạo database: {e}")

    def create_tables(self) -> bool:
        """Tạo tất cả các bảng cần thiết (THÊM registration_period)"""
        if not self.connection or not self.connection.is_connected():
            print("✗ Chưa kết nối database")
            return False

        cursor = self.connection.cursor()
        tables = [
            # users
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(15) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('teacher', 'moderator', 'student') NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                gender ENUM('male', 'female', 'other'),
                date_of_birth DATE,
                first_login BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """,
            # students
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE,
                student_code VARCHAR(20) UNIQUE NOT NULL,
                major VARCHAR(100),
                enrollment_year INT,
                face_encoding_path VARCHAR(255),
                face_image LONGTEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """,
            # teachers (THÊM BẢNG MỚI)
            """
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE,
                teacher_code VARCHAR(20) UNIQUE NOT NULL,
                department VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """,
            # classes
            """
            CREATE TABLE IF NOT EXISTS classes (
                class_id INT AUTO_INCREMENT PRIMARY KEY,
                class_code VARCHAR(20) UNIQUE NOT NULL,
                class_name VARCHAR(100) NOT NULL,
                teacher_id INT NOT NULL,
                total_sessions INT NOT NULL,
                credits INT NOT NULL,
                max_students INT NOT NULL,
                semester INT NOT NULL,
                academic_year VARCHAR(9) NOT NULL,
                schedule JSON,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(user_id)
            ) ENGINE=InnoDB;
            """,
            # class_enrollments
            """
            CREATE TABLE IF NOT EXISTS class_enrollments (
                enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
                class_id INT NOT NULL,
                student_id INT NOT NULL,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('enrolled', 'dropped') DEFAULT 'enrolled',
                FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                UNIQUE KEY unique_enrollment (class_id, student_id)
            ) ENGINE=InnoDB;
            """,
            # sessions
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                class_id INT NOT NULL,
                session_date DATE NOT NULL,
                session_time ENUM('morning', 'afternoon') NOT NULL,
                session_number INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """,
            # attendance
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                student_id INT NOT NULL,
                check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('present', 'absent', 'late') DEFAULT 'present',
                confidence_score FLOAT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                UNIQUE KEY unique_attendance (session_id, student_id)
            ) ENGINE=InnoDB;
            """,
            # email_logs
            """
            CREATE TABLE IF NOT EXISTS email_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                student_id INT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email_status ENUM('sent', 'failed') DEFAULT 'sent',
                FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            ) ENGINE=InnoDB;
            """,
            # registration_period (BẢNG MỚI - QUAN TRỌNG!)
            """
            CREATE TABLE IF NOT EXISTS registration_period (
                id INT AUTO_INCREMENT PRIMARY KEY,
                start_datetime DATETIME NOT NULL,
                end_datetime DATETIME NOT NULL,
                semester INT NOT NULL,
                academic_year VARCHAR(9) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """,
            # class_documents (Lưu tài liệu dưới dạng BLOB)
            """
            CREATE TABLE IF NOT EXISTS class_documents (
                document_id INT AUTO_INCREMENT PRIMARY KEY,
                class_id INT NOT NULL,
                document_name VARCHAR(255) NOT NULL,
                file_data LONGBLOB NOT NULL,
                file_size BIGINT,
                file_type VARCHAR(50),
                description TEXT,
                uploaded_by INT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
            ) ENGINE=InnoDB;
            """
        ]

        try:
            for sql in tables:
                cursor.execute(sql)
            self.connection.commit()
            print("✓ Tất cả bảng đã được tạo (bao gồm registration_period, teachers & class_documents)")
            return True
        except Error as e:
            print(f"✗ Lỗi tạo bảng: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    # ---------- Utility ----------
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password: str, hashed: str) -> bool:
        return self.hash_password(password) == hashed

    # ==================== USER ====================
    def create_user(self, username: str, email: str, password: str, role: str,
                    full_name: str, gender: Optional[str] = None, date_of_birth: Optional[str] = None) -> Optional[int]:
        cursor = self.connection.cursor()
        try:
            password_hash = self.hash_password(password)
            query = """
                INSERT INTO users (username, email, password_hash, role, full_name, gender, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (username, email, password_hash, role, full_name, gender, date_of_birth))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"✗ Lỗi tạo user: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()

    def login(self, username: str, password: str) -> Optional[dict]:
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            if user and self.verify_password(password, user['password_hash']):
                return user
            return None
        except Error as e:
            print(f"✗ Lỗi đăng nhập: {e}")
            return None
        finally:
            cursor.close()

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    # ==================== STUDENT ====================
    def create_student(self, user_id: int, student_code: str, major: Optional[str] = None,
                       enrollment_year: Optional[int] = None, face_encoding_path: Optional[str] = None) -> Optional[int]:
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO students (user_id, student_code, major, enrollment_year, face_encoding_path)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, student_code, major, enrollment_year, face_encoding_path))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"✗ Lỗi tạo student: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()

    def get_all_students(self) -> List[dict]:
        cursor = self.connection.cursor(dictionary=True)
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

    def get_student_by_code(self, student_code: str) -> Optional[dict]:
        cursor = self.connection.cursor(dictionary=True)
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

    # ==================== TEACHER (MỚI) ====================
    def create_teacher(self, user_id: int, teacher_code: str, department: Optional[str] = None) -> Optional[int]:
        """Tạo hồ sơ giảng viên"""
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO teachers (user_id, teacher_code, department)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, teacher_code, department))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"✗ Lỗi tạo teacher: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()

    def get_all_teachers(self) -> List[dict]:
        """Lấy danh sách tất cả giảng viên"""
        cursor = self.connection.cursor(dictionary=True)
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

    # ==================== CLASS ====================
    def create_class(self, class_code: str, class_name: str, teacher_id: int, total_sessions: int, credits: int,
                     max_students: int, semester: int, academic_year: str, schedule: Optional[dict] = None) -> Optional[int]:
        cursor = self.connection.cursor()
        try:
            import json
            schedule_json = json.dumps(schedule) if schedule else None
            query = """
                INSERT INTO classes (class_code, class_name, teacher_id, total_sessions,
                                   credits, max_students, semester, academic_year, schedule)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (class_code, class_name, teacher_id, total_sessions,
                                   credits, max_students, semester, academic_year, schedule_json))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"✗ Lỗi tạo lớp: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()

    def get_classes_by_teacher(self, teacher_id: int) -> List[dict]:
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM classes WHERE teacher_id = %s"
            cursor.execute(query, (teacher_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def get_classes_for_approval(self, semester: Optional[int] = None, academic_year: Optional[str] = None) -> List[dict]:
        cursor = self.connection.cursor(dictionary=True)
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

    def approve_class(self, class_id: int) -> bool:
        cursor = self.connection.cursor()
        try:
            query = "UPDATE classes SET status = 'approved' WHERE class_id = %s"
            cursor.execute(query, (class_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Lỗi duyệt lớp: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def reject_class(self, class_id: int) -> bool:
        cursor = self.connection.cursor()
        try:
            query = "UPDATE classes SET status = 'rejected' WHERE class_id = %s"
            cursor.execute(query, (class_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Lỗi từ chối lớp: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    # ==================== ENROLLMENT ====================
    def enroll_student(self, class_id: int, student_id: int) -> Tuple[bool, str]:
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT max_students, status FROM classes WHERE class_id = %s", (class_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Lớp không tồn tại"
            max_students, status = result
            
            if status != 'approved':
                return False, "Lớp chưa được duyệt"
            
            cursor.execute("""
                SELECT COUNT(*) FROM class_enrollments 
                WHERE class_id = %s AND status = 'enrolled'
            """, (class_id,))
            current_count = cursor.fetchone()[0]
            
            if current_count >= max_students:
                return False, "Lớp đã đầy"
            
            query = "INSERT INTO class_enrollments (class_id, student_id) VALUES (%s, %s)"
            cursor.execute(query, (class_id, student_id))
            self.connection.commit()
            return True, "Đăng ký thành công"
        except Error as e:
            self.connection.rollback()
            return False, f"Lỗi: {e}"
        finally:
            cursor.close()

    def get_student_classes(self, student_id: int) -> List[dict]:
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, u.full_name as teacher_name, ce.enrollment_date
                FROM class_enrollments ce
                JOIN classes c ON ce.class_id = c.class_id
                JOIN users u ON c.teacher_id = u.user_id
                WHERE ce.student_id = %s AND ce.status = 'enrolled'
            """
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def get_student_classes_approved(self, student_id: int) -> List[dict]:
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, u.full_name AS teacher_name, ce.enrollment_date
                FROM class_enrollments ce
                JOIN classes c ON ce.class_id = c.class_id
                JOIN users u ON c.teacher_id = u.user_id
                WHERE ce.student_id = %s
                AND ce.status = 'enrolled'
                AND c.status = 'approved'
            """
            cursor.execute(query, (student_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    # ==================== ATTENDANCE ====================
    def mark_attendance(self, session_id: int, student_id: int, status: str = 'present',
                        confidence_score: Optional[float] = None) -> bool:
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO attendance (session_id, student_id, status, confidence_score)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status = VALUES(status), confidence_score = VALUES(confidence_score)
            """
            cursor.execute(query, (session_id, student_id, status, confidence_score))
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Lỗi điểm danh: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def get_attendance_stats(self, student_id: int, semester: Optional[int] = None, academic_year: Optional[str] = None) -> List[dict]:
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT a.*, s.session_date, s.session_time, s.session_number,
                       c.class_name, c.class_code
                FROM attendance a
                JOIN sessions s ON a.session_id = s.session_id
                JOIN classes c ON s.class_id = c.class_id
                WHERE a.student_id = %s
            """
            params: List[Any] = [student_id]
            if semester is not None:
                query += " AND c.semester = %s"
                params.append(semester)
            if academic_year is not None:
                query += " AND c.academic_year = %s"
                params.append(academic_year)
            query += " ORDER BY s.session_date DESC"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()

    # ==================== REGISTRATION PERIOD (CẬP NHẬT) ====================
    def save_registration_period(self, start_datetime, end_datetime, semester: int, academic_year: str) -> bool:
        """Lưu khung giờ đăng ký với học kỳ và năm học"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM registration_period")
            cursor.execute("""
                INSERT INTO registration_period (start_datetime, end_datetime, semester, academic_year)
                VALUES (%s, %s, %s, %s)
            """, (start_datetime, end_datetime, semester, academic_year))
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Lỗi lưu khung giờ đăng ký: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def get_latest_registration_window(self):
        """Lấy khung giờ đăng ký mới nhất"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM registration_period
                ORDER BY start_datetime DESC
                LIMIT 1
            """)
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_approved_classes_by_period(self, semester: int, academic_year: str) -> List[dict]:
        """Lấy danh sách lớp đã duyệt theo học kỳ và năm học"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT c.*, u.full_name as teacher_name
                FROM classes c
                JOIN users u ON c.teacher_id = u.user_id
                WHERE c.status = 'approved'
                AND c.semester = %s
                AND c.academic_year = %s
            """
            cursor.execute(query, (semester, academic_year))
            return cursor.fetchall()
        finally:
            cursor.close()

    # ==================== BULK CREATION ====================
    def create_students_bulk(self, students_data: List[dict]) -> Tuple[int, List[dict]]:
        """Tạo nhiều sinh viên cùng lúc"""
        cursor = self.connection.cursor()
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
                
                password_hash = self.hash_password(password)
                
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
                    'email': email,
                    'gender': student.get('gender', ''),
                    'date_of_birth': student.get('date_of_birth', ''),
                    'major': student.get('major', ''),
                    'enrollment_year': student.get('enrollment_year', '')
                })
                success_count += 1
            
            self.connection.commit()
            return success_count, created_accounts
            
        except Error as e:
            print(f"✗ Lỗi tạo sinh viên hàng loạt: {e}")
            self.connection.rollback()
            return 0, []
        finally:
            cursor.close()

    def create_teachers_bulk(self, teachers_data: List[dict]) -> Tuple[int, List[dict]]:
        """Tạo nhiều giảng viên cùng lúc (FIX LỖI)"""
        cursor = self.connection.cursor()
        created_accounts = []
        success_count = 0
        
        try:
            for teacher in teachers_data:
                # Lấy teacher_code từ dict (key có thể là 'teacher_code' hoặc 'code')
                teacher_code = teacher.get('teacher_code') or teacher.get('code')
                if not teacher_code:
                    continue
                
                username = teacher_code.lower()
                password = teacher_code
                email = f"{teacher_code}@faculty.edu.vn"
                
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    continue
                
                password_hash = self.hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, full_name, gender, date_of_birth)
                    VALUES (%s, %s, %s, 'teacher', %s, %s, %s)
                """, (username, email, password_hash, teacher['full_name'], 
                    teacher.get('gender'), teacher.get('date_of_birth')))
                
                user_id = cursor.lastrowid
                
                # Sử dụng 'department' thay vì 'bộ môn'
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
                    'email': email,
                    'gender': teacher.get('gender', ''),
                    'date_of_birth': teacher.get('date_of_birth', ''),
                    'department': department or ''
                })
                success_count += 1
            
            self.connection.commit()
            return success_count, created_accounts
            
        except Error as e:
            print(f"✗ Lỗi tạo giảng viên hàng loạt: {e}")
            self.connection.rollback()
            return 0, []
        finally:
            cursor.close()


if __name__ == "__main__":
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=5000)
    db.create_database()
    if not db.connect():
        print("Không thể kết nối tới database.")
        exit(1)
    ok = db.create_tables()
    if not ok:
        print("Tạo bảng không thành công.")
        db.disconnect()
        exit(1)
    
    # Kiểm tra 10 bảng (THÊM registration_period, teachers & class_documents)
    try:
        cursor = db.connection.cursor()
        expected_tables = ['users', 'students', 'teachers', 'classes', 'class_enrollments', 
                          'sessions', 'attendance', 'email_logs', 'registration_period', 'class_documents']
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s
        """, (db.database,))
        existing = {row[0] for row in cursor.fetchall()}
        missing = [t for t in expected_tables if t not in existing]
        if not missing:
            print("✓ Kiểm tra: Tất cả 10 bảng đã tồn tại:")
            for t in expected_tables:
                print(f"  - {t}")
        else:
            print("✗ Thiếu bảng:", missing)
    except Error as e:
        print("✗ Lỗi kiểm tra bảng:", e)
    finally:
        try:
            cursor.close()
        except:
            pass
        db.disconnect()