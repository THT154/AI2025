# utils/webcam_capture.py - Chụp ảnh từ webcam
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
from datetime import datetime

class WebcamCapture:
    """Class để chụp ảnh từ webcam"""
    
    def __init__(self, parent, callback, title="Chụp ảnh từ Webcam"):
        """
        Args:
            parent: Cửa sổ cha (Tkinter)
            callback: Hàm callback nhận ảnh đã chụp (numpy array)
            title: Tiêu đề dialog
        """
        self.parent = parent
        self.callback = callback
        self.title = title
        
        self.cap = None
        self.dialog = None
        self.video_label = None
        self.is_running = False
        self.captured_frame = None
        
    def open_camera(self):
        """Mở camera và hiển thị dialog"""
        # Thử mở camera
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", 
                "Không thể mở camera!\n\n"
                "Vui lòng kiểm tra:\n"
                "• Camera đã được kết nối\n"
                "• Không có ứng dụng nào đang sử dụng camera\n"
                "• Driver camera đã được cài đặt")
            return False
        
        # Tạo dialog - đẹp hơn
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("900x720")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#f5f5f5')
        
        # Center dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Xử lý đóng dialog
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_camera)
        
        # Header - đẹp hơn
        header_frame = tk.Frame(self.dialog, bg='#4a5568', height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📷 Chụp ảnh khuôn mặt",
            font=('Arial', 18, 'bold'),
            bg='#4a5568',
            fg='white'
        ).pack(pady=10)
        
        tk.Label(
            header_frame,
            text="Nhìn thẳng vào camera • Đảm bảo ánh sáng đủ",
            font=('Arial', 10),
            bg='#4a5568',
            fg='#e2e8f0'
        ).pack()
        
        # Video container
        video_container = tk.Frame(self.dialog, bg='#f5f5f5')
        video_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Video frame - đẹp hơn với shadow effect
        video_frame = tk.Frame(
            video_container, 
            bg='#2d3748', 
            relief=tk.RAISED, 
            borderwidth=3
        )
        video_frame.pack(anchor='center')
        
        self.video_label = tk.Label(video_frame, bg='#2d3748')
        self.video_label.pack(padx=3, pady=3)
        
        # Status label - đẹp hơn
        status_frame = tk.Frame(self.dialog, bg='#f5f5f5')
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="🟢 Camera đang hoạt động",
            font=('Arial', 11, 'bold'),
            bg='#f5f5f5',
            fg='#48bb78'
        )
        self.status_label.pack()
        
        # Button container - đẹp hơn
        button_container = tk.Frame(self.dialog, bg='#f5f5f5')
        button_container.pack(pady=15)
        
        # Row 1: Chụp và Chụp lại
        button_frame1 = tk.Frame(button_container, bg='#f5f5f5')
        button_frame1.pack(pady=5)
        
        self.capture_btn = tk.Button(
            button_frame1,
            text="📸 Chụp ảnh",
            font=('Arial', 12, 'bold'),
            bg='#48bb78',
            fg='white',
            cursor='hand2',
            command=self.capture_photo,
            width=20,
            height=2,
            relief=tk.RAISED,
            borderwidth=2
        )
        self.capture_btn.pack(side=tk.LEFT, padx=8)
        
        self.retry_btn = tk.Button(
            button_frame1,
            text="🔄 Chụp lại",
            font=('Arial', 12, 'bold'),
            bg='#ed8936',
            fg='white',
            cursor='hand2',
            command=self.retry_capture,
            width=20,
            height=2,
            state=tk.DISABLED,
            relief=tk.RAISED,
            borderwidth=2
        )
        self.retry_btn.pack(side=tk.LEFT, padx=8)
        
        # Row 2: Sử dụng và Hủy
        button_frame2 = tk.Frame(button_container, bg='#f5f5f5')
        button_frame2.pack(pady=5)
        
        self.save_btn = tk.Button(
            button_frame2,
            text="✅ Sử dụng ảnh này",
            font=('Arial', 12, 'bold'),
            bg='#4299e1',
            fg='white',
            cursor='hand2',
            command=self.use_photo,
            width=20,
            height=2,
            state=tk.DISABLED,
            relief=tk.RAISED,
            borderwidth=2
        )
        self.save_btn.pack(side=tk.LEFT, padx=8)
        
        tk.Button(
            button_frame2,
            text="❌ Hủy",
            font=('Arial', 12, 'bold'),
            bg='#f56565',
            fg='white',
            cursor='hand2',
            command=self.close_camera,
            width=20,
            height=2,
            relief=tk.RAISED,
            borderwidth=2
        ).pack(side=tk.LEFT, padx=8)
        
        # Bắt đầu hiển thị video
        self.is_running = True
        self.update_frame()
        
        return True
    
    def update_frame(self):
        """Cập nhật frame từ camera"""
        if not self.is_running or not self.cap or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        
        if ret:
            # Lật ảnh theo chiều ngang (mirror effect)
            frame = cv2.flip(frame, 1)
            
            # Detect face và vẽ khung
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Vẽ khung face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, 'Face Detected', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Resize để hiển thị - to hơn
            display_frame = cv2.resize(frame, (800, 480))
            
            # Chuyển BGR sang RGB
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Chuyển sang PIL Image
            pil_image = Image.fromarray(display_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Cập nhật label
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
            # Lưu frame gốc (chưa resize) để chụp
            self.current_frame = frame
        
        # Lặp lại sau 10ms
        if self.is_running:
            self.dialog.after(10, self.update_frame)
    
    def capture_photo(self):
        """Chụp ảnh"""
        if self.current_frame is None:
            messagebox.showerror("Lỗi", "Không có frame để chụp!")
            return
        
        # Dừng video
        self.is_running = False
        
        # Lưu frame đã chụp
        self.captured_frame = self.current_frame.copy()
        
        # Hiển thị ảnh đã chụp
        display_frame = cv2.resize(self.captured_frame, (800, 480))
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(display_frame)
        photo = ImageTk.PhotoImage(pil_image)
        
        self.video_label.config(image=photo)
        self.video_label.image = photo
        
        # Cập nhật UI
        self.status_label.config(text="📸 Đã chụp ảnh", fg='#4299e1')
        self.capture_btn.config(state=tk.DISABLED)
        self.retry_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
    
    def retry_capture(self):
        """Chụp lại"""
        self.captured_frame = None
        self.is_running = True
        
        # Cập nhật UI
        self.status_label.config(text="🟢 Camera đang hoạt động", fg='#48bb78')
        self.capture_btn.config(state=tk.NORMAL)
        self.retry_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        
        # Tiếp tục hiển thị video
        self.update_frame()
    
    def use_photo(self):
        """Sử dụng ảnh đã chụp"""
        if self.captured_frame is None:
            messagebox.showerror("Lỗi", "Chưa có ảnh được chụp!")
            return
        
        # Gọi callback với ảnh đã chụp
        self.callback(self.captured_frame)
        
        # Đóng dialog
        self.close_camera()
    
    def close_camera(self):
        """Đóng camera và dialog"""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
    
    @staticmethod
    def save_frame_to_temp(frame):
        """Lưu frame vào file tạm"""
        import tempfile
        import os
        
        # Tạo file tạm
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_file = os.path.join(temp_dir, f'webcam_capture_{timestamp}.jpg')
        
        # Lưu ảnh
        cv2.imwrite(temp_file, frame)
        
        return temp_file
