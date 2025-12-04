# Hướng Dẫn Xuất Excel Sinh Viên & Giảng Viên

## Tổng Quan

Hệ thống cung cấp 2 chức năng xuất Excel:

1. **Xuất danh sách vừa tạo** - Xuất các tài khoản vừa được tạo trong phiên làm việc
2. **Xuất tất cả từ Database** - Truy vấn và xuất toàn bộ dữ liệu từ database

---

## PHẦN 1: XUẤT DANH SÁCH VỪA TẠO

### Mục Đích
Xuất danh sách tài khoản (username, password) vừa được tạo để:
- Gửi cho sinh viên/giảng viên
- Lưu trữ thông tin đăng nhập
- In phát cho người dùng

### Cách Sử Dụng

**Bước 1:** Tạo tài khoản
1. Đăng nhập với tài khoản Moderator
2. Vào tab **"👥 Cấp tài khoản sinh viên"** hoặc **"👩‍🏫 Cấp tài khoản giảng viên"**
3. Chọn file Excel hoặc thêm thủ công
4. Click **"✓ Tạo tài khoản"**

**Bước 2:** Xuất Excel
1. Click nút **"📥 Xuất danh sách vừa tạo"**
2. Chọn nơi lưu file
3. File Excel sẽ chứa:
   - Mã sinh viên/giảng viên
   - Họ tên
   - Username (= Mã)
   - Password (= Mã)
   - Email
   - Các thông tin khác

### Nội Dung File Excel

**Đối với Sinh viên:**
```
| MSSV    | Họ tên          | Username | Password | Email                    | Giới tính | Ngày sinh  | Ngành học | Khóa |
|---------|-----------------|----------|----------|--------------------------|-----------|------------|-----------|------|
| 23IT001 | Nguyễn Văn An   | 23it001  | 23IT001  | 23it001@student.edu.vn   | Nam       | 2005-01-15 | CNTT      | 2023 |
| 23IT002 | Trần Thị Bình   | 23it002  | 23IT002  | 23it002@student.edu.vn   | Nữ        | 2005-03-20 | CNTT      | 2023 |
```

**Đối với Giảng viên:**
```
| Mã GV | Họ tên              | Username | Password | Email                  | Giới tính | Ngày sinh  | Khoa/Bộ môn |
|-------|---------------------|----------|----------|------------------------|-----------|------------|-------------|
| GV001 | TS. Nguyễn Thị Lan  | gv001    | GV001    | gv001@faculty.edu.vn   | Nữ        | 1985-03-20 | CNTT        |
| GV002 | PGS. Trần Văn Minh  | gv002    | GV002    | gv002@faculty.edu.vn   | Nam       | 1978-07-15 | CNTT        |
```

### Lưu Ý
- ⚠️ Chỉ xuất được sau khi đã click "Tạo tài khoản"
- ⚠️ Danh sách sẽ bị xóa khi đóng ứng dụng
- ⚠️ Nên xuất ngay sau khi tạo để không mất dữ liệu

---

## PHẦN 2: XUẤT TẤT CẢ TỪ DATABASE (MỚI)

### Mục Đích
Truy vấn và xuất toàn bộ sinh viên/giảng viên đang có trong hệ thống để:
- Thống kê tổng số người dùng
- Kiểm tra dữ liệu
- Báo cáo cho ban giám hiệu
- Sao lưu dữ liệu

### Cách Sử Dụng

**Bước 1:** Mở chức năng
1. Đăng nhập với tài khoản Moderator
2. Vào tab **"👥 Cấp tài khoản sinh viên"** hoặc **"👩‍🏫 Cấp tài khoản giảng viên"**

**Bước 2:** Xuất Database
1. Tìm phần **"📊 Xuất dữ liệu từ Database"**
2. Click nút **"📤 Xuất tất cả từ Database"**
3. Chọn nơi lưu file
4. File sẽ tự động đặt tên: `DanhSach_Student_20241203_143025.xlsx`

