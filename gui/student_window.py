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
        self.center_window()
        self.create_widgets()
        self.refresh_data()
        self.load_available_classes()

        # Overlay tự động refresh mỗi phút
        self.update_overlay()

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
        self.create_schedule_tab()  # TAB MỚI
        self.create_attendance_tab()
        self.create_face_upload_tab()

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

        tk.Button(
            tab,
            text="✗ Hủy đăng ký",
            bg="#dc3545",
            fg="white",
            font=('Arial', 12, 'bold'),
            command=self.drop_class
        ).pack(pady=10)

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

        info = tk.Label(
            tab,
            text="Mỗi sinh viên chỉ được upload 1 ảnh khuôn mặt chuẩn diện\nẢnh dùng cho hệ thống nhận diện điểm danh",
            font=("Arial", 12),
            bg="white",
            fg="#333",
            justify="center"
        )
        info.pack(pady=10)

        self.preview_label = tk.Label(tab, bg="white")
        self.preview_label.pack(pady=10)

        control_frame = tk.Frame(tab, bg="white")
        control_frame.pack(pady=10)

        tk.Button(control_frame, text="📂 Chọn ảnh", bg="#007bff", fg="white",
                  font=("Arial", 11), command=self.select_face_image).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="💾 Lưu ảnh", bg="#28a745", fg="white",
                  font=("Arial", 11), command=self.save_face_image).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="📸 Cập nhật lại", bg="#ffc107", fg="black",
                  font=("Arial", 11), command=self.select_face_image).pack(side=tk.LEFT, padx=10)

        self.face_image_path = None
        self.load_existing_face_image()

    # ======================== Nghiệp vụ ======================
    def refresh_data(self):
        self.refresh_available_classes()
        self.refresh_my_classes()
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
    def select_face_image(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh khuôn mặt",
            filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
        )
        if not file_path:
            return

        self.face_image_path = os.path.abspath(file_path)

        img = Image.open(self.face_image_path).resize((250, 250))
        self.tk_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.tk_img)

    def save_face_image(self):
        if not self.face_image_path:
            messagebox.showwarning("Thiếu ảnh", "Vui lòng chọn ảnh trước!")
            return

        student_code = self.student['student_code']
        save_dir = os.path.join("uploads", "face_images", str(student_code))
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, "face.jpg")

        try:
            # Đọc ảnh bằng PIL (ổn định hơn cv2 với đường dẫn tiếng Việt)
            pil_img = Image.open(self.face_image_path).convert("RGB")
            pil_img = pil_img.resize((200, 200))

            # Lưu bằng PIL
            pil_img.save(save_path)

            messagebox.showinfo("Thành công", "Ảnh khuôn mặt đã được lưu thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu ảnh!\n{e}")

    def load_existing_face_image(self):
        student_code = self.student['student_code']
        path = os.path.join("uploads", "face_images", str(student_code), "face.jpg")

        if os.path.exists(path):
            img = Image.open(path).resize((250, 250))
            self.tk_img = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.tk_img)


    # ======================== Logout ==========================
    def logout(self):
        self.root.destroy()
        self.logout_callback()