═══════════════════════════════════════════════════════════════
    HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG NHẬN DIỆN KHUÔN MẶT
═══════════════════════════════════════════════════════════════

� GIỚ I THIỆU
────────────────────────────────────────────────────────────────
Hệ thống quản lý điểm danh sinh viên sử dụng công nghệ nhận diện
khuôn mặt AI, được xây dựng với Python và MySQL.

Tính năng chính:
• Điểm danh tự động bằng nhận diện khuôn mặt
• Quản lý lớp học, sinh viên, giảng viên
• Đăng ký tín chỉ trực tuyến
• Quản lý tài liệu học tập
• Thời khóa biểu tự động
• Báo cáo điểm danh chi tiết

🎯 YÊU CẦU HỆ THỐNG
────────────────────────────────────────────────────────────────
• Python 3.8+
• MySQL 5.7+ hoặc MariaDB 10.3+
• XAMPP (khuyến nghị) hoặc MySQL Server
• Webcam (cho chức năng điểm danh)
• Windows/Linux/MacOS

📦 CÀI ĐẶT
────────────────────────────────────────────────────────────────

BƯỚC 1: Cài đặt Python
────────────────────────────────────────────────────────────────
Tải và cài đặt Python từ: https://www.python.org/downloads/
Chọn "Add Python to PATH" khi cài đặt

BƯỚC 2: Cài đặt XAMPP
────────────────────────────────────────────────────────────────
1. Tải XAMPP: https://www.apachefriends.org/
2. Cài đặt và khởi động MySQL trong XAMPP Control Panel

BƯỚC 3: Clone/Download project
────────────────────────────────────────────────────────────────
git clone <repository-url>
cd face-attendance-desktop

BƯỚC 4: Cài đặt thư viện Python
────────────────────────────────────────────────────────────────
pip install -r requirements.txt

Lưu ý: Nếu gặp lỗi với opencv-python:
pip uninstall opencv-python opencv-contrib-python -y
pip install opencv-contrib-python==4.10.0.84

BƯỚC 5: Cấu hình MySQL
────────────────────────────────────────────────────────────────
1. Mở file: C:\xampp\mysql\bin\my.ini
2. Tìm và sửa (hoặc thêm vào [mysqld]):
   max_allowed_packet = 64M
3. Restart MySQL trong XAMPP

BƯỚC 6: Cấu hình database
────────────────────────────────────────────────────────────────
Mở file config.py và kiểm tra:
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Mặc định XAMPP không có password
DB_NAME = 'attendance_db'

BƯỚC 7: Chạy ứng dụng
────────────────────────────────────────────────────────────────
python main.py

Lần đầu chạy, hệ thống sẽ tự động:
• Tạo database
• Tạo các bảng
• Tạo dữ liệu mẫu

🔑 TÀI KHOẢN MẶC ĐỊNH
────────────────────────────────────────────────────────────────

QUẢN TRỊ VIÊN (Moderator):
• Username: admin
• Password: admin123
• Quyền: Duyệt lớp, quản lý hệ thống

GIẢNG VIÊN:
• Username: gv001 (hoặc mã GV khác)
• Password: GV001 (giống username, viết hoa)
• Quyền: Tạo lớp, điểm danh, upload tài liệu

SINH VIÊN:
• Username: 21it001 (hoặc MSSV khác)
• Password: 21IT001 (giống username, viết hoa)
• Quyền: Đăng ký lớp, xem điểm danh, tải tài liệu

📚 HƯỚNG DẪN SỬ DỤNG
────────────────────────────────────────────────────────────────

QUẢN TRỊ VIÊN
────────────────────────────────────────────────────────────────
1. Đăng nhập với admin/admin123
2. Thiết lập khung giờ đăng ký tín chỉ
3. Duyệt lớp học do giảng viên tạo
4. Quản lý tài khoản sinh viên/giảng viên
5. Xem báo cáo thống kê

