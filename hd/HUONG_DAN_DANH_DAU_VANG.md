# Hướng Dẫn Đánh Dấu Sinh Viên Vắng

## Tính Năng Mới

Khi giáo viên kết thúc buổi điểm danh, hệ thống sẽ tự động:
- ✅ Đánh dấu sinh viên chưa điểm danh là **VẮNG**
- ✅ Hiển thị danh sách sinh viên vắng với màu đỏ
- ✅ Cập nhật vào database để sinh viên xem được trạng thái
- ✅ Tạo báo cáo chi tiết về buổi điểm danh

## Cách Sử Dụng

### Bước 1: Bắt Đầu Điểm Danh

1. Đăng nhập với tài khoản giáo viên
2. Vào tab **"✅ Điểm danh"**
3. Chọn lớp cần điểm danh
4. Click **"📸 Bắt đầu điểm danh"**
5. Camera sẽ tự động bật và nhận diện sinh viên

### Bước 2: Sinh Viên Điểm Danh

- Sinh viên lần lượt đứng trước camera
- Hệ thống tự động nhận diện và điểm danh
- Sinh viên có mặt sẽ hiển thị với **nền màu xanh lá**
- Thông tin hiển thị: Mã SV, Họ tên, Giờ, Độ tin cậy

### Bước 3: Kết Thúc Điểm Danh

Click lại nút **"📸 Bắt đầu điểm danh"** (hoặc đóng camera)

Hệ thống sẽ hiển thị hộp thoại với 3 lựa chọn:

#### ✅ YES - Đánh dấu vắng
- Tự động đánh dấu tất cả sinh viên chưa điểm danh là **VẮNG**
- Sinh viên vắng sẽ hiển thị với **nền màu đỏ**
- Cập nhật vào database
- Hiển thị thống kê: Tổng SV, Có mặt, Vắng

#### ❌ NO - Chỉ dừng camera
- Dừng camera nhưng không đánh dấu vắng
- Sinh viên chưa điểm danh vẫn chưa có trạng thái
- Có thể tiếp tục điểm danh sau

#### ⏸️ CANCEL - Tiếp tục điểm danh
- Không dừng camera
- Tiếp tục nhận diện sinh viên
- Dùng khi nhấn nhầm hoặc muốn điểm danh thêm

### Bước 4: Xem Báo Cáo

Click nút **"📋 Xem báo cáo"** để xem chi tiết:

**Tab "✅ Có mặt":**
- STT
- Mã sinh viên
- Họ tên
- Giờ điểm danh
- Độ tin cậy

**Tab "❌ Vắng":**
- STT
- Mã sinh viên
- Họ tên

**Thống kê:**
- Tổng sinh viên
- Số sinh viên có mặt (%)
- Số sinh viên vắng (%)

## Sinh Viên Xem Trạng Thái

Sinh viên có thể xem trạng thái điểm danh của mình:

1. Đăng nhập với tài khoản sinh viên
2. Vào tab **"📊 Điểm danh"**
3. Xem danh sách các buổi học:
   - **present** = Có mặt ✅
   - **absent** = Vắng ❌
   - **late** = Đi muộn ⏰

## Ví Dụ Quy Trình

```
1. Giáo viên bắt đầu điểm danh lúc 7:00
2. Sinh viên A, B, C đứng trước camera → Tự động điểm danh
3. Lúc 7:15, giáo viên kết thúc điểm danh
4. Chọn "YES" để đánh dấu vắng
5. Sinh viên D, E chưa điểm danh → Tự động đánh dấu VẮNG
6. Kết quả:
   - Có mặt: A, B, C (màu xanh)
   - Vắng: D, E (màu đỏ)
7. Sinh viên D, E đăng nhập → Thấy trạng thái "absent"
```

## Màu Sắc Hiển Thị

| Trạng thái | Màu nền | Ý nghĩa |
|------------|---------|---------|
| Có mặt | 🟢 Xanh lá (#ccffcc) | Đã điểm danh qua camera |
| Vắng | 🔴 Đỏ (#ffcccc) | Chưa điểm danh khi kết thúc |

## Lưu Ý Quan Trọng

⚠️ **Khi nào nên đánh dấu vắng?**
- Khi đã chắc chắn kết thúc buổi học
- Sau khi đã cho sinh viên đủ thời gian điểm danh
- Trước khi đóng ứng dụng

⚠️ **Không nên đánh dấu vắng khi:**
- Vẫn còn sinh viên chưa điểm danh
- Muốn tiếp tục điểm danh sau giờ nghỉ
- Chưa chắc chắn về danh sách

⚠️ **Lưu ý:**
- Một khi đã đánh dấu vắng, không thể hoàn tác tự động
- Cần sửa thủ công trong database nếu đánh dấu nhầm
- Sinh viên sẽ thấy trạng thái "absent" ngay lập tức

## Xử Lý Trường Hợp Đặc Biệt

### Sinh viên đến muộn sau khi đã đánh dấu vắng

**Cách 1: Sửa trong database**
```sql
UPDATE attendance 
SET status = 'late', check_in_time = NOW()
WHERE session_id = <ID> AND student_id = <ID>;
```

**Cách 2: Điểm danh thủ công**
- Giáo viên có thể thêm chức năng điểm danh thủ công (sẽ cập nhật sau)

### Sinh viên có lý do chính đáng

- Giáo viên có thể sửa trạng thái từ "absent" → "present" trong database
- Hoặc thêm ghi chú vào hệ thống (tính năng tương lai)

## Thống Kê và Báo Cáo

Sau mỗi buổi điểm danh, hệ thống lưu:
- ✅ Thời gian điểm danh của từng sinh viên
- ✅ Độ tin cậy nhận diện (%)
- ✅ Trạng thái: present/absent/late
- ✅ Ngày, buổi, tiết học

Dữ liệu này dùng để:
- Tính tỷ lệ tham gia của sinh viên
- Gửi email thông báo vắng (tính năng tương lai)
- Xuất báo cáo cuối kỳ
- Cảnh báo sinh viên vắng nhiều

## Tính Năng Sắp Tới

- [ ] Điểm danh thủ công (cho trường hợp đặc biệt)
- [ ] Sửa trạng thái điểm danh
- [ ] Gửi email tự động cho sinh viên vắng
- [ ] Xuất báo cáo Excel
- [ ] Thống kê tỷ lệ tham gia theo lớp/sinh viên
- [ ] Cảnh báo sinh viên vắng quá 20%

## Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra kết nối database
2. Đảm bảo đã tạo session trước khi điểm danh
3. Xem log trong console
4. Liên hệ quản trị viên nếu cần sửa dữ liệu
