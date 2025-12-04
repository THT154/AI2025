# main.py - File chính để chạy ứng dụng Desktop
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from config import Config
from gui.login_window import LoginWindow

class AttendanceApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Ẩn cửa sổ chính ban đầu
        
        # Khởi tạo database
        print("🚀 Đang khởi động ứng dụng...")
        self.db = Database(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        # Tạo database và kết nối
        self.db.create_database()
        
        if not self.db.connect():
            messagebox.showerror(
                "Lỗi kết nối",
                "Không thể kết nối đến MySQL!\n\n"
                "Vui lòng:\n"
                "1. Mở XAMPP\n"
                "2. Start MySQL\n"
                "3. Thử lại"
            )
            sys.exit(1)
        
        # Tạo bảng
        self.db.create_tables()
        
        # Kiểm tra và tạo dữ liệu mẫu nếu cần
        self.check_and_create_sample_data()
        
        self.current_user = None
        self.current_window = None
        
        # Hiển thị login
        self.show_login()
    
    def check_and_create_sample_data(self):
        """Kiểm tra và tạo dữ liệu mẫu nếu database trống"""
        try:
            cursor = self.db.connection.cursor()
            
            # Kiểm tra xem đã có user nào chưa
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            cursor.close()
            
            # Nếu chưa có user nào, tạo dữ liệu mẫu
            if user_count == 0:
                print("\n📦 Database trống, đang tạo dữ liệu mẫu...")
                
                # Import và chạy create_sample_data
                from create_sample_data import create_sample_data
                create_sample_data()
                
                print("\n✅ Đã tạo dữ liệu mẫu thành công!")
                print("\n🔑 Tài khoản mặc định:")
                print("   • Moderator: admin / admin123")
                print("   • Giáo viên: gv001 / GV001")
                print("   • Sinh viên: 21it001 / 21IT001")
                print("\n💡 Xem file README.txt để biết thêm chi tiết\n")
                
                messagebox.showinfo(
                    "Khởi tạo thành công",
                    "Đã tạo dữ liệu mẫu!\n\n"
                    "Tài khoản mặc định:\n"
                    "• Moderator: admin / admin123\n"
                    "• Giáo viên: gv001 / GV001\n"
                    "• Sinh viên: 21it001 / 21IT001\n\n"
                    "Xem README.txt để biết thêm chi tiết"
                )
        except Exception as e:
            print(f"⚠️ Lỗi khi kiểm tra/tạo dữ liệu mẫu: {e}")
            # Không dừng ứng dụng, chỉ cảnh báo
        
    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        login_root = tk.Toplevel(self.root)
        LoginWindow(login_root, self.db, self.on_login_success)
    
    def on_login_success(self, user):
        """Callback khi đăng nhập thành công"""
        self.current_user = user
        role = user['role']
        
        print(f"✓ Đăng nhập thành công: {user['full_name']} ({role})")
        
        # Mở dashboard tương ứng với role
        if role == 'teacher':
            self.open_teacher_dashboard()
        elif role == 'moderator':
            self.open_moderator_dashboard()
        elif role == 'student':
            self.open_student_dashboard()
    
    def open_teacher_dashboard(self):
        """Mở dashboard giáo viên"""
        from gui.teacher_window import TeacherWindow
        
        if self.current_window:
            self.current_window.destroy()
        
        dashboard_root = tk.Toplevel(self.root)
        self.current_window = dashboard_root
        TeacherWindow(dashboard_root, self.db, self.current_user, self.logout)
    
    def open_moderator_dashboard(self):
        """Mở dashboard kiểm duyệt"""
        from gui.moderator_window import ModeratorWindow
        
        if self.current_window:
            self.current_window.destroy()
        
        dashboard_root = tk.Toplevel(self.root)
        self.current_window = dashboard_root
        ModeratorWindow(dashboard_root, self.db, self.current_user, self.logout)
    
    def open_student_dashboard(self):
        """Mở dashboard sinh viên"""
        from gui.student_window import StudentWindow
        
        if self.current_window:
            self.current_window.destroy()
        
        dashboard_root = tk.Toplevel(self.root)
        self.current_window = dashboard_root
        StudentWindow(dashboard_root, self.db, self.current_user, self.logout)
    
    def logout(self):
        """Đăng xuất"""
        if self.current_window:
            self.current_window.destroy()
            self.current_window = None
        
        self.current_user = None
        self.show_login()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()
        
        # Đóng kết nối database khi thoát
        self.db.disconnect()

def main():
    """Entry point của ứng dụng"""
    try:
        app = AttendanceApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")
        messagebox.showerror("Lỗi", f"Không thể khởi động ứng dụng:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()