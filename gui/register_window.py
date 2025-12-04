# gui/register_window.py - Màn hình đăng ký
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime

class RegisterWindow:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        
        self.root.title("Đăng ký tài khoản")
        self.root.geometry("500x750")
        self.root.resizable(False, False)
        
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Main container with scrollbar
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Header
        header = tk.Frame(scrollable_frame, bg='#667eea', height=100)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="📝 ĐĂNG KÝ TÀI KHOẢN",
            font=('Arial', 18, 'bold'),
            bg='#667eea',
            fg='white'
        ).pack(pady=20)
        
        # Form container
        form = tk.Frame(scrollable_frame, bg='white')
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Username
        tk.Label(form, text="Tên đăng nhập *", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.username_entry = tk.Entry(form, font=('Arial', 11), relief=tk.SOLID, borderwidth=1)
        self.username_entry.pack(fill=tk.X, ipady=6)
        
        # Email
        tk.Label(form, text="Email *", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.email_entry = tk.Entry(form, font=('Arial', 11), relief=tk.SOLID, borderwidth=1)
        self.email_entry.pack(fill=tk.X, ipady=6)
        
        # Password
        tk.Label(form, text="Mật khẩu *", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.password_entry = tk.Entry(form, font=('Arial', 11), show='•', 
                                      relief=tk.SOLID, borderwidth=1)
        self.password_entry.pack(fill=tk.X, ipady=6)
        
        # Confirm Password
        tk.Label(form, text="Xác nhận mật khẩu *", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.confirm_password_entry = tk.Entry(form, font=('Arial', 11), show='•', 
                                              relief=tk.SOLID, borderwidth=1)
        self.confirm_password_entry.pack(fill=tk.X, ipady=6)
        
        # Full Name
        tk.Label(form, text="Họ và tên *", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.fullname_entry = tk.Entry(form, font=('Arial', 11), relief=tk.SOLID, borderwidth=1)
        self.fullname_entry.pack(fill=tk.X, ipady=6)
        
        # Gender
        tk.Label(form, text="Giới tính", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.gender_var = tk.StringVar(value='male')
        gender_frame = tk.Frame(form, bg='white')
        gender_frame.pack(fill=tk.X)
        tk.Radiobutton(gender_frame, text='Nam', variable=self.gender_var, value='male',
                      font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(gender_frame, text='Nữ', variable=self.gender_var, value='female',
                      font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(gender_frame, text='Khác', variable=self.gender_var, value='other',
                      font=('Arial', 10), bg='white').pack(side=tk.LEFT)
        
        # Date of Birth
        tk.Label(form, text="Ngày sinh", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.dob_entry = DateEntry(form, font=('Arial', 11), date_pattern='yyyy-mm-dd',
                                  width=18, background='#667eea', foreground='white',
                                  borderwidth=1, year=2000)
        self.dob_entry.pack(anchor='w', ipady=4)
        
        # Role
        tk.Label(form, text="Vai trò *", font=('Arial', 10, 'bold'), 
                bg='white', fg='#333').pack(anchor='w', pady=(10, 2))
        self.role_var = tk.StringVar(value='student')
        role_frame = tk.Frame(form, bg='white')
        role_frame.pack(fill=tk.X)
        tk.Radiobutton(role_frame, text='👨‍🏫 Giáo viên', variable=self.role_var, 
                      value='teacher', font=('Arial', 10), bg='white',
                      command=self.toggle_student_fields).pack(side=tk.LEFT, padx=(0, 15))
        tk.Radiobutton(role_frame, text='🔍 Kiểm duyệt', variable=self.role_var, 
                      value='moderator', font=('Arial', 10), bg='white',
                      command=self.toggle_student_fields).pack(side=tk.LEFT, padx=(0, 15))
        tk.Radiobutton(role_frame, text='🎓 Sinh viên', variable=self.role_var, 
                      value='student', font=('Arial', 10), bg='white',
                      command=self.toggle_student_fields).pack(side=tk.LEFT)
        
        # Student-specific fields
        self.student_frame = tk.Frame(form, bg='#f0f0f0')
        self.student_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(self.student_frame, text="━━━ Thông tin sinh viên ━━━", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#667eea').pack(pady=10)
        
        # Student Code
        tk.Label(self.student_frame, text="Mã sinh viên *", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0', fg='#333').pack(anchor='w', padx=10)
        self.student_code_entry = tk.Entry(self.student_frame, font=('Arial', 11), 
                                          relief=tk.SOLID, borderwidth=1)
        self.student_code_entry.pack(fill=tk.X, padx=10, pady=(2, 10), ipady=6)
        
        # Major
        tk.Label(self.student_frame, text="Ngành học", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0', fg='#333').pack(anchor='w', padx=10)
        self.major_entry = tk.Entry(self.student_frame, font=('Arial', 11), 
                                   relief=tk.SOLID, borderwidth=1)
        self.major_entry.pack(fill=tk.X, padx=10, pady=(2, 10), ipady=6)
        
        # Enrollment Year
        tk.Label(self.student_frame, text="Khóa học", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0', fg='#333').pack(anchor='w', padx=10)
        self.enrollment_year_entry = tk.Entry(self.student_frame, font=('Arial', 11), 
                                             relief=tk.SOLID, borderwidth=1)
        self.enrollment_year_entry.insert(0, str(datetime.now().year))
        self.enrollment_year_entry.pack(fill=tk.X, padx=10, pady=(2, 10), ipady=6)
        
        # Buttons
        btn_frame = tk.Frame(form, bg='white')
        btn_frame.pack(fill=tk.X, pady=20)
        
        register_btn = tk.Button(
            btn_frame,
            text="✓ Đăng ký",
            font=('Arial', 12, 'bold'),
            bg='#667eea',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            command=self.register
        )
        register_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 5))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="✗ Hủy",
            font=('Arial', 12, 'bold'),
            bg='#ccc',
            fg='#333',
            cursor='hand2',
            relief=tk.FLAT,
            command=self.root.destroy
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(5, 0))
    
    def toggle_student_fields(self):
        """Hiển thị/ẩn các trường sinh viên"""
        if self.role_var.get() == 'student':
            self.student_frame.pack(fill=tk.X, pady=(15, 0))
        else:
            self.student_frame.pack_forget()
    
    def register(self):
        """Xử lý đăng ký"""
        # Get common fields
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        full_name = self.fullname_entry.get().strip()
        gender = self.gender_var.get()
        date_of_birth = self.dob_entry.get_date().strftime('%Y-%m-%d')
        role = self.role_var.get()
        
        # Validation
        if not all([username, email, password, full_name]):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ các trường bắt buộc (*)")
            return
        
        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return
        
        # Create user
        user_id = self.db.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            full_name=full_name,
            gender=gender,
            date_of_birth=date_of_birth
        )
        
        if not user_id:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc email đã tồn tại!")
            return
        
        # If student, create student profile
        if role == 'student':
            student_code = self.student_code_entry.get().strip()
            major = self.major_entry.get().strip()
            enrollment_year = self.enrollment_year_entry.get().strip()
            
            if not student_code:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã sinh viên!")
                return
            
            student_id = self.db.create_student(
                user_id=user_id,
                student_code=student_code,
                major=major if major else None,
                enrollment_year=int(enrollment_year) if enrollment_year else None
            )
            
            if not student_id:
                messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại!")
                return
        
        messagebox.showinfo("Thành công", "Đăng ký thành công! Bạn có thể đăng nhập ngay.")
        self.root.destroy()