# test_recognition.py - Test nhận diện khuôn mặt real-time
import cv2
from face_recognition_service import face_service
from config import Config

def test_recognition():
    """Test nhận diện khuôn mặt từ camera"""
    print("=== TEST NHẬN DIỆN KHUÔN MẶT ===\n")
    
    # Kiểm tra model đã train chưa
    if not face_service.recognizer:
        print("❌ Model chưa được train!")
        print("   Vui lòng chạy: python test_train_model.py")
        return
    
    print("✓ Model đã sẵn sàng")
    print(f"✓ Số sinh viên trong model: {len(face_service.labels)}")
    print(f"✓ Danh sách: {', '.join(face_service.labels.values())}\n")
    
    # Mở camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Không thể mở camera!")
        return
    
    print("📹 Camera đã sẵn sàng!")
    print(f"🎯 Ngưỡng tin cậy: {Config.CONFIDENCE_THRESHOLD}%")
    print("\nHướng dẫn:")
    print("  - Nhìn vào camera để được nhận diện")
    print("  - Khung XANH = Nhận diện thành công (>= 50%)")
    print("  - Khung ĐỎ = Độ tin cậy thấp (< 50%)")
    print("  - Nhấn 'q' hoặc ESC để thoát\n")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không đọc được frame!")
            break
        
        frame_count += 1
        
        # Nhận diện mỗi 3 frame để tăng tốc độ
        if frame_count % 3 == 0:
            # Nhận diện khuôn mặt
            recognized = face_service.recognize_faces(frame)
            
            # Vẽ kết quả lên frame
            frame = face_service.draw_faces(frame, recognized, Config.CONFIDENCE_THRESHOLD)
            
            # In kết quả ra console
            if recognized and frame_count % 30 == 0:  # In mỗi 30 frame
                for face in recognized:
                    status = "✓" if face['confidence'] >= Config.CONFIDENCE_THRESHOLD else "✗"
                    print(f"{status} {face['student_code']}: {face['confidence']:.1f}% "
                          f"(raw: {face['raw_confidence']:.1f})")
        
        # Hiển thị hướng dẫn
        cv2.putText(frame, "Nhan 'q' hoac ESC de thoat", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Nguong: {Config.CONFIDENCE_THRESHOLD}%", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Test Nhan Dien - Nhan q de thoat', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' hoặc ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✓ Đã dừng test")

if __name__ == "__main__":
    test_recognition()
