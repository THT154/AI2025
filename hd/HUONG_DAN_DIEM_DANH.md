# Hướng Dẫn Sử Dụng Chức Năng Điểm Danh Bằng Khuôn Mặt

## Yêu Cầu Hệ Thống

1. **Python 3.8+** đã cài đặt
2. **MySQL/XAMPP** đang chạy
3. **Webcam** hoạt động tốt
4. Các thư viện Python đã cài đặt (xem `requirements.txt`)

## Các Bước Chuẩn Bị

### 1. Cài Đặt Thư Viện

```bash
pip install -r requirements.txt
```

### 2. Khởi Động Database

- Mở XAMPP và start MySQL
- Database sẽ tự động được tạo khi chạy ứng dụng

### 3. Thêm Sinh Viên và Ảnh Khuôn Mặt

Có 2 cách:

**Cách 1: Qua Moderator Window**
- Đăng nhập với tài khoản moderator
- Vào tab "Quản lý sinh viên"
- Thêm sinh viên và upload ảnh khuôn mặt (ít nhất 5 ảnh/sinh viên)

**Cách 2: Import từ Excel**
- Chuẩn bị file Excel với các cột: Mã SV, Họ tên, Email, Ngành, Khóa
- Import qua chức năng "Import từ Excel"
- Upload ảnh khuôn mặt cho từng sinh viên

### 4. Train Model AI

1. Đăng nhập với tài khoản giáo viên
2. Vào tab "🤖 Train Model AI"
3. Click nút "🚀 Train Model"
4. Đợi quá trình train hoàn tất (có thể mất vài phút)
5. Thông báo thành công sẽ hiện ra

## Sử Dụng Chức Năng Điểm Danh

### Bước 1: Tạo Lớp Học

1. Đăng nhập với tài khoản giáo viên
2. Vào tab "🏫 Lớp học của tôi"
3. Click "➕ Đăng ký lớp mới"
4. Điền thông tin lớp học:
   - Mã lớp
   - Tên lớp
   - Số tiết học (2, 3, hoặc 4)
   - Số sinh viên tối đa
   - Học kỳ và năm học
   - Lịch học (thứ, tiết từ - đến)
5. Click "✓ Đăng ký lớp"
6. Đợi moderator duyệt lớp

### Bước 2: Sinh Viên Đăng Ký Lớp

1. Sinh viên đăng nhập vào hệ thống
2. Vào tab "Đăng ký lớp"
3. Chọn lớp muốn đăng ký
4. Click "Đăng ký"

### Bước 3: Điểm Danh Bằng Khuôn Mặt

1. Giáo viên đăng nhập vào hệ thống
2. Vào tab "✅ Điểm danh"
3. Chọn lớp cần điểm danh từ dropdown
4. Click "📸 Bắt đầu điểm danh"
5. Camera sẽ tự động bật
6. Sinh viên lần lượt đứng trước camera
7. Hệ thống sẽ tự động:
   - Nhận diện khuôn mặt
   - Hiển thị tên và độ tin cậy
   - Điểm danh nếu độ tin cậy >= 50%
   - Thêm vào danh sách "Đã điểm danh"
8. Click lại nút để dừng camera

## Lưu Ý Quan Trọng

### Về Ảnh Khuôn Mặt

- **Số lượng**: Tối thiểu 5 ảnh/sinh viên, khuyến nghị 10-15 ảnh
- **Chất lượng**: Ảnh rõ nét, ánh sáng tốt
- **Góc độ**: Chụp từ nhiều góc độ khác nhau (thẳng, nghiêng trái/phải)
- **Biểu cảm**: Có thể chụp với các biểu cảm khác nhau
- **Định dạng**: JPG, JPEG, hoặc PNG

### Về Điểm Danh

- **Ánh sáng**: Đảm bảo phòng có đủ ánh sáng
- **Khoảng cách**: Sinh viên đứng cách camera 0.5-1m
- **Tư thế**: Nhìn thẳng vào camera
- **Độ tin cậy**: Mặc định >= 50%, có thể điều chỉnh trong `config.py`

### Xử Lý Lỗi

**Lỗi: "Model chưa được train"**
- Giải pháp: Vào tab "Train Model AI" và train lại model

**Lỗi: "Không thể mở camera"**
- Kiểm tra camera có hoạt động không
- Đóng các ứng dụng khác đang sử dụng camera
- Khởi động lại ứng dụng

**Lỗi: Nhận diện sai người**
- Thêm nhiều ảnh hơn cho sinh viên đó
- Train lại model
- Tăng ngưỡng confidence trong config

**Lỗi: Không nhận diện được**
- Kiểm tra ánh sáng
- Đảm bảo khuôn mặt rõ ràng
- Thử đứng gần camera hơn

## Cấu Hình Nâng Cao

Chỉnh sửa file `config.py`:

```python
# Thay đổi ngưỡng tin cậy (mặc định 50%)
CONFIDENCE_THRESHOLD = 60  # Tăng lên để chặt chẽ hơn

# Thay đổi kích thước cửa sổ
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
```

## Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log trong console
2. Đảm bảo database đang chạy
3. Kiểm tra camera hoạt động
4. Train lại model nếu cần

## Tính Năng Sắp Tới

- [ ] Điểm danh hàng loạt (nhiều người cùng lúc)
- [ ] Xuất báo cáo điểm danh
- [ ] Gửi email thông báo vắng mặt
- [ ] Thống kê tỷ lệ tham gia
- [ ] Nhận diện qua video/ảnh tĩnh
