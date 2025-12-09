# fix_moderator_account.py - Sửa/tạo lại tài khoản moderator
"""
Script kiểm tra và tạo lại tài khoản moderator nếu cần
"""

from models.database import Database
from config import Config

def fix_moderator_account():
    """Kiểm tra và sửa tài khoản moderator"""
    print("=" * 60)
    print("🔧 KIỂM TRA VÀ SỬA TÀI KHOẢN MODERATOR")
    print("=" * 60)
    
    db = Database(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
    
    if not db.connect():
        print("❌ Không thể kết nối database")
        return False
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # 1. Kiểm tra tài khoản moderator
        print("\n1. Kiểm tra tài khoản moderator...")
        cursor.execute("SELECT * FROM users WHERE role = 'moderator'")
        moderators = cursor.fetchall()
        
        if moderators:
            print(f"   ✓ Tìm thấy {len(moderators)} tài khoản moderator:")
            for mod in moderators:
                print(f"     • Username: {mod['username']}")
                print(f"       Email: {mod['email']}")
                print(f"       Họ tên: {mod['full_name']}")
        else:
            print("   ⚠️  Không tìm thấy tài khoản moderator nào!")
        
        # 2. Kiểm tra tài khoản admin cụ thể
        print("\n2. Kiểm tra tài khoản 'admin'...")
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"   ✓ Tài khoản 'admin' tồn tại")
            print(f"     • Role: {admin['role']}")
            print(f"     • Email: {admin['email']}")
            print(f"     • Họ tên: {admin['full_name']}")
            
            # Kiểm tra role
            if admin['role'] != 'moderator':
                print(f"\n   ⚠️  Role không đúng: {admin['role']} (phải là 'moderator')")
                print("   🔧 Đang sửa role...")
                cursor.execute("UPDATE users SET role = 'moderator' WHERE username = 'admin'")
                db.connection.commit()
                print("   ✓ Đã sửa role thành 'moderator'")
            
            # Test đăng nhập
            print("\n3. Test đăng nhập...")
            test_user = db.login('admin', 'admin123')
            if test_user:
                print("   ✓ Đăng nhập thành công với admin/admin123")
            else:
                print("   ❌ Không thể đăng nhập với admin/admin123")
                print("   🔧 Đang reset mật khẩu...")
                
                # Reset password
                password_hash = db.hash_password('admin123')
                cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (password_hash,))
                db.connection.commit()
                print("   ✓ Đã reset mật khẩu thành 'admin123'")
                
                # Test lại
                test_user = db.login('admin', 'admin123')
                if test_user:
                    print("   ✓ Đăng nhập thành công sau khi reset")
                else:
                    print("   ❌ Vẫn không thể đăng nhập")
        else:
            print("   ❌ Tài khoản 'admin' không tồn tại")
            print("\n   🔧 Đang tạo tài khoản mới...")
            
            # Tạo tài khoản admin mới
            moderator_id = db.create_user(
                username='admin',
                email='admin@university.edu.vn',
                password='admin123',
                role='moderator',
                full_name='Quản trị viên',
                gender='male',
                date_of_birth='1980-01-01'
            )
            
            if moderator_id:
                print(f"   ✓ Đã tạo tài khoản moderator (ID: {moderator_id})")
                print("   ✓ Username: admin")
                print("   ✓ Password: admin123")
                
                # Test đăng nhập
                test_user = db.login('admin', 'admin123')
                if test_user:
                    print("   ✓ Đăng nhập thành công")
                else:
                    print("   ❌ Không thể đăng nhập")
            else:
                print("   ❌ Không thể tạo tài khoản")
        
        cursor.close()
        
        print("\n" + "=" * 60)
        print("✅ HOÀN TẤT!")
        print("=" * 60)
        print("\n📌 Thông tin đăng nhập:")
        print("   • Username: admin")
        print("   • Password: admin123")
        print("   • Role: moderator")
        print("\n💡 Bây giờ có thể đăng nhập vào ứng dụng")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    fix_moderator_account()
