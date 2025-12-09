# app/example_integration.py
"""
Ví dụ tích hợp kiến trúc mới vào code hiện tại

File này demo cách sử dụng repositories, services, và controllers
trong ứng dụng thực tế.
"""

from models.database import Database
from app.repositories import (
    UserRepository, StudentRepository, TeacherRepository,
    ClassRepository, AttendanceRepository
)
from app.services import AuthService, StudentService, TeacherService
from app.controllers import AuthController, StudentController, TeacherController


class AppContainer:
    """
    Dependency Injection Container
    Khởi tạo và quản lý tất cả dependencies
    """
    
    def __init__(self, db: Database):
        self.db = db
        
        # Initialize Repositories
        self.user_repo = UserRepository(db)
        self.student_repo = StudentRepository(db)
        self.teacher_repo = TeacherRepository(db)
        self.class_repo = ClassRepository(db)
        self.attendance_repo = AttendanceRepository(db)
        
        # Initialize Services
        self.auth_service = AuthService(
            self.user_repo,
            self.student_repo,
            self.teacher_repo
        )
        
        self.student_service = StudentService(
            self.student_repo,
            self.class_repo,
            self.attendance_repo
        )
        
        self.teacher_service = TeacherService(
            self.teacher_repo,
            self.class_repo,
            self.student_repo,
            self.attendance_repo
        )
        
        # Initialize Controllers
        self.auth_controller = AuthController(self.auth_service)
        self.student_controller = StudentController(self.student_service)
        self.teacher_controller = TeacherController(self.teacher_service)


# ============================================================================
# EXAMPLE 1: Sử dụng trong main.py
# ============================================================================

def example_main_integration():
    """
    Ví dụ tích hợp vào main.py
    """
    # Khởi tạo database
    db = Database(host='localhost', user='root', password='', database='attendance_db')
    db.create_database()
    db.connect()
    db.create_tables()
    
    # Khởi tạo container
    container = AppContainer(db)
    
    # Bây giờ có thể truyền controllers vào views
    # from views.login_window import LoginWindow
    # login_window = LoginWindow(root, container.auth_controller)
    
    return container


# ============================================================================
# EXAMPLE 2: Refactor LoginWindow
# ============================================================================

def example_login_window_refactor():
    """
    Ví dụ refactor LoginWindow để sử dụng AuthController
    
    TRƯỚC (trong views/login_window.py):
    ```python
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user = self.db.login(username, password)  # ❌ Direct DB call
        
        if user:
            messagebox.showinfo("Thành công", "Đăng nhập thành công")
            self.on_login_success(user)
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")
    ```
    
    SAU (sử dụng controller):
    ```python
    def __init__(self, root, auth_controller):
        self.root = root
        self.auth_controller = auth_controller  # ✅ Inject controller
        # ... rest of init
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        result = self.auth_controller.login(username, password)  # ✅ Use controller
        
        if result['success']:
            user_data = result['data']
            messagebox.showinfo("Thành công", "Đăng nhập thành công")
            self.on_login_success(user_data['user'])
        else:
            messagebox.showerror("Lỗi", result['error'])
    ```
    """
    pass


# ============================================================================
# EXAMPLE 3: Refactor StudentWindow
# ============================================================================

def example_student_window_refactor():
    """
    Ví dụ refactor StudentWindow để sử dụng StudentController
    
    TRƯỚC:
    ```python
    def load_my_classes(self):
        cursor = self.db.connection.cursor(dictionary=True)  # ❌ Direct SQL
        cursor.execute('''
            SELECT c.*, u.full_name as teacher_name
            FROM class_enrollments ce
            JOIN classes c ON ce.class_id = c.class_id
            JOIN users u ON c.teacher_id = u.user_id
            WHERE ce.student_id = %s
        ''', (self.student_id,))
        classes = cursor.fetchall()
        cursor.close()
        
        # Display classes...
    ```
    
    SAU:
    ```python
    def __init__(self, root, user, student_controller):
        self.root = root
        self.user = user
        self.student_controller = student_controller  # ✅ Inject controller
        # ... rest of init
    
    def load_my_classes(self):
        result = self.student_controller.get_enrolled_classes(self.student_id)  # ✅ Use controller
        
        if result['success']:
            classes = result['data']
            # Display classes...
        else:
            messagebox.showerror("Lỗi", result['error'])
    ```
    """
    pass


# ============================================================================
# EXAMPLE 4: Refactor TeacherWindow
# ============================================================================

