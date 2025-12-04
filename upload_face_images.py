# upload_face_images.py - Upload ảnh khuôn mặt cho sinh viên
import os
import shutil
from database import Database
from config import Config

def upload_faces_from_existing_folders():
    """
    Tự động cập nhật face_encoding_path cho sinh viên 
    dựa trên các folder đã có trong uploads/face_images
    """
    print("=== UPLOAD ẢNH KHUÔN MẶT ===\n")
    
    # Kết nối database
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("❌ Không thể kết nối database!")
        return
    
    print("✓ Đã kết nối database\n")
    
    # Lấy danh sách sinh viên
    students = db.get_all_students()
    print(f"📊 Tổng số sinh viên: {len(students)}\n")
    
    # Kiểm tra folder face_images
    face_images_dir = Config.FACE_IMAGES_FOLDER
    if not os.path.exists(face_images_dir):
        print(f"❌ Không tìm thấy folder: {face_images_dir}")
        db.disconnect()
        return
    
    # Lấy danh sách folder trong face_images
    existing_folders = [f for f in os.listdir(face_images_dir) 
                       if os.path.isdir(os.path.join(face_images_dir, f))]
    
    print(f"📁 Tìm thấy {len(existing_folders)} folder ảnh:\n")
    
    updated_count = 0
    cursor = db.connection.cursor()
    
    for student in students:
        student_code = student['student_code']
        student_id = student['student_id']
        
        # Kiểm tra xem có folder tương ứng không
        if student_code in existing_folders:
            folder_path = os.path.join(face_images_dir, student_code)
            
            # Đếm số ảnh trong folder
            image_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if len(image_files) > 0:
                # Cập nhật database
                cursor.execute("""
                    UPDATE students 
                    SET face_encoding_path = %s 
                    WHERE student_id = %s
                """, (folder_path, student_id))
                
                print(f"✓ {student_code} - {student['full_name']}")
                print(f"  Folder: {folder_path}")
                print(f"  Số ảnh: {len(image_files)}\n")
                
                updated_count += 1
            else:
                print(f"⚠ {student_code} - Folder rỗng, bỏ qua\n")
    
    db.connection.commit()
    cursor.close()
    
    print(f"\n✅ Đã cập nhật {updated_count} sinh viên")
    
    db.disconnect()
    print("\n=== HOÀN TẤT ===")

def create_sample_structure():
    """
    Tạo cấu trúc folder mẫu cho sinh viên
    """
    print("\n=== TẠO CẤU TRÚC FOLDER MẪU ===\n")
    
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("❌ Không thể kết nối database!")
        return
    
    students = db.get_all_students()
    
    print(f"📊 Tạo folder cho {len(students)} sinh viên:\n")
    
    for student in students:
        student_code = student['student_code']
        folder_path = os.path.join(Config.FACE_IMAGES_FOLDER, student_code)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            print(f"✓ Đã tạo folder: {folder_path}")
        else:
            print(f"⚠ Folder đã tồn tại: {folder_path}")
    
    db.disconnect()
    
    print("\n✅ Hoàn tất tạo cấu trúc folder")
    print(f"\n📝 Hướng dẫn:")
    print(f"1. Vào folder: {Config.FACE_IMAGES_FOLDER}")
    print(f"2. Mỗi sinh viên có 1 folder riêng (tên = mã sinh viên)")
    print(f"3. Copy ảnh khuôn mặt vào folder tương ứng (ít nhất 5 ảnh)")
    print(f"4. Chạy lại script này để cập nhật database")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        create_sample_structure()
    else:
        upload_faces_from_existing_folders()
        
    print("\n💡 Tip: Chạy 'python upload_face_images.py --create' để tạo folder mẫu")