GIẢNG VIÊN
────────────────────────────────────────────────────────────────
1. Đăng nhập với tài khoản giảng viên
2. Tạo lớp học mới (tab "Lớp học của tôi")
3. Chờ quản trị viên duyệt
4. Upload tài liệu: Double-click vào lớp → Upload file
5. Điểm danh: Tab "Điểm danh" → Chọn lớp → Bắt đầu
6. Rà soát điểm danh: Sửa trạng thái nếu cần
7. Đổi mật khẩu: Tab "Đổi mật khẩu"

SINH VIÊN
────────────────────────────────────────────────────────────────
1. Đăng nhập với tài khoản sinh viên
2. Upload ảnh khuôn mặt (tab "Ảnh khuôn mặt"):
   • Chọn ảnh từ máy hoặc chụp webcam
   • Lưu vào hệ thống
3. Đăng ký lớp (tab "Đăng ký tín chỉ"):
   • Chọn lớp
   • Double-click hoặc click "Đăng ký lớp"
4. Xem lớp đã đăng ký (tab "Lớp của tôi"):
   • Double-click để xem chi tiết
   • Xem tài liệu, lịch sử điểm danh
5. Xem tài liệu (tab "Tài liệu"):
   • Chọn lớp
   • Double-click để tải xuống
6. Xem thời khóa biểu (tab "Thời khóa biểu")
7. Xem điểm danh (tab "Điểm danh")

🎨 TÍNH NĂNG CHI TIẾT
────────────────────────────────────────────────────────────────

ĐIỂM DANH BẰNG KHUÔN MẶT
────────────────────────────────────────────────────────────────
• Nhận diện tự động qua webcam
• Độ chính xác cao với AI
• Lưu ảnh khuôn mặt trong database
• Điểm danh nhiều sinh viên cùng lúc
• Rà soát và chỉnh sửa sau điểm danh

QUẢN LÝ TÀI LIỆU
────────────────────────────────────────────────────────────────
• Giảng viên upload tài liệu cho lớp
• File lưu trực tiếp trong database (BLOB)
• Sinh viên tải xuống tài liệu
• Hỗ trợ: PDF, Word, Excel, PowerPoint, ảnh
• Giới hạn: 50MB/file (có thể tăng)

ĐĂNG KÝ TÍN CHỈ
────────────────────────────────────────────────────────────────
• Quản trị viên thiết lập khung giờ đăng ký
• Sinh viên đăng ký trong khung giờ
• Kiểm tra sĩ số tự động
• Hủy đăng ký nếu cần

THỜI KHÓA BIỂU
────────────────────────────────────────────────────────────────
• Tự động tạo từ lớp đã đăng ký
• Hiển thị theo tuần
• Màu sắc phân biệt buổi sáng/chiều
• Thông tin chi tiết: phòng, giảng viên

ĐỔI MẬT KHẨU
────────────────────────────────────────────────────────────────
• Bắt buộc đổi mật khẩu lần đầu đăng nhập
• Đổi mật khẩu bất kỳ lúc nào
• Yêu cầu: Tối thiểu 6 ký tự

🔧 XỬ LÝ LỖI THƯỜNG GẶP
────────────────────────────────────────────────────────────────

LỖI: "Không thể kết nối MySQL"
────────────────────────────────────────────────────────────────
Giải pháp:
1. Mở XAMPP Control Panel
2. Start MySQL
3. Kiểm tra MySQL đang chạy (port 3306)
4. Chạy lại ứng dụng

LỖI: "module 'cv2' has no attribute 'face'"
────────────────────────────────────────────────────────────────
Giải pháp:
pip uninstall opencv-python opencv-contrib-python -y
pip install opencv-contrib-python==4.10.0.84

LỖI: "Lost connection to MySQL server during query"
────────────────────────────────────────────────────────────────
Giải pháp:
1. Mở: C:\xampp\mysql\bin\my.ini
2. Thêm vào [mysqld]:
   max_allowed_packet = 64M
3. Restart MySQL trong XAMPP

LỖI: "No module named 'tkcalendar'"
────────────────────────────────────────────────────────────────
Giải pháp:
pip install tkcalendar

LỖI: "Không đăng nhập được admin"
────────────────────────────────────────────────────────────────
Giải pháp:
python fix_moderator_account.py

