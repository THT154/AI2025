# test_attendance.py - Test chức năng điểm danh
import tkinter as tk
from database import Database
from gui.teacher_window import TeacherWindow

def test_attendance():
    """Test chức năng điểm danh"""
    # Kết nối database
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("Không thể kết nối database!")
        return
    
    # Tạo user giáo viên test (nếu chưa có)
    cursor = db.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = 'teacher_test'")
    user = cursor.fetchone()
    
    if not user:
        user_id = db.create_user(
            username='teacher_test',
            email='teacher@test.com',
            password='123456',
            role='teacher',
            full_name='Giáo viên Test'
        )
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
    
    cursor.close()
    
    # Tạo cửa sổ
    root = tk.Tk()
    
    def logout():
        root.destroy()
    
    # Mở teacher window
    TeacherWindow(root, db, user, logout)
    
    root.mainloop()
    
    db.disconnect()

if __name__ == "__main__":
    test_attendance()