def example_teacher_window_refactor():
    """
    Ví dụ refactor TeacherWindow để sử dụng TeacherController
    
    TRƯỚC:
    ```python
    def create_class(self):
        # Get form data...
        
        class_id = self.db.create_class(  # ❌ Direct DB call
            class_code, class_name, self.user['user_id'],
            total_sessions, credits, max_students,
            semester, academic_year, schedule
        )
        
        if class_id:
            messagebox.showinfo("Thành công", "Tạo lớp thành công")
        else:
            messagebox.showerror("Lỗi", "Không thể tạo lớp")
    ```
    
    SAU:
    ```python
    def __init__(self, root, user, teacher_controller):
        self.root = root
        self.user = user
        self.teacher_controller = teacher_controller  # ✅ Inject controller
        # ... rest of init
    
    def create_class(self):
        # Get form data...
        
        result = self.teacher_controller.create_class(  # ✅ Use controller
            self.user['user_id'], class_code, class_name,
            total_sessions, credits, max_students,
            semester, academic_year, schedule
        )
        
        if result['success']:
            messagebox.showinfo("Thành công", f"Tạo lớp thành công! ID: {result['class_id']}")
            self.load_my_classes()
        else:
            messagebox.showerror("Lỗi", result['error'])
    ```
    """
    pass


# ============================================================================
# EXAMPLE 5: Xử lý điểm danh với controller
# ============================================================================

def example_attendance_with_controller():
    """
    Ví dụ xử lý điểm danh sử dụng controller
    
    ```python
    def mark_attendance(self, session_id, student_id, confidence_score):
        result = self.teacher_controller.mark_attendance(
            session_id=session_id,
            student_id=student_id,
            status='present',
            confidence_score=confidence_score
        )
        
        if result['success']:
            print(f"✓ Điểm danh thành công: {student_id}")
            return True
        else:
            print(f"✗ Lỗi điểm danh: {result['error']}")
            return False
    
    def get_attendance_list(self, session_id):
        result = self.teacher_controller.get_session_attendance(session_id)
        
        if result['success']:
            attendance_list = result['data']
            
            # Display in treeview
            for att in attendance_list:
                self.attendance_tree.insert('', 'end', values=(
                    att['student_code'],
                    att['full_name'],
                    att['status'],
                    att['check_in_time'],
                    f"{att['confidence_score']:.2f}" if att['confidence_score'] else 'N/A'
                ))
        else:
            messagebox.showerror("Lỗi", result['error'])
    ```
    """
    pass


# ============================================================================
# EXAMPLE 6: Xử lý đăng ký lớp với validation
# ============================================================================

def example_class_registration():
    """
    Ví dụ đăng ký lớp với validation đầy đủ
    
    ```python
    def register_for_class(self, class_id):
        # Validate registration period
        window = self.db.get_latest_registration_window()
        if not window:
            messagebox.showerror("Lỗi", "Chưa có khung giờ đăng ký")
            return
        
        now = datetime.now()
        if not (window['start_datetime'] <= now <= window['end_datetime']):
            messagebox.showerror("Lỗi", "Ngoài khung giờ đăng ký")
            return
        
        # Register through controller
        result = self.student_controller.register_class(
            student_id=self.student_id,
            class_id=class_id
        )
        
        if result['success']:
            messagebox.showinfo("Thành công", result['message'])
            self.load_my_classes()
            self.load_available_classes()
        else:
            messagebox.showerror("Lỗi", result['error'])
    ```
    """
    pass


# ============================================================================
# EXAMPLE 7: Thống kê điểm danh
# ============================================================================

def example_attendance_statistics():
    """
    Ví dụ hiển thị thống kê điểm danh
    
    ```python
    def show_attendance_stats(self, class_id=None):
        result = self.student_controller.get_attendance_statistics(
            student_id=self.student_id,
            class_id=class_id
        )
        
        if result['success']:
            stats = result['data']
            
            # Display statistics
            stats_text = f'''
            Tổng số buổi: {stats['total']}
            Có mặt: {stats['present']} ({stats['percentage']:.1f}%)
            Vắng: {stats['absent']}
            Muộn: {stats['late']}
            '''
            
            messagebox.showinfo("Thống kê điểm danh", stats_text)
        else:
            messagebox.showerror("Lỗi", result['error'])
    ```
    """
    pass


# ============================================================================
# MAIN - Demo usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("VÍ DỤ TÍCH HỢP KIẾN TRÚC MỚI")
    print("=" * 80)
    
    # Initialize
    db = Database(host='localhost', user='root', password='', database='attendance_db')
    db.connect()
    
    container = AppContainer(db)
    
    print("\n✓ Đã khởi tạo AppContainer với tất cả dependencies")
    print("\nCác controllers có sẵn:")
    print("  - container.auth_controller")
    print("  - container.student_controller")
    print("  - container.teacher_controller")
    
    print("\n" + "=" * 80)
    print("DEMO: Đăng nhập")
    print("=" * 80)
    
    # Demo login
    result = container.auth_controller.login('sv001', 'SV001')
    
    if result['success']:
        user = result['data']['user']
        print(f"✓ Đăng nhập thành công!")
        print(f"  User: {user['full_name']}")
        print(f"  Role: {user['role']}")
        print(f"  First login: {result['data']['first_login']}")
    else:
        print(f"✗ Đăng nhập thất bại: {result['error']}")
    
    print("\n" + "=" * 80)
    print("Xem file này để biết thêm ví dụ tích hợp!")
    print("=" * 80)
    
    db.disconnect()