### Nội Dung File Excel

**Đối với Sinh viên:**
```
| STT | Mã sinh viên | Họ và tên       | Giới tính | Ngày sinh  | Email                    | Ngành học | Khóa học | Có ảnh khuôn mặt |
|-----|--------------|-----------------|-----------|------------|--------------------------|-----------|----------|------------------|
| 1   | 21IT001      | Nguyễn Văn An   | Nam       | 15/01/2003 | 21it001@student.edu.vn   | CNTT      | 2021     | Có               |
| 2   | 21IT002      | Trần Thị Bình   | Nữ        | 20/03/2003 | 21it002@student.edu.vn   | CNTT      | 2021     | Chưa             |
| 3   | 22IT001      | Lê Văn Cường    | Nam       | 10/05/2004 | 22it001@student.edu.vn   | CNTT      | 2022     | Có               |

Tổng số: 20 student
Ngày xuất: 03/12/2024 14:30:25
```

**Đối với Giảng viên:**
```
| STT | Mã giảng viên | Họ và tên           | Giới tính | Ngày sinh  | Email                  | Khoa/Bộ môn |
|-----|---------------|---------------------|-----------|------------|------------------------|-------------|
| 1   | GV001         | TS. Nguyễn Thị Lan  | Nữ        | 20/03/1985 | gv001@faculty.edu.vn   | CNTT        |
| 2   | GV002         | PGS. Trần Văn Minh  | Nam       | 15/07/1978 | gv002@faculty.edu.vn   | CNTT        |
| 3   | GV003         | ThS. Lê Thị Hương   | Nữ        | 08/11/1990 | gv003@faculty.edu.vn   | Toán - Tin  |

Tổng số: 5 teacher
Ngày xuất: 03/12/2024 14:30:25
```

### Đặc Điểm File Excel

**Format chuyên nghiệp:**
- ✅ Header màu xanh, chữ trắng, in đậm
- ✅ Tự động điều chỉnh độ rộng cột
- ✅ Căn giữa header, căn trái nội dung
- ✅ Có STT tự động
- ✅ Có tổng kết ở cuối
- ✅ Ghi ngày giờ xuất

**Thông tin đầy đủ:**
- Tất cả thông tin cá nhân
- Trạng thái ảnh khuôn mặt (sinh viên)
- Khoa/Bộ môn (giảng viên)
- Email hệ thống

### Lưu Ý
- ✅ Không cần tạo tài khoản trước
- ✅ Truy vấn trực tiếp từ database
- ✅ Luôn có dữ liệu mới nhất
- ✅ Có thể xuất bất cứ lúc nào
- ⚠️ Không chứa password (bảo mật)

---

## SO SÁNH 2 CHỨC NĂNG

| Tiêu chí | Xuất vừa tạo | Xuất từ Database |
|----------|--------------|------------------|
| **Dữ liệu** | Chỉ tài khoản vừa tạo | Tất cả trong DB |
| **Có Password** | ✅ Có | ❌ Không |
| **Khi nào dùng** | Sau khi tạo TK mới | Bất cứ lúc nào |
| **Mục đích** | Phát cho người dùng | Thống kê, báo cáo |
| **Yêu cầu** | Phải tạo TK trước | Không yêu cầu |

---

## CÁC TRƯỜNG HỢP SỬ DỤNG

### Trường Hợp 1: Đầu Năm Học - Tạo TK Sinh Viên Mới

**Quy trình:**
1. Import file Excel sinh viên K2024
2. Click "Tạo tài khoản"
3. Click "Xuất danh sách vừa tạo" → Có password
4. In ra phát cho sinh viên

### Trường Hợp 2: Giữa Năm - Kiểm Tra Dữ Liệu

**Quy trình:**
1. Vào tab sinh viên
2. Click "Xuất tất cả từ Database"
3. Mở Excel kiểm tra
4. Xem ai chưa có ảnh khuôn mặt

