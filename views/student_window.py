# gui/student_window.py - Dashboard Sinh Viên (THÊM TAB THỜI KHÓA BIỂU)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config import Config
from datetime import datetime
from PIL import Image, ImageTk
import os
import cv2
import json


class StudentWindow:
    def __init__(self, root, db, user, logout_callback):
        self.root = root
        self.db = db
        self.user = user
        self.logout_callback = logout_callback

        # Lấy thông tin sinh viên
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE user_id = %s", (user['user_id'],))
        self.student = cursor.fetchone()
        cursor.close()

        if not self.student:
            messagebox.showerror("Lỗi", "Không tìm thấy hồ sơ sinh viên!")
            self.logout_callback()
            return

        self.root.title(f"{Config.WINDOW_TITLE} - Sinh Viên")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(1000, 600)  # Kích thước tối thiểu
        self.root.resizable(True, True)  # Cho phép resize
        self.center_window()
        self.create_widgets()
        self.refresh_data()
        self.load_available_classes()

        # Overlay tự động refresh mỗi phút
        self.update_overlay()
        
        # Xử lý đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ======================== Hỗ trợ ============================
    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ======================== UI Chính ==========================
    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg='#667eea', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"🎓 {self.user['full_name']}",
            font=('Arial', 16, 'bold'),
            bg='#667eea',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            header,
            text=f"MSSV: {self.student['student_code']}",
            font=('Arial', 12),
            bg='#667eea',
            fg='white'
        ).pack(side=tk.LEFT)

        tk.Button(
            header,
            text="🚪 Đăng xuất",
            font=('Arial', 11),
            bg='white',
            fg='#667eea',
            command=self.logout
        ).pack(side=tk.RIGHT, padx=20)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Các tab
        self.create_register_tab()
        self.create_my_classes_tab()
        self.create_documents_tab()  # TAB TÀI LIỆU MỚI
        self.create_schedule_tab()  # TAB MỚI
        self.create_attendance_tab()
        self.create_face_upload_tab()
        self.create_change_password_tab()  # TAB ĐỔI MẬT KHẨU

    # ======================== TAB Đăng ký =======================
    def create_register_tab(self):
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="📝 Đăng ký tín chỉ")

        # Overlay trạng thái đăng ký
        self.overlay_label = tk.Label(tab, text="", font=("Arial", 12, "bold"), bg="#ffc107", fg="black")
        self.overlay_label.pack(fill=tk.X, padx=10, pady=5)

        # Info frame
        self.info_frame = tk.LabelFrame(tab, text="📅 Thông tin đăng ký", bg='white', font=('Arial', 11, 'bold'))
        self.info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_label = tk.Label(self.info_frame, text="", bg='white', justify='left', font=('Arial', 10))
        self.info_label.pack(padx=10, pady=10, anchor='w')

        # Treeview danh sách lớp
        tree_frame = tk.Frame(tab, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(tree_frame, text="Danh sách lớp có thể đăng ký:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=5)
        
        y_scroll = ttk.Scrollbar(tree_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.available_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "code", "name", "teacher", "credits", "slots", "semester", "year"),
            show="headings",
            yscrollcommand=y_scroll.set
        )
        y_scroll.config(command=self.available_tree.yview)
        
        headers = {
            "id": ("ID", 50), "code": ("Mã lớp", 100), "name": ("Tên lớp", 200),
            "teacher": ("Giảng viên", 150), "credits": ("TC", 70),
            "slots": ("Còn trống", 100), "semester": ("Kỳ", 50), "year": ("Năm học", 100)
        }
        for c, (text, width) in headers.items():
            self.available_tree.heading(c, text=text)
            self.available_tree.column(c, width=width)
        
        self.available_tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click để đăng ký lớp
        self.available_tree.bind('<Double-Button-1>', lambda e: self.register_class())

        # Nút đăng ký lớp
        btn_frame = tk.Frame(tab, bg='white')
        btn_frame.pack(pady=10)
        
        self.register_btn = tk.Button(
            btn_frame,
            text="✓ Đăng ký lớp",
            bg="#28a745", fg="white",
            font=('Arial', 12, 'bold'),
            command=self.register_class,
            width=20
        )
        self.register_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Làm mới",
            bg="#17a2b8", fg="white",
            font=('Arial', 12, 'bold'),
            command=self.refresh_available_classes,
            width=20
        ).pack(side=tk.LEFT, padx=10)

    # ======================== TAB Lớp của tôi ==================
    def create_my_classes_tab(self):
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="📖 Lớp của tôi")

        self.my_tree = ttk.Treeview(
            tab,
            columns=("id", "code", "name", "teacher", "credits", "semester", "year", "date"),
            show="headings"
        )
        self.my_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        headers = {
            "id": "ID", "code": "Mã lớp", "name": "Tên lớp",
            "teacher": "GV", "credits": "TC",
            "semester": "Kỳ", "year": "Năm", "date": "Ngày ĐK"
        }
        for c in headers:
            self.my_tree.heading(c, text=headers[c])
            self.my_tree.column(c, width=120)
        
        # Double-click để xem chi tiết
        self.my_tree.bind('<Double-Button-1>', lambda e: self.view_class_detail())

        # Button frame
        btn_frame = tk.Frame(tab, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="ℹ️ Xem chi tiết",
            bg="#17a2b8",
            fg="white",
            font=('Arial', 12, 'bold'),
            command=self.view_class_detail,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✗ Hủy đăng ký",
            bg="#dc3545",
            fg="white",
            font=('Arial', 12, 'bold'),
            command=self.drop_class,
            width=20
        ).pack(side=tk.LEFT, padx=5)

    # ======================== TAB TÀI LIỆU (MỚI) ==================
    def create_documents_tab(self):
        """Tab xem tài liệu của các lớp đã đăng ký"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="📁 Tài liệu")
        
        # Header
        header_frame = tk.Frame(tab, bg='#667eea', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📚 Tài liệu học tập",
            font=('Arial', 16, 'bold'),
            bg='#667eea',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Toolbar
        toolbar = tk.Frame(tab, bg='white')
        toolbar.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(toolbar, text="Chọn lớp:", font=('Arial', 11, 'bold'), bg='white').pack(side=tk.LEFT, padx=5)
        
        self.doc_class_var = tk.StringVar()
        self.doc_class_combo = ttk.Combobox(toolbar, textvariable=self.doc_class_var, 
                                            width=50, state='readonly')
        self.doc_class_combo.pack(side=tk.LEFT, padx=5)
        self.doc_class_combo.bind('<<ComboboxSelected>>', lambda e: self.load_class_documents())
        
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
            text="📥 Tải xuống",
            font=('Arial', 11),
            bg='#28a745',
            fg='white',
            cursor='hand2',
            command=self.download_student_document
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = tk.Frame(tab, bg='white')
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
        self.docs_tree.bind('<Double-Button-1>', lambda e: self.download_student_document())
        
        # Load danh sách lớp
        self.refresh_document_classes()
    
    def refresh_document_classes(self):
        """Làm mới danh sách lớp cho combo box tài liệu"""
        try:
            classes = self.db.get_student_classes_approved(self.student['student_id'])
            
            class_options = [f"{c['class_code']} - {c['class_name']}" for c in classes]
            self.doc_class_combo['values'] = class_options
            
            if class_options:
                self.doc_class_combo.current(0)
                self.load_class_documents()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp:\n{str(e)}")
    
    def refresh_documents(self):
        """Làm mới danh sách tài liệu"""
        self.refresh_document_classes()
    
    def load_class_documents(self):
        """Load tài liệu của lớp được chọn"""
        try:
            # Xóa danh sách cũ
            for item in self.docs_tree.get_children():
                self.docs_tree.delete(item)
            
            selected = self.doc_class_var.get()
            if not selected:
                return
            
            # Lấy class_code từ selection
            class_code = selected.split(' - ')[0]
            
            # Tìm class_id
            classes = self.db.get_student_classes_approved(self.student['student_id'])
            class_obj = next((c for c in classes if c['class_code'] == class_code), None)
            
            if not class_obj:
                return
            
            class_id = class_obj['class_id']
            
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
            """, (class_id,))
            
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
    
    def download_student_document(self):
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
                
                messagebox.showinfo("Thành công", f"Đã tải xuống:\n{dest_path}")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải xuống:\n{str(e)}")

    # ======================== TAB THỜI KHÓA BIỂU (MỚI) ==================
    def create_schedule_tab(self):
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="📅 Thời khóa biểu")

        # Header thông tin
        info_frame = tk.Frame(tab, bg='#e8eaf6', height=60)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        info_frame.pack_propagate(False)
        
        self.schedule_info_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 11, 'bold'),
            bg='#e8eaf6',
            fg='#333'
        )
        self.schedule_info_label.pack(pady=15)

        # Frame chứa bảng thời khóa biểu
        schedule_frame = tk.Frame(tab, bg='white')
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tạo canvas để scroll
        canvas = tk.Canvas(schedule_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=canvas.yview)
        self.schedule_content = tk.Frame(canvas, bg='white')

        self.schedule_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.schedule_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame nút điều khiển
        btn_frame = tk.Frame(tab, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Làm mới",
            bg="#17a2b8", fg="white",
            font=('Arial', 10, 'bold'),
            command=self.refresh_schedule,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            btn_frame,
            text="💡 Ghi chú: Nhắc nhở - Nghỉ học",
            font=('Arial', 9, 'italic'),
            bg='white',
            fg='#666'
        ).pack(side=tk.LEFT, padx=10)

    def refresh_schedule(self):
        """Làm mới thời khóa biểu - robust parsing và hiển thị (fix lỗi khi có nhiều lớp)"""
        # Xóa nội dung cũ
        for widget in self.schedule_content.winfo_children():
            widget.destroy()

        # Lấy danh sách lớp đã đăng ký (đã được lọc là approved)
        classes = self.db.get_student_classes_approved(self.student['student_id'])

        if not classes:
            tk.Label(
                self.schedule_content,
                text="📚 Bạn chưa đăng ký lớp nào",
                font=('Arial', 14),
                bg='white',
                fg='#999'
            ).pack(pady=50)
            self.schedule_info_label.config(text="")
            return

        # Thống kê
        total_credits = sum(c.get('credits', 0) for c in classes)
        self.schedule_info_label.config(
            text=f"🎓 Tổng số lớp: {len(classes)} | 📚 Tổng tín chỉ: {total_credits}"
        )

        # Chuẩn danh sách ngày (các tên hiển thị trong bảng)
        days = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]
        day_colors = ["#FFF4E6", "#E8F5E9", "#E3F2FD", "#F3E5F5", "#FFF9C4", "#FFE0B2", "#FFEBEE"]

        # Helper: chuẩn hoá các biến thể tên ngày về tên trong `days`
        mapping = {
            '2': "Thứ hai", 't2': "Thứ hai", 'thứ 2': "Thứ hai", 'thứ hai': "Thứ hai", 'thu 2': "Thứ hai", 'monday': "Thứ hai", 'mon': "Thứ hai",
            '3': "Thứ ba", 't3': "Thứ ba", 'thứ 3': "Thứ ba", 'thứ ba': "Thứ ba", 'tue': "Thứ ba", 'tuesday': "Thứ ba",
            '4': "Thứ tư", 't4': "Thứ tư", 'thứ 4': "Thứ tư", 'thứ tư': "Thứ tư", 'wed': "Thứ tư", 'wednesday': "Thứ tư",
            '5': "Thứ năm", 't5': "Thứ năm", 'thứ 5': "Thứ năm", 'thứ năm': "Thứ năm", 'thu 5': "Thứ năm", 'thursday': "Thứ năm",
            '6': "Thứ sáu", 't6': "Thứ sáu", 'thứ 6': "Thứ sáu", 'thứ sáu': "Thứ sáu", 'fri': "Thứ sáu", 'friday': "Thứ sáu",
            '7': "Thứ bảy", 't7': "Thứ bảy", 'thứ 7': "Thứ bảy", 'thứ bảy': "Thứ bảy", 'sat': "Thứ bảy", 'saturday': "Thứ bảy",
            'cn': "Chủ nhật", 'chủ nhật': "Chủ nhật", 'chu nhat': "Chủ nhật", 'sunday': "Chủ nhật", 'sun': "Chủ nhật", '0': "Chủ nhật", '8': "Chủ nhật"
        }

        def normalize_day(raw):
            if not raw:
                return None
            s = str(raw).strip().lower()
            s = s.replace('.', '').replace(',', '').replace('-', ' ').replace('_', ' ')
            if s in mapping:
                return mapping[s]
            s_noprefix = s.replace('thứ ', '').replace('thu ', '')
            if s_noprefix in mapping:
                return mapping[s_noprefix]
            return None

        # Map period number (absolute or relative) -> (session_name, period_in_session)
        def map_period(p, session_hint=None):
            """
            Input p: int (could be 1..10 meaning absolute slot)
            session_hint: 'Sáng'/'Chiều' or 'morning'/'afternoon' or None
            Return ('Sáng' or 'Chiều', period_index 1..5) or (None, None) if invalid
            """
            try:
                p = int(p)
            except Exception:
                return None, None
            # absolute 1..5 => morning
            if 1 <= p <= 5:
                if session_hint and session_hint.lower().startswith('c'):
                    # explicitly afternoon but small number -> treat as afternoon period p
                    return 'Chiều', p
                return 'Sáng', p
            # absolute 6..10 => afternoon (map to 1..5)
            if 6 <= p <= 10:
                return 'Chiều', p - 5
            # out of supported range
            return None, None

        # Khởi tạo cấu trúc lưu lịch: {day: {session: {period: [classes]}}}
        schedule_dict = {}
        for day in days:
            schedule_dict[day] = {'Sáng': {i: [] for i in range(1, 6)}, 'Chiều': {i: [] for i in range(1, 6)}}

        # Parse schedule từ từng lớp (hỗ trợ nhiều kiểu dữ liệu)
        for cls in classes:
            raw_schedule = cls.get('schedule')
            if not raw_schedule:
                continue

            # chuẩn thành Python object
            schedule_obj = None
            try:
                if isinstance(raw_schedule, str):
                    schedule_obj = json.loads(raw_schedule)
                else:
                    schedule_obj = raw_schedule
            except Exception:
                print(f"[refresh_schedule] Không parse được schedule cho lớp {cls.get('class_code')}")
                continue

            # Nếu dict mapping day -> entries
            if isinstance(schedule_obj, dict):
                for k, entries in schedule_obj.items():
                    norm_day = normalize_day(k) or k
                    if norm_day not in schedule_dict:
                        continue
                    if not isinstance(entries, list):
                        continue
                    for entry in entries:
                        if not isinstance(entry, dict):
                            continue
                        session_hint = entry.get('session', '')
                        periods = entry.get('periods', entry.get('period', []))
                        room = entry.get('room', 'N/A')
                        # normalize list
                        if isinstance(periods, int):
                            periods = [periods]
                        if not isinstance(periods, list):
                            continue
                        for p in periods:
                            sess, per = map_period(p, session_hint)
                            if not sess:
                                continue
                            # per must be 1..5
                            if 1 <= per <= 5:
                                schedule_dict[norm_day][sess][per].append({
                                    'class_code': cls.get('class_code'),
                                    'class_name': cls.get('class_name'),
                                    'teacher': cls.get('teacher_name'),
                                    'room': room,
                                    'credits': cls.get('credits', 0)
                                })

            # Nếu list of entries
            elif isinstance(schedule_obj, list):
                for entry in schedule_obj:
                    if not isinstance(entry, dict):
                        continue

                    raw_day = entry.get('day', '')
                    norm_day = normalize_day(raw_day)
                    if not norm_day or norm_day not in schedule_dict:
                        continue

                    # derive session hint from entry (if present)
                    session_hint = entry.get('session', '')
                    # support both 'from'/'to' and 'periods' or 'period'
                    if 'from' in entry and 'to' in entry:
                        try:
                            p_from = int(entry.get('from'))
                            p_to = int(entry.get('to'))
                        except Exception:
                            continue
                        if p_from > p_to:
                            continue
                        period_list = list(range(p_from, p_to + 1))
                    else:
                        period_list = entry.get('periods', entry.get('period', []))
                        if isinstance(period_list, int):
                            period_list = [period_list]
                        if not isinstance(period_list, list):
                            continue

                    room = entry.get('room', 'N/A')

                    for p in period_list:
                        sess, per = map_period(p, session_hint)
                        if not sess:
                            continue
                        if 1 <= per <= 5:
                            schedule_dict[norm_day][sess][per].append({
                                'class_code': cls.get('class_code'),
                                'class_name': cls.get('class_name'),
                                'teacher': cls.get('teacher_name'),
                                'room': room,
                                'credits': cls.get('credits', 0)
                            })
            else:
                print(f"[refresh_schedule] Kiểu schedule không hỗ trợ: {type(schedule_obj)} cho lớp {cls.get('class_code')}")
                continue

        # Vẽ bảng thời khóa biểu (giữ nguyên layout)
        table_frame = tk.Frame(self.schedule_content, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        header_row = tk.Frame(table_frame, bg='white')
        header_row.grid(row=0, column=0, columnspan=len(days) + 1, sticky='ew', pady=2)

        tk.Label(
            header_row,
            text="Buổi | tiết",
            font=('Arial', 10, 'bold'),
            bg='#9575CD',
            fg='white',
            width=12,
            height=2,
            relief='solid',
            borderwidth=1
        ).grid(row=0, column=0, padx=1)

        for idx, (day, color) in enumerate(zip(days, day_colors)):
            tk.Label(
                header_row,
                text=day,
                font=('Arial', 10, 'bold'),
                bg=color,
                fg='#333',
                width=18,
                height=2,
                relief='solid',
                borderwidth=1
            ).grid(row=0, column=idx+1, padx=1)

        row_index = 1
        for session in ['Sáng', 'Chiều']:
            for period in range(1, 6):
                session_label = f"{session}\n{period}"
                bg_color = '#E8EAF6' if session == 'Sáng' else '#FFF3E0'

                tk.Label(
                    table_frame,
                    text=session_label,
                    font=('Arial', 9, 'bold'),
                    bg=bg_color,
                    fg='#333',
                    width=12,
                    height=4,
                    relief='solid',
                    borderwidth=1,
                    justify='center'
                ).grid(row=row_index, column=0, padx=1, pady=1, sticky='nsew')

                for day_idx, day in enumerate(days):
                    classes_in_period = schedule_dict[day][session][period]

                    cell_frame = tk.Frame(table_frame, bg='white', relief='solid', borderwidth=1)
                    cell_frame.grid(row=row_index, column=day_idx+1, padx=1, pady=1, sticky='nsew')

                    if classes_in_period:
                        for cls_info in classes_in_period:
                            class_text = f"{cls_info['class_name']}"
                            tk.Label(
                                cell_frame,
                                text=class_text,
                                font=('Arial', 8, 'bold'),
                                bg='#BBDEFB',
                                fg='#0D47A1',
                                relief='raised',
                                borderwidth=1,
                                justify='center',
                                wraplength=120
                            ).pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                    else:
                        tk.Label(cell_frame, text="", bg='white', height=3).pack(fill=tk.BOTH, expand=True)

                row_index += 1

        for i in range(len(days) + 1):
            table_frame.grid_columnconfigure(i, weight=1, minsize=120)


    # ======================== TAB Điểm danh ===================
    def create_attendance_tab(self):
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="📊 Điểm danh")

        self.summary_label = tk.Label(tab, text="Đang tải...", font=("Arial", 12))
        self.summary_label.pack(pady=10)

        self.att_tree = ttk.Treeview(
            tab,
            columns=("id", "class", "date", "session", "status"),
            show="headings"
        )
        self.att_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        headers = {
            "id": "ID", "class": "Lớp",
            "date": "Ngày", "session": "Buổi", "status": "Trạng thái"
        }
        for c in headers:
            self.att_tree.heading(c, text=headers[c])
            self.att_tree.column(c, width=120)

    # ======================== TAB Upload ảnh ===================
    def create_face_upload_tab(self):
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text="📷 Ảnh khuôn mặt")

        # Hướng dẫn
        info_frame = tk.LabelFrame(tab, text="📖 Hướng dẫn", bg='white', font=('Arial', 11, 'bold'))
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_text = """
• Upload ảnh khuôn mặt để sử dụng cho điểm danh tự động
• Yêu cầu: Ảnh rõ nét, khuôn mặt nhìn thẳng, ánh sáng đủ
• Định dạng: JPG, PNG, BMP (tối đa 5MB)
• Kích thước khuyến nghị: 800x800 pixels
• Ảnh sẽ được lưu trực tiếp vào hệ thống
        """
        tk.Label(info_frame, text=info_text, bg='white', justify='left', 
                 font=('Arial', 10)).pack(padx=10, pady=10)

        # Preview frame
        preview_frame = tk.LabelFrame(tab, text="🖼️ Ảnh hiện tại", bg='white', font=('Arial', 11, 'bold'))
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.preview_label = tk.Label(
            preview_frame, 
            bg="white",
            text="Đang tải...",
            font=('Arial', 12),
            fg='gray'
        )
        self.preview_label.pack(pady=20, expand=True)

        # Control buttons - Row 1
        control_frame1 = tk.Frame(tab, bg="white")
        control_frame1.pack(pady=5)

        tk.Button(
            control_frame1, 
            text="📂 Chọn ảnh từ máy", 
            bg="#007bff", 
            fg="white",
            font=("Arial", 11, 'bold'), 
            command=self.select_face_image,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame1, 
            text="📸 Chụp từ Webcam", 
            bg="#6f42c1", 
            fg="white",
            font=("Arial", 11, 'bold'), 
            command=self.capture_from_webcam,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame1, 
            text="💾 Lưu vào hệ thống", 
            bg="#28a745", 
            fg="white",
            font=("Arial", 11, 'bold'), 
            command=self.save_face_image,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Control buttons - Row 2
        control_frame2 = tk.Frame(tab, bg="white")
        control_frame2.pack(pady=5)
        
        tk.Button(
            control_frame2, 
            text="👁️ Xem ảnh đầy đủ", 
            bg="#17a2b8", 
            fg="white",
            font=("Arial", 11, 'bold'), 
            command=self.view_full_face_image,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame2, 
            text="🗑️ Xóa ảnh", 
            bg="#dc3545", 
            fg="white",
            font=("Arial", 11, 'bold'), 
            command=self.delete_face_image,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        self.face_image_path = None
        self.load_existing_face_image()

    # ======================== Nghiệp vụ ======================
    def refresh_data(self):
        self.refresh_available_classes()
        self.refresh_my_classes()
        self.refresh_document_classes()  # Thêm refresh documents
        self.refresh_schedule()  # Thêm refresh schedule
        self.refresh_attendance()

    def refresh_available_classes(self):
        self.load_available_classes()

    def load_available_classes(self):
        """Load danh sách lớp có thể đăng ký"""
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)

        window = self.db.get_latest_registration_window()
        now = datetime.now()
        
        if not window:
            self.show_overlay_message("⚠️ Chưa có lịch đăng ký tín chỉ nào được thiết lập")
            self.update_info_label(None, False)
            return
        
        self.registration_open = (window['start_datetime'] <= now <= window['end_datetime'])
        
        if not self.registration_open:
            start_str = window['start_datetime'].strftime('%d/%m/%Y %H:%M')
            end_str = window['end_datetime'].strftime('%d/%m/%Y %H:%M')
            self.show_overlay_message(f"⏰ Ngoài giờ đăng ký! Thời gian: {start_str} - {end_str}")
            self.update_info_label(window, False)
            return
        
        semester = window.get('semester')
        academic_year = window.get('academic_year')
        
        if not semester or not academic_year:
            self.show_overlay_message("⚠️ Khung giờ đăng ký chưa có thông tin học kỳ/năm học")
            self.update_info_label(window, False)
            return
        
        classes = self.db.get_approved_classes_by_period(semester, academic_year)

        if not classes:
            self.show_overlay_message(f"📚 Chưa có lớp nào được duyệt cho Kỳ {semester} - {academic_year}")
            self.update_info_label(window, True)
            return

        for cls in classes:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM class_enrollments 
                WHERE class_id=%s AND status='enrolled'
            """, (cls['class_id'],))
            enrolled = cursor.fetchone()[0]
            cursor.close()
            
            slots_left = cls['max_students'] - enrolled
            
            self.available_tree.insert(
                '',
                'end',
                values=(
                    cls['class_id'],
                    cls['class_code'],
                    cls['class_name'],
                    cls['teacher_name'],
                    cls['credits'],
                    f"{enrolled}/{cls['max_students']} (còn {slots_left})",
                    cls['semester'],
                    cls['academic_year'],
                )
            )

        self.hide_overlay_message()
        self.update_info_label(window, True)

    def show_overlay_message(self, text):
        self.overlay_label.config(text=text)
        self.register_btn.config(state=tk.DISABLED)

    def hide_overlay_message(self):
        self.overlay_label.config(text="")
        self.register_btn.config(state=tk.NORMAL)
    
    def update_info_label(self, window, is_open):
        if not window:
            self.info_label.config(text="Chưa có thông tin đăng ký")
            return
        
        semester = window.get('semester', 'N/A')
        academic_year = window.get('academic_year', 'N/A')
        start_str = window['start_datetime'].strftime('%d/%m/%Y %H:%M')
        end_str = window['end_datetime'].strftime('%d/%m/%Y %H:%M')
        
        status_text = "🟢 ĐANG MỞ" if is_open else "🔴 ĐÓNG"
        status_color = "#28a745" if is_open else "#dc3545"
        
        info_text = f"""
Học kỳ: {semester} | Năm học: {academic_year}
Thời gian: {start_str} - {end_str}
Trạng thái: {status_text}
        """
        
        self.info_label.config(text=info_text, fg=status_color)

    def update_overlay(self):
        self.load_available_classes()
        self.root.after(60000, self.update_overlay)

    def register_class(self):
        if not getattr(self, 'registration_open', False):
            messagebox.showwarning("Ngoài giờ đăng ký", "Hiện tại chưa tới giờ đăng ký hoặc đã hết giờ!")
            return

        sel = self.available_tree.selection()
        if not sel:
            messagebox.showwarning("Chọn lớp", "Vui lòng chọn lớp!")
            return

        item = self.available_tree.item(sel[0])
        class_id = item['values'][0]
        class_name = item['values'][2]

        if not messagebox.askyesno("Xác nhận", f"Đăng ký lớp {class_name}?"):
            return

        success, msg = self.db.enroll_student(class_id, self.student['student_id'])
        if success:
            messagebox.showinfo("OK", "Đăng ký thành công!")
            self.refresh_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def refresh_my_classes(self):
        self.my_tree.delete(*self.my_tree.get_children())
        classes = self.db.get_student_classes_approved(self.student['student_id'])

        for c in classes:
            date = c['enrollment_date'].strftime('%d/%m/%Y')
            self.my_tree.insert('', tk.END, values=(
                c['class_id'], c['class_code'], c['class_name'],
                c['teacher_name'], c['credits'],
                c['semester'], c['academic_year'], date
            ))

    def view_class_detail(self):
        """Xem thông tin chi tiết lớp học"""
        sel = self.my_tree.selection()
        if not sel:
            messagebox.showwarning("Chọn lớp", "Vui lòng chọn lớp cần xem!")
            return

        item = self.my_tree.item(sel[0])
        class_id = item['values'][0]
        
        # Lấy thông tin chi tiết lớp
        cursor = self.db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, u.full_name as teacher_name, u.email as teacher_email,
                   u.phone as teacher_phone
            FROM classes c
            JOIN teachers t ON c.teacher_id = t.teacher_id
            JOIN users u ON t.user_id = u.user_id
            WHERE c.class_id = %s
        """, (class_id,))
        class_info = cursor.fetchone()
        
        # Đếm số sinh viên
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM class_enrollments
            WHERE class_id = %s AND status = 'enrolled'
        """, (class_id,))
        enrollment_count = cursor.fetchone()['total']
        
        # Lấy lịch sử điểm danh của sinh viên trong lớp này
        cursor.execute("""
            SELECT s.session_date, s.session_time, a.status
            FROM attendance a
            JOIN sessions s ON a.session_id = s.session_id
            WHERE s.class_id = %s AND a.student_id = %s
            ORDER BY s.session_date DESC, s.session_time DESC
            LIMIT 10
        """, (class_id, self.student['student_id']))
        attendance_history = cursor.fetchall()
        
        cursor.close()
        
        if not class_info:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin lớp!")
            return
        
        # Tạo dialog hiển thị
        self._show_class_detail_dialog(class_info, enrollment_count, attendance_history)
    
    def _show_class_detail_dialog(self, class_info, enrollment_count, attendance_history):
        """Hiển thị dialog thông tin chi tiết lớp"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Chi tiết lớp: {class_info['class_code']}")
        dialog.geometry("700x650")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='white')
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350)
        y = (dialog.winfo_screenheight() // 2) - (325)
        dialog.geometry(f'700x650+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg='#4a5568', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"📚 {class_info['class_name']}",
            font=('Arial', 16, 'bold'),
            bg='#4a5568',
            fg='white'
        ).pack(pady=10)
        
        tk.Label(
            header,
            text=f"Mã lớp: {class_info['class_code']}",
            font=('Arial', 11),
            bg='#4a5568',
            fg='#e2e8f0'
        ).pack()
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg='white')
        
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Thông tin cơ bản
        info_frame = tk.LabelFrame(
            content_frame, 
            text="📋 Thông tin cơ bản", 
            bg='white', 
            font=('Arial', 11, 'bold'),
            fg='#2d3748'
        )
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_data = [
            ("Tên lớp:", class_info['class_name']),
            ("Mã lớp:", class_info['class_code']),
            ("Số tín chỉ:", f"{class_info['credits']} TC"),
            ("Học kỳ:", f"Kỳ {class_info['semester']} - {class_info['academic_year']}"),
            ("Sĩ số:", f"{enrollment_count}/{class_info['max_students']} sinh viên"),
            ("Trạng thái:", "✅ Đã duyệt" if class_info['status'] == 'approved' else "⏳ Chờ duyệt")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = tk.Frame(info_frame, bg='white')
            row.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(
                row,
                text=label,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg='#4a5568',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=value,
                font=('Arial', 10),
                bg='white',
                fg='#2d3748',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Thông tin giảng viên
        teacher_frame = tk.LabelFrame(
            content_frame, 
            text="👨‍🏫 Thông tin giảng viên", 
            bg='white', 
            font=('Arial', 11, 'bold'),
            fg='#2d3748'
        )
        teacher_frame.pack(fill=tk.X, padx=10, pady=10)
        
        teacher_data = [
            ("Họ tên:", class_info['teacher_name']),
            ("Email:", class_info['teacher_email'] or "Chưa cập nhật"),
            ("Số điện thoại:", class_info['teacher_phone'] or "Chưa cập nhật")
        ]
        
        for label, value in teacher_data:
            row = tk.Frame(teacher_frame, bg='white')
            row.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(
                row,
                text=label,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg='#4a5568',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=value,
                font=('Arial', 10),
                bg='white',
                fg='#2d3748',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Lịch sử điểm danh
        attendance_frame = tk.LabelFrame(
            content_frame, 
            text="📊 Lịch sử điểm danh (10 buổi gần nhất)", 
            bg='white', 
            font=('Arial', 11, 'bold'),
            fg='#2d3748'
        )
        attendance_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if attendance_history:
            # Treeview
            att_tree = ttk.Treeview(
                attendance_frame,
                columns=("date", "time", "status"),
                show="headings",
                height=8
            )
            
            att_tree.heading("date", text="Ngày")
            att_tree.heading("time", text="Buổi")
            att_tree.heading("status", text="Trạng thái")
            
            att_tree.column("date", width=120)
            att_tree.column("time", width=100)
            att_tree.column("status", width=120)
            
            for record in attendance_history:
                status_text = "✅ Có mặt" if record['status'] == 'present' else "❌ Vắng"
                att_tree.insert('', tk.END, values=(
                    record['session_date'].strftime('%d/%m/%Y'),
                    record['session_time'],
                    status_text
                ))
            
            att_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Thống kê
            present_count = sum(1 for r in attendance_history if r['status'] == 'present')
            absent_count = len(attendance_history) - present_count
            
            stats_text = f"Có mặt: {present_count} | Vắng: {absent_count}"
            tk.Label(
                attendance_frame,
                text=stats_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg='#4a5568'
            ).pack(pady=5)
        else:
            tk.Label(
                attendance_frame,
                text="Chưa có dữ liệu điểm danh",
                font=('Arial', 10, 'italic'),
                bg='white',
                fg='#999'
            ).pack(pady=20)
        
        # Tài liệu lớp học
        docs_frame = tk.LabelFrame(
            content_frame, 
            text="📁 Tài liệu lớp học", 
            bg='white', 
            font=('Arial', 11, 'bold'),
            fg='#2d3748'
        )
        docs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lấy danh sách tài liệu
        cursor = self.db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                cd.document_id,
                cd.document_name,
                cd.file_type,
                cd.file_size,
                cd.uploaded_at,
                u.full_name as uploader_name
            FROM class_documents cd
            LEFT JOIN users u ON cd.uploaded_by = u.user_id
            WHERE cd.class_id = %s
            ORDER BY cd.uploaded_at DESC
        """, (class_info['class_id'],))
        documents = cursor.fetchall()
        cursor.close()
        
        if documents:
            # Treeview tài liệu
            docs_tree = ttk.Treeview(
                docs_frame,
                columns=("name", "type", "size", "date"),
                show="headings",
                height=6
            )
            
            docs_tree.heading("name", text="Tên tài liệu")
            docs_tree.heading("type", text="Loại")
            docs_tree.heading("size", text="Kích thước")
            docs_tree.heading("date", text="Ngày tải lên")
            
            docs_tree.column("name", width=250)
            docs_tree.column("type", width=80)
            docs_tree.column("size", width=100)
            docs_tree.column("date", width=120)
            
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
                
                docs_tree.insert('', tk.END, values=(
                    doc['document_name'],
                    doc.get('file_type', 'N/A'),
                    size_str,
                    uploaded_at
                ), tags=(doc['document_id'],))
            
            docs_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Button tải xuống
            def download_selected_doc():
                selected = docs_tree.selection()
                if not selected:
                    messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài liệu cần tải!")
                    return
                
                item = docs_tree.item(selected[0])
                doc_id = item['tags'][0]
                doc_name = item['values'][0]
                
                try:
                    cursor = self.db.connection.cursor(dictionary=True)
                    cursor.execute("SELECT file_data FROM class_documents WHERE document_id = %s", (doc_id,))
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
                        with open(dest_path, 'wb') as f:
                            f.write(file_data)
                        messagebox.showinfo("Thành công", f"Đã tải xuống:\n{dest_path}")
                
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể tải xuống:\n{str(e)}")
            
            # Double-click để tải
            docs_tree.bind('<Double-Button-1>', lambda e: download_selected_doc())
            
            tk.Button(
                docs_frame,
                text="📥 Tải xuống tài liệu",
                font=('Arial', 10, 'bold'),
                bg='#28a745',
                fg='white',
                command=download_selected_doc,
                width=20
            ).pack(pady=10)
            
            tk.Label(
                docs_frame,
                text=f"💡 Tổng số: {len(documents)} tài liệu | Double-click để tải nhanh",
                font=('Arial', 9, 'italic'),
                bg='white',
                fg='#666'
            ).pack(pady=5)
        else:
            tk.Label(
                docs_frame,
                text="📭 Chưa có tài liệu nào",
                font=('Arial', 10, 'italic'),
                bg='white',
                fg='#999'
            ).pack(pady=20)
        
        # Button đóng
        tk.Button(
            dialog,
            text="✖️ Đóng",
            font=('Arial', 11, 'bold'),
            bg='#6c757d',
            fg='white',
            command=dialog.destroy,
            width=15
        ).pack(pady=10)
    
    def drop_class(self):
        sel = self.my_tree.selection()
        if not sel:
            messagebox.showwarning("Chọn lớp", "Chọn lớp cần hủy!")
            return

        item = self.my_tree.item(sel[0])
        class_id = item['values'][0]
        class_name = item['values'][2]

        if not messagebox.askyesno("Xác nhận", f"Hủy lớp {class_name}?"):
            return

        cursor = self.db.connection.cursor()
        cursor.execute("""
            UPDATE class_enrollments
            SET status='dropped'
            WHERE class_id=%s AND student_id=%s
        """, (class_id, self.student['student_id']))
        self.db.connection.commit()
        cursor.close()

        messagebox.showinfo("OK", "Đã hủy đăng ký!")
        self.refresh_data()

    def refresh_attendance(self):
        self.att_tree.delete(*self.att_tree.get_children())
        records = self.db.get_attendance_stats(self.student['student_id'], None, None)

        total = len(records)
        present = sum(1 for r in records if r['status'] == 'present')
        absent = sum(1 for r in records if r['status'] == 'absent')
        rate = (present / total * 100) if total else 0

        self.summary_label.config(
            text=f"Tổng: {total} | Có mặt: {present} | Vắng: {absent} | Tỷ lệ: {rate:.1f}%"
        )

        for r in records:
            self.att_tree.insert('', tk.END, values=(
                r['attendance_id'],
                r['class_name'],
                r['session_date'].strftime('%d/%m/%Y'),
                r['session_time'],
                r['status']
            ))

    # ======================== Upload ảnh ======================
    def capture_from_webcam(self):
        """Chụp ảnh từ webcam"""
        from utils.webcam_capture import WebcamCapture
        import cv2
        
        def on_capture(frame):
            """Callback khi chụp ảnh xong"""
            # Lưu frame vào file tạm
            temp_file = WebcamCapture.save_frame_to_temp(frame)
            self.face_image_path = temp_file
            
            # Hiển thị preview
            try:
                # Chuyển BGR sang RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((250, 250))
                self.tk_img = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.tk_img)
                
                messagebox.showinfo("Thành công", 
                    "Đã chụp ảnh từ webcam!\n\n"
                    "Click 'Lưu vào hệ thống' để lưu ảnh.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể hiển thị ảnh:\n{e}")
        
        # Mở webcam capture
        webcam = WebcamCapture(self.root, on_capture, "Chụp ảnh khuôn mặt")
        webcam.open_camera()
    
    def select_face_image(self):
        """Chọn ảnh từ máy tính và hiển thị preview"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh khuôn mặt",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return

        # Validate ảnh trước khi hiển thị
        from utils.image_handler import ImageHandler
        
        is_valid, msg = ImageHandler.validate_image(file_path)
        if not is_valid:
            messagebox.showerror("Ảnh không hợp lệ", f"Không thể sử dụng ảnh này:\n{msg}")
            return

        self.face_image_path = os.path.abspath(file_path)

        # Hiển thị preview
        try:
            img = Image.open(self.face_image_path)
            img.thumbnail((250, 250))  # Giữ tỷ lệ
            self.tk_img = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.tk_img)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị ảnh:\n{e}")

    def save_face_image(self):
        """Lưu ảnh vào database"""
        if not self.face_image_path:
            messagebox.showwarning("Thiếu ảnh", "Vui lòng chọn ảnh trước!")
            return

        # Xác nhận lưu
        if not messagebox.askyesno("Xác nhận", 
            "Lưu ảnh khuôn mặt vào hệ thống?\n\n"
            "Ảnh này sẽ được sử dụng cho điểm danh tự động."):
            return

        try:
            from utils.image_handler import FaceImageDB
            
            # Lưu vào database
            face_db = FaceImageDB(self.db)
            success, message = face_db.save_face_image(
                student_id=self.student['student_id'],
                image_path=self.face_image_path,
                compress=True
            )
            
            if success:
                # Auto-train model AI
                try:
                    from services.face_recognition_service import face_service
                    print("🤖 Đang tự động cập nhật AI model...")
                    result = face_service.train_model(self.db)
                    if result.get('success'):
                        print(f"✓ AI model đã được cập nhật tự động!")
                    else:
                        print(f"⚠️ Không thể cập nhật AI: {result.get('error')}")
                except Exception as e:
                    print(f"⚠️ Lỗi auto-train: {e}")
                
                messagebox.showinfo("Thành công", 
                    f"Đã lưu ảnh khuôn mặt thành công!\n\n{message}\n\n"
                    "Ảnh của bạn đã được lưu vào hệ thống và sẵn sàng cho điểm danh tự động.\n\n"
                    "🤖 Hệ thống AI đang được cập nhật tự động...")
                
                # Refresh để hiển thị ảnh từ DB
                self.load_existing_face_image()
            else:
                messagebox.showerror("Lỗi", f"Không thể lưu ảnh:\n{message}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu ảnh:\n{str(e)}")

    def load_existing_face_image(self):
        """Load ảnh hiện có từ database"""
        try:
            from utils.image_handler import FaceImageDB
            import cv2
            
            face_db = FaceImageDB(self.db)
            
            # Lấy ảnh từ database
            image_array = face_db.get_face_image(
                student_id=self.student['student_id'],
                as_array=True
            )
            
            if image_array is not None:
                # Chuyển BGR sang RGB
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                
                # Chuyển sang PIL Image
                pil_image = Image.fromarray(image_rgb)
                pil_image.thumbnail((250, 250))  # Giữ tỷ lệ
                
                # Hiển thị
                self.tk_img = ImageTk.PhotoImage(pil_image)
                self.preview_label.config(image=self.tk_img)
                
                # Hiển thị thông tin
                base64_str = face_db.get_face_image(
                    student_id=self.student['student_id'],
                    as_array=False
                )
                if base64_str:
                    from utils.image_handler import ImageHandler
                    info = ImageHandler.get_image_info(base64_str)
                    info_text = f"Ảnh hiện tại: {info.get('width')}x{info.get('height')} | {info.get('size_kb')} KB"
                    
                    # Tạo label info nếu chưa có
                    if not hasattr(self, 'face_info_label'):
                        self.face_info_label = tk.Label(
                            self.preview_label.master,
                            text="",
                            font=('Arial', 9),
                            bg='white',
                            fg='gray'
                        )
                        self.face_info_label.pack(pady=5)
                    
                    self.face_info_label.config(text=info_text)
            else:
                # Chưa có ảnh - hiển thị placeholder
                self.preview_label.config(image='', text='Chưa có ảnh khuôn mặt\n\nClick "Chọn ảnh" để upload')
                
                if hasattr(self, 'face_info_label'):
                    self.face_info_label.config(text='')
                    
        except Exception as e:
            print(f"Lỗi load ảnh: {e}")
            self.preview_label.config(image='', text='Chưa có ảnh khuôn mặt')


    def view_full_face_image(self):
        """Xem ảnh khuôn mặt đầy đủ trong dialog"""
        try:
            from utils.image_handler import FaceImageDB
            import cv2
            
            face_db = FaceImageDB(self.db)
            image_array = face_db.get_face_image(
                student_id=self.student['student_id'],
                as_array=True
            )
            
            if image_array is None:
                messagebox.showinfo("Thông báo", "Bạn chưa upload ảnh khuôn mặt")
                return
            
            # Tạo dialog xem ảnh
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Ảnh khuôn mặt: {self.user['full_name']}")
            dialog.geometry("600x700")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Info frame
            info_frame = tk.Frame(dialog, bg='white')
            info_frame.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Label(
                info_frame, 
                text=f"Sinh viên: {self.user['full_name']}", 
                bg='white', 
                font=('Arial', 12, 'bold')
            ).pack(anchor='w')
            
            tk.Label(
                info_frame, 
                text=f"MSSV: {self.student['student_code']}", 
                bg='white', 
                font=('Arial', 11)
            ).pack(anchor='w')
            
            # Image frame
            image_frame = tk.Frame(dialog, bg='white')
            image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Resize ảnh để hiển thị
            height, width = image_array.shape[:2]
            max_size = 500
            if width > max_size or height > max_size:
                scale = min(max_size / width, max_size / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                display_image = cv2.resize(image_array, (new_width, new_height))
            else:
                display_image = image_array
            
            # Chuyển BGR sang RGB
            display_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
            
            # Chuyển sang PIL Image
            pil_image = Image.fromarray(display_image)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Label hiển thị ảnh
            image_label = tk.Label(image_frame, image=photo, bg='white')
            image_label.image = photo  # Giữ reference
            image_label.pack()
            
            # Info text
            from utils.image_handler import ImageHandler
            base64_str = face_db.get_face_image(
                student_id=self.student['student_id'],
                as_array=False
            )
            if base64_str:
                info = ImageHandler.get_image_info(base64_str)
                info_text = f"Kích thước: {info.get('width')}x{info.get('height')} | "
                info_text += f"Dung lượng: {info.get('size_kb')} KB"
                tk.Label(
                    dialog, 
                    text=info_text, 
                    bg='white', 
                    font=('Arial', 9), 
                    fg='gray'
                ).pack(pady=5)
            
            # Close button
            tk.Button(
                dialog, 
                text="✖️ Đóng", 
                bg='#6c757d', 
                fg='white',
                command=dialog.destroy, 
                width=15,
                font=('Arial', 11, 'bold')
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xem ảnh:\n{str(e)}")
    
    def delete_face_image(self):
        """Xóa ảnh khuôn mặt khỏi hệ thống"""
        try:
            from utils.image_handler import FaceImageDB
            
            face_db = FaceImageDB(self.db)
            
            # Kiểm tra có ảnh không
            image_array = face_db.get_face_image(
                student_id=self.student['student_id'],
                as_array=True
            )
            
            if image_array is None:
                messagebox.showinfo("Thông báo", "Bạn chưa có ảnh khuôn mặt trong hệ thống")
                return
            
            # Xác nhận xóa
            if not messagebox.askyesno(
                "Xác nhận xóa", 
                "⚠️ Bạn có chắc muốn xóa ảnh khuôn mặt?\n\n"
                "Sau khi xóa, bạn sẽ không thể sử dụng điểm danh tự động\n"
                "cho đến khi upload ảnh mới."
            ):
                return
            
            # Xóa ảnh
            success, message = face_db.delete_face_image(self.student['student_id'])
            
            if success:
                messagebox.showinfo("Thành công", "Đã xóa ảnh khuôn mặt")
                
                # Refresh preview
                self.preview_label.config(
                    image='', 
                    text='Chưa có ảnh khuôn mặt\n\nClick "Chọn ảnh mới" để upload'
                )
                if hasattr(self, 'face_info_label'):
                    self.face_info_label.config(text='')
            else:
                messagebox.showerror("Lỗi", f"Không thể xóa ảnh:\n{message}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa ảnh:\n{str(e)}")

    # ======================== TAB ĐỔI MẬT KHẨU ===================
    def create_change_password_tab(self):
        """Tab đổi mật khẩu cho sinh viên"""
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
                
                # Cập nhật password_hash trong user object (để verify lần sau)
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

    # ======================== Logout ==========================
    def logout(self):
        self.root.destroy()
        self.logout_callback()

    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        if messagebox.askyesno("Xác nhận thoát", "Bạn có chắc muốn thoát?"):
            self.root.destroy()
            import sys
            sys.exit(0)
