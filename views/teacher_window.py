# teacher_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Tuple, List, Any, Optional
import os
import shutil
from datetime import datetime
import json
import cv2
from PIL import Image, ImageTk

from config import Config
from services.face_recognition_service import face_service


class TeacherWindow:
    def __init__(self, root, db, user, logout_callback):
        self.root = root
        self.db = db
        self.user = user
        self.logout_callback = logout_callback

        # Lấy thông tin giảng viên
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE user_id = %s", (user['user_id'],))
        self.teacher = cursor.fetchone()
        cursor.close()

        if not self.teacher:
            messagebox.showerror("Lỗi", "Không tìm thấy hồ sơ giảng viên!")
            self.logout_callback()
            return

        self.root.title(f"{Config.WINDOW_TITLE} - Giảng Viên")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(1000, 600)  # Kích thước tối thiểu
        self.root.resizable(True, True)  # Cho phép resize

        self.center_window()
        self.create_widgets()
        self.refresh_data()
        
        # Xử lý đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width() or Config.WINDOW_WIDTH
        height = self.root.winfo_height() or Config.WINDOW_HEIGHT
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Header - cải thiện
        header = tk.Frame(self.root, bg='#667eea', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Left side - Thông tin
        left_frame = tk.Frame(header, bg='#667eea')
        left_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(
            left_frame,
            text=f"👨‍🏫 {self.user.get('full_name', '')}",
            font=('Arial', 16, 'bold'),
            bg='#667eea',
            fg='white'
        ).pack(anchor='w')
        
        tk.Label(
            left_frame,
            text=f"Mã GV: {self.teacher['teacher_code']}",
            font=('Arial', 11),
            bg='#667eea',
            fg='#e2e8f0'
        ).pack(anchor='w')

        # Right side - Buttons
        tk.Button(
            header,
            text="🚪 Đăng xuất",
            font=('Arial', 11),
            bg='white',
            fg='#667eea',
            cursor='hand2',
            command=self.logout
        ).pack(side=tk.RIGHT, padx=20)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs
        self.create_classes_tab()
        self.create_attendance_tab()
        self.create_support_request_tab()  # Tab yêu cầu hỗ trợ (thay Train Model)
        self.create_change_password_tab()  # Tab đổi mật khẩu


    def create_classes_tab(self):
        """Tab quản lý lớp học"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='🏫 Lớp học của tôi')

        # Toolbar
        toolbar = tk.Frame(tab, bg='white')
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            toolbar,
            text="➕ Đăng ký lớp mới",
            font=('Arial', 11, 'bold'),
            bg='#667eea',
            fg='white',
            cursor='hand2',
            command=self.create_class
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🔄 Làm mới",
            font=('Arial', 11),
            bg='#e0e0e0',
            cursor='hand2',
            command=self.refresh_classes
        ).pack(side=tk.LEFT, padx=5)

        # Treeview
        tree_frame = tk.Frame(tab, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.classes_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'code', 'name', 'credits', 'students', 'semester', 'year', 'status', 'creator'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.classes_tree.yview)

        self.classes_tree.heading('id', text='ID')
        self.classes_tree.heading('code', text='Mã lớp')
        self.classes_tree.heading('name', text='Tên lớp')
        self.classes_tree.heading('credits', text='Tín chỉ')
        self.classes_tree.heading('students', text='SV')
        self.classes_tree.heading('semester', text='Kỳ')
        self.classes_tree.heading('year', text='Năm học')
        self.classes_tree.heading('status', text='Trạng thái')
        self.classes_tree.heading('creator', text='Người tạo')

        self.classes_tree.column('id', width=50)
        self.classes_tree.column('code', width=100)
        self.classes_tree.column('name', width=200)
        self.classes_tree.column('credits', width=70)
        self.classes_tree.column('students', width=70)
        self.classes_tree.column('semester', width=50)
        self.classes_tree.column('year', width=100)
        self.classes_tree.column('status', width=100)
        self.classes_tree.column('creator', width=200)

        self.classes_tree.pack(fill=tk.BOTH, expand=True)

        self.classes_tree.bind('<Button-3>', self.show_class_menu)
        self.classes_tree.bind('<Double-Button-1>', self.upload_class_document)

    def create_attendance_tab(self):
        """Tab điểm danh"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='✅ Điểm danh')

        # Toolbar
        toolbar = tk.Frame(tab, bg='white')
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(toolbar, text="Chọn lớp:", font=('Arial', 11, 'bold'), bg='white').pack(side=tk.LEFT, padx=5)
        
        self.attendance_class_var = tk.StringVar()
        self.attendance_class_combo = ttk.Combobox(toolbar, textvariable=self.attendance_class_var, 
                                                    width=40, state='readonly')
        self.attendance_class_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📸 Bắt đầu điểm danh",
            font=('Arial', 11, 'bold'),
            bg='#667eea',
            fg='white',
            cursor='hand2',
            command=self.start_face_attendance
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🔄 Làm mới",
            font=('Arial', 11),
            bg='#e0e0e0',
            cursor='hand2',
            command=self.refresh_attendance_classes
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📋 Xem báo cáo",
            font=('Arial', 11),
            bg='#17a2b8',
            fg='white',
            cursor='hand2',
            command=self.show_attendance_report
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="✏️ Rà soát điểm danh",
            font=('Arial', 11, 'bold'),
            bg='#ffc107',
            fg='black',
            cursor='hand2',
            command=self.open_review_attendance
        ).pack(side=tk.LEFT, padx=5)

        # Frame chứa camera và danh sách
        content_frame = tk.Frame(tab, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Camera frame (bên trái)
        camera_frame = tk.Frame(content_frame, bg='#f0f0f0', relief=tk.RIDGE, borderwidth=2)
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(camera_frame, text="📹 Camera", font=('Arial', 12, 'bold'), 
                bg='#f0f0f0').pack(pady=10)

        self.camera_label = tk.Label(camera_frame, bg='black')
        self.camera_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Danh sách điểm danh (bên phải)
        list_frame = tk.Frame(content_frame, bg='white')
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(list_frame, text="✅ Đã điểm danh", font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)

        # Treeview
        tree_container = tk.Frame(list_frame, bg='white')
        tree_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.attendance_tree = ttk.Treeview(
            tree_container,
            columns=('student_code', 'name', 'time', 'confidence'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.attendance_tree.yview)

        self.attendance_tree.heading('student_code', text='Mã SV')
        self.attendance_tree.heading('name', text='Họ tên')
        self.attendance_tree.heading('time', text='Thời gian')
        self.attendance_tree.heading('confidence', text='Độ tin cậy')

        self.attendance_tree.column('student_code', width=100)
        self.attendance_tree.column('name', width=150)
        self.attendance_tree.column('time', width=100)
        self.attendance_tree.column('confidence', width=80)

        self.attendance_tree.pack(fill=tk.BOTH, expand=True)

        # Camera state
        self.camera_active = False
        self.camera_capture = None
        self.current_session_id = None

    def create_support_request_tab(self):
        """Tab yêu cầu hỗ trợ từ kiểm duyệt"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text='📨 Yêu cầu hỗ trợ')

        # Info frame
        info_frame = tk.LabelFrame(tab, text="📖 Hướng dẫn", bg='white', font=('Arial', 11, 'bold'))
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        info_text = """
• Gửi yêu cầu cập nhật hệ thống AI khi:
  - Có sinh viên mới upload ảnh khuôn mặt
  - Hệ thống nhận diện không chính xác
  - Cần cập nhật model AI

• Kiểm duyệt viên sẽ xem xét và train lại model
• Thời gian xử lý: 1-2 ngày làm việc
        """
        tk.Label(info_frame, text=info_text, bg='white', justify='left', 
                 font=('Arial', 10)).pack(padx=10, pady=10)

        # Form frame
        form_frame = tk.LabelFrame(tab, text="📝 Gửi yêu cầu", bg='white', font=('Arial', 11, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Loại yêu cầu
        tk.Label(form_frame, text="Loại yêu cầu:", bg='white', 
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(20,5))
        
        self.request_type_var = tk.StringVar(value="update_ai")
        request_types = [
            ("🤖 Cập nhật AI Model", "update_ai"),
            ("❌ Báo lỗi nhận diện", "recognition_error"),
            ("➕ Thêm sinh viên mới", "new_student"),
            ("❓ Khác", "other")
        ]
        
        for text, value in request_types:
            tk.Radiobutton(
                form_frame,
                text=text,
                variable=self.request_type_var,
                value=value,
                bg='white',
                font=('Arial', 10)
            ).pack(anchor='w', padx=40)

        # Nội dung
        tk.Label(form_frame, text="Nội dung chi tiết:", bg='white', 
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(15,5))
        
        self.request_content_text = tk.Text(
            form_frame,
            font=('Arial', 10),
            height=8,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.request_content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Button frame
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Button(
            button_frame,
            text="📤 Gửi yêu cầu",
            font=('Arial', 12, 'bold'),
            bg='#4299e1',
            fg='white',
            cursor='hand2',
            command=self.send_support_request,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="🗑️ Xóa nội dung",
            font=('Arial', 12, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=lambda: self.request_content_text.delete('1.0', tk.END),
            width=20
        ).pack(side=tk.LEFT, padx=5)

    def send_support_request(self):
        """Gửi yêu cầu hỗ trợ"""
        request_type = self.request_type_var.get()
        content = self.request_content_text.get('1.0', tk.END).strip()

        if not content:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập nội dung yêu cầu!")
            return

        try:
            cursor = self.db.connection.cursor()
            
            # Tạo bảng support_requests nếu chưa có
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_requests (
                    request_id INT AUTO_INCREMENT PRIMARY KEY,
                    teacher_id INT,
                    request_type VARCHAR(50),
                    content TEXT,
                    status ENUM('pending', 'processing', 'completed') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
                ) ENGINE=InnoDB
            """)
            
            # Lưu yêu cầu
            cursor.execute("""
                INSERT INTO support_requests (teacher_id, request_type, content)
                VALUES (%s, %s, %s)
            """, (self.teacher['teacher_id'], request_type, content))
            
            self.db.connection.commit()
            cursor.close()

            messagebox.showinfo("Thành công", 
                "Đã gửi yêu cầu thành công!\n\n"
                "Kiểm duyệt viên sẽ xem xét và xử lý trong thời gian sớm nhất.")
            
            # Xóa form
            self.request_content_text.delete('1.0', tk.END)
            self.request_type_var.set("update_ai")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể gửi yêu cầu:\n{str(e)}")

    def refresh_data(self):
        """Làm mới tất cả dữ liệu"""
        self.refresh_classes()
        self.refresh_attendance_classes()



    def refresh_classes(self):
        """Làm mới danh sách lớp"""
        try:
            for item in self.classes_tree.get_children():
                self.classes_tree.delete(item)

            classes = self.db.get_classes_by_teacher(self.user['user_id'])
            
            for cls in classes:
                try:
                    # Get enrolled count
                    cursor = self.db.connection.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM class_enrollments 
                        WHERE class_id = %s AND status = 'enrolled'
                    """, (cls['class_id'],))
                    enrolled = cursor.fetchone()[0]
                    cursor.close()

                    status_display = {
                        'pending': '⏳ Chờ duyệt',
                        'approved': '✓ Đã duyệt',
                        'rejected': '✗ Bị từ chối'
                    }.get(cls.get('status', ''), cls.get('status', ''))

                    # display creator (teacher name/email) if schedule stored
                    creator = cls.get('creator_name', '')

                    self.classes_tree.insert('', tk.END, values=(
                        cls['class_id'],
                        cls['class_code'],
                        cls['class_name'],
                        cls['credits'],
                        f"{enrolled}/{cls['max_students']}",
                        cls['semester'],
                        cls['academic_year'],
                        status_display,
                        creator
                    ))
                except Exception as e:
                    print(f"Lỗi xử lý lớp {cls.get('class_code', 'N/A')}: {e}")
                    continue
                    
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp:\n{str(e)}")



    def create_class(self):
        """Mở cửa sổ tạo lớp"""
        CreateClassDialog(self.root, self.db, self.user['user_id'], self.refresh_classes)



        self.train_btn.config(state=tk.NORMAL, text="🚀 Train Model")



    def show_class_menu(self, event):
        """Hiển thị menu context cho lớp"""
        item = self.classes_tree.identify_row(event.y)
        if item:
            self.classes_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="📧 Gửi email sinh viên vắng", command=self.send_absence_emails)
            menu.add_command(label="🗑️ Xóa lớp", command=self.delete_class)
            menu.post(event.x_root, event.y_root)





    def send_absence_emails(self):
        """Gửi email cho sinh viên vắng"""
        messagebox.showinfo("Thông báo", "Chức năng này cần tạo session trước. Sẽ triển khai sau!")

    def delete_class(self):
        """Xóa lớp"""
        try:
            selected = self.classes_tree.selection()
            if not selected:
                return

            item = self.classes_tree.item(selected[0])
            class_name = item['values'][2]

            if not messagebox.askyesno("Xác nhận", f"Xóa lớp {class_name}?"):
                return

            class_id = item['values'][0]
            cursor = self.db.connection.cursor()
            try:
                cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
                self.db.connection.commit()
                messagebox.showinfo("Thành công", "Đã xóa lớp!")
                self.refresh_classes()
            except Exception as e:
                self.db.connection.rollback()
                messagebox.showerror("Lỗi", f"Không thể xóa lớp:\n{str(e)}")
            finally:
                cursor.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý xóa lớp:\n{str(e)}")

    def upload_class_document(self, event):
        """Upload tài liệu cho lớp học khi double-click"""
        try:
            selected = self.classes_tree.selection()
            if not selected:
                return

            item = self.classes_tree.item(selected[0])
            class_id = item['values'][0]
            class_code = item['values'][1]
            class_name = item['values'][2]

            # Mở dialog upload file
            UploadDocumentDialog(self.root, self.db, class_id, class_code, class_name)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi mở dialog upload:\n{str(e)}")

    # ======================== TAB ĐỔI MẬT KHẨU ===================
    def create_change_password_tab(self):
        """Tab đổi mật khẩu cho giảng viên"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="🔑 Đổi mật khẩu")
        
        # Hướng dẫn
        info_frame = tk.LabelFrame(tab, text="📖 Hướng dẫn", bg='white', font=('Arial', 11, 'bold'))
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_text = """
• Để bảo mật tài khoản, bạn nên đổi mật khẩu định kỳ
• Mật khẩu mới phải khác mật khẩu hiện tại
• Độ dài tối thiểu: 6 ký tự
• Không chia sẻ mật khẩu cho người khác
        """
        tk.Label(info_frame, text=info_text, bg='white', justify='left', 
                 font=('Arial', 10)).pack(padx=10, pady=10)
        
        # Form frame
        form_frame = tk.LabelFrame(tab, text="🔐 Đổi mật khẩu", bg='white', font=('Arial', 11, 'bold'))
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Mật khẩu hiện tại
        tk.Label(form_frame, text="🔒 Mật khẩu hiện tại:", bg='white', 
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(20,5))
        self.current_password_entry = tk.Entry(form_frame, font=('Arial', 11), show='•', 
                                                relief=tk.SOLID, borderwidth=1)
        self.current_password_entry.pack(fill=tk.X, padx=20, ipady=8)
        
        # Mật khẩu mới
        tk.Label(form_frame, text="🔑 Mật khẩu mới:", bg='white', 
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(15,5))
        self.new_password_entry = tk.Entry(form_frame, font=('Arial', 11), show='•', 
                                            relief=tk.SOLID, borderwidth=1)
        self.new_password_entry.pack(fill=tk.X, padx=20, ipady=8)
        
        # Xác nhận mật khẩu mới
        tk.Label(form_frame, text="✅ Xác nhận mật khẩu mới:", bg='white', 
                 font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(15,5))
        self.confirm_password_entry = tk.Entry(form_frame, font=('Arial', 11), show='•', 
                                                relief=tk.SOLID, borderwidth=1)
        self.confirm_password_entry.pack(fill=tk.X, padx=20, ipady=8)
        
        # Button frame
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(
            button_frame,
            text="🔄 Đổi mật khẩu",
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            cursor='hand2',
            command=self.change_password,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑️ Xóa form",
            font=('Arial', 12, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=self.clear_password_form,
            width=20
        ).pack(side=tk.LEFT, padx=5)
    
    def change_password(self):
        """Xử lý đổi mật khẩu"""
        current_pwd = self.current_password_entry.get().strip()
        new_pwd = self.new_password_entry.get().strip()
        confirm_pwd = self.confirm_password_entry.get().strip()
        
        # Validation
        if not current_pwd or not new_pwd or not confirm_pwd:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        # Kiểm tra mật khẩu hiện tại
        from models.user import User
        if not User.verify_password(current_pwd, self.user['password_hash']):
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
        
        # Xác nhận đổi
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đổi mật khẩu?"):
            return
        
        # Đổi mật khẩu
        try:
            user_model = User(self.db)
            if user_model.reset_password(self.user['user_id'], new_pwd):
                messagebox.showinfo("Thành công", 
                    "Đã đổi mật khẩu thành công!\n\n"
                    "Vui lòng ghi nhớ mật khẩu mới.\n"
                    "Bạn sẽ cần mật khẩu mới để đăng nhập lần sau.")
                
                # Xóa form
                self.clear_password_form()
                
                # Cập nhật password_hash trong user object
                self.user['password_hash'] = User.hash_password(new_pwd)
            else:
                messagebox.showerror("Lỗi", "Không thể đổi mật khẩu!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi đổi mật khẩu:\n{str(e)}")
    
    def clear_password_form(self):
        """Xóa form đổi mật khẩu"""
        self.current_password_entry.delete(0, tk.END)
        self.new_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.current_password_entry.focus()

    def logout(self):
        """Đăng xuất"""
        self.root.destroy()
        self.logout_callback()

    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        if messagebox.askyesno("Xác nhận thoát", "Bạn có chắc muốn thoát?"):
            self.root.destroy()
            import sys
            sys.exit(0)

    def show_profile(self):
        """Hiển thị thông tin cá nhân"""
        from gui.profile_window import ProfileWindow
        ProfileWindow(self.root, self.user)

    def refresh_attendance_classes(self):
        """Làm mới danh sách lớp cho điểm danh"""
        try:
            classes = self.db.get_classes_by_teacher(self.user['user_id'])
            approved_classes = [c for c in classes if c.get('status') == 'approved']
            
            class_options = [f"{c['class_code']} - {c['class_name']}" for c in approved_classes]
            self.attendance_class_combo['values'] = class_options
            
            if class_options:
                self.attendance_class_combo.current(0)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp:\n{str(e)}")

    def start_face_attendance(self):
        """Bắt đầu điểm danh bằng khuôn mặt"""
        if self.camera_active:
            self.stop_camera()
            return

        selected = self.attendance_class_var.get()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp!")
            return

        # Lấy class_code từ selection
        class_code = selected.split(' - ')[0]
        
        # Tìm class_id
        classes = self.db.get_classes_by_teacher(self.user['user_id'])
        class_obj = next((c for c in classes if c['class_code'] == class_code), None)
        
        if not class_obj:
            messagebox.showerror("Lỗi", "Không tìm thấy lớp!")
            return

        class_id = class_obj['class_id']

        # Kiểm tra model đã train chưa
        if not face_service.recognizer:
            messagebox.showerror("Lỗi", "Model chưa được train! Vui lòng train model trước.")
            return

        # Tạo session mới
        from datetime import date
        cursor = self.db.connection.cursor()
        try:
            # Đếm số session hiện tại
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE class_id = %s", (class_id,))
            session_count = cursor.fetchone()[0]
            
            session_number = session_count + 1
            session_date = date.today()
            session_time = 'morning'  # Có thể thêm logic chọn buổi

            cursor.execute("""
                INSERT INTO sessions (class_id, session_date, session_time, session_number)
                VALUES (%s, %s, %s, %s)
            """, (class_id, session_date, session_time, session_number))
            self.db.connection.commit()
            self.current_session_id = cursor.lastrowid
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo buổi học: {e}")
            return
        finally:
            cursor.close()

        # Xóa danh sách cũ
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        # Bắt đầu camera
        self.camera_active = True
        self.camera_capture = cv2.VideoCapture(0)
        
        if not self.camera_capture.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở camera!")
            self.camera_active = False
            return

        self.update_camera_frame()

    def update_camera_frame(self):
        """Cập nhật frame từ camera và nhận diện khuôn mặt"""
        if not self.camera_active or not self.camera_capture:
            return

        ret, frame = self.camera_capture.read()
        if not ret:
            self.stop_camera()
            return

        # Nhận diện khuôn mặt
        recognized = face_service.recognize_faces(frame)
        
        # Vẽ khung lên frame
        frame = face_service.draw_faces(frame, recognized)

        # Điểm danh tự động
        for face in recognized:
            if face['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                student_code = face['student_code']
                
                # Lấy thông tin sinh viên
                student = self.db.get_student_by_code(student_code)
                if student:
                    student_id = student['student_id']
                    
                    # Kiểm tra đã điểm danh chưa
                    cursor = self.db.connection.cursor()
                    cursor.execute("""
                        SELECT * FROM attendance 
                        WHERE session_id = %s AND student_id = %s
                    """, (self.current_session_id, student_id))
                    existing = cursor.fetchone()
                    cursor.close()

                    if not existing:
                        # Điểm danh
                        success = self.db.mark_attendance(
                            session_id=self.current_session_id,
                            student_id=student_id,
                            status='present',
                            confidence_score=face['confidence']
                        )
                        
                        if success:
                            # Thêm vào danh sách
                            now = datetime.now().strftime('%H:%M:%S')
                            self.attendance_tree.insert('', 0, values=(
                                student_code,
                                student['full_name'],
                                now,
                                f"{face['confidence']:.1f}%"
                            ), tags=('present',))
                            
                            # Tô màu xanh cho sinh viên có mặt
                            self.attendance_tree.tag_configure('present', background='#ccffcc')

        # Chuyển đổi frame sang định dạng Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Resize để vừa với label
        label_width = self.camera_label.winfo_width()
        label_height = self.camera_label.winfo_height()
        
        if label_width > 1 and label_height > 1:
            img = img.resize((label_width, label_height), Image.LANCZOS)
        
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)

        # Lặp lại sau 30ms
        if self.camera_active:
            self.root.after(30, self.update_camera_frame)

    def stop_camera(self):
        """Dừng camera và đánh dấu sinh viên vắng"""
        self.camera_active = False
        if self.camera_capture:
            self.camera_capture.release()
            self.camera_capture = None
        
        self.camera_label.configure(image='', bg='black')
        
        # Hỏi có muốn đánh dấu sinh viên vắng không
        if self.current_session_id:
            result = messagebox.askyesnocancel(
                "Kết thúc điểm danh",
                "Bạn có muốn đánh dấu các sinh viên chưa điểm danh là VẮNG không?\n\n"
                "• YES: Đánh dấu vắng cho sinh viên chưa điểm danh\n"
                "• NO: Chỉ dừng camera, không đánh dấu vắng\n"
                "• CANCEL: Tiếp tục điểm danh"
            )
            
            if result is None:  # Cancel - tiếp tục điểm danh
                self.camera_active = True
                self.camera_capture = cv2.VideoCapture(0)
                if self.camera_capture.isOpened():
                    self.update_camera_frame()
                return
            elif result:  # Yes - đánh dấu vắng
                self.mark_absent_students()
        
        messagebox.showinfo("Thông báo", "Đã dừng điểm danh!")
    
    def mark_absent_students(self):
        """Đánh dấu sinh viên chưa điểm danh là vắng"""
        if not self.current_session_id:
            return
        
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            
            # Lấy class_id từ session
            cursor.execute("""
                SELECT class_id FROM sessions WHERE session_id = %s
            """, (self.current_session_id,))
            session = cursor.fetchone()
            
            if not session:
                cursor.close()
                return
            
            class_id = session['class_id']
            
            # Lấy danh sách sinh viên đã đăng ký lớp
            cursor.execute("""
                SELECT ce.student_id, s.student_code, u.full_name
                FROM class_enrollments ce
                JOIN students s ON ce.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE ce.class_id = %s AND ce.status = 'enrolled'
            """, (class_id,))
            enrolled_students = cursor.fetchall()
            
            # Lấy danh sách sinh viên đã điểm danh
            cursor.execute("""
                SELECT student_id FROM attendance 
                WHERE session_id = %s
            """, (self.current_session_id,))
            attended_ids = {row['student_id'] for row in cursor.fetchall()}
            
            # Tìm sinh viên chưa điểm danh
            absent_students = [s for s in enrolled_students if s['student_id'] not in attended_ids]
            
            if not absent_students:
                cursor.close()
                messagebox.showinfo("Thông báo", "Tất cả sinh viên đã điểm danh!")
                return
            
            # Đánh dấu vắng
            absent_count = 0
            for student in absent_students:
                success = self.db.mark_attendance(
                    session_id=self.current_session_id,
                    student_id=student['student_id'],
                    status='absent',
                    confidence_score=None
                )
                if success:
                    absent_count += 1
                    # Thêm vào danh sách hiển thị
                    now = datetime.now().strftime('%H:%M:%S')
                    self.attendance_tree.insert('', tk.END, values=(
                        student['student_code'],
                        student['full_name'],
                        now,
                        'VẮNG'
                    ), tags=('absent',))
            
            # Tô màu đỏ cho sinh viên vắng
            self.attendance_tree.tag_configure('absent', background='#ffcccc')
            
            cursor.close()
            
            messagebox.showinfo(
                "Hoàn tất",
                f"Đã đánh dấu {absent_count} sinh viên vắng!\n\n"
                f"Tổng sinh viên: {len(enrolled_students)}\n"
                f"Có mặt: {len(attended_ids)}\n"
                f"Vắng: {absent_count}"
            )
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đánh dấu vắng: {e}")
    
    def show_attendance_report(self):
        """Hiển thị báo cáo điểm danh chi tiết"""
        if not self.current_session_id:
            messagebox.showwarning("Cảnh báo", "Chưa có buổi điểm danh nào!")
            return
        
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            
            # Lấy thông tin session
            cursor.execute("""
                SELECT s.*, c.class_code, c.class_name
                FROM sessions s
                JOIN classes c ON s.class_id = c.class_id
                WHERE s.session_id = %s
            """, (self.current_session_id,))
            session = cursor.fetchone()
            
            if not session:
                cursor.close()
                return
            
            # Lấy danh sách sinh viên có mặt
            cursor.execute("""
                SELECT s.student_code, u.full_name, a.check_in_time, a.confidence_score
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE a.session_id = %s AND a.status = 'present'
                ORDER BY a.check_in_time
            """, (self.current_session_id,))
            present_students = cursor.fetchall()
            
            # Lấy danh sách sinh viên vắng
            cursor.execute("""
                SELECT s.student_code, u.full_name
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE a.session_id = %s AND a.status = 'absent'
                ORDER BY s.student_code
            """, (self.current_session_id,))
            absent_students = cursor.fetchall()
            
            cursor.close()
            
            # Tạo cửa sổ báo cáo
            report_window = tk.Toplevel(self.root)
            report_window.title("Báo Cáo Điểm Danh")
            report_window.geometry("700x600")
            
            # Header
            header_frame = tk.Frame(report_window, bg='#667eea', height=80)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text=f"📊 Báo Cáo Điểm Danh",
                font=('Arial', 16, 'bold'),
                bg='#667eea',
                fg='white'
            ).pack(pady=10)
            
            tk.Label(
                header_frame,
                text=f"{session['class_code']} - {session['class_name']}",
                font=('Arial', 12),
                bg='#667eea',
                fg='white'
            ).pack()
            
            # Thống kê
            stats_frame = tk.Frame(report_window, bg='#f0f0f0', relief=tk.RIDGE, borderwidth=2)
            stats_frame.pack(fill=tk.X, padx=10, pady=10)
            
            total = len(present_students) + len(absent_students)
            present_rate = (len(present_students) / total * 100) if total > 0 else 0
            
            stats_text = f"""
📅 Ngày: {session['session_date'].strftime('%d/%m/%Y')} | Buổi: {session['session_time']} | Tiết: {session['session_number']}

📊 Thống kê:
   • Tổng sinh viên: {total}
   • Có mặt: {len(present_students)} ({present_rate:.1f}%)
   • Vắng: {len(absent_students)} ({100-present_rate:.1f}%)
            """
            
            tk.Label(
                stats_frame,
                text=stats_text,
                font=('Arial', 11),
                bg='#f0f0f0',
                justify=tk.LEFT
            ).pack(padx=10, pady=10, anchor='w')
            
            # Notebook cho 2 tab
            notebook = ttk.Notebook(report_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab có mặt
            present_tab = tk.Frame(notebook, bg='white')
            notebook.add(present_tab, text=f'✅ Có mặt ({len(present_students)})')
            
            present_tree = ttk.Treeview(
                present_tab,
                columns=('stt', 'code', 'name', 'time', 'confidence'),
                show='headings'
            )
            present_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            present_tree.heading('stt', text='STT')
            present_tree.heading('code', text='Mã SV')
            present_tree.heading('name', text='Họ tên')
            present_tree.heading('time', text='Giờ điểm danh')
            present_tree.heading('confidence', text='Độ tin cậy')
            
            present_tree.column('stt', width=50)
            present_tree.column('code', width=100)
            present_tree.column('name', width=200)
            present_tree.column('time', width=120)
            present_tree.column('confidence', width=100)
            
            for i, student in enumerate(present_students, 1):
                time_str = student['check_in_time'].strftime('%H:%M:%S')
                conf_str = f"{student['confidence_score']:.1f}%" if student['confidence_score'] else "N/A"
                present_tree.insert('', tk.END, values=(
                    i,
                    student['student_code'],
                    student['full_name'],
                    time_str,
                    conf_str
                ))
            
            # Tab vắng
            absent_tab = tk.Frame(notebook, bg='white')
            notebook.add(absent_tab, text=f'❌ Vắng ({len(absent_students)})')
            
            absent_tree = ttk.Treeview(
                absent_tab,
                columns=('stt', 'code', 'name'),
                show='headings'
            )
            absent_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            absent_tree.heading('stt', text='STT')
            absent_tree.heading('code', text='Mã SV')
            absent_tree.heading('name', text='Họ tên')
            
            absent_tree.column('stt', width=50)
            absent_tree.column('code', width=150)
            absent_tree.column('name', width=300)
            
            for i, student in enumerate(absent_students, 1):
                absent_tree.insert('', tk.END, values=(
                    i,
                    student['student_code'],
                    student['full_name']
                ))
            
            # Nút đóng
            tk.Button(
                report_window,
                text="Đóng",
                font=('Arial', 11),
                bg='#e0e0e0',
                command=report_window.destroy,
                width=15
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo báo cáo: {e}")
    
    def open_review_attendance(self):
        """Mở cửa sổ rà soát điểm danh"""
        if not self.current_session_id:
            messagebox.showwarning("Cảnh báo", "Chưa có buổi điểm danh nào!")
            return
        
        ReviewAttendanceDialog(self.root, self.db, self.current_session_id, self.refresh_attendance_display)
    
    def refresh_attendance_display(self):
        """Làm mới hiển thị danh sách điểm danh"""
        # Xóa danh sách cũ
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        if not self.current_session_id:
            return
        
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            
            # Lấy danh sách tất cả sinh viên đã điểm danh
            cursor.execute("""
                SELECT s.student_code, u.full_name, a.check_in_time, 
                       a.confidence_score, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE a.session_id = %s
                ORDER BY a.check_in_time
            """, (self.current_session_id,))
            
            records = cursor.fetchall()
            cursor.close()
            
            for record in records:
                time_str = record['check_in_time'].strftime('%H:%M:%S')
                
                if record['status'] == 'present':
                    conf_str = f"{record['confidence_score']:.1f}%" if record['confidence_score'] else "Thủ công"
                    tag = 'present'
                else:
                    conf_str = 'VẮNG'
                    tag = 'absent'
                
                self.attendance_tree.insert('', tk.END, values=(
                    record['student_code'],
                    record['full_name'],
                    time_str,
                    conf_str
                ), tags=(tag,))
            
            # Cấu hình màu
            self.attendance_tree.tag_configure('present', background='#ccffcc')
            self.attendance_tree.tag_configure('absent', background='#ffcccc')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể làm mới danh sách: {e}")


class CreateClassDialog:
    """Dialog tạo lớp học (mở rộng: chọn thứ, tiết từ->đến, kiểm tra xung đột)"""
    def __init__(self, parent, db, teacher_id, callback):
        self.db = db
        self.teacher_id = teacher_id
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Đăng ký lớp học")
        self.dialog.geometry("620x700")
        self.dialog.resizable(False, False)

        # Data structures
        self.schedule_entries: List[dict] = []  # list of dicts: {'day': 'Thứ 2', 'from': 3, 'to': 4, 'session': 'morning'}

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.dialog, bg='white', padx=20, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header with teacher info
        user_info = self.db.get_user_by_id(self.teacher_id) or {}
        teacher_display = f"{user_info.get('full_name', 'Không rõ')} - {user_info.get('email', '')}"
        tk.Label(frame, text="Người đăng ký:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        tk.Label(frame, text=teacher_display, font=('Arial', 10), bg='#f7f7f7', anchor='w', relief=tk.FLAT).pack(fill=tk.X, pady=(0,10))

        # Row: class code + class name (side by side)
        row1 = tk.Frame(frame, bg='white')
        row1.pack(fill=tk.X, pady=(0,8))
        tk.Label(row1, text="Mã lớp *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w')
        self.class_code = tk.Entry(row1, font=('Arial', 11))
        self.class_code.grid(row=1, column=0, sticky='we', padx=(0,10))
        tk.Label(row1, text="Tên lớp *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=1, sticky='w')
        self.class_name = tk.Entry(row1, font=('Arial', 11))
        self.class_name.grid(row=1, column=1, sticky='we')
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=2)

        # Sessions and credits
        row2 = tk.Frame(frame, bg='white')
        row2.pack(fill=tk.X, pady=(8,8))
        tk.Label(row2, text="Số tiết học *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w')
        self.sessions_var = tk.StringVar(value='2')
        sessions_frame = tk.Frame(row2, bg='white')
        sessions_frame.grid(row=1, column=0, sticky='w')
        for val in ['2', '3', '4']:
            tk.Radiobutton(sessions_frame, text=f"{val}", variable=self.sessions_var,
                          value=val, font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=6)

        tk.Label(row2, text="Tín chỉ", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=1, sticky='w', padx=(20,0))
        self.credits_label = tk.Label(row2, text="1 tín chỉ", font=('Arial', 11), bg='#f0f0f0', anchor='w')
        self.credits_label.grid(row=1, column=1, sticky='we', padx=(20,0))
        self.sessions_var.trace('w', self.update_credits)
        row2.grid_columnconfigure(1, weight=1)

        # Max students, semester, year
        row3 = tk.Frame(frame, bg='white')
        row3.pack(fill=tk.X, pady=(8,8))
        tk.Label(row3, text="Số SV tối đa *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w')
        self.max_students = tk.Entry(row3, font=('Arial', 11))
        self.max_students.insert(0, '40')
        self.max_students.grid(row=1, column=0, sticky='we', padx=(0,10))

        tk.Label(row3, text="Học kỳ *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=1, sticky='w')
        self.semester = ttk.Combobox(row3, values=['1', '2', '3'], font=('Arial', 11), state='readonly')
        self.semester.set('1')
        self.semester.grid(row=1, column=1, sticky='we', padx=(0,10))

        tk.Label(row3, text="Năm học *", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w')
        current_year = datetime.now().year
        self.academic_year = tk.Entry(row3, font=('Arial', 11))
        self.academic_year.insert(0, f"{current_year}-{current_year+1}")
        self.academic_year.grid(row=1, column=2, sticky='we')
        row3.grid_columnconfigure(0, weight=1)
        row3.grid_columnconfigure(1, weight=0)
        row3.grid_columnconfigure(2, weight=0)

        # ---------- Schedule builder ----------
        tk.Label(frame, text="Lịch học (Thêm nhiều mục nếu cần)", font=('Arial', 11, 'bold'), bg='white').pack(anchor='w', pady=(10,4))

        sched_frame = tk.Frame(frame, bg='white')
        sched_frame.pack(fill=tk.X, pady=(0,8))

        tk.Label(sched_frame, text="Thứ", bg='white').grid(row=0, column=0, sticky='w')
        self.day_cb = ttk.Combobox(sched_frame, values=[
            'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'
        ], state='readonly', width=12)
        self.day_cb.grid(row=1, column=0, padx=4)

        tk.Label(sched_frame, text="Tiết từ", bg='white').grid(row=0, column=1, sticky='w')
        self.period_from = ttk.Combobox(sched_frame, values=list(range(1, 13)), width=6, state='readonly')
        self.period_from.grid(row=1, column=1, padx=4)

        tk.Label(sched_frame, text="Tiết đến", bg='white').grid(row=0, column=2, sticky='w')
        self.period_to = ttk.Combobox(sched_frame, values=list(range(1, 13)), width=6, state='readonly')
        self.period_to.grid(row=1, column=2, padx=4)

        tk.Button(sched_frame, text="➕ Thêm tiết", command=self.add_schedule_entry, bg='#4caf50', fg='white').grid(row=1, column=3, padx=8)

        # Listbox show schedule entries
        list_frame = tk.Frame(frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=False, pady=(6,8))

        self.schedule_listbox = tk.Listbox(list_frame, height=6, font=('Arial', 10))
        self.schedule_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))
        lb_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.schedule_listbox.yview)
        lb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.schedule_listbox.config(yscrollcommand=lb_scroll.set)

        tk.Button(frame, text="🗑️ Xóa mục chọn", command=self.remove_selected_schedule, bg='#e53935', fg='white').pack(pady=(0,8), anchor='e', padx=20)

        # Submit
        tk.Button(
            frame,
            text="✓ Đăng ký lớp",
            font=('Arial', 12, 'bold'),
            bg='#667eea',
            fg='white',
            command=self.save,
            cursor='hand2'
        ).pack(fill=tk.X, pady=10, ipady=10)

    def update_credits(self, *args):
        try:
            sessions = int(self.sessions_var.get())
            credits = Config.CREDITS_MAPPING.get(sessions, 1)
            self.credits_label.config(text=f"{credits} tín chỉ")
        except Exception:
            pass

    def add_schedule_entry(self):
        day = self.day_cb.get()
        start = self.period_from.get()
        end = self.period_to.get()

        if not day or not start or not end:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thứ, tiết bắt đầu và tiết kết thúc.")
            return

        start = int(start)
        end = int(end)
        if end < start:
            messagebox.showwarning("Cảnh báo", "Tiết đến phải lớn hơn hoặc bằng tiết từ.")
            return

        # Lấy số tiết giáo viên đã chọn (số tiết cho 1 buổi)
        try:
            sessions = int(self.sessions_var.get())
        except Exception:
            sessions = 1

        duration = end - start + 1

        # Không cho phép cắt ngang buổi (sáng/chiều)
        # Qui ước: tiết 1..5 = morning, 6..10 = afternoon
        def session_of(t):
            return 'morning' if t <= 5 else 'afternoon'

        if session_of(start) != session_of(end):
            messagebox.showerror("Không hợp lệ", "Không được chọn khoảng tiết cắt ngang buổi (ví dụ: 5 → 7). Vui lòng chọn các tiết trong cùng một buổi.")
            return

        # Nếu số tiết chọn không khớp với duration, đề xuất auto-điền period_to
        if duration != sessions:
            auto_end = start + sessions - 1
            # kiểm tra auto_end hợp lệ trong giới hạn tiết (1..12)
            if auto_end > 10:
                messagebox.showerror("Không hợp lệ", f"Với {sessions} tiết bắt đầu từ tiết {start}, tiết kết thúc sẽ vượt quá giới hạn (>{12}). Vui lòng chọn tiết bắt đầu khác hoặc giảm số tiết.")
                return

            # kiểm tra auto_end có cắt buổi không
            if session_of(start) != session_of(auto_end):
                messagebox.showerror("Không hợp lệ", f"Khoảng {start} → {auto_end} sẽ cắt buổi (sáng/chiều). Vui lòng chọn tiết bắt đầu khác hoặc thay đổi số tiết.")
                return

            # hỏi người dùng có muốn auto sửa period_to không
            if messagebox.showerror("Không hợp lệ", f"Bạn đã chọn {sessions} tiết nhưng khoảng {start} → {end} có {duration} tiết.\n"):
                return
            else:
                # nếu không đồng ý, hủy
                return

        # Sau tất cả kiểm tra, vẫn đảm bảo same session (một lần nữa)
        if session_of(start) != session_of(end):
            messagebox.showerror("Không hợp lệ", "Khoảng tiết không thuộc cùng buổi. Vui lòng kiểm tra lại.")
            return

        session_time = 'morning' if start <= 6 else 'afternoon'

        entry = {'day': day, 'from': start, 'to': end, 'session': session_time}
        self.schedule_entries.append(entry)
        self.schedule_listbox.insert(tk.END, f"{day}: Tiết {start} - {end} ({session_time})")

        # reset selects
        self.day_cb.set('')
        self.period_from.set('')
        self.period_to.set('')


    def remove_selected_schedule(self):
        sel = self.schedule_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.schedule_listbox.delete(idx)
        del self.schedule_entries[idx]

    def _has_conflict_with_existing_classes(self, schedule_entries: List[dict], academic_year: str, semester: Any) -> Tuple[bool, str]:
        """
        Kiểm tra xung đột: so sánh schedule_entries (list dict) với các class đã tồn tại của cùng giáo viên
        Trả về (True, message) nếu xung đột, ngược lại (False, "")
        """
        cursor = self.db.connection.cursor()
        try:
            # Lấy các lớp cùng GV, cùng học kỳ & năm, trừ lớp bị từ chối
            cursor.execute("""
                SELECT class_code, schedule, academic_year, semester, status 
                FROM classes 
                WHERE teacher_id = %s AND status != 'rejected'
            """, (self.teacher_id,))
            rows = cursor.fetchall()
        except Exception:
            try:
                cursor.close()
            except:
                pass
            return False, ""

        for row in rows:
            class_code = row[0]
            schedule_json = row[1]
            ay = row[2]
            sem = row[3]

            # chỉ check trong cùng học kỳ & năm
            try:
                if ay != academic_year or int(sem) != int(semester):
                    continue
            except Exception:
                continue

            if not schedule_json:
                continue

            try:
                existing_schedules = json.loads(schedule_json)
            except Exception:
                continue

            for e in existing_schedules:
                e_day = e.get('day')
                try:
                    e_from = int(e.get('from'))
                    e_to = int(e.get('to'))
                except Exception:
                    continue

                for n in schedule_entries:
                    if n['day'] != e_day:
                        continue
                    # kiểm tra overlap
                    if not (n['to'] < e_from or n['from'] > e_to):
                        msg = f"Xung đột với lớp {class_code} ({e_day} tiết {e_from}-{e_to})"
                        try:
                            cursor.close()
                        except:
                            pass
                        return True, msg

        try:
            cursor.close()
        except:
            pass
        return False, ""


    def save(self):
        class_code = self.class_code.get().strip()
        class_name = self.class_name.get().strip()
        try:
            total_sessions = int(self.sessions_var.get())
        except:
            total_sessions = 2
        max_students = self.max_students.get().strip()
        semester = self.semester.get()
        academic_year = self.academic_year.get().strip()

        if not all([class_code, class_name, max_students, semester, academic_year]):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
            return

        if not self.schedule_entries:
            messagebox.showwarning("Cảnh báo", "Vui lòng thêm ít nhất một mục lịch học (thứ + tiết).")
            return

        credits = Config.CREDITS_MAPPING.get(total_sessions, 1)

        # Check conflicts BEFORE create
        conflict, msg = self._has_conflict_with_existing_classes(self.schedule_entries, academic_year, semester)
        if conflict:
            messagebox.showerror("Xung đột lịch", f"Không thể đăng ký lớp do: {msg}")
            return

        # Prepare schedule JSON (list of entries)
        schedule_json = json.dumps(self.schedule_entries, ensure_ascii=False)

        class_id = self.db.create_class(
            class_code=class_code,
            class_name=class_name,
            teacher_id=self.teacher_id,
            total_sessions=total_sessions,
            credits=credits,
            max_students=int(max_students),
            semester=int(semester),
            academic_year=academic_year,
            schedule=self.schedule_entries  # Database.create_class sẽ json.dumps
        )

        if not class_id:
            messagebox.showerror("Lỗi", "Mã lớp đã tồn tại hoặc lỗi hệ thống!")
            return

        messagebox.showinfo("Thành công", "Đã đăng ký lớp! Chờ kiểm duyệt.")
        self.callback()
        self.dialog.destroy()



class ReviewAttendanceDialog:
    """Dialog rà soát và điều chỉnh điểm danh"""
    def __init__(self, parent, db, session_id, refresh_callback):
        self.db = db
        self.session_id = session_id
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Rà Soát Điểm Danh")
        self.dialog.geometry("900x700")
        self.dialog.resizable(True, True)
        
        # Lấy thông tin session
        self.load_session_info()
        
        self.create_widgets()
        self.load_attendance_data()
    
    def load_session_info(self):
        """Lấy thông tin buổi học"""
        cursor = self.db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, c.class_code, c.class_name
            FROM sessions s
            JOIN classes c ON s.class_id = c.class_id
            WHERE s.session_id = %s
        """, (self.session_id,))
        self.session_info = cursor.fetchone()
        cursor.close()
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.dialog, bg='#ffc107', height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="✏️ RÀ SOÁT ĐIỂM DANH",
            font=('Arial', 18, 'bold'),
            bg='#ffc107',
            fg='black'
        ).pack(pady=10)
        
        if self.session_info:
            info_text = f"{self.session_info['class_code']} - {self.session_info['class_name']}\n"
            info_text += f"Ngày: {self.session_info['session_date'].strftime('%d/%m/%Y')} | "
            info_text += f"Buổi: {self.session_info['session_time']} | "
            info_text += f"Tiết: {self.session_info['session_number']}"
            
            tk.Label(
                header,
                text=info_text,
                font=('Arial', 11),
                bg='#ffc107',
                fg='black'
            ).pack()
        
        # Thống kê
        self.stats_frame = tk.Frame(self.dialog, bg='#f0f0f0', relief=tk.RIDGE, borderwidth=2)
        self.stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = tk.Label(
            self.stats_frame,
            text="Đang tải...",
            font=('Arial', 11),
            bg='#f0f0f0',
            justify=tk.LEFT
        )
        self.stats_label.pack(padx=10, pady=10, anchor='w')
        
        # Hướng dẫn
        guide_frame = tk.Frame(self.dialog, bg='#e3f2fd', relief=tk.RIDGE, borderwidth=1)
        guide_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        guide_text = "💡 Hướng dẫn: Chọn sinh viên → Click nút để thay đổi trạng thái"
        tk.Label(
            guide_frame,
            text=guide_text,
            font=('Arial', 10),
            bg='#e3f2fd',
            fg='#1976d2'
        ).pack(padx=10, pady=5)
        
        # Main content - 2 cột
        content_frame = tk.Frame(self.dialog, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cột trái - Sinh viên có mặt
        left_frame = tk.Frame(content_frame, bg='white')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_frame,
            text="✅ CÓ MẶT",
            font=('Arial', 12, 'bold'),
            bg='#d4edda',
            fg='#155724',
            relief=tk.RIDGE,
            borderwidth=2
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Treeview cho sinh viên có mặt
        present_tree_frame = tk.Frame(left_frame)
        present_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        present_scroll = ttk.Scrollbar(present_tree_frame)
        present_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.present_tree = ttk.Treeview(
            present_tree_frame,
            columns=('code', 'name', 'time'),
            show='headings',
            yscrollcommand=present_scroll.set
        )
        present_scroll.config(command=self.present_tree.yview)
        
        self.present_tree.heading('code', text='Mã SV')
        self.present_tree.heading('name', text='Họ tên')
        self.present_tree.heading('time', text='Giờ')
        
        self.present_tree.column('code', width=100)
        self.present_tree.column('name', width=200)
        self.present_tree.column('time', width=80)
        
        self.present_tree.pack(fill=tk.BOTH, expand=True)
        
        # Nút chuyển sang vắng
        tk.Button(
            left_frame,
            text="➡️ Đánh dấu VẮNG",
            font=('Arial', 11, 'bold'),
            bg='#dc3545',
            fg='white',
            cursor='hand2',
            command=self.mark_as_absent
        ).pack(fill=tk.X, pady=5)
        
        # Cột phải - Sinh viên vắng
        right_frame = tk.Frame(content_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="❌ VẮNG",
            font=('Arial', 12, 'bold'),
            bg='#f8d7da',
            fg='#721c24',
            relief=tk.RIDGE,
            borderwidth=2
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Treeview cho sinh viên vắng
        absent_tree_frame = tk.Frame(right_frame)
        absent_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        absent_scroll = ttk.Scrollbar(absent_tree_frame)
        absent_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.absent_tree = ttk.Treeview(
            absent_tree_frame,
            columns=('code', 'name', 'time'),
            show='headings',
            yscrollcommand=absent_scroll.set
        )
        absent_scroll.config(command=self.absent_tree.yview)
        
        self.absent_tree.heading('code', text='Mã SV')
        self.absent_tree.heading('name', text='Họ tên')
        self.absent_tree.heading('time', text='Giờ đánh dấu')
        
        self.absent_tree.column('code', width=100)
        self.absent_tree.column('name', width=200)
        self.absent_tree.column('time', width=80)
        
        self.absent_tree.pack(fill=tk.BOTH, expand=True)
        
        # Nút chuyển sang có mặt
        tk.Button(
            right_frame,
            text="⬅️ Đánh dấu CÓ MẶT",
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            cursor='hand2',
            command=self.mark_as_present
        ).pack(fill=tk.X, pady=5)
        
        # Footer buttons
        footer = tk.Frame(self.dialog, bg='white')
        footer.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            footer,
            text="💾 Lưu và Đóng",
            font=('Arial', 12, 'bold'),
            bg='#007bff',
            fg='white',
            cursor='hand2',
            command=self.save_and_close,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            footer,
            text="🔄 Làm mới",
            font=('Arial', 12),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=self.load_attendance_data,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            footer,
            text="❌ Đóng",
            font=('Arial', 12),
            bg='#e0e0e0',
            cursor='hand2',
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
    
    def load_attendance_data(self):
        """Tải dữ liệu điểm danh"""
        # Xóa dữ liệu cũ
        for item in self.present_tree.get_children():
            self.present_tree.delete(item)
        for item in self.absent_tree.get_children():
            self.absent_tree.delete(item)
        
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            
            # Lấy sinh viên có mặt
            cursor.execute("""
                SELECT s.student_id, s.student_code, u.full_name, a.check_in_time
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE a.session_id = %s AND a.status = 'present'
                ORDER BY a.check_in_time
            """, (self.session_id,))
            present_students = cursor.fetchall()
            
            # Lấy sinh viên vắng
            cursor.execute("""
                SELECT s.student_id, s.student_code, u.full_name, a.check_in_time
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE a.session_id = %s AND a.status = 'absent'
                ORDER BY s.student_code
            """, (self.session_id,))
            absent_students = cursor.fetchall()
            
            cursor.close()
            
            # Hiển thị sinh viên có mặt
            for student in present_students:
                time_str = student['check_in_time'].strftime('%H:%M:%S')
                self.present_tree.insert('', tk.END, values=(
                    student['student_code'],
                    student['full_name'],
                    time_str
                ), tags=(student['student_id'],))
            
            # Hiển thị sinh viên vắng
            for student in absent_students:
                time_str = student['check_in_time'].strftime('%H:%M:%S') if student['check_in_time'] else 'N/A'
                self.absent_tree.insert('', tk.END, values=(
                    student['student_code'],
                    student['full_name'],
                    time_str
                ), tags=(student['student_id'],))
            
            # Cập nhật thống kê
            total = len(present_students) + len(absent_students)
            present_rate = (len(present_students) / total * 100) if total > 0 else 0
            
            stats_text = f"📊 Thống kê: Tổng {total} SV | "
            stats_text += f"Có mặt: {len(present_students)} ({present_rate:.1f}%) | "
            stats_text += f"Vắng: {len(absent_students)} ({100-present_rate:.1f}%)"
            
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
    
    def mark_as_absent(self):
        """Chuyển sinh viên từ có mặt sang vắng"""
        selected = self.present_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên!")
            return
        
        item = self.present_tree.item(selected[0])
        student_id = item['tags'][0]
        student_code = item['values'][0]
        student_name = item['values'][1]
        
        if not messagebox.askyesno(
            "Xác nhận",
            f"Đánh dấu sinh viên {student_code} - {student_name} là VẮNG?"
        ):
            return
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE attendance 
                SET status = 'absent', check_in_time = NOW()
                WHERE session_id = %s AND student_id = %s
            """, (self.session_id, student_id))
            self.db.connection.commit()
            cursor.close()
            
            # Làm mới danh sách
            self.load_attendance_data()
            
            messagebox.showinfo("Thành công", f"Đã đánh dấu {student_code} là VẮNG")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
    
    def mark_as_present(self):
        """Chuyển sinh viên từ vắng sang có mặt"""
        selected = self.absent_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên!")
            return
        
        item = self.absent_tree.item(selected[0])
        student_id = item['tags'][0]
        student_code = item['values'][0]
        student_name = item['values'][1]
        
        if not messagebox.askyesno(
            "Xác nhận",
            f"Đánh dấu sinh viên {student_code} - {student_name} là CÓ MẶT?"
        ):
            return
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE attendance 
                SET status = 'present', check_in_time = NOW(), confidence_score = NULL
                WHERE session_id = %s AND student_id = %s
            """, (self.session_id, student_id))
            self.db.connection.commit()
            cursor.close()
            
            # Làm mới danh sách
            self.load_attendance_data()
            
            messagebox.showinfo("Thành công", f"Đã đánh dấu {student_code} là CÓ MẶT")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")
    
    def save_and_close(self):
        """Lưu và đóng cửa sổ"""
        # Gọi callback để làm mới danh sách ở cửa sổ chính
        if self.refresh_callback:
            self.refresh_callback()
        
        messagebox.showinfo("Thành công", "Đã lưu thay đổi!")
        self.dialog.destroy()

    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        if messagebox.askyesno("Xác nhận thoát", "Bạn có chắc muốn thoát?"):
            self.root.destroy()
            import sys
            sys.exit(0)



class UploadDocumentDialog:
    """Dialog upload tài liệu cho lớp học"""
    def __init__(self, parent, db, class_id, class_code, class_name):
        self.db = db
        self.class_id = class_id
        self.class_code = class_code
        self.class_name = class_name
        
        # Tạo dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"📁 Tài liệu lớp {class_code}")
        self.dialog.geometry("900x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        
        # Center dialog
        self.center_dialog()
        
        # Tạo widgets
        self.create_widgets()
        
        # Load danh sách tài liệu
        self.refresh_documents()
    
    def center_dialog(self):
        """Căn giữa dialog"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Tạo giao diện"""
        # Header
        header = tk.Frame(self.dialog, bg='#667eea', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"📁 Tài liệu lớp: {self.class_name}",
            font=('Arial', 16, 'bold'),
            bg='#667eea',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Label(
            header,
            text=f"Mã lớp: {self.class_code}",
            font=('Arial', 11),
            bg='#667eea',
            fg='#e2e8f0'
        ).pack(side=tk.LEFT, padx=20)
        
        # Toolbar
        toolbar = tk.Frame(self.dialog, bg='white')
        toolbar.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Button(
            toolbar,
            text="📤 Tải lên tài liệu",
            font=('Arial', 11, 'bold'),
            bg='#667eea',
            fg='white',
            cursor='hand2',
            command=self.upload_document
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🗑️ Xóa tài liệu",
            font=('Arial', 11),
            bg='#dc3545',
            fg='white',
            cursor='hand2',
            command=self.delete_document
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📥 Tải xuống",
            font=('Arial', 11),
            bg='#28a745',
            fg='white',
            cursor='hand2',
            command=self.download_document
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🔄 Làm mới",
            font=('Arial', 11),
            bg='#e0e0e0',
            cursor='hand2',
            command=self.refresh_documents
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="❌ Đóng",
            font=('Arial', 11),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(self.dialog, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.docs_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'name', 'type', 'size', 'description', 'uploaded_by', 'uploaded_at'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        vsb.config(command=self.docs_tree.yview)
        hsb.config(command=self.docs_tree.xview)
        
        self.docs_tree.heading('id', text='ID')
        self.docs_tree.heading('name', text='Tên tài liệu')
        self.docs_tree.heading('type', text='Loại file')
        self.docs_tree.heading('size', text='Kích thước')
        self.docs_tree.heading('description', text='Mô tả')
        self.docs_tree.heading('uploaded_by', text='Người tải lên')
        self.docs_tree.heading('uploaded_at', text='Ngày tải lên')
        
        self.docs_tree.column('id', width=50)
        self.docs_tree.column('name', width=250)
        self.docs_tree.column('type', width=100)
        self.docs_tree.column('size', width=100)
        self.docs_tree.column('description', width=200)
        self.docs_tree.column('uploaded_by', width=150)
        self.docs_tree.column('uploaded_at', width=150)
        
        self.docs_tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click để tải xuống
        self.docs_tree.bind('<Double-Button-1>', lambda e: self.download_document())
    
    def refresh_documents(self):
        """Làm mới danh sách tài liệu"""
        try:
            # Xóa danh sách cũ
            for item in self.docs_tree.get_children():
                self.docs_tree.delete(item)
            
            # Lấy danh sách tài liệu
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    cd.*,
                    u.full_name as uploader_name
                FROM class_documents cd
                LEFT JOIN users u ON cd.uploaded_by = u.user_id
                WHERE cd.class_id = %s
                ORDER BY cd.uploaded_at DESC
            """, (self.class_id,))
            
            documents = cursor.fetchall()
            cursor.close()
            
            for doc in documents:
                # Format file size
                size_bytes = doc.get('file_size', 0) or 0
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                
                # Format datetime
                uploaded_at = doc.get('uploaded_at', '')
                if uploaded_at:
                    uploaded_at = uploaded_at.strftime('%d/%m/%Y %H:%M')
                
                self.docs_tree.insert('', tk.END, values=(
                    doc['document_id'],
                    doc['document_name'],
                    doc.get('file_type', 'N/A'),
                    size_str,
                    doc.get('description', '')[:50] + '...' if doc.get('description', '') else '',
                    doc.get('uploader_name', 'N/A'),
                    uploaded_at
                ))
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách tài liệu:\n{str(e)}")
    
    def upload_document(self):
        """Upload tài liệu mới"""
        # Chọn file
        file_path = filedialog.askopenfilename(
            title="Chọn tài liệu",
            filetypes=[
                ("Tất cả file", "*.*"),
                ("PDF", "*.pdf"),
                ("Word", "*.doc *.docx"),
                ("Excel", "*.xls *.xlsx"),
                ("PowerPoint", "*.ppt *.pptx"),
                ("Ảnh", "*.jpg *.jpeg *.png *.gif"),
                ("Text", "*.txt"),
                ("Archive", "*.zip *.rar")
            ]
        )
        
        if not file_path:
            return
        
        # Lấy thông tin file
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Kiểm tra kích thước (giới hạn 50MB)
        if file_size > 50 * 1024 * 1024:
            messagebox.showerror("Lỗi", "File quá lớn! Giới hạn 50MB.")
            return
        
        # Hỏi mô tả
        description = self.ask_description()
        
        try:
            # Đọc file thành binary
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Lưu vào database
            cursor = self.db.connection.cursor()
            
            # Lấy user_id từ teacher
            cursor.execute("SELECT user_id FROM teachers WHERE teacher_id = (SELECT teacher_id FROM classes WHERE class_id = %s)", 
                          (self.class_id,))
            result = cursor.fetchone()
            user_id = result[0] if result else None
            
            # Insert file data vào database dưới dạng BLOB
            cursor.execute("""
                INSERT INTO class_documents 
                (class_id, document_name, file_data, file_size, file_type, description, uploaded_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.class_id, file_name, file_data, file_size, file_ext, description, user_id))
            
            self.db.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Thành công", f"Đã tải lên tài liệu vào database:\n{file_name}\nKích thước: {file_size / 1024:.1f} KB")
            self.refresh_documents()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải lên tài liệu:\n{str(e)}")
    
    def ask_description(self):
        """Hỏi mô tả cho tài liệu"""
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Mô tả tài liệu")
        dialog.geometry("400x250")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Nhập mô tả cho tài liệu (tùy chọn):",
            font=('Arial', 11, 'bold')
        ).pack(padx=20, pady=(20,10))
        
        text_widget = tk.Text(dialog, font=('Arial', 10), height=6, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        result = {'description': ''}
        
        def save():
            result['description'] = text_widget.get('1.0', tk.END).strip()
            dialog.destroy()
        
        def skip():
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu",
            font=('Arial', 10, 'bold'),
            bg='#28a745',
            fg='white',
            command=save,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="⏭️ Bỏ qua",
            font=('Arial', 10),
            bg='#6c757d',
            fg='white',
            command=skip,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result['description']
    
    def delete_document(self):
        """Xóa tài liệu"""
        selected = self.docs_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài liệu cần xóa!")
            return
        
        item = self.docs_tree.item(selected[0])
        doc_id = item['values'][0]
        doc_name = item['values'][1]
        
        if not messagebox.askyesno("Xác nhận", f"Xóa tài liệu:\n{doc_name}?"):
            return
        
        try:
            cursor = self.db.connection.cursor()
            
            # Xóa trực tiếp trong database (file đã lưu dưới dạng BLOB)
            cursor.execute("DELETE FROM class_documents WHERE document_id = %s", (doc_id,))
            self.db.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Thành công", "Đã xóa tài liệu khỏi database!")
            self.refresh_documents()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa tài liệu:\n{str(e)}")
    
    def download_document(self):
        """Tải xuống tài liệu"""
        selected = self.docs_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài liệu cần tải xuống!")
            return
        
        item = self.docs_tree.item(selected[0])
        doc_id = item['values'][0]
        doc_name = item['values'][1]
        
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT file_data, file_type FROM class_documents WHERE document_id = %s", (doc_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result or not result['file_data']:
                messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu tài liệu!")
                return
            
            file_data = result['file_data']
            
            # Chọn nơi lưu
            dest_path = filedialog.asksaveasfilename(
                title="Lưu tài liệu",
                initialfile=doc_name,
                defaultextension=os.path.splitext(doc_name)[1]
            )
            
            if dest_path:
                # Ghi file từ BLOB ra ổ đĩa
                with open(dest_path, 'wb') as f:
                    f.write(file_data)
                
                messagebox.showinfo("Thành công", f"Đã tải xuống từ database:\n{dest_path}")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải xuống:\n{str(e)}")