LỖI: "Unknown column 'session_date'"
────────────────────────────────────────────────────────────────
Đã sửa trong phiên bản mới nhất. Update code từ Git.

📁 CẤU TRÚC PROJECT
────────────────────────────────────────────────────────────────
face-attendance-desktop/
├── main.py                 # Entry point
├── config.py              # Cấu hình
├── requirements.txt       # Thư viện Python
├── create_sample_data.py  # Tạo dữ liệu mẫu
├── models/                # Database models
│   ├── database.py
│   └── user.py
├── views/                 # Giao diện
│   ├── login_window.py
│   ├── moderator_window.py
│   ├── teacher_window.py
│   └── student_window.py
├── controllers/           # Business logic
├── services/              # AI services
│   └── face_recognition_service.py
├── utils/                 # Utilities
└── uploads/              # File uploads

🗄️ CẤU TRÚC DATABASE
────────────────────────────────────────────────────────────────
Bảng chính:
• users                    # Tài khoản người dùng
• students                 # Thông tin sinh viên
• teachers                 # Thông tin giảng viên
• classes                  # Lớp học
• class_enrollments        # Đăng ký lớp
• sessions                 # Buổi học
• attendance               # Điểm danh
• class_documents          # Tài liệu (BLOB)
• registration_period      # Khung giờ đăng ký
• email_logs              # Log email

🔒 BẢO MẬT
────────────────────────────────────────────────────────────────
• Mật khẩu được hash (SHA-256)
• Bắt buộc đổi mật khẩu lần đầu
• Phân quyền rõ ràng (moderator/teacher/student)
• File tài liệu lưu trong database (BLOB)
• Sinh viên chỉ xem tài liệu lớp đã đăng ký

🚀 TRIỂN KHAI
────────────────────────────────────────────────────────────────

DEVELOPMENT:
python main.py

PRODUCTION:
1. Đổi password MySQL trong config.py
2. Tắt debug mode
3. Backup database định kỳ
4. Cấu hình firewall
5. Sử dụng HTTPS nếu deploy web

BACKUP DATABASE:
mysqldump -u root -p attendance_db > backup.sql

RESTORE DATABASE:
mysql -u root -p attendance_db < backup.sql

📊 THỐNG KÊ
────────────────────────────────────────────────────────────────
• Ngôn ngữ: Python 3
• Framework: Tkinter (GUI)
• Database: MySQL
• AI: OpenCV, face_recognition
• Kiến trúc: MVC
• Dòng code: ~15,000+

👥 ĐÓNG GÓP
────────────────────────────────────────────────────────────────
Xem file CONTRIBUTING.md để biết cách đóng góp.

📄 LICENSE
────────────────────────────────────────────────────────────────
Xem file LICENSE

📞 HỖ TRỢ
────────────────────────────────────────────────────────────────
Nếu gặp vấn đề:
1. Kiểm tra phần "Xử lý lỗi thường gặp"
2. Xem log trong terminal
3. Kiểm tra MySQL error log
4. Tạo issue trên GitHub

🎓 TÀI LIỆU THAM KHẢO
────────────────────────────────────────────────────────────────
• Python: https://docs.python.org/3/
• Tkinter: https://docs.python.org/3/library/tkinter.html
• MySQL: https://dev.mysql.com/doc/
• OpenCV: https://docs.opencv.org/
• Face Recognition: https://github.com/ageitgey/face_recognition

📝 CHANGELOG
────────────────────────────────────────────────────────────────
v2.0.0 (Latest)
• Thêm quản lý tài liệu (upload/download BLOB)
• Sinh viên xem tài liệu trong chi tiết lớp
• Double-click để xem chi tiết/đăng ký/tải xuống
• Sửa lỗi session_date
• Sửa lỗi đăng nhập moderator
• Cải thiện UI/UX
• Thêm thời khóa biểu tự động

v1.0.0
• Phiên bản đầu tiên
• Điểm danh bằng khuôn mặt
• Quản lý lớp học
• Đăng ký tín chỉ

═══════════════════════════════════════════════════════════════
                    CHÚC BẠN SỬ DỤNG THÀNH CÔNG!
═══════════════════════════════════════════════════════════════
