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
        
        # Xử lý đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
            # Kiểm tra first_login
            if user.get('first_login', False):
                # Bắt buộc đổi mật khẩu lần đầu
                self.show_change_password_dialog(user)
            else:
                # Đăng nhập thẳng không hiện bảng chào mừng
                self.root.withdraw()
                self.on_login_success(user)
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")

    def show_change_password_dialog(self, user):
        """Dialog bắt buộc đổi mật khẩu lần đầu"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Đổi mật khẩu lần đầu")
        dialog.geometry("600x650")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Không cho đóng dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Header
        header_frame = tk.Frame(dialog, bg='#ff9800', height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="⚠️ BẮT BUỘC ĐỔI MẬT KHẨU",
            font=('Arial', 18, 'bold'),
            bg='#ff9800',
            fg='white'
        ).pack(pady=30)
        
        # Info frame
        info_frame = tk.Frame(dialog, bg='#fff3e0')
        info_frame.pack(fill=tk.X, padx=25, pady=15)
        
        tk.Label(
            info_frame,
            text=f"Xin chào {user['full_name']}!",
            bg='#fff3e0',
            font=('Arial', 12, 'bold'),
            fg='#e65100'
        ).pack(anchor='w', pady=(10,5))
        
        info_text = """Đây là lần đăng nhập đầu tiên hoặc mật khẩu đã được reset.
Vì lý do bảo mật, bạn phải đổi mật khẩu mới trước khi tiếp tục."""
        
        tk.Label(
            info_frame,
            text=info_text,
            bg='#fff3e0',
            justify='left',
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0,10))
        
        # Yêu cầu mật khẩu
        requirements_text = """Mật khẩu mới phải:
  • Khác với mật khẩu mặc định
  • Độ dài tối thiểu 6 ký tự
  • Không được để trống"""
        
        tk.Label(
            info_frame,
            text=requirements_text,
            bg='#fff3e0',
            justify='left',
            font=('Arial', 9),
            fg='#555'
        ).pack(anchor='w', pady=(0,10))
        
        # Form frame
        form_frame = tk.Frame(dialog, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        # Mật khẩu hiện tại
        tk.Label(form_frame, text="🔒 Mật khẩu hiện tại:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5,8))
        current_password_entry = tk.Entry(form_frame, font=('Arial', 12), show='•', relief=tk.SOLID, borderwidth=1)
        current_password_entry.pack(fill=tk.X, ipady=10)
        
        # Mật khẩu mới
        tk.Label(form_frame, text="🔑 Mật khẩu mới:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(20,8))
        new_password_entry = tk.Entry(form_frame, font=('Arial', 12), show='•', relief=tk.SOLID, borderwidth=1)
        new_password_entry.pack(fill=tk.X, ipady=10)
        
        # Xác nhận mật khẩu mới
        tk.Label(form_frame, text="✅ Xác nhận mật khẩu mới:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(20,8))
        confirm_password_entry = tk.Entry(form_frame, font=('Arial', 12), show='•', relief=tk.SOLID, borderwidth=1)
        confirm_password_entry.pack(fill=tk.X, ipady=10)
        
        def change_password():
            current_pwd = current_password_entry.get().strip()
            new_pwd = new_password_entry.get().strip()
            confirm_pwd = confirm_password_entry.get().strip()
            
            # Validation
            if not current_pwd or not new_pwd or not confirm_pwd:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return
            
            # Kiểm tra mật khẩu hiện tại
            from models.user import User
            if not User.verify_password(current_pwd, user['password_hash']):
                messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng!")
                return
            
            # Kiểm tra mật khẩu mới khác mật khẩu cũ
            if current_pwd == new_pwd:
                messagebox.showerror("Lỗi", "Mật khẩu mới phải khác mật khẩu hiện tại!")
                return
            
            # Kiểm tra độ dài
            if len(new_pwd) < 6:
                messagebox.showerror("Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự!")
                return
            
            # Kiểm tra khớp
            if new_pwd != confirm_pwd:
                messagebox.showerror("Lỗi", "Mật khẩu mới và xác nhận không khớp!")
                return
            
            # Đổi mật khẩu
            try:
                user_model = User(self.db)
                if user_model.reset_password(user['user_id'], new_pwd):
                    # Đặt first_login = FALSE
                    cursor = self.db.connection.cursor()
                    try:
                        cursor.execute("UPDATE users SET first_login = FALSE WHERE user_id = %s", (user['user_id'],))
                        self.db.connection.commit()
                    finally:
                        cursor.close()
                    
                    messagebox.showinfo("Thành công", "Đã đổi mật khẩu thành công!\n\nVui lòng đăng nhập lại với mật khẩu mới.")
                    dialog.destroy()
                    # Không tự động đăng nhập, yêu cầu đăng nhập lại
                    self.username_entry.delete(0, tk.END)
                    self.password_entry.delete(0, tk.END)
                    self.username_entry.focus()
                else:
                    messagebox.showerror("Lỗi", "Không thể đổi mật khẩu!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi đổi mật khẩu:\n{str(e)}")
        
        # Button
        tk.Button(
            form_frame,
            text="🔄 Đổi mật khẩu",
            font=('Arial', 13, 'bold'),
            bg='#ff9800',
            fg='white',
            cursor='hand2',
            command=change_password,
            relief=tk.FLAT,
            activebackground='#f57c00',
            activeforeground='white'
        ).pack(fill=tk.X, pady=(30,10), ipady=14)
        
        # Focus vào ô đầu tiên
        current_password_entry.focus()

    def show(self):
        self.root.deiconify()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()

    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ login"""
        if messagebox.askyesno("Xác nhận thoát", "Bạn có chắc muốn thoát ứng dụng?"):
            self.root.destroy()
            import sys
            sys.exit(0)
