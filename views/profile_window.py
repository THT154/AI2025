# gui/profile_window.py - Trang thông tin cá nhân
import tkinter as tk
from tkinter import messagebox

class ProfileWindow:
    def __init__(self, parent, user):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Thông tin cá nhân")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        self.user = user
        
        self.center_window()
        self.create_widgets()
    
    def center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.dialog, bg='#667eea', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="👤",
            font=('Arial', 36),
            bg='#667eea',
            fg='white'
        ).pack(pady=(20, 0))
        
        tk.Label(
            header,
            text=self.user['full_name'],
            font=('Arial', 16, 'bold'),
            bg='#667eea',
            fg='white'
        ).pack()
        
        # Info frame
        info_frame = tk.Frame(self.dialog, bg='white', padx=30, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Role badge
        role_colors = {
            'teacher': '#667eea',
            'moderator': '#f39c12',
            'student': '#27ae60'
        }
        
        role_names = {
            'teacher': '👨‍🏫 Giáo viên',
            'moderator': '🔍 Kiểm duyệt',
            'student': '🎓 Sinh viên'
        }
        
        role_badge = tk.Label(
            info_frame,
            text=role_names.get(self.user['role'], self.user['role']),
            font=('Arial', 12, 'bold'),
            bg=role_colors.get(self.user['role'], '#667eea'),
            fg='white',
            padx=15,
            pady=5
        )
        role_badge.pack(pady=10)
        
        # Info fields
        fields = [
            ('👤 Tên đăng nhập', self.user.get('username', 'N/A')),
            ('📧 Email', self.user.get('email', 'N/A')),
            ('🎭 Vai trò', role_names.get(self.user['role'], self.user['role'])),
            ('👥 Giới tính', self.format_gender(self.user.get('gender'))),
            ('📅 Ngày sinh', self.format_date(self.user.get('date_of_birth'))),
            ('🕐 Ngày tạo', self.format_datetime(self.user.get('created_at')))
        ]
        
        for label, value in fields:
            self.create_info_row(info_frame, label, value)
        
        # Close button
        tk.Button(
            info_frame,
            text="✓ Đóng",
            font=('Arial', 12, 'bold'),
            bg='#667eea',
            fg='white',
            cursor='hand2',
            command=self.dialog.destroy,
            width=20
        ).pack(pady=20)
    
    def create_info_row(self, parent, label, value):
        """Tạo một dòng thông tin"""
        row = tk.Frame(parent, bg='white')
        row.pack(fill=tk.X, pady=8)
        
        tk.Label(
            row,
            text=label,
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#666',
            width=20,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            row,
            text=value,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            anchor='w'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def format_gender(self, gender):
        """Format giới tính"""
        gender_map = {
            'male': 'Nam',
            'female': 'Nữ',
            'other': 'Khác'
        }
        return gender_map.get(gender, 'Chưa cập nhật')
    
    def format_date(self, date_obj):
        """Format ngày"""
        if date_obj:
            if hasattr(date_obj, 'strftime'):
                return date_obj.strftime('%d/%m/%Y')
            return str(date_obj)
        return 'Chưa cập nhật'
    
    def format_datetime(self, datetime_obj):
        """Format ngày giờ"""
        if datetime_obj:
            if hasattr(datetime_obj, 'strftime'):
                return datetime_obj.strftime('%d/%m/%Y %H:%M')
            return str(datetime_obj)
        return 'Chưa cập nhật'