# views/dialogs.py - Các dialog form với validation
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime

def create_date_entry(parent, width=32):
    """
    Tạo DateEntry với cấu hình ổn định, tránh lỗi mất bảng chọn
    """
    return DateEntry(
        parent,
        width=width,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        maxdate=datetime.now(),
        # Các tham số để ổn định widget
        showweeknumbers=False,
        showothermonthdays=True,
        selectbackground='#4472C4',
        selectforeground='white',
        normalbackground='white',
        normalforeground='black',
        weekendbackground='#f0f0f0',
        weekendforeground='black',
        othermonthforeground='gray',
        othermonthbackground='white',
        othermonthweforeground='gray',
        othermonthwebackground='white',
        headersbackground='#4472C4',
        headersforeground='white',
        # Quan trọng: Tránh lỗi mất calendar khi click nút lùi
        state='normal',
        cursor='hand2'
    )

class UpdateStudentDialog:
    """Dialog cập nhật sinh viên với validation"""
    
    def __init__(self, parent, db, student_data, on_success_callback):
        self.parent = parent
        self.db = db
        self.student_data = student_data
        self.on_success_callback = on_success_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Cập nhật sinh viên: {student_data['code']}")
        self.dialog.geometry("500x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        tk.Label(
            self.dialog,
            text="📝 Cập nhật thông tin sinh viên",
            font=('Arial', 14, 'bold'),
            bg='#4472C4',
            fg='white',
            pady=10
        ).pack(fill=tk.X)
        
        # Form frame
        form_frame = tk.Frame(self.dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fields = {}
        row = 0
        
        # Mã SV (disabled)
        tk.Label(form_frame, text="Mã sinh viên:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        code_entry = tk.Entry(form_frame, width=35, state='disabled')
        code_entry.insert(0, self.student_data['code'])
        code_entry.grid(row=row, column=1, pady=8)
        row += 1
        
        # Họ tên
        tk.Label(form_frame, text="Họ và tên: *", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['full_name'] = tk.Entry(form_frame, width=35)
        self.fields['full_name'].insert(0, self.student_data['name'])
        self.fields['full_name'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Email
        tk.Label(form_frame, text="Email: *", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['email'] = tk.Entry(form_frame, width=35)
        self.fields['email'].insert(0, self.student_data['email'])
        self.fields['email'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Số điện thoại
        tk.Label(form_frame, text="Số điện thoại:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['phone'] = tk.Entry(form_frame, width=35)
        self.fields['phone'].insert(0, self.student_data.get('phone', ''))
        self.fields['phone'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Giới tính
        tk.Label(form_frame, text="Giới tính:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        gender_map = {'Nam': 'male', 'Nữ': 'female', 'Khác': 'other'}
        reverse_map = {v: k for k, v in gender_map.items()}
        self.fields['gender'] = ttk.Combobox(form_frame, values=['Nam', 'Nữ', 'Khác'], width=32, state='readonly')
        self.fields['gender'].set(reverse_map.get(self.student_data.get('gender', 'male'), 'Nam'))
        self.fields['gender'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Ngày sinh (DateEntry)
        tk.Label(form_frame, text="Ngày sinh:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['date_of_birth'] = create_date_entry(form_frame, width=32)
        # Set ngày hiện tại nếu có
        if self.student_data.get('dob'):
            try:
                dob_str = self.student_data['dob']
                if '/' in dob_str:  # Format dd/mm/yyyy
                    dob = datetime.strptime(dob_str, '%d/%m/%Y')
                else:  # Format yyyy-mm-dd
                    dob = datetime.strptime(dob_str, '%Y-%m-%d')
                self.fields['date_of_birth'].set_date(dob)
            except:
                pass
        self.fields['date_of_birth'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Ngành học
        tk.Label(form_frame, text="Ngành học:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['major'] = tk.Entry(form_frame, width=35)
        self.fields['major'].insert(0, self.student_data.get('major', ''))
        self.fields['major'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Khóa học
        tk.Label(form_frame, text="Khóa học:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['enrollment_year'] = tk.Entry(form_frame, width=35)
        self.fields['enrollment_year'].insert(0, self.student_data.get('year', ''))
        self.fields['enrollment_year'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Note
        tk.Label(
            form_frame,
            text="* Trường bắt buộc",
            font=('Arial', 9, 'italic'),
            fg='red'
        ).grid(row=row, column=0, columnspan=2, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu",
            bg='#28a745',
            fg='white',
            font=('Arial', 12, 'bold'),
            command=self.save,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Hủy",
            bg='#6c757d',
            fg='white',
            font=('Arial', 12, 'bold'),
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """Lưu thông tin với validation"""
        from models.user import User
        from models.student import Student
        from utils.validators import Validators
        
        try:
            # Lấy dữ liệu
            full_name = self.fields['full_name'].get().strip()
            email = self.fields['email'].get().strip()
            phone = self.fields['phone'].get().strip()
            gender_map = {'Nam': 'male', 'Nữ': 'female', 'Khác': 'other'}
            gender = gender_map[self.fields['gender'].get()]
            date_of_birth = self.fields['date_of_birth'].get_date().strftime('%Y-%m-%d')
            major = self.fields['major'].get().strip()
            enrollment_year = self.fields['enrollment_year'].get().strip()
            
            # Validate
            is_valid, msg = Validators.validate_full_name(full_name)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            is_valid, msg = Validators.validate_email(email)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            is_valid, msg = Validators.validate_phone(phone)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            is_valid, msg = Validators.validate_date(date_of_birth)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            if enrollment_year:
                is_valid, msg = Validators.validate_year(enrollment_year)
                if not is_valid:
                    messagebox.showerror("Lỗi", msg)
                    return
            
            # Lấy user_id
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM students WHERE student_id = %s", (self.student_data['id'],))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy sinh viên")
                return
            
            user_id = result['user_id']
            
            # Cập nhật user
            user_model = User(self.db)
            user_model.update(
                user_id,
                full_name=full_name,
                email=email,
                phone=phone if phone else None,
                gender=gender,
                date_of_birth=date_of_birth
            )
            
            # Cập nhật student
            student_model = Student(self.db)
            student_model.update(
                self.student_data['id'],
                major=major,
                enrollment_year=int(enrollment_year) if enrollment_year else None
            )
            
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin sinh viên")
            self.dialog.destroy()
            self.on_success_callback()
            
        except ValueError as e:
            messagebox.showerror("Lỗi validation", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật:\n{str(e)}")


class UpdateTeacherDialog:
    """Dialog cập nhật giảng viên với validation"""
    
    def __init__(self, parent, db, teacher_data, on_success_callback):
        self.parent = parent
        self.db = db
        self.teacher_data = teacher_data
        self.on_success_callback = on_success_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Cập nhật giảng viên: {teacher_data['code']}")
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        tk.Label(
            self.dialog,
            text="📝 Cập nhật thông tin giảng viên",
            font=('Arial', 14, 'bold'),
            bg='#4472C4',
            fg='white',
            pady=10
        ).pack(fill=tk.X)
        
        # Form frame
        form_frame = tk.Frame(self.dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fields = {}
        row = 0
        
        # Mã GV (disabled)
        tk.Label(form_frame, text="Mã giảng viên:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        code_entry = tk.Entry(form_frame, width=35, state='disabled')
        code_entry.insert(0, self.teacher_data['code'])
        code_entry.grid(row=row, column=1, pady=8)
        row += 1
        
        # Họ tên
        tk.Label(form_frame, text="Họ và tên: *", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['full_name'] = tk.Entry(form_frame, width=35)
        self.fields['full_name'].insert(0, self.teacher_data['name'])
        self.fields['full_name'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Email
        tk.Label(form_frame, text="Email: *", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['email'] = tk.Entry(form_frame, width=35)
        self.fields['email'].insert(0, self.teacher_data['email'])
        self.fields['email'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Số điện thoại
        tk.Label(form_frame, text="Số điện thoại:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['phone'] = tk.Entry(form_frame, width=35)
        self.fields['phone'].insert(0, self.teacher_data.get('phone', ''))
        self.fields['phone'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Giới tính
        tk.Label(form_frame, text="Giới tính:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        gender_map = {'Nam': 'male', 'Nữ': 'female', 'Khác': 'other'}
        reverse_map = {v: k for k, v in gender_map.items()}
        self.fields['gender'] = ttk.Combobox(form_frame, values=['Nam', 'Nữ', 'Khác'], width=32, state='readonly')
        self.fields['gender'].set(reverse_map.get(self.teacher_data.get('gender', 'male'), 'Nam'))
        self.fields['gender'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Ngày sinh (DateEntry)
        tk.Label(form_frame, text="Ngày sinh:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['date_of_birth'] = create_date_entry(form_frame, width=32)
        # Set ngày hiện tại nếu có
        if self.teacher_data.get('dob'):
            try:
                dob_str = self.teacher_data['dob']
                if '/' in dob_str:
                    dob = datetime.strptime(dob_str, '%d/%m/%Y')
                else:
                    dob = datetime.strptime(dob_str, '%Y-%m-%d')
                self.fields['date_of_birth'].set_date(dob)
            except:
                pass
        self.fields['date_of_birth'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Khoa/Bộ môn
        tk.Label(form_frame, text="Khoa/Bộ môn:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky='w', pady=8
        )
        self.fields['department'] = tk.Entry(form_frame, width=35)
        self.fields['department'].insert(0, self.teacher_data.get('department', ''))
        self.fields['department'].grid(row=row, column=1, pady=8)
        row += 1
        
        # Note
        tk.Label(
            form_frame,
            text="* Trường bắt buộc",
            font=('Arial', 9, 'italic'),
            fg='red'
        ).grid(row=row, column=0, columnspan=2, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="💾 Lưu",
            bg='#28a745',
            fg='white',
            font=('Arial', 12, 'bold'),
            command=self.save,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Hủy",
            bg='#6c757d',
            fg='white',
            font=('Arial', 12, 'bold'),
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """Lưu thông tin với validation"""
        from models.user import User
        from models.teacher import Teacher
        from utils.validators import Validators
        
        try:
            # Lấy dữ liệu
            full_name = self.fields['full_name'].get().strip()
            email = self.fields['email'].get().strip()
            phone = self.fields['phone'].get().strip()
            gender_map = {'Nam': 'male', 'Nữ': 'female', 'Khác': 'other'}
            gender = gender_map[self.fields['gender'].get()]
            date_of_birth = self.fields['date_of_birth'].get_date().strftime('%Y-%m-%d')
            department = self.fields['department'].get().strip()
            
            # Validate
            is_valid, msg = Validators.validate_full_name(full_name)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            is_valid, msg = Validators.validate_email(email)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            is_valid, msg = Validators.validate_phone(phone)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            is_valid, msg = Validators.validate_date(date_of_birth)
            if not is_valid:
                messagebox.showerror("Lỗi", msg)
                return
            
            # Lấy user_id
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM teachers WHERE teacher_id = %s", (self.teacher_data['id'],))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                messagebox.showerror("Lỗi", "Không tìm thấy giảng viên")
                return
            
            user_id = result['user_id']
            
            # Cập nhật user
            user_model = User(self.db)
            user_model.update(
                user_id,
                full_name=full_name,
                email=email,
                phone=phone if phone else None,
                gender=gender,
                date_of_birth=date_of_birth
            )
            
            # Cập nhật teacher
            teacher_model = Teacher(self.db)
            teacher_model.update(
                self.teacher_data['id'],
                department=department
            )
            
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin giảng viên")
            self.dialog.destroy()
            self.on_success_callback()
            
        except ValueError as e:
            messagebox.showerror("Lỗi validation", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật:\n{str(e)}")
