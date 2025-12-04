# Hướng Dẫn Chụp Ảnh Khuôn Mặt

## Vấn Đề: Không Nhận Diện Được

Nếu hệ thống không nhận diện được bạn, nguyên nhân thường là:
1. **Quá ít ảnh để train** (chỉ có 1-2 ảnh)
2. **Ảnh không đa dạng** (cùng góc độ, biểu cảm)
3. **Chất lượng ảnh kém** (mờ, tối, xa camera)

## Giải Pháp: Chụp Nhiều Ảnh Đa Dạng

### Bước 1: Xem Danh Sách Sinh Viên

```bash
python capture_face_images.py --list
```

### Bước 2: Chụp Ảnh Cho Sinh Viên

```bash
python capture_face_images.py <MÃ_SINH_VIÊN> <SỐ_ẢNH>
```

**Ví dụ:**
```bash
# Chụp 15 ảnh cho sinh viên 23NS064
python capture_face_images.py 23NS064 15

# Chụp 20 ảnh cho sinh viên 23NS091
python capture_face_images.py 23NS091 20
```

### Bước 3: Khi Camera Mở

1. **Đứng trước camera** (khoảng 50cm - 1m)
2. **Nhìn thẳng vào camera** để thấy khung xanh quanh mặt
3. **Nhấn SPACE** để chụp ảnh
4. **Thay đổi tư thế** sau mỗi lần chụp:
   - Quay mặt sang trái
   - Quay mặt sang phải
   - Ngẩng đầu lên
   - Cúi đầu xuống một chút
   - Thay đổi biểu cảm (cười, nghiêm túc)
   - Di chuyển gần/xa camera
5. **Lặp lại** cho đến khi đủ số ảnh
6. **Nhấn ESC** để thoát sớm (nếu cần)

### Bước 4: Train Lại Model

Sau khi chụp đủ ảnh cho tất cả sinh viên:

```bash
python test_train_model.py
```

Hoặc trong ứng dụng: Vào tab "🤖 Train Model AI" → Click "🚀 Train Model"

## Mẹo Để Nhận Diện Tốt

### Khi Chụp Ảnh:
- ✅ **Ánh sáng tốt** - Chụp ở nơi sáng, tránh ngược sáng
- ✅ **Nhiều góc độ** - Ít nhất 15-20 ảnh với các góc khác nhau
- ✅ **Khuôn mặt rõ ràng** - Không đeo khẩu trang, kính đen
- ✅ **Nền đơn giản** - Tránh nền quá rối
- ✅ **Khoảng cách vừa phải** - 50cm - 1m từ camera

### Khi Điểm Danh:
- ✅ **Cùng điều kiện ánh sáng** với lúc chụp
- ✅ **Nhìn thẳng vào camera** 2-3 giây
- ✅ **Khoảng cách tương tự** lúc chụp
- ✅ **Kiên nhẫn** - Hệ thống cần vài giây để nhận diện

## Khắc Phục Lỗi Thường Gặp

### "Không phát hiện khuôn mặt"
- Đứng gần camera hơn
- Bật đèn, tăng ánh sáng
- Nhìn thẳng vào camera

### "Độ tin cậy thấp" (< 50%)
- Chụp thêm ảnh (20-30 ảnh)
- Train lại model
- Đảm bảo ánh sáng tốt khi điểm danh

### "Nhận diện sai người"
- Mỗi sinh viên cần ít nhất 15 ảnh riêng biệt
- Không dùng ảnh chung nhiều người
- Train lại model sau khi thêm ảnh

## Quy Trình Hoàn Chỉnh

```bash
# 1. Xem danh sách sinh viên
python capture_face_images.py --list

# 2. Chụp ảnh cho từng sinh viên (15-20 ảnh/người)
python capture_face_images.py 23NS064 15
python capture_face_images.py 23NS091 15
python capture_face_images.py 23IT056 15
# ... (lặp lại cho tất cả sinh viên)

# 3. Kiểm tra đã cập nhật chưa
python upload_face_images.py

# 4. Train model
python test_train_model.py

# 5. Chạy ứng dụng và điểm danh
python main.py
```

## Thông Số Khuyến Nghị

| Thông số | Giá trị khuyến nghị |
|----------|---------------------|
| Số ảnh/sinh viên | 15-20 ảnh |
| Độ tin cậy tối thiểu | 50% (có thể tăng lên 60-70%) |
| Khoảng cách camera | 50cm - 1m |
| Ánh sáng | Sáng, không ngược sáng |
| Góc độ | Đa dạng (thẳng, trái, phải, trên, dưới) |

## Điều Chỉnh Độ Tin Cậy

Nếu muốn chặt chẽ hơn, sửa file `config.py`:

```python
CONFIDENCE_THRESHOLD = 60  # Tăng từ 50 lên 60
```

Lưu ý: Tăng quá cao có thể khiến hệ thống khó nhận diện hơn.
