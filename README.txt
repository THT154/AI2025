================================================================================
    HỆ THỐNG ĐIỂM DANH TỰ ĐỘNG BẰNG NHẬN DIỆN KHUÔN MẶT
================================================================================

📋 MỤC LỤC
    1. Giới thiệu
    2. Yêu cầu hệ thống
    3. Cài đặt
    4. Chạy ứng dụng
    5. Tài khoản mặc định
    6. Hướng dẫn sử dụng
    7. Cấu trúc thư mục
    8. Xử lý lỗi
    9. Liên hệ

================================================================================
1. GIỚI THIỆU
================================================================================

Hệ thống điểm danh tự động sử dụng AI nhận diện khuôn mặt để:
    • Tự động hóa quy trình điểm danh
    • Giảm thời gian và công sức cho giáo viên
    • Tăng độ chính xác, tránh gian lận
    • Lưu trữ dữ liệu điện tử, dễ quản lý

Công nghệ sử dụng:
    • Python 3.8+
    • OpenCV (LBPH Face Recognition)
    • MySQL Database
    • Tkinter GUI

================================================================================
2. YÊU CẦU HỆ THỐNG
================================================================================

Phần cứng:
    • CPU: Intel i3 hoặc tương đương
    • RAM: 4GB (khuyến nghị 8GB)
    • Webcam: 720p trở lên
    • HDD: 1GB trống

Phần mềm:
    • Windows 10/11 hoặc Linux
    • Python 3.8 trở lên
    • XAMPP (MySQL)
    • Webcam driver

================================================================================
3. CÀI ĐẶT
================================================================================

BƯỚC 1: Cài đặt Python
    1. Download Python từ: https://www.python.org/downloads/
    2. Chạy installer
    3. ✅ QUAN TRỌNG: Tick "Add Python to PATH"
    4. Click "Install Now"
    5. Kiểm tra: Mở CMD, gõ: python --version

BƯỚC 2: Cài đặt XAMPP
    1. Download XAMPP từ: https://www.apachefriends.org/
    2. Chạy installer
    3. Chọn MySQL (bắt buộc)
    4. Cài đặt vào: C:\xampp
    5. Mở XAMPP Control Panel
    6. Click "Start" cho MySQL

BƯỚC 3: Cài đặt thư viện Python
    1. Mở CMD/Terminal
    2. Di chuyển đến thư mục dự án:
       cd D:\face-attendance-desktop
    
    3. Cài đặt thư viện:
       pip install -r requirements.txt
    
    4. Nếu gặp lỗi, cài từng thư viện:
       pip install opencv-python
       pip install opencv-contrib-python
       pip install mysql-connector-python
       pip install pillow
       pip install openpyxl
       pip install tkcalendar

BƯỚC 4: Kiểm tra cài đặt
    1. Kiểm tra Python:
       python --version
       → Kết quả: Python 3.8.x hoặc cao hơn
    
    2. Kiểm tra MySQL:
       - Mở XAMPP Control Panel
       - MySQL phải có trạng thái "Running"
    
    3. Kiểm tra thư viện:
       python -c "import cv2; print(cv2.__version__)"
       → Kết quả: 4.x.x

================================================================================
4. CHẠY ỨNG DỤNG
================================================================================

CÁCH 1: Chạy lần đầu (Tự động tạo dữ liệu mẫu)
    1. Mở XAMPP Control Panel
    2. Start MySQL
    3. Mở CMD/Terminal
    4. Di chuyển đến thư mục dự án:
       cd D:\face-attendance-desktop
    
    5. Chạy ứng dụng:
       python main.py
    
    6. Lần đầu chạy, hệ thống sẽ:
       ✅ Tạo database: attendance_db
       ✅ Tạo các bảng cần thiết
       ✅ Tạo dữ liệu mẫu (nếu database trống)
       ✅ Hiển thị thông báo tài khoản mặc định
    
    7. Đăng nhập với tài khoản mặc định (xem mục 5)

CÁCH 2: Chạy các lần sau
    1. Mở XAMPP, Start MySQL
    2. Chạy: python main.py
    3. Đăng nhập

CÁCH 3: Tạo dữ liệu mẫu thủ công (nếu cần)
    python create_sample_data.py

================================================================================
5. TÀI KHOẢN MẶC ĐỊNH
================================================================================

Sau khi chạy lần đầu, hệ thống tạo sẵn các tài khoản:

