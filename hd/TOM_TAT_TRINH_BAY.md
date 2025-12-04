# TÓM TẮT TRÌNH BÀY - HỆ THỐNG ĐIỂM DANH AI

## SLIDE 1: GIỚI THIỆU (2 phút)

**Đề tài:** Hệ thống điểm danh tự động sử dụng AI nhận diện khuôn mặt

**Vấn đề:**
- Điểm danh thủ công tốn thời gian
- Dễ gian lận (ký hộ)
- Khó quản lý, thống kê

**Giải pháp:**
- Sử dụng AI nhận diện khuôn mặt
- Tự động điểm danh qua camera
- Lưu trữ điện tử, dễ quản lý

---

## SLIDE 2: CÔNG NGHỆ SỬ DỤNG (3 phút)

**Thuật toán chính: LBPH (Local Binary Patterns Histograms)**

**Tại sao chọn LBPH?**
- ✅ Nhanh: 30 FPS real-time
- ✅ Không cần GPU
- ✅ Độ chính xác: 85-92%
- ✅ Dễ triển khai

**So sánh:**
| Thuật toán | Độ chính xác | Tốc độ | GPU |
|------------|--------------|--------|-----|
| LBPH | 85% | Rất nhanh | Không |
| Deep Learning | 99% | Chậm | Cần |

---

## SLIDE 3: CÁCH HOẠT ĐỘNG (5 phút)

**Bước 1: Training**
```
Ảnh sinh viên (15-20 ảnh)
    ↓
Chuyển Grayscale
    ↓
Tính Local Binary Pattern
    ↓
Tạo Histogram
    ↓
Lưu Model
```

**Bước 2: Recognition**
```
Camera → Detect Face → Nhận diện → Điểm danh
```

**Công thức:**
```
LBP: So sánh pixel trung tâm với 8 pixel xung quanh
Confidence = 100 - Chi-Square Distance
```

---

## SLIDE 4: DEMO THỰC TẾ (5 phút)

**Demo 1: Training**
- Chụp ảnh sinh viên
- Train model (5-10 giây)
- Hiển thị kết quả

**Demo 2: Điểm danh**
- Mở camera
- Sinh viên đứng trước camera
- Tự động nhận diện và điểm danh
- Hiển thị danh sách

**Demo 3: Rà soát**
- Điều chỉnh trạng thái thủ công
- Chuyển vắng ↔ có mặt

---

## SLIDE 5: KẾT QUẢ (2 phút)

**Hiệu suất:**
- Accuracy: 85-92%
- FPS: 25-30
- Training time: 5-10s
- Model size: < 2MB

**Ưu điểm:**
- Tự động hóa hoàn toàn
- Tiết kiệm thời gian
- Chống gian lận
- Chi phí thấp

---

## SLIDE 6: HẠN CHẾ & PHÁT TRIỂN (2 phút)

**Hạn chế:**
- Độ chính xác chưa cao như Deep Learning
- Nhạy cảm với ánh sáng
- Có thể gian lận bằng ảnh

**Hướng phát triển:**
- Nâng cấp lên Deep Learning (FaceNet)
- Thêm Liveness Detection
- Multi-camera support
- Cloud integration

---

## CÂU HỎI DỰ ĐOÁN & TRẢ LỜI

### Câu 1: "Tại sao không dùng Deep Learning?"

**Trả lời:**
- Deep Learning cần GPU mạnh (10-20 triệu)
- Training lâu (1-24 giờ)
- Model lớn (100MB+)
- LBPH đủ tốt cho quy mô nhỏ (< 100 SV)
- Chi phí thấp, dễ triển khai

### Câu 2: "Làm sao tránh gian lận bằng ảnh?"

**Trả lời:**
- Hiện tại: Chưa có liveness detection
- Giải pháp tương lai:
  - Kiểm tra chuyển động (blink, nod)
  - Phân tích depth (camera 3D)
  - Yêu cầu thực hiện hành động ngẫu nhiên

### Câu 3: "Độ chính xác 85% có đủ không?"

**Trả lời:**
- Đủ cho điểm danh vì:
  - Có cơ chế rà soát thủ công
  - 15% sai có thể do góc nghiêng, ánh sáng
  - Giáo viên có thể sửa sau
