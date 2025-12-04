# capture_face_images.py - Chụp ảnh khuôn mặt từ webcam
import cv2
import os
from datetime import datetime
from config import Config
from database import Database

def capture_faces_for_student(student_code, num_images=15):
    """
    Chụp nhiều ảnh khuôn mặt cho sinh viên
    
    Args:
        student_code: Mã sinh viên
        num_images: Số ảnh cần chụp (mặc định 15)
    """
    print(f"\n=== CHỤP ẢNH CHO SINH VIÊN {student_code} ===\n")
    
    # Tạo folder cho sinh viên
    student_folder = os.path.join(Config.FACE_IMAGES_FOLDER, student_code)
    os.makedirs(student_folder, exist_ok=True)
    
    # Khởi động camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Không thể mở camera!")
        return False
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    print("📹 Camera đã sẵn sàng!")
    print(f"🎯 Mục tiêu: Chụp {num_images} ảnh")
    print("\nHướng dẫn:")
    print("  - Nhìn thẳng vào camera")
    print("  - Nhấn SPACE để chụp ảnh")
    print("  - Thay đổi góc độ, biểu cảm sau mỗi lần chụp")
    print("  - Nhấn ESC để thoát\n")
    
    captured_count = 0
    
    while captured_count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không đọc được frame từ camera!")
            break
        
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(100, 100)
        )
        
        # Vẽ khung quanh khuôn mặt
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Nhan SPACE de chup", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Hiển thị số ảnh đã chụp
        text = f"Da chup: {captured_count}/{num_images}"
        cv2.putText(frame, text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Hiển thị hướng dẫn
        cv2.putText(frame, "SPACE: Chup | ESC: Thoat", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow(f'Chup anh - {student_code}', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Nhấn SPACE để chụp
        if key == ord(' '):
            if len(faces) > 0:
                # Lưu ảnh
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{student_code}_{captured_count+1}_{timestamp}.jpg"
                filepath = os.path.join(student_folder, filename)
                
                cv2.imwrite(filepath, frame)
                captured_count += 1
                
                print(f"✓ Đã chụp ảnh {captured_count}/{num_images}: {filename}")
                
                # Hiệu ứng flash
                flash = frame.copy()
                flash[:] = (255, 255, 255)
                cv2.imshow(f'Chup anh - {student_code}', flash)
                cv2.waitKey(100)
            else:
                print("⚠ Không phát hiện khuôn mặt! Hãy nhìn vào camera.")
        
        # Nhấn ESC để thoát
        elif key == 27:
            print("\n⚠ Đã hủy chụp ảnh")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if captured_count >= num_images:
        print(f"\n✅ Hoàn tất! Đã chụp {captured_count} ảnh")
        print(f"📁 Lưu tại: {student_folder}")
        return True
    else:
        print(f"\n⚠ Chỉ chụp được {captured_count}/{num_images} ảnh")
        return False

def update_database(student_code):
    """Cập nhật database với đường dẫn ảnh"""
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("❌ Không thể kết nối database!")
        return False
    
    student_folder = os.path.join(Config.FACE_IMAGES_FOLDER, student_code)
    
    cursor = db.connection.cursor()
    cursor.execute("""
        UPDATE students 
        SET face_encoding_path = %s 
        WHERE student_code = %s
    """, (student_folder, student_code))
    db.connection.commit()
    cursor.close()
    
    db.disconnect()
    print("✓ Đã cập nhật database")
    return True

def list_students():
    """Hiển thị danh sách sinh viên"""
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("❌ Không thể kết nối database!")
        return
    
    students = db.get_all_students()
    
    print("\n=== DANH SÁCH SINH VIÊN ===\n")
    print(f"{'STT':<5} {'Mã SV':<15} {'Họ tên':<30} {'Có ảnh':<10}")
    print("-" * 65)
    
    for i, student in enumerate(students, 1):
        has_face = "✓" if student.get('face_encoding_path') else "✗"
        print(f"{i:<5} {student['student_code']:<15} {student['full_name']:<30} {has_face:<10}")
    
    db.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_students()
        else:
            student_code = sys.argv[1]
            num_images = int(sys.argv[2]) if len(sys.argv) > 2 else 15
            
            # Chụp ảnh
            success = capture_faces_for_student(student_code, num_images)
            
            if success:
                # Cập nhật database
                update_database(student_code)
                
                print("\n🎉 Hoàn tất! Bây giờ bạn có thể:")
                print("  1. Chụp ảnh cho sinh viên khác")
                print("  2. Train model: python test_train_model.py")
                print("  3. Bắt đầu điểm danh")
    else:
        print("=== CÔNG CỤ CHỤP ẢNH KHUÔN MẶT ===\n")
        print("Cách sử dụng:")
        print("  python capture_face_images.py <mã_sinh_viên> [số_ảnh]")
        print("\nVí dụ:")
        print("  python capture_face_images.py 23NS064 15")
        print("  python capture_face_images.py 23NS091 20")
        print("\nXem danh sách sinh viên:")
        print("  python capture_face_images.py --list")
        
        list_students()
