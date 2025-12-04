# config.py - Cấu hình cho Desktop App
import os

class Config:
    # MySQL Configuration (XAMPP)
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''  # XAMPP mặc định không có password
    DB_NAME = 'attendance_db'
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    FACE_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'face_images')
    MODELS_FOLDER = os.path.join(BASE_DIR, 'models')
    
    # Face Recognition
    FACE_MODEL_PATH = os.path.join(MODELS_FOLDER, 'face_model.yml')
    LABELS_PATH = os.path.join(MODELS_FOLDER, 'labels.pkl')
    CONFIDENCE_THRESHOLD = 50  # Ngưỡng tin cậy tối thiểu (%)
    
    # Email Configuration (Gmail SMTP)
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_SENDER = ''  # Để trống nếu không dùng email
    EMAIL_PASSWORD = ''  # App password của Gmail
    
    # UI Configuration
    WINDOW_TITLE = "Hệ Thống Điểm Danh AI"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    
    # Session Configuration
    SESSION_TIMES = {
        'morning': [1, 2, 3, 4, 5],  # 5 tiết sáng
        'afternoon': [6, 7, 8, 9, 10]  # 5 tiết chiều
    }
    
    # Credits mapping
    CREDITS_MAPPING = {
        2: 1,  # 2 tiết = 1 tín chỉ
        3: 2,  # 3 tiết = 2 tín chỉ
        4: 3   # 4 tiết = 3 tín chỉ
    }
    
    @staticmethod
    def init_folders():
        """Tạo các thư mục cần thiết"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.FACE_IMAGES_FOLDER, exist_ok=True)
        os.makedirs(Config.MODELS_FOLDER, exist_ok=True)
        print("✓ Đã tạo các thư mục cần thiết")

# Khởi tạo folders khi import
Config.init_folders()