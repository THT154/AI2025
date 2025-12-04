# Hướng Dẫn Rà Soát Điểm Danh

## Tổng Quan

Chức năng **Rà soát điểm danh** cho phép giáo viên điều chỉnh trạng thái điểm danh sau khi kết thúc buổi học, xử lý các trường hợp:
- ✅ Sinh viên đến muộn sau khi đã đánh dấu vắng
- ✅ Sinh viên có lý do chính đáng (xin phép, ốm đau)
- ✅ Sửa lỗi nhận diện sai
- ✅ Điểm danh thủ công cho sinh viên không nhận diện được

## Giao Diện

Cửa sổ rà soát chia làm 2 cột:

### Cột Trái - ✅ CÓ MẶT (Nền xanh)
- Danh sách sinh viên đã điểm danh
- Hiển thị: Mã SV, Họ tên, Giờ điểm danh
- Nút: **"➡️ Đánh dấu VẮNG"**

### Cột Phải - ❌ VẮNG (Nền đỏ)
- Danh sách sinh viên vắng
- Hiển thị: Mã SV, Họ tên, Giờ đánh dấu
- Nút: **"⬅️ Đánh dấu CÓ MẶT"**

### Thống kê
- Tổng số sinh viên
- Số sinh viên có mặt (%)
- Số sinh viên vắng (%)

## Cách Sử Dụng

### Bước 1: Mở Cửa Sổ Rà Soát

1. Sau khi kết thúc điểm danh
2. Click nút **"✏️ Rà soát điểm danh"** trên toolbar
3. Cửa sổ rà soát sẽ hiển thị

### Bước 2: Chuyển Sinh Viên Từ Có Mặt → Vắng

**Trường hợp sử dụng:**
- Sinh viên được nhận diện nhầm
- Sinh viên rời lớp sớm không xin phép
- Điều chỉnh theo quy định của trường

**Các bước:**
1. Chọn sinh viên trong cột **"✅ CÓ MẶT"**
2. Click nút **"➡️ Đánh dấu VẮNG"**
3. Xác nhận trong hộp thoại
4. Sinh viên sẽ chuyển sang cột **"❌ VẮNG"**

### Bước 3: Chuyển Sinh Viên Từ Vắng → Có Mặt

**Trường hợp sử dụng:**
- Sinh viên đến muộn sau khi đã đánh dấu vắng
- Sinh viên có giấy xin phép hợp lệ
- Sinh viên có lý do chính đáng (ốm, việc gia đình)
- Điểm danh thủ công

**Các bước:**
1. Chọn sinh viên trong cột **"❌ VẮNG"**
2. Click nút **"⬅️ Đánh dấu CÓ MẶT"**
3. Xác nhận trong hộp thoại
4. Sinh viên sẽ chuyển sang cột **"✅ CÓ MẶT"**

### Bước 4: Lưu Thay Đổi

Click nút **"💾 Lưu và Đóng"** để:
- Lưu tất cả thay đổi vào database
- Cập nhật danh sách ở cửa sổ chính
- Đóng cửa sổ rà soát

## Ví Dụ Thực Tế

### Ví Dụ 1: Sinh Viên Đến Muộn

**Tình huống:**
- Giáo viên kết thúc điểm danh lúc 7:15
- Sinh viên A đến lúc 7:20 (sau khi đã đánh dấu vắng)

**Xử lý:**
1. Mở cửa sổ rà soát
2. Tìm sinh viên A trong cột **"❌ VẮNG"**
3. Chọn sinh viên A
4. Click **"⬅️ Đánh dấu CÓ MẶT"**
5. Xác nhận
6. Click **"💾 Lưu và Đóng"**

**Kết quả:**
- Sinh viên A chuyển sang trạng thái "Có mặt"
- Giờ điểm danh được cập nhật là 7:20

### Ví Dụ 2: Nhận Diện Sai

**Tình huống:**
- Hệ thống nhận diện nhầm sinh viên B là sinh viên C
- Sinh viên B thực tế không có mặt

**Xử lý:**
1. Mở cửa sổ rà soát
2. Tìm sinh viên B trong cột **"✅ CÓ MẶT"**
3. Chọn sinh viên B
4. Click **"➡️ Đánh dấu VẮNG"**
5. Xác nhận
6. Nếu sinh viên C vắng, tìm trong cột **"❌ VẮNG"** và đánh dấu có mặt
7. Click **"💾 Lưu và Đóng"**

### Ví Dụ 3: Sinh Viên Có Giấy Phép

