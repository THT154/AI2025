# gui/login_window.py - Màn hình đăng nhập (Full, nút hiển thị đầy đủ)
import tkinter as tk
from tkinter import messagebox
from config import Config

class LoginWindow:
    def __init__(self, root, db, on_login_success):
        self.root = root
        self.db = db
        self.on_login_success = on_login_success

        self.root.title(f"{Config.WINDOW_TITLE} - Đăng nhập")
        self.root.geometry("400x550")  # tăng chiều cao để nút hiển thị đầy đủ
        self.root.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Căn giữa cửa sổ với kích thước tối thiểu"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width < 400:
            width = 400
        if height < 550:
            height = 550
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#4f5bd5')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_frame, bg='#4f5bd5')
        header_frame.pack(pady=20)  # giảm padding để tiết kiệm chỗ
        tk.Label(header_frame, text="🎓", font=('Arial', 48), bg='#4f5bd5', fg='white').pack()
        tk.Label(header_frame, text="HỆ THỐNG ĐIỂM DANH AI", font=('Arial', 20, 'bold'), bg='#4f5bd5', fg='white').pack(pady=5)
        tk.Label(header_frame, text="Đăng nhập tài khoản được cấp", font=('Arial', 12), bg='#4f5bd5', fg='white').pack()

        # Form frame
        form_frame = tk.Frame(main_frame, bg='white', padx=30, pady=30)
        form_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)

        # Username
        tk.Label(form_frame, text="👤 Tên đăng nhập", font=('Arial', 11, 'bold'), bg='white', fg='#333').pack(anchor='w', pady=(0,5))
        self.username_entry = tk.Entry(form_frame, font=('Arial', 12), relief=tk.SOLID, borderwidth=1)
        self.username_entry.pack(fill=tk.X, ipady=8)

        # Password
        tk.Label(form_frame, text="🔒 Mật khẩu", font=('Arial', 11, 'bold'), bg='white', fg='#333').pack(anchor='w', pady=(15,5))
        self.password_entry = tk.Entry(form_frame, font=('Arial', 12), show='•', relief=tk.SOLID, borderwidth=1)
        self.password_entry.pack(fill=tk.X, ipady=8)
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Login button
        login_btn = tk.Button(
            form_frame,
            text="🚀 Đăng nhập",
            font=('Arial', 14, 'bold'),  # font lớn để đẹp
            bg='#4f5bd5',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            command=self.login
        )
        login_btn.pack(fill=tk.X, pady=(30,20), ipady=15)  # ipady tăng để chữ không bị cắt
        login_btn.bind('<Enter>', lambda e: login_btn.config(bg='#3e4db8'))
        login_btn.bind('<Leave>', lambda e: login_btn.config(bg='#4f5bd5'))

        # Version
        tk.Label(form_frame, text="v1.0.0 - Face Recognition System", font=('Arial', 8), bg='white', fg='#999').pack(side=tk.BOTTOM, pady=(10,0))

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        user = self.db.login(username, password)
        if user:
            messagebox.showinfo("Thành công", f"Chào mừng {user['full_name']}!")
            self.root.withdraw()
            self.on_login_success(user)
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")

    def show(self):
        self.root.deiconify()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()
