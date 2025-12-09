# Migration Guide - Chuyển đổi sang Kiến trúc v3.0

## Tổng quan

Hướng dẫn này giúp bạn chuyển đổi code hiện tại sang kiến trúc mới với Repository Pattern, Service Layer, và Controllers.

## Bước 1: Hiểu kiến trúc mới

### Trước (v2.0)
```
View → Database (Direct SQL)
```

### Sau (v3.0)
```
View → Controller → Service → Repository → Database
```

## Bước 2: Refactor từng View

### 2.1. LoginWindow

#### Trước
```python
class LoginWindow:
    def __init__(self, root, db, on_login_success):
        self.root = root
        self.db = db  # ❌ Direct database access
        self.on_login_success = on_login_success
        # ...
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # ❌ Direct SQL call
        user = self.db.login(username, password)
        
        if user:
            messagebox.showinfo("Thành công", "Đăng nhập thành công")
            self.on_login_success(user)
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")
```

#### Sau
```python
class LoginWindow:
    def __init__(self, root, auth_controller, on_login_success):
        self.root = root
        self.auth_controller = auth_controller  # ✅ Use controller
        self.on_login_success = on_login_success
        # ...
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # ✅ Call controller
        result = self.auth_controller.login(username, password)
        
        if result['success']:
            user_data = result['data']
            messagebox.showinfo("Thành công", "Đăng nhập thành công")
            self.on_login_success(user_data['user'])
        else:
            messagebox.showerror("Lỗi", result['error'])
```

### 2.2. StudentWindow

#### Trước
```python
class StudentWindow:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db  # ❌ Direct database access
        # ...
    
    def load_my_classes(self):
        # ❌ Direct SQL
        cursor = self.db.connection.cursor(dictionary=True)
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
    
    def register_class(self, class_id):
        # ❌ Direct SQL with business logic
        success, message = self.db.enroll_student(class_id, self.student_id)
        
        if success:
            messagebox.showinfo("Thành công", message)
            self.load_my_classes()
        else:
            messagebox.showerror("Lỗi", message)
```

#### Sau
```python
class StudentWindow:
    def __init__(self, root, user, student_controller):
        self.root = root
        self.user = user
        self.student_controller = student_controller  # ✅ Use controller
        # ...
    
    def load_my_classes(self):
        # ✅ Call controller
        result = self.student_controller.get_enrolled_classes(self.student_id)
        
        if result['success']:
            classes = result['data']
            # Display classes...
        else:
            messagebox.showerror("Lỗi", result['error'])
    
    def register_class(self, class_id):
        # ✅ Call controller
        result = self.student_controller.register_class(self.student_id, class_id)
        
        if result['success']:
            messagebox.showinfo("Thành công", result['message'])
            self.load_my_classes()
        else:
            messagebox.showerror("Lỗi", result['error'])
```

### 2.3. TeacherWindow

#### Trước
```python
class TeacherWindow:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db  # ❌ Direct database access
        # ...
    
    def create_class(self):
        # Get form data...
        
        # ❌ Direct SQL
        class_id = self.db.create_class(
            class_code, class_name, self.user['user_id'],
            total_sessions, credits, max_students,
            semester, academic_year, schedule
        )
        
        if class_id:
            messagebox.showinfo("Thành công", "Tạo lớp thành công")
            self.load_my_classes()
        else:
            messagebox.showerror("Lỗi", "Không thể tạo lớp")
    
    def mark_attendance(self, session_id, student_id, confidence):
        # ❌ Direct SQL
        success = self.db.mark_attendance(
            session_id, student_id, 'present', confidence
        )
        
        if success:
            print(f"✓ Điểm danh: {student_id}")
        else:
            print(f"✗ Lỗi điểm danh: {student_id}")
```

#### Sau
```python
class TeacherWindow:
    def __init__(self, root, user, teacher_controller):
        self.root = root
        self.user = user
        self.teacher_controller = teacher_controller  # ✅ Use controller
        # ...
    
    def create_class(self):
        # Get form data...
        
        # ✅ Call controller
        result = self.teacher_controller.create_class(
            self.user['user_id'], class_code, class_name,
            total_sessions, credits, max_students,
            semester, academic_year, schedule
        )
        
        if result['success']:
            messagebox.showinfo("Thành công", f"Tạo lớp thành công! ID: {result['class_id']}")
            self.load_my_classes()
        else:
            messagebox.showerror("Lỗi", result['error'])
    
    def mark_attendance(self, session_id, student_id, confidence):
        # ✅ Call controller
        result = self.teacher_controller.mark_attendance(
            session_id, student_id, 'present', confidence
        )
        
        if result['success']:
            print(f"✓ Điểm danh: {student_id}")
        else:
            print(f"✗ Lỗi điểm danh: {result['error']}")
```

## Bước 3: Update main.py

### Trước
```python
def main():
    db = Database()
    db.connect()
    
    root = tk.Tk()
    
    def on_login_success(user):
        if user['role'] == 'student':
            StudentWindow(root, user, db)  # ❌ Pass db
        elif user['role'] == 'teacher':
            TeacherWindow(root, user, db)  # ❌ Pass db
    
    LoginWindow(root, db, on_login_success)  # ❌ Pass db
    root.mainloop()
```

