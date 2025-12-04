# test_train_model.py - Test train model
from database import Database
from face_recognition_service import face_service

def test_train():
    """Test chức năng train model"""
    print("=== TEST TRAIN MODEL ===\n")
    
    # Kết nối database
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("❌ Không thể kết nối database!")
        return
    
    print("✓ Đã kết nối database\n")
    
    # Kiểm tra số lượng sinh viên có ảnh
    students = db.get_all_students()
    students_with_face = [s for s in students if s.get('face_encoding_path')]
    
    print(f"📊 Thống kê:")
    print(f"  - Tổng số sinh viên: {len(students)}")
    print(f"  - Sinh viên có ảnh: {len(students_with_face)}")
    
    if len(students_with_face) == 0:
        print("\n❌ Không có sinh viên nào có ảnh khuôn mặt!")
        print("   Vui lòng thêm sinh viên và upload ảnh trước khi train.")
        db.disconnect()
        return
    
    print("\n📋 Danh sách sinh viên có ảnh:")
    for s in students_with_face:
        print(f"  - {s['student_code']}: {s['full_name']}")
        print(f"    Đường dẫn: {s['face_encoding_path']}")
    
    # Train model
    print("\n🚀 Bắt đầu train model...")
    try:
        result = face_service.train_model(db)
        
        if result.get('success'):
            print("\n✅ TRAIN THÀNH CÔNG!")
            print(f"  - Số sinh viên: {result.get('total_students', 0)}")
            print(f"  - Tổng số ảnh: {result.get('total_images', 0)}")
            print(f"  - Danh sách: {', '.join(result.get('students', []))}")
        else:
            print(f"\n❌ TRAIN THẤT BẠI!")
            print(f"  - Lỗi: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"\n❌ LỖI EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    
    db.disconnect()
    print("\n=== KẾT THÚC TEST ===")

if __name__ == "__main__":
    test_train()
