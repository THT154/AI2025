# models/attendance.py - Model cho Attendance
from typing import Optional, List, Any

class Attendance:
    def __init__(self, db):
        self.db = db
    
    def mark(self, session_id: int, student_id: int, status: str = 'present',
             confidence_score: Optional[float] = None) -> bool:
        """Điểm danh"""
        cursor = self.db.connection.cursor()
        try:
            query = """
                INSERT INTO attendance (session_id, student_id, status, confidence_score)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status = VALUES(status), confidence_score = VALUES(confidence_score)
            """
            cursor.execute(query, (session_id, student_id, status, confidence_score))
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Lỗi điểm danh: {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def get_stats(self, student_id: int, semester: Optional[int] = None, 
                  academic_year: Optional[str] = None) -> List[dict]:
        """Lấy thống kê điểm danh"""
        cursor = self.db.connection.cursor(dictionary=True)
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
    
    def create_session(self, class_id: int, session_date: str, 
                      session_time: str, session_number: int) -> Optional[int]:
        """Tạo buổi học"""
        cursor = self.db.connection.cursor()
        try:
            query = """
                INSERT INTO sessions (class_id, session_date, session_time, session_number)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (class_id, session_date, session_time, session_number))
            self.db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"✗ Lỗi tạo session: {e}")
            self.db.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def get_session_by_class(self, class_id: int) -> List[dict]:
        """Lấy các buổi học của lớp"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = "SELECT * FROM sessions WHERE class_id = %s ORDER BY session_date DESC"
            cursor.execute(query, (class_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