### Sau
```python
from app.example_integration import AppContainer

def main():
    db = Database()
    db.connect()
    
    # ✅ Initialize container with all dependencies
    container = AppContainer(db)
    
    root = tk.Tk()
    
    def on_login_success(user):
        if user['role'] == 'student':
            # ✅ Pass controller
            StudentWindow(root, user, container.student_controller)
        elif user['role'] == 'teacher':
            # ✅ Pass controller
            TeacherWindow(root, user, container.teacher_controller)
    
    # ✅ Pass controller
    LoginWindow(root, container.auth_controller, on_login_success)
    root.mainloop()
```

## Bước 4: Checklist Migration

### LoginWindow
- [ ] Thay `db` parameter bằng `auth_controller`
- [ ] Thay `self.db.login()` bằng `self.auth_controller.login()`
- [ ] Xử lý `result['success']` và `result['error']`
- [ ] Test đăng nhập với các trường hợp: success, wrong password, empty fields

### StudentWindow
- [ ] Thay `db` parameter bằng `student_controller`
- [ ] Refactor `load_my_classes()` → `student_controller.get_enrolled_classes()`
- [ ] Refactor `register_class()` → `student_controller.register_class()`
- [ ] Refactor `load_attendance()` → `student_controller.get_attendance_history()`
- [ ] Refactor `show_statistics()` → `student_controller.get_attendance_statistics()`
- [ ] Test tất cả chức năng

### TeacherWindow
- [ ] Thay `db` parameter bằng `teacher_controller`
- [ ] Refactor `create_class()` → `teacher_controller.create_class()`
- [ ] Refactor `load_my_classes()` → `teacher_controller.get_my_classes()`
- [ ] Refactor `mark_attendance()` → `teacher_controller.mark_attendance()`
- [ ] Refactor `get_class_students()` → `teacher_controller.get_class_students()`
- [ ] Test tất cả chức năng

### ModeratorWindow
- [ ] Tương tự như trên, sử dụng các controllers phù hợp
- [ ] Có thể cần tạo `ModeratorController` nếu có logic riêng

## Bước 5: Testing

### Manual Testing
1. Test đăng nhập với tất cả roles (student, teacher, moderator)
2. Test tạo lớp, đăng ký lớp
3. Test điểm danh
4. Test xem thống kê
5. Test upload/download documents

### Automated Testing (Optional)
```python
# tests/test_auth_service.py
import unittest
from unittest.mock import Mock
from app.services import AuthService

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.user_repo = Mock()
        self.student_repo = Mock()
        self.teacher_repo = Mock()
        self.service = AuthService(
            self.user_repo, 
            self.student_repo, 
            self.teacher_repo
        )
    
    def test_login_success(self):
        # Mock data
        self.user_repo.authenticate.return_value = {
            'user_id': 1,
            'username': 'sv001',
            'role': 'student',
            'full_name': 'Nguyễn Văn A'
        }
        self.student_repo.get_by_user_id.return_value = {
            'student_id': 1,
            'student_code': 'SV001'
        }
        
        # Test
        result = self.service.login('sv001', 'SV001')
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['user']['username'], 'sv001')
```

## Bước 6: Cleanup

Sau khi migration xong:

1. **Backup code cũ**
   ```bash
   git checkout -b backup-v2.0
   git commit -am "Backup v2.0 before migration"
   git checkout main
   ```

2. **Remove unused code**
   - Có thể giữ `models/database.py` cho backward compatibility
   - Hoặc mark deprecated và dần dần remove

3. **Update documentation**
   - Update README.txt
   - Update comments trong code
   - Tạo API documentation nếu cần

## Tips

1. **Migration từng phần**: Không cần migrate tất cả cùng lúc. Bắt đầu với LoginWindow, sau đó StudentWindow, rồi TeacherWindow.

2. **Backward compatibility**: Giữ `models/database.py` hoạt động song song với repositories trong quá trình migration.

3. **Testing**: Test kỹ sau mỗi bước migration.

4. **Git commits**: Commit sau mỗi view được migrate thành công.

5. **Code review**: Review code với team trước khi merge.

## Troubleshooting

### Lỗi: "AttributeError: 'Database' object has no attribute 'connection'"
**Nguyên nhân**: Chưa gọi `db.connect()`
**Giải pháp**: Đảm bảo gọi `db.connect()` trước khi khởi tạo repositories

### Lỗi: "TypeError: __init__() missing required positional argument"
**Nguyên nhân**: Quên truyền controller vào view
**Giải pháp**: Kiểm tra lại constructor của view, đảm bảo truyền đúng controller

### Lỗi: "KeyError: 'success'"
**Nguyên nhân**: Controller không trả về dict với key 'success'
**Giải pháp**: Kiểm tra controller method, đảm bảo luôn trả về `{'success': bool, ...}`

## Kết luận

Migration sang kiến trúc mới sẽ mất thời gian nhưng đáng giá:
- Code dễ maintain hơn
- Dễ test hơn
- Dễ mở rộng hơn
- Chuẩn production-ready

Hãy làm từng bước, test kỹ, và commit thường xuyên!
