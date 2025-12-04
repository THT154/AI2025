# Contributing to Face Attendance System

Cảm ơn bạn đã quan tâm đến việc đóng góp cho dự án! 🎉

## Cách Đóng Góp

### 1. Báo Lỗi (Bug Reports)

Nếu bạn tìm thấy lỗi, vui lòng tạo [Issue](https://github.com/yourusername/face-attendance-system/issues) với thông tin:

- **Mô tả lỗi:** Mô tả chi tiết lỗi
- **Các bước tái hiện:** Cách tái hiện lỗi
- **Kết quả mong đợi:** Điều bạn mong đợi xảy ra
- **Kết quả thực tế:** Điều thực sự xảy ra
- **Screenshots:** Nếu có
- **Môi trường:**
  - OS: Windows/Linux/macOS
  - Python version
  - OpenCV version

### 2. Đề Xuất Tính Năng (Feature Requests)

Tạo [Issue](https://github.com/yourusername/face-attendance-system/issues) với:

- **Mô tả tính năng:** Tính năng bạn muốn thêm
- **Lý do:** Tại sao tính năng này hữu ích
- **Giải pháp đề xuất:** Cách bạn nghĩ nó nên hoạt động
- **Giải pháp thay thế:** Các cách khác bạn đã xem xét

### 3. Pull Requests

1. **Fork repository**
   ```bash
   # Click nút "Fork" trên GitHub
   ```

2. **Clone fork của bạn**
   ```bash
   git clone https://github.com/your-username/face-attendance-system.git
   cd face-attendance-system
   ```

3. **Tạo branch mới**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Thực hiện thay đổi**
   - Viết code rõ ràng, dễ hiểu
   - Thêm comments khi cần
   - Follow coding style hiện tại

5. **Test thay đổi**
   ```bash
   python main.py
   # Test kỹ tính năng mới
   ```

6. **Commit changes**
   ```bash
   git add .
   git commit -m "Add: Amazing feature description"
   ```

7. **Push to GitHub**
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Tạo Pull Request**
   - Vào GitHub repository của bạn
   - Click "New Pull Request"
   - Mô tả chi tiết thay đổi

## Coding Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Sử dụng 4 spaces cho indentation
- Tên biến: `snake_case`
- Tên class: `PascalCase`
- Tên hằng số: `UPPER_CASE`

### Comments

```python
# Tốt
def calculate_confidence(distance):
    """
    Tính confidence score từ distance
    
    Args:
        distance: Chi-square distance
    
    Returns:
        Confidence score (0-100%)
    """
    return max(0, 100 - distance)

# Không tốt
def calc(d):
    return max(0, 100 - d)
```

### Commit Messages

- Sử dụng tiếng Anh
- Bắt đầu với động từ: Add, Fix, Update, Remove
- Ngắn gọn, rõ ràng

```bash
# Tốt
git commit -m "Add: Liveness detection feature"
git commit -m "Fix: Camera not releasing properly"
git commit -m "Update: Improve face detection accuracy"

# Không tốt
git commit -m "update"
git commit -m "fix bug"
```

## Quy Trình Review

1. Maintainer sẽ review Pull Request
2. Có thể yêu cầu thay đổi
3. Sau khi approve, PR sẽ được merge
4. Tên bạn sẽ được thêm vào Contributors

## Các Vấn Đề Cần Giúp Đỡ

Chúng tôi đang tìm kiếm sự giúp đỡ cho:

- [ ] Nâng cấp lên Deep Learning
- [ ] Thêm Liveness Detection
- [ ] Multi-camera support
- [ ] RESTful API
- [ ] Mobile app
- [ ] Viết tests
- [ ] Cải thiện documentation
- [ ] Dịch sang tiếng Anh

## Câu Hỏi?

Nếu có câu hỏi, vui lòng:
- Tạo [Issue](https://github.com/yourusername/face-attendance-system/issues)
- Email: your.email@example.com

## Code of Conduct

- Tôn trọng mọi người
- Không spam
- Không toxic
- Giúp đỡ người mới

Cảm ơn bạn đã đóng góp! 🙏