**Tình huống:**
- Sinh viên D vắng nhưng có giấy xin phép hợp lệ
- Theo quy định trường, tính là có mặt

**Xử lý:**
1. Mở cửa sổ rà soát
2. Tìm sinh viên D trong cột **"❌ VẮNG"**
3. Chọn sinh viên D
4. Click **"⬅️ Đánh dấu CÓ MẶT"**
5. Xác nhận
6. Click **"💾 Lưu và Đóng"**

## Các Nút Chức Năng

| Nút | Chức năng |
|-----|-----------|
| **💾 Lưu và Đóng** | Lưu thay đổi và đóng cửa sổ |
| **🔄 Làm mới** | Tải lại dữ liệu từ database |
| **❌ Đóng** | Đóng cửa sổ (không lưu nếu chưa click "Lưu") |
| **➡️ Đánh dấu VẮNG** | Chuyển sinh viên từ có mặt → vắng |
| **⬅️ Đánh dấu CÓ MẶT** | Chuyển sinh viên từ vắng → có mặt |

## Lưu Ý Quan Trọng

### ⚠️ Về Thời Gian

- Khi chuyển trạng thái, giờ điểm danh sẽ được cập nhật là thời điểm hiện tại
- Nếu muốn giữ nguyên giờ cũ, cần sửa trực tiếp trong database

### ⚠️ Về Độ Tin Cậy

- Sinh viên được chuyển từ vắng → có mặt sẽ có `confidence_score = NULL`
- Điều này cho biết đây là điểm danh thủ công, không phải qua AI

### ⚠️ Về Lưu Dữ Liệu

- Mỗi lần click nút chuyển trạng thái, dữ liệu được lưu ngay vào database
- Nút "Lưu và Đóng" chỉ để làm mới danh sách ở cửa sổ chính
- Có thể đóng cửa sổ bất cứ lúc nào mà không mất dữ liệu

### ⚠️ Về Quyền Hạn

- Chỉ giáo viên mới có quyền rà soát điểm danh
- Sinh viên không thể tự thay đổi trạng thái của mình
- Moderator có thể thêm quyền này (tính năng tương lai)

## Quy Trình Hoàn Chỉnh

```
1. Giáo viên bắt đầu điểm danh (7:00)
   ↓
2. Sinh viên A, B, C điểm danh qua camera (7:00-7:10)
   ↓
3. Giáo viên kết thúc điểm danh (7:15)
   → Chọn "YES" để đánh dấu vắng
   → Sinh viên D, E được đánh dấu vắng
   ↓
4. Sinh viên D đến muộn (7:20)
   ↓
5. Giáo viên mở "Rà soát điểm danh"
   ↓
6. Chuyển sinh viên D từ vắng → có mặt
   ↓
7. Click "Lưu và Đóng"
   ↓
8. Kết quả cuối:
   - Có mặt: A, B, C, D
   - Vắng: E
```

## Thống Kê Sau Rà Soát

Sau khi rà soát, sinh viên có thể xem:
- Trạng thái điểm danh đã được cập nhật
- Giờ điểm danh mới (nếu có thay đổi)
- Tỷ lệ tham gia chính xác hơn

## Tính Năng Nâng Cao (Tương Lai)

- [ ] Thêm ghi chú cho mỗi lần thay đổi
- [ ] Lịch sử thay đổi trạng thái
- [ ] Xuất báo cáo rà soát
- [ ] Gửi thông báo cho sinh viên khi thay đổi
- [ ] Cho phép moderator rà soát
- [ ] Điểm danh thủ công hàng loạt

## Câu Hỏi Thường Gặp

**Q: Có thể rà soát nhiều lần không?**
A: Có, bạn có thể mở cửa sổ rà soát bao nhiêu lần tùy thích.

**Q: Thay đổi có ảnh hưởng đến sinh viên ngay lập tức không?**
A: Có, sinh viên sẽ thấy trạng thái mới khi làm mới trang điểm danh.

**Q: Có thể hoàn tác thay đổi không?**
A: Có, chỉ cần mở lại cửa sổ rà soát và chuyển ngược lại.

**Q: Làm sao biết ai đã thay đổi trạng thái?**
A: Hiện tại chưa có log, sẽ được thêm trong phiên bản sau.

**Q: Có giới hạn số lần thay đổi không?**
A: Không, bạn có thể thay đổi không giới hạn.

## Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra kết nối database
2. Đảm bảo đã kết thúc buổi điểm danh
3. Làm mới danh sách bằng nút "🔄 Làm mới"
4. Liên hệ quản trị viên nếu cần hỗ trợ