- Nếu cần cao hơn: Chuyển sang Deep Learning

### Câu 4: "Xử lý bao nhiêu sinh viên cùng lúc?"

**Trả lời:**
- Không giới hạn về mặt lý thuyết
- Thực tế: 5-10 người cùng lúc vẫn mượt
- Mỗi face: ~50ms
- 10 faces: ~500ms = 2 FPS (vẫn OK)

### Câu 5: "Chi phí triển khai?"

**Trả lời:**
- Phần mềm: Miễn phí (open source)
- Phần cứng: 5-10 triệu/phòng
  - Máy tính: 3-5 triệu
  - Webcam: 500k-1 triệu
- Bảo trì: Rất thấp (không cần cloud, GPU)

### Câu 6: "Có thể scale lên bao nhiêu người?"

**Trả lời:**
- LBPH: Tốt với < 100 người
- 100-500: Vẫn OK nhưng chậm hơn
- > 500: Nên chuyển Deep Learning
- Lý do: Model size tăng, so sánh lâu hơn

### Câu 7: "Training mất bao lâu?"

**Trả lời:**
- 20 SV × 15 ảnh = 300 ảnh
- Thời gian: 5-10 giây
- Có thể train lại bất cứ lúc nào
- Không cần GPU

### Câu 8: "Làm sao xử lý ánh sáng kém?"

**Trả lời:**
- Tiền xử lý: Histogram equalization
- Cân bằng độ sáng tự động
- Khuyến nghị: Ánh sáng tốt khi chụp & điểm danh
- Tương lai: Sử dụng IR camera (hồng ngoại)

### Câu 9: "Có thể tích hợp với hệ thống khác?"

**Trả lời:**
- Hiện tại: Standalone
- Tương lai: Xây dựng RESTful API
- Có thể tích hợp với:
  - Hệ thống quản lý sinh viên
  - Portal trường
  - Mobile app

### Câu 10: "Bảo mật dữ liệu như thế nào?"

**Trả lời:**
- Ảnh lưu local, không upload cloud
- Database có password
- Không lưu ảnh gốc, chỉ lưu features
- Có thể mã hóa model file
- Tuân thủ GDPR về dữ liệu sinh trắc học

---

## TIPS TRÌNH BÀY

**Chuẩn bị:**
- ✅ Laptop có webcam
- ✅ Đã train model trước
- ✅ Có 2-3 người để demo
- ✅ Ánh sáng tốt
- ✅ Backup slides PDF

**Trong khi trình bày:**
- Nói chậm, rõ ràng
- Giải thích thuật ngữ kỹ thuật
- Dùng ví dụ cụ thể
- Tương tác với hội đồng
- Tự tin, mỉm cười

**Khi demo:**
- Test trước 5 phút
- Có plan B nếu lỗi
- Giải thích từng bước
- Highlight điểm mạnh

**Trả lời câu hỏi:**
- Lắng nghe kỹ câu hỏi
- Suy nghĩ 2-3 giây
- Trả lời ngắn gọn, đúng trọng tâm
- Thừa nhận nếu không biết
- Đề xuất hướng giải quyết

---

## THỜI GIAN PHÂN BỔ (20 phút)

- Giới thiệu: 2 phút
- Công nghệ: 3 phút
- Cách hoạt động: 5 phút
- Demo: 5 phút
- Kết quả: 2 phút
- Hạn chế & phát triển: 2 phút
- Dự phòng: 1 phút

**Vấn đáp: 10-15 phút**

---

## CHECKLIST TRƯỚC KHI TRÌNH BÀY

- [ ] Đã test demo
- [ ] Đã train model
- [ ] Laptop đầy pin
- [ ] Webcam hoạt động
- [ ] Database đã có dữ liệu
- [ ] Slides đã chuẩn bị
- [ ] Đã đọc lại tài liệu
- [ ] Đã chuẩn bị câu trả lời
- [ ] Ăn mặc chỉnh tề
- [ ] Tinh thần thoải mái

---

**CHÚC BẠN THÀNH CÔNG! 🎓🚀**