┌─────────────────────────────────────────────────────────────────┐
│ MODERATOR (Quản trị viên)                                       │
├─────────────────────────────────────────────────────────────────┤
│ Username: admin                                                 │
│ Password: admin123                                              │
│ Chức năng: Duyệt lớp, quản lý tài khoản, xuất Excel            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ GIẢNG VIÊN (5 tài khoản)                                        │
├─────────────────────────────────────────────────────────────────┤
│ GV001: TS. Nguyễn Thị Lan      | Username: gv001 | Pass: GV001 │
│ GV002: PGS.TS. Trần Văn Minh   | Username: gv002 | Pass: GV002 │
│ GV003: ThS. Lê Thị Hương       | Username: gv003 | Pass: GV003 │
│ GV004: TS. Phạm Đức Anh        | Username: gv004 | Pass: GV004 │
│ GV005: ThS. Hoàng Thị Mai      | Username: gv005 | Pass: GV005 │
│ Chức năng: Tạo lớp, điểm danh, train model AI                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SINH VIÊN (20 tài khoản)                                        │
├─────────────────────────────────────────────────────────────────┤
│ 21IT001: Nguyễn Văn An    | Username: 21it001 | Pass: 21IT001  │
│ 21IT002: Trần Thị Bình    | Username: 21it002 | Pass: 21IT002  │
│ 22IT001: Vũ Thị Phương    | Username: 22it001 | Pass: 22IT001  │
│ 23IT001: Trương Văn Khoa  | Username: 23it001 | Pass: 23IT001  │
│ 23AI001: Đặng Thị Phương  | Username: 23ai001 | Pass: 23AI001  │
│ ... và 15 tài khoản khác                                        │
│ Chức năng: Đăng ký lớp, xem điểm danh, upload ảnh              │
└─────────────────────────────────────────────────────────────────┘

📝 LƯU Ý:
    • Username: Viết thường (gv001, 21it001)
    • Password: Viết hoa (GV001, 21IT001)
    • Có thể đổi password sau khi đăng nhập

================================================================================
6. HƯỚNG DẪN SỬ DỤNG
================================================================================

A. MODERATOR (Quản trị viên)
    1. Đăng nhập: admin / admin123
    2. Duyệt lớp học:
       - Tab "Duyệt Lớp Học"
       - Chọn lớp → Click "Duyệt" hoặc "Từ chối"
    
    3. Quản lý thời gian đăng ký:
       - Tab "Quản lý thời gian đăng ký"
       - Chọn học kỳ, năm học
       - Chọn thời gian bắt đầu/kết thúc
       - Click "Lưu"
    
    4. Tạo tài khoản sinh viên:
       - Tab "Cấp tài khoản sinh viên"
       - Chọn file Excel hoặc thêm thủ công
       - Click "Tạo tài khoản"
       - Click "Xuất Excel" để lấy username/password
    
    5. Xuất danh sách từ Database:
       - Tab "Cấp tài khoản sinh viên/giảng viên"
       - Click "Xuất tất cả từ Database"
       - Chọn nơi lưu file

B. GIẢNG VIÊN
    1. Đăng nhập: gv001 / GV001
    2. Tạo lớp học:
       - Tab "Lớp học của tôi"
       - Click "Đăng ký lớp mới"
       - Điền thông tin, lịch học
       - Click "Đăng ký lớp"
    
    3. Train Model AI:
       - Tab "Train Model AI"
       - Click "Train Model"
       - Đợi 5-10 giây
    
    4. Điểm danh:
       - Tab "Điểm danh"
       - Chọn lớp
       - Click "Bắt đầu điểm danh"
       - Sinh viên đứng trước camera
       - Hệ thống tự động nhận diện
       - Click lại để dừng → Chọn "YES" để đánh dấu vắng
    
    5. Rà soát điểm danh:
       - Click "Rà soát điểm danh"
       - Chuyển sinh viên giữa "Có mặt" và "Vắng"
       - Click "Lưu và Đóng"

C. SINH VIÊN
    1. Đăng nhập: 21it001 / 21IT001
    2. Đăng ký lớp:
       - Tab "Đăng ký tín chỉ"
       - Chọn lớp → Click "Đăng ký lớp"
    
    3. Xem điểm danh:
       - Tab "Điểm danh"
       - Xem lịch sử có mặt/vắng
    
    4. Upload ảnh khuôn mặt:
       - Tab "Ảnh khuôn mặt"
       - Click "Chọn ảnh"
       - Click "Lưu ảnh"

================================================================================
7. CẤU TRÚC THƯ MỤC
================================================================================

face-attendance-desktop/
│
├── main.py                     # File chính để chạy
├── database.py                 # Quản lý database
├── config.py                   # Cấu hình hệ thống
├── face_recognition_service.py # Nhận diện khuôn mặt
├── email_service.py            # Gửi email
├── create_sample_data.py       # Tạo dữ liệu mẫu
│
├── gui/                        # Giao diện
│   ├── login_window.py
│   ├── teacher_window.py
│   ├── student_window.py
│   ├── moderator_window.py
│   └── profile_window.py
│
├── models/                     # Lưu model AI
│   ├── face_model.yml
│   └── labels.pkl
│
├── uploads/                    # Lưu ảnh
│   └── face_images/
│       ├── 21IT001/
│       ├── 22IT001/
│       └── ...
│
├── requirements.txt            # Danh sách thư viện
├── README.txt                  # File này
│
└── Tài liệu/
    ├── GIAI_THICH_HE_THONG_AI.md
    ├── HUONG_DAN_DIEM_DANH.md
    ├── HUONG_DAN_CHUP_ANH.md
    ├── HUONG_DAN_RA_SOAT.md
    ├── HUONG_DAN_XUAT_EXCEL.md
    └── TOM_TAT_TRINH_BAY.md

