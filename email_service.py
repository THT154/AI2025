# email_service.py - Email Service cho Desktop App
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.EMAIL_SENDER
        self.sender_password = Config.EMAIL_PASSWORD
    
    def is_configured(self):
        """Kiểm tra email đã được cấu hình chưa"""
        return bool(self.sender_email and self.sender_password)
    
    def send_email(self, recipient_email, subject, body):
        """
        Gửi email
        
        Args:
            recipient_email: Email người nhận
            subject: Tiêu đề
            body: Nội dung
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_configured():
            return False, "Email chưa được cấu hình trong config.py"
        
        try:
            # Tạo message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Kết nối SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True, "Email đã được gửi"
            
        except Exception as e:
            return False, f"Lỗi gửi email: {str(e)}"
    
    def send_absence_notification(self, student_info, session_info, class_info):
        """
        Gửi thông báo vắng học
        
        Args:
            student_info: dict với keys: full_name, email
            session_info: dict với keys: session_date, session_time, session_number
            class_info: dict với keys: class_name, teacher_name, teacher_email
        
        Returns:
            tuple: (success, message)
        """
        subject = f"Thông báo vắng học - {class_info['class_name']}"
        
        session_time_vn = "Sáng" if session_info['session_time'] == 'morning' else "Chiều"
        
        body = f"""
Xin chào {student_info['full_name']},

Hệ thống điểm danh ghi nhận bạn đã vắng mặt tại buổi học:

📚 Môn học: {class_info['class_name']}
📅 Ngày học: {session_info['session_date']}
⏰ Buổi: {session_time_vn}
📍 Tiết: {session_info['session_number']}

Nếu bạn có lý do chính đáng, vui lòng liên hệ với giảng viên:
👨‍🏫 {class_info['teacher_name']}
📧 {class_info['teacher_email']}

Lưu ý: Việc vắng mặt quá nhiều có thể ảnh hưởng đến kết quả học tập của bạn.

---
Đây là email tự động từ Hệ thống điểm danh AI.
Vui lòng không trả lời email này.

Thời gian gửi: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        
        return self.send_email(student_info['email'], subject, body)
    
    def send_bulk_absence_notifications(self, absent_students, session_info, class_info, db):
        """
        Gửi email hàng loạt cho sinh viên vắng
        
        Args:
            absent_students: list các student_id vắng
            session_info: thông tin buổi học
            class_info: thông tin lớp học
            db: Database instance để log email
        
        Returns:
            dict: Thống kê gửi email
        """
        results = {
            'total': len(absent_students),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for student_id in absent_students:
            # Lấy thông tin sinh viên
            cursor = db.connection.cursor(dictionary=True)
            query = """
                SELECT u.full_name, u.email, s.student_code
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.student_id = %s
            """
            cursor.execute(query, (student_id,))
            student = cursor.fetchone()
            cursor.close()
            
            if not student:
                results['failed'] += 1
                results['errors'].append(f"Student ID {student_id} không tìm thấy")
                continue
            
            # Gửi email
            success, message = self.send_absence_notification(student, session_info, class_info)
            
            if success:
                results['sent'] += 1
                
                # Log email
                cursor = db.connection.cursor()
                try:
                    query = """
                        INSERT INTO email_logs (session_id, student_id, email_status)
                        VALUES (%s, %s, 'sent')
                    """
                    cursor.execute(query, (session_info['session_id'], student_id))
                    db.connection.commit()
                except:
                    pass
                finally:
                    cursor.close()
            else:
                results['failed'] += 1
                results['errors'].append(f"{student['full_name']}: {message}")
                
                # Log failed email
                cursor = db.connection.cursor()
                try:
                    query = """
                        INSERT INTO email_logs (session_id, student_id, email_status)
                        VALUES (%s, %s, 'failed')
                    """
                    cursor.execute(query, (session_info['session_id'], student_id))
                    db.connection.commit()
                except:
                    pass
                finally:
                    cursor.close()
        
        return results

# Global instance
email_service = EmailService()