# models/validation.py - Validation logic cho business rules
import json
from typing import Tuple, List, Optional

class ValidationRules:
    """Các quy tắc validation cho hệ thống"""
    
    def __init__(self, db):
        self.db = db
    
    def check_schedule_conflict(self, student_id: int, new_class_id: int) -> Tuple[bool, str]:
        """
        Kiểm tra trùng lịch học
        Returns: (is_valid, message)
        """
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            # Lấy lịch của lớp mới
            cursor.execute("""
                SELECT schedule, class_name, class_code 
                FROM classes 
                WHERE class_id = %s
            """, (new_class_id,))
            new_class = cursor.fetchone()
            
            if not new_class or not new_class['schedule']:
                return True, "OK"
            
            new_schedule = json.loads(new_class['schedule'])
            
            # Lấy tất cả lớp đã đăng ký của sinh viên
            cursor.execute("""
                SELECT c.class_id, c.class_name, c.class_code, c.schedule
                FROM class_enrollments ce
                JOIN classes c ON ce.class_id = c.class_id
                WHERE ce.student_id = %s 
                AND ce.status = 'enrolled'
                AND c.status = 'approved'
            """, (student_id,))
            
            enrolled_classes = cursor.fetchall()
            
            # Kiểm tra từng lớp đã đăng ký
            for enrolled_class in enrolled_classes:
                if not enrolled_class['schedule']:
                    continue
                
                enrolled_schedule = json.loads(enrolled_class['schedule'])
                
                # So sánh lịch
                conflict = self._check_schedule_overlap(new_schedule, enrolled_schedule)
                if conflict:
                    return False, f"Trùng lịch với môn {enrolled_class['class_name']} ({enrolled_class['class_code']}) - {conflict}"
            
            return True, "OK"
            
        except Exception as e:
            print(f"✗ Lỗi kiểm tra trùng lịch: {e}")
            return False, f"Lỗi kiểm tra: {str(e)}"
        finally:
            cursor.close()
    
    def _check_schedule_overlap(self, schedule1: dict, schedule2: dict) -> Optional[str]:
        """
        Kiểm tra 2 lịch có trùng không
        schedule format: {
            "thu_2": [1, 2, 3],  # Thứ 2 tiết 1,2,3
            "thu_3": [4, 5]
        }
        Returns: Mô tả trùng lịch hoặc None
        """
        for day, periods1 in schedule1.items():
            if day in schedule2:
                periods2 = schedule2[day]
                # Kiểm tra có tiết nào trùng không
                overlap = set(periods1) & set(periods2)
                if overlap:
                    day_name = self._get_day_name(day)
                    periods_str = ", ".join(map(str, sorted(overlap)))
                    return f"{day_name} tiết {periods_str}"
        return None
    
    def _get_day_name(self, day_key: str) -> str:
        """Chuyển key thành tên thứ"""
        day_map = {
            'thu_2': 'Thứ 2',
            'thu_3': 'Thứ 3',
            'thu_4': 'Thứ 4',
            'thu_5': 'Thứ 5',
            'thu_6': 'Thứ 6',
            'thu_7': 'Thứ 7',
            'chu_nhat': 'Chủ nhật'
        }
        return day_map.get(day_key, day_key)
    
    def check_credit_limit(self, student_id: int, new_class_credits: int, 
                          semester: int, academic_year: str, max_credits: int = 24) -> Tuple[bool, str]:
        """
        Kiểm tra giới hạn tín chỉ (thường là 24 tín chỉ/học kỳ)
        """
        cursor = self.db.connection.cursor()
        try:
            cursor.execute("""
                SELECT SUM(c.credits) as total_credits
                FROM class_enrollments ce
                JOIN classes c ON ce.class_id = c.class_id
                WHERE ce.student_id = %s 
                AND ce.status = 'enrolled'
                AND c.status = 'approved'
                AND c.semester = %s
                AND c.academic_year = %s
            """, (student_id, semester, academic_year))
            
            result = cursor.fetchone()
            current_credits = result[0] if result[0] else 0
            total_credits = current_credits + new_class_credits
            
            if total_credits > max_credits:
                return False, f"Vượt quá giới hạn tín chỉ ({total_credits}/{max_credits})"
            
            return True, f"Tín chỉ hiện tại: {total_credits}/{max_credits}"
            
        except Exception as e:
            print(f"✗ Lỗi kiểm tra tín chỉ: {e}")
            return False, f"Lỗi kiểm tra: {str(e)}"
        finally:
            cursor.close()
    
    def check_duplicate_enrollment(self, student_id: int, class_id: int) -> Tuple[bool, str]:
        """Kiểm tra đã đăng ký lớp này chưa"""
        cursor = self.db.connection.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM class_enrollments
                WHERE student_id = %s AND class_id = %s AND status = 'enrolled'
            """, (student_id, class_id))
            
            count = cursor.fetchone()[0]
            if count > 0:
                return False, "Bạn đã đăng ký lớp này rồi"
            return True, "OK"
            
        except Exception as e:
            return False, f"Lỗi kiểm tra: {str(e)}"
        finally:
            cursor.close()
    
    def check_registration_period(self) -> Tuple[bool, str]:
        """Kiểm tra có trong khung giờ đăng ký không"""
        from datetime import datetime
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM registration_period
                ORDER BY start_datetime DESC
                LIMIT 1
            """)
            period = cursor.fetchone()
            
            if not period:
                return False, "Chưa có khung giờ đăng ký nào được thiết lập"
            
            now = datetime.now()
            start = period['start_datetime']
            end = period['end_datetime']
            
            if now < start:
                return False, f"Chưa đến thời gian đăng ký (Bắt đầu: {start.strftime('%d/%m/%Y %H:%M')})"
            
            if now > end:
                return False, f"Đã hết thời gian đăng ký (Kết thúc: {end.strftime('%d/%m/%Y %H:%M')})"
            
            return True, "Trong thời gian đăng ký"
            
        except Exception as e:
            return False, f"Lỗi kiểm tra: {str(e)}"
        finally:
            cursor.close()
    
    def check_teacher_schedule_conflict(self, teacher_id: int, new_schedule: dict, 
                                       semester: int, academic_year: str,
                                       exclude_class_id: Optional[int] = None) -> Tuple[bool, str]:
        """Kiểm tra giảng viên có bị trùng lịch dạy không"""
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            query = """
                SELECT class_id, class_name, class_code, schedule
                FROM classes
                WHERE teacher_id = %s 
                AND semester = %s
                AND academic_year = %s
                AND status != 'rejected'
            """
            params = [teacher_id, semester, academic_year]
            
            if exclude_class_id:
                query += " AND class_id != %s"
                params.append(exclude_class_id)
            
            cursor.execute(query, tuple(params))
            existing_classes = cursor.fetchall()
            
            for existing_class in existing_classes:
                if not existing_class['schedule']:
                    continue
                
                existing_schedule = json.loads(existing_class['schedule'])
                conflict = self._check_schedule_overlap(new_schedule, existing_schedule)
                
                if conflict:
                    return False, f"Giảng viên bị trùng lịch với lớp {existing_class['class_name']} ({existing_class['class_code']}) - {conflict}"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Lỗi kiểm tra: {str(e)}"
        finally:
            cursor.close()
    
    def validate_class_creation(self, class_code: str, teacher_id: int, 
                               total_sessions: int, credits: int, max_students: int,
                               schedule: dict, semester: int, academic_year: str) -> Tuple[bool, str]:
        """Validate toàn bộ khi tạo lớp"""
        
        # 1. Kiểm tra mã lớp trùng
        cursor = self.db.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM classes WHERE class_code = %s", (class_code,))
            if cursor.fetchone()[0] > 0:
                return False, "Mã lớp đã tồn tại"
        finally:
            cursor.close()
        
        # 2. Kiểm tra số tiết hợp lệ
        if total_sessions < 1 or total_sessions > 60:
            return False, "Số tiết không hợp lệ (1-60)"
        
        # 3. Kiểm tra tín chỉ hợp lệ
        if credits < 1 or credits > 5:
            return False, "Số tín chỉ không hợp lệ (1-5)"
        
        # 4. Kiểm tra sĩ số
        if max_students < 1 or max_students > 200:
            return False, "Sĩ số không hợp lệ (1-200)"
        
        # 5. Kiểm tra lịch giảng viên
        if schedule:
            is_valid, message = self.check_teacher_schedule_conflict(
                teacher_id, schedule, semester, academic_year
            )
            if not is_valid:
                return False, message
        
        return True, "OK"