================================================================================
8. XỬ LÝ LỖI
================================================================================

LỖI 1: "Không thể kết nối đến MySQL"
    Nguyên nhân: MySQL chưa chạy
    Giải pháp:
        1. Mở XAMPP Control Panel
        2. Click "Start" cho MySQL
        3. Chạy lại ứng dụng

LỖI 2: "ModuleNotFoundError: No module named 'cv2'"
    Nguyên nhân: Chưa cài OpenCV
    Giải pháp:
        pip install opencv-python
        pip install opencv-contrib-python

LỖI 3: "Access denied for user 'root'@'localhost'"
    Nguyên nhân: Sai password MySQL
    Giải pháp:
        1. Mở file config.py
        2. Sửa DB_PASSWORD = 'your_password'
        3. Lưu và chạy lại

LỖI 4: "Không thể mở camera"
    Nguyên nhân: Camera đang được sử dụng
    Giải pháp:
        1. Đóng các ứng dụng khác đang dùng camera
        2. Kiểm tra camera hoạt động
        3. Thử lại

LỖI 5: "Model chưa được train"
    Nguyên nhân: Chưa train model AI
    Giải pháp:
        1. Đăng nhập giáo viên
        2. Vào tab "Train Model AI"
        3. Click "Train Model"

LỖI 6: "Không nhận diện được"
    Nguyên nhân: Chưa có ảnh training hoặc quá ít
    Giải pháp:
        1. Chụp 15-20 ảnh cho sinh viên
        2. Chạy: python capture_face_images.py 21IT001 15
        3. Train lại model

================================================================================
9. CÔNG CỤ HỖ TRỢ
================================================================================

A. Chụp ảnh khuôn mặt:
    python capture_face_images.py <mã_sinh_viên> <số_ảnh>
    
    Ví dụ:
    python capture_face_images.py 21IT001 15

B. Test nhận diện:
    python test_recognition.py

C. Test train model:
    python test_train_model.py

D. Upload ảnh từ folder:
    python upload_face_images.py

E. Tạo dữ liệu mẫu:
    python create_sample_data.py

================================================================================
10. CẤU HÌNH NÂNG CAO
================================================================================

File: config.py

Thay đổi ngưỡng tin cậy:
    CONFIDENCE_THRESHOLD = 50  # Mặc định
    CONFIDENCE_THRESHOLD = 60  # Chặt chẽ hơn
    CONFIDENCE_THRESHOLD = 40  # Dễ dàng hơn

Thay đổi kích thước cửa sổ:
    WINDOW_WIDTH = 1200   # Mặc định
    WINDOW_HEIGHT = 700   # Mặc định

Thay đổi cấu hình MySQL:
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'attendance_db'

================================================================================
11. BACKUP & RESTORE
================================================================================

A. Backup Database:
    1. Mở phpMyAdmin: http://localhost/phpmyadmin
    2. Chọn database "attendance_db"
    3. Click "Export"
    4. Click "Go"
    5. Lưu file .sql

B. Restore Database:
    1. Mở phpMyAdmin
    2. Tạo database mới: attendance_db
    3. Click "Import"
    4. Chọn file .sql
    5. Click "Go"

C. Backup Model AI:
    Copy thư mục models/ sang nơi an toàn

D. Backup Ảnh:
    Copy thư mục uploads/ sang nơi an toàn

================================================================================
12. LIÊN HỆ & HỖ TRỢ
================================================================================

Nếu gặp vấn đề, vui lòng:
    1. Đọc kỹ phần "Xử lý lỗi"
    2. Xem các file hướng dẫn trong thư mục dự án
    3. Kiểm tra log trong console

Tài liệu tham khảo:
    • GIAI_THICH_HE_THONG_AI.md - Giải thích chi tiết về AI
    • HUONG_DAN_DIEM_DANH.md - Hướng dẫn điểm danh
    • HUONG_DAN_CHUP_ANH.md - Hướng dẫn chụp ảnh
    • HUONG_DAN_RA_SOAT.md - Hướng dẫn rà soát
    • HUONG_DAN_XUAT_EXCEL.md - Hướng dẫn xuất Excel

================================================================================
13. CHANGELOG
================================================================================

Version 1.0.0 (2024-12-03)
    ✅ Nhận diện khuôn mặt bằng LBPH
    ✅ Điểm danh tự động real-time
    ✅ Quản lý lớp học, sinh viên, giảng viên
    ✅ Rà soát điểm danh thủ công
    ✅ Xuất Excel sinh viên/giảng viên
    ✅ Tự động tạo dữ liệu mẫu lần đầu chạy
    ✅ 3 loại tài khoản: Moderator, Giáo viên, Sinh viên

================================================================================
14. LICENSE
================================================================================

MIT License - Sử dụng tự do cho mục đích học tập và nghiên cứu.

================================================================================

🎓 CHÚC BẠN SỬ DỤNG THÀNH CÔNG!

Nếu có câu hỏi, vui lòng tham khảo các file hướng dẫn chi tiết.

================================================================================
