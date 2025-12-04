# create_sample_data.py - Tạo dữ liệu mẫu cho hệ thống
from database import Database
from datetime import datetime, timedelta, date
import random

def create_sample_data():
    """Tạo dữ liệu mẫu đầy đủ"""
    print("=== TẠO DỮ LIỆU MẪU ===\n")
    
    # Kết nối database
    db = Database(host='localhost', user='root', password='', database='attendance_db', port=3306)
    
    if not db.connect():
        print("❌ Không thể kết nối database!")
        return
    
    print("✓ Đã kết nối database\n")
    
    # 1. Tạo Moderator
    print("1️⃣ Tạo Moderator...")
    moderator_id = db.create_user(
        username='admin',
        email='admin@university.edu.vn',
        password='admin123',
        role='moderator',
        full_name='Nguyễn Văn Admin',
        gender='male',
        date_of_birth='1980-01-15'
    )
    if moderator_id:
        print(f"   ✓ Moderator: admin / admin123")
    
    # 2. Tạo Giáo viên
    print("\n2️⃣ Tạo Giáo viên...")
    teachers_data = [
        {
            'teacher_code': 'GV001',
            'full_name': 'TS. Nguyễn Thị Lan',
            'email': 'nguyenlan@university.edu.vn',
            'gender': 'female',
            'date_of_birth': '1985-03-20',
            'department': 'Khoa Công nghệ Thông tin'
        },
        {
            'teacher_code': 'GV002',
            'full_name': 'PGS.TS. Trần Văn Minh',
            'email': 'tranminh@university.edu.vn',
            'gender': 'male',
            'date_of_birth': '1978-07-15',
            'department': 'Khoa Công nghệ Thông tin'
        },
        {
            'teacher_code': 'GV003',
            'full_name': 'ThS. Lê Thị Hương',
            'email': 'lehuong@university.edu.vn',
            'gender': 'female',
            'date_of_birth': '1990-11-08',
            'department': 'Khoa Toán - Tin'
        },
        {
            'teacher_code': 'GV004',
            'full_name': 'TS. Phạm Đức Anh',
            'email': 'phamanh@university.edu.vn',
            'gender': 'male',
            'date_of_birth': '1982-05-25',
            'department': 'Khoa Công nghệ Thông tin'
        },
        {
            'teacher_code': 'GV005',
            'full_name': 'ThS. Hoàng Thị Mai',
            'email': 'hoangmai@university.edu.vn',
            'gender': 'female',
            'date_of_birth': '1988-09-12',
            'department': 'Khoa Ngoại ngữ'
        }
    ]
    
    teacher_ids = {}
    for teacher in teachers_data:
        user_id = db.create_user(
            username=teacher['teacher_code'].lower(),
            email=teacher['email'],
            password=teacher['teacher_code'],
            role='teacher',
            full_name=teacher['full_name'],
            gender=teacher['gender'],
            date_of_birth=teacher['date_of_birth']
        )
        if user_id:
            teacher_id = db.create_teacher(
                user_id=user_id,
                teacher_code=teacher['teacher_code'],
                department=teacher['department']
            )
            teacher_ids[teacher['teacher_code']] = user_id
            print(f"   ✓ {teacher['teacher_code']}: {teacher['full_name']} / {teacher['teacher_code']}")
    
    # 3. Tạo Sinh viên
    print("\n3️⃣ Tạo Sinh viên...")
    students_data = [
        {'student_code': '21IT001', 'full_name': 'Nguyễn Văn An', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2021},
        {'student_code': '21IT002', 'full_name': 'Trần Thị Bình', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2021},
        {'student_code': '21IT003', 'full_name': 'Lê Văn Cường', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2021},
        {'student_code': '21IT004', 'full_name': 'Phạm Thị Dung', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2021},
        {'student_code': '21IT005', 'full_name': 'Hoàng Văn Em', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2021},
        {'student_code': '22IT001', 'full_name': 'Vũ Thị Phương', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2022},
        {'student_code': '22IT002', 'full_name': 'Đỗ Văn Giang', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2022},
        {'student_code': '22IT003', 'full_name': 'Bùi Thị Hà', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2022},
        {'student_code': '22IT004', 'full_name': 'Ngô Văn Hùng', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2022},
        {'student_code': '22IT005', 'full_name': 'Đinh Thị Lan', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2022},
        {'student_code': '23IT001', 'full_name': 'Trương Văn Khoa', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2023},
        {'student_code': '23IT002', 'full_name': 'Lý Thị Linh', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2023},
        {'student_code': '23IT003', 'full_name': 'Phan Văn Minh', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2023},
        {'student_code': '23IT004', 'full_name': 'Mai Thị Nga', 'gender': 'female', 'major': 'Công nghệ Thông tin', 'year': 2023},
        {'student_code': '23IT005', 'full_name': 'Võ Văn Oanh', 'gender': 'male', 'major': 'Công nghệ Thông tin', 'year': 2023},
        {'student_code': '23AI001', 'full_name': 'Đặng Thị Phương', 'gender': 'female', 'major': 'Trí tuệ Nhân tạo', 'year': 2023},
        {'student_code': '23AI002', 'full_name': 'Hồ Văn Quang', 'gender': 'male', 'major': 'Trí tuệ Nhân tạo', 'year': 2023},
        {'student_code': '23AI003', 'full_name': 'Tô Thị Rạng', 'gender': 'female', 'major': 'Trí tuệ Nhân tạo', 'year': 2023},
        {'student_code': '23AI004', 'full_name': 'Lưu Văn Sơn', 'gender': 'male', 'major': 'Trí tuệ Nhân tạo', 'year': 2023},
        {'student_code': '23AI005', 'full_name': 'Dương Thị Tâm', 'gender': 'female', 'major': 'Trí tuệ Nhân tạo', 'year': 2023},
    ]
    
    student_ids = {}
    for student in students_data:
        user_id = db.create_user(
            username=student['student_code'].lower(),
            email=f"{student['student_code'].lower()}@student.edu.vn",
            password=student['student_code'],
            role='student',
            full_name=student['full_name'],
            gender=student['gender'],
            date_of_birth=f"{student['year']-18}-01-01"
        )
        if user_id:
            student_id = db.create_student(
                user_id=user_id,
                student_code=student['student_code'],
                major=student['major'],
                enrollment_year=student['year']
            )
            student_ids[student['student_code']] = student_id
            print(f"   ✓ {student['student_code']}: {student['full_name']} / {student['student_code']}")
    
    # 4. Tạo Lớp học
    print("\n4️⃣ Tạo Lớp học...")
    classes_data = [
        {
            'class_code': 'IT301',
            'class_name': 'Cấu trúc dữ liệu và Giải thuật',
            'teacher': 'GV001',
            'total_sessions': 3,
            'credits': 2,
            'max_students': 40,
            'semester': 1,
            'academic_year': '2024-2025',
            'schedule': [
                {'day': 'Thứ 2', 'from': 1, 'to': 3, 'session': 'morning'},
                {'day': 'Thứ 5', 'from': 1, 'to': 3, 'session': 'morning'}
            ]
        },
        {
            'class_code': 'IT302',
            'class_name': 'Lập trình Hướng đối tượng',
            'teacher': 'GV002',
            'total_sessions': 4,
            'credits': 3,
            'max_students': 35,
            'semester': 1,
            'academic_year': '2024-2025',
            'schedule': [
                {'day': 'Thứ 3', 'from': 6, 'to': 9, 'session': 'afternoon'}
            ]
        },
        {
            'class_code': 'IT303',
            'class_name': 'Cơ sở dữ liệu',
            'teacher': 'GV001',
            'total_sessions': 3,
            'credits': 2,
            'max_students': 40,
            'semester': 1,
            'academic_year': '2024-2025',
            'schedule': [
                {'day': 'Thứ 4', 'from': 1, 'to': 3, 'session': 'morning'}
            ]
        },
        {
            'class_code': 'IT304',
            'class_name': 'Mạng máy tính',
            'teacher': 'GV004',
            'total_sessions': 2,
            'credits': 1,
            'max_students': 30,
            'semester': 1,
            'academic_year': '2024-2025',
            'schedule': [
                {'day': 'Thứ 6', 'from': 6, 'to': 7, 'session': 'afternoon'}
            ]
        },
        {
            'class_code': 'AI301',
            'class_name': 'Học máy cơ bản',
            'teacher': 'GV003',
            'total_sessions': 4,
            'credits': 3,
            'max_students': 25,
            'semester': 1,
            'academic_year': '2024-2025',
            'schedule': [
                {'day': 'Thứ 2', 'from': 6, 'to': 9, 'session': 'afternoon'}
            ]
        },
        {
            'class_code': 'EN301',
            'class_name': 'Tiếng Anh chuyên ngành',
            'teacher': 'GV005',
            'total_sessions': 2,
            'credits': 1,
            'max_students': 45,
            'semester': 1,
            'academic_year': '2024-2025',
            'schedule': [
                {'day': 'Thứ 7', 'from': 1, 'to': 2, 'session': 'morning'}
            ]
        }
    ]
    
    class_ids = {}
    for cls in classes_data:
        class_id = db.create_class(
            class_code=cls['class_code'],
            class_name=cls['class_name'],
            teacher_id=teacher_ids[cls['teacher']],
            total_sessions=cls['total_sessions'],
            credits=cls['credits'],
            max_students=cls['max_students'],
            semester=cls['semester'],
            academic_year=cls['academic_year'],
            schedule=cls['schedule']
        )
        if class_id:
            # Duyệt lớp
            db.approve_class(class_id)
            class_ids[cls['class_code']] = class_id
            print(f"   ✓ {cls['class_code']}: {cls['class_name']} (GV: {cls['teacher']})")
    
    # 5. Thiết lập khung giờ đăng ký
    print("\n5️⃣ Thiết lập khung giờ đăng ký...")
    start_time = datetime.now() - timedelta(days=7)
    end_time = datetime.now() + timedelta(days=30)
    db.save_registration_period(start_time, end_time, 1, '2024-2025')
    print(f"   ✓ Khung giờ: {start_time.strftime('%d/%m/%Y %H:%M')} - {end_time.strftime('%d/%m/%Y %H:%M')}")
    
    # 6. Đăng ký lớp cho sinh viên
    print("\n6️⃣ Đăng ký lớp cho sinh viên...")
    enrollments = [
        # IT301 - Cấu trúc dữ liệu
        ('IT301', ['21IT001', '21IT002', '21IT003', '22IT001', '22IT002', '23IT001', '23IT002', '23IT003']),
        # IT302 - Lập trình OOP
        ('IT302', ['21IT001', '21IT004', '22IT001', '22IT003', '23IT001', '23IT004']),
        # IT303 - Cơ sở dữ liệu
        ('IT303', ['21IT002', '21IT003', '21IT005', '22IT002', '22IT004', '23IT002', '23IT005']),
        # IT304 - Mạng máy tính
        ('IT304', ['21IT001', '21IT002', '22IT001', '22IT002', '23IT001']),
        # AI301 - Học máy
        ('AI301', ['23AI001', '23AI002', '23AI003', '23AI004', '23AI005', '23IT003']),
        # EN301 - Tiếng Anh
        ('EN301', ['21IT001', '21IT002', '22IT001', '23IT001', '23AI001', '23AI002'])
    ]
    
    enrollment_count = 0
    for class_code, students in enrollments:
        class_id = class_ids[class_code]
        for student_code in students:
            if student_code in student_ids:
                success, msg = db.enroll_student(class_id, student_ids[student_code])
                if success:
                    enrollment_count += 1
    
    print(f"   ✓ Đã đăng ký {enrollment_count} lượt")
    
    # 7. Tạo buổi học và điểm danh mẫu
    print("\n7️⃣ Tạo buổi học và điểm danh mẫu...")
    
    cursor = db.connection.cursor(dictionary=True)
    
    # Tạo 3 buổi học cho mỗi lớp
    session_count = 0
    attendance_count = 0
    
    for class_code, class_id in class_ids.items():
        # Lấy danh sách sinh viên đã đăng ký
        cursor.execute("""
            SELECT student_id FROM class_enrollments 
            WHERE class_id = %s AND status = 'enrolled'
        """, (class_id,))
        enrolled = [row['student_id'] for row in cursor.fetchall()]
        
        if not enrolled:
            continue
        
        # Tạo 3 buổi học trong quá khứ
        for i in range(1, 4):
            session_date = date.today() - timedelta(days=(4-i)*7)  # 3 tuần trước, 2 tuần trước, 1 tuần trước
            session_time = 'morning' if i % 2 == 1 else 'afternoon'
            
            cursor.execute("""
                INSERT INTO sessions (class_id, session_date, session_time, session_number)
                VALUES (%s, %s, %s, %s)
            """, (class_id, session_date, session_time, i))
            session_id = cursor.lastrowid
            session_count += 1
            
            # Điểm danh ngẫu nhiên (80-95% sinh viên có mặt)
            present_rate = random.uniform(0.8, 0.95)
            num_present = int(len(enrolled) * present_rate)
            
            # Chọn ngẫu nhiên sinh viên có mặt
            present_students = random.sample(enrolled, num_present)
            
            for student_id in enrolled:
                if student_id in present_students:
                    # Có mặt với confidence ngẫu nhiên
                    confidence = random.uniform(60, 95)
                    check_in_time = datetime.combine(session_date, datetime.min.time()) + timedelta(hours=7, minutes=random.randint(0, 15))
                    cursor.execute("""
                        INSERT INTO attendance (session_id, student_id, check_in_time, status, confidence_score)
                        VALUES (%s, %s, %s, 'present', %s)
                    """, (session_id, student_id, check_in_time, confidence))
                else:
                    # Vắng
                    cursor.execute("""
                        INSERT INTO attendance (session_id, student_id, status)
                        VALUES (%s, %s, 'absent')
                    """, (session_id, student_id))
                
                attendance_count += 1
    
    db.connection.commit()
    cursor.close()
    
    print(f"   ✓ Đã tạo {session_count} buổi học")
    print(f"   ✓ Đã tạo {attendance_count} bản ghi điểm danh")
    
    db.disconnect()
    
    # Tổng kết
    print("\n" + "="*60)
    print("✅ HOÀN TẤT TẠO DỮ LIỆU MẪU")
    print("="*60)
    print(f"\n📊 Thống kê:")
    print(f"   • Moderator: 1 (admin/admin123)")
    print(f"   • Giáo viên: {len(teachers_data)}")
    print(f"   • Sinh viên: {len(students_data)}")
    print(f"   • Lớp học: {len(classes_data)}")
    print(f"   • Đăng ký: {enrollment_count} lượt")
    print(f"   • Buổi học: {session_count}")
    print(f"   • Điểm danh: {attendance_count} bản ghi")
    
    print(f"\n🔑 Tài khoản đăng nhập:")
    print(f"\n   Moderator:")
    print(f"   • Username: admin | Password: admin123")
    
    print(f"\n   Giáo viên (username = mã GV, password = mã GV):")
    for teacher in teachers_data[:3]:
        print(f"   • {teacher['teacher_code']}: {teacher['full_name']}")
    print(f"   • ... và {len(teachers_data)-3} giáo viên khác")
    
    print(f"\n   Sinh viên (username = mã SV, password = mã SV):")
    for student in students_data[:5]:
        print(f"   • {student['student_code']}: {student['full_name']}")
    print(f"   • ... và {len(students_data)-5} sinh viên khác")
    
    print(f"\n💡 Lưu ý:")
    print(f"   • Tất cả lớp đã được duyệt")
    print(f"   • Đã có 3 buổi học mẫu cho mỗi lớp")
    print(f"   • Điểm danh mẫu với tỷ lệ 80-95% có mặt")
    print(f"   • Khung giờ đăng ký đang mở")

if __name__ == "__main__":
    create_sample_data()