### Trường Hợp 3: Cuối Năm - Báo Cáo

**Quy trình:**
1. Xuất sinh viên từ Database
2. Xuất giảng viên từ Database
3. Tổng hợp số liệu
4. Gửi báo cáo cho ban giám hiệu

### Trường Hợp 4: Sinh Viên Quên Mật Khẩu

**Lưu ý:**
- File "Xuất vừa tạo" có password
- File "Xuất từ Database" không có password
- Cần reset password trong database nếu quên

---

## TIPS & TRICKS

### Tip 1: Đặt Tên File Có Ý Nghĩa

Hệ thống tự động đặt tên:
```
DanhSach_Student_20241203_143025.xlsx
         ↑        ↑        ↑
      Loại    Ngày    Giờ
```

Bạn có thể đổi tên thành:
```
SinhVien_K2024_DaDangKy.xlsx
GiangVien_KhoaCNTT_2024.xlsx
```

### Tip 2: Lọc Dữ Liệu Trong Excel

Sau khi xuất, có thể:
- Lọc theo khóa học
- Lọc theo ngành
- Lọc sinh viên chưa có ảnh
- Sắp xếp theo tên

### Tip 3: Sao Lưu Định Kỳ

Nên xuất database:
- Đầu mỗi tháng
- Trước khi cập nhật hệ thống
- Trước kỳ thi
- Cuối năm học

### Tip 4: Bảo Mật File Excel

File có password nên:
- Không gửi qua email
- Không lưu trên cloud công cộng
- In ra và phát trực tiếp
- Hoặc mã hóa file Excel

---

## XỬ LÝ LỖI

### Lỗi: "Không có student/teacher nào trong database"

**Nguyên nhân:** Database trống

**Giải pháp:**
1. Kiểm tra đã tạo tài khoản chưa
2. Chạy `create_sample_data.py` để tạo dữ liệu mẫu
3. Import từ Excel

### Lỗi: "Không thể xuất Excel"

**Nguyên nhân:** 
- File đang mở
- Không có quyền ghi
- Đường dẫn không hợp lệ

**Giải pháp:**
1. Đóng file Excel nếu đang mở
2. Chọn thư mục khác
3. Kiểm tra quyền ghi

### Lỗi: "Chưa có student/teacher nào để xuất" (Xuất vừa tạo)

**Nguyên nhân:** Chưa click "Tạo tài khoản"

**Giải pháp:**
1. Import file Excel
2. Click "Tạo tài khoản"
3. Sau đó mới xuất

---

## CÂU HỎI THƯỜNG GẶP

**Q: Có thể xuất cả sinh viên và giảng viên vào 1 file không?**

A: Không, phải xuất riêng. Nhưng có thể:
1. Xuất sinh viên → Sheet1
2. Xuất giảng viên → Sheet2
3. Copy-paste vào 1 file Excel

**Q: File Excel có thể mở bằng Google Sheets không?**

A: Có, upload lên Google Drive và mở bằng Google Sheets.

**Q: Có thể xuất ra CSV không?**

A: Hiện tại chỉ hỗ trợ Excel (.xlsx). Nhưng có thể:
1. Mở file Excel
2. Save As → CSV

**Q: Dữ liệu có bị mất khi xuất không?**

A: Không, xuất Excel chỉ đọc dữ liệu, không xóa.

**Q: Có giới hạn số lượng xuất không?**

A: Không giới hạn, có thể xuất hàng nghìn bản ghi.

---

## KẾT LUẬN

Hệ thống cung cấp 2 chức năng xuất Excel linh hoạt:

1. **Xuất vừa tạo** - Cho việc phát tài khoản
2. **Xuất từ Database** - Cho việc thống kê, báo cáo

Sử dụng đúng chức năng cho đúng mục đích để tối ưu quy trình làm việc!

---

**Liên hệ hỗ trợ:** Nếu gặp vấn đề, liên hệ quản trị viên hệ thống.
