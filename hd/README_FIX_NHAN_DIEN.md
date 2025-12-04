# Khắc Phục Lỗi "Không Nhận Diện Được"

## Vấn Đề

Bạn đang gặp lỗi hệ thống không nhận diện được khuôn mặt khi điểm danh.

## Nguyên Nhân

✗ **Chỉ có 1 ảnh để train** - Không đủ để AI học tốt  
✗ **Ảnh không đa dạng** - Cùng góc độ, biểu cảm  
✗ **Điều kiện ánh sáng khác nhau** - Chụp ở nơi sáng, điểm danh ở nơi tối  

## Giải Pháp Nhanh (3 Bước)

### Bước 1: Chụp Nhiều Ảnh (15-20 ảnh)

```bash
# Xem danh sách sinh viên
python capture_face_images.py --list

# Chụp 15 ảnh cho sinh viên (thay MÃ_SV bằng mã của bạn)
python capture_face_images.py 23NS064 15
```

**Khi camera mở:**
1. Nhìn vào camera → Thấy khung xanh
2. Nhấn **SPACE** để chụp
3. **Thay đổi tư thế** sau mỗi lần:
   - Quay trái/phải
   - Ngẩng/cúi đầu nhẹ
   - Cười/nghiêm túc
   - Gần/xa camera
4. Lặp lại đến khi đủ 15 ảnh

### Bước 2: Train Lại Model

```bash
python test_train_model.py
```

Kết quả mong đợi:
```
✅ TRAIN THÀNH CÔNG!
  - Số sinh viên: 1
  - Tổng số ảnh: 15
```

### Bước 3: Test Nhận Diện

```bash
python test_recognition.py
```

Nhìn vào camera và kiểm tra:
- ✅ Khung XANH + tên + độ tin cậy >= 50% → **Thành công!**
- ✗ Khung ĐỎ hoặc độ tin cậy < 50% → Cần chụp thêm ảnh

## Quy Trình Đầy Đủ Cho Nhiều Sinh Viên

```bash
# 1. Chụp ảnh cho tất cả sinh viên
python capture_face_images.py 23NS064 15
python capture_face_images.py 23NS091 15
python capture_face_images.py 23IT056 15
# ... (lặp lại cho từng sinh viên)

# 2. Cập nhật database (nếu cần)
python upload_face_images.py

# 3. Train model
python test_train_model.py

# 4. Test nhận diện
python test_recognition.py

# 5. Chạy ứng dụng chính
python main.py
```

## Mẹo Để Nhận Diện Tốt

### ✅ Khi Chụp Ảnh:
- Ánh sáng tốt (không ngược sáng)
- 15-20 ảnh với nhiều góc độ
- Khuôn mặt rõ ràng (không đeo khẩu trang)
- Khoảng cách 50cm - 1m

### ✅ Khi Điểm Danh:
- Cùng điều kiện ánh sáng với lúc chụp
- Nhìn thẳng vào camera 2-3 giây
- Khoảng cách tương tự lúc chụp

## Điều Chỉnh Độ Tin Cậy

Nếu muốn dễ dàng hơn (chấp nhận độ chính xác thấp hơn):

**File: `config.py`**
```python
CONFIDENCE_THRESHOLD = 40  # Giảm từ 50 xuống 40
```

Nếu muốn chặt chẽ hơn (độ chính xác cao hơn):
```python
CONFIDENCE_THRESHOLD = 60  # Tăng từ 50 lên 60
```

## Kiểm Tra Nhanh

### Có bao nhiêu ảnh?
```bash
python upload_face_images.py
```

### Model đã train chưa?
```bash
python test_train_model.py
```

### Nhận diện có hoạt động không?
```bash
python test_recognition.py
```

## Kết Quả Mong Đợi

Sau khi làm theo 3 bước trên, bạn sẽ thấy:

```
Test Nhận Diện:
✓ 23NS064: 75.3% (Khung XANH)
```

Điều này có nghĩa là:
- ✅ Hệ thống nhận diện được bạn
- ✅ Độ tin cậy 75.3% (> 50%)
- ✅ Sẵn sàng điểm danh

## Lưu Ý Quan Trọng

⚠ **Số ảnh tối thiểu:** 10 ảnh/sinh viên  
⚠ **Số ảnh khuyến nghị:** 15-20 ảnh/sinh viên  
⚠ **Đa dạng góc độ:** Càng nhiều càng tốt  
⚠ **Ánh sáng:** Phải tương tự giữa lúc chụp và lúc điểm danh  

## Hỗ Trợ

Nếu vẫn không nhận diện được sau khi làm theo hướng dẫn:

1. Kiểm tra log trong console
2. Chụp thêm ảnh (20-30 ảnh)
3. Đảm bảo ánh sáng tốt
4. Thử giảm CONFIDENCE_THRESHOLD xuống 40

## Các File Hỗ Trợ

- `capture_face_images.py` - Chụp ảnh từ webcam
- `upload_face_images.py` - Cập nhật database
- `test_train_model.py` - Train và test model
- `test_recognition.py` - Test nhận diện real-time
- `HUONG_DAN_CHUP_ANH.md` - Hướng dẫn chi tiết
