# utils/image_handler.py - Xử lý ảnh: encode/decode, lưu vào DB
import base64
import cv2
import numpy as np
from typing import Optional, Tuple
from io import BytesIO
from PIL import Image

class ImageHandler:
    """Xử lý ảnh: chuyển đổi giữa file, numpy array, base64 string"""
    
    @staticmethod
    def image_to_base64(image_path: str) -> Optional[str]:
        """
        Chuyển ảnh từ file thành base64 string để lưu vào database
        
        Args:
            image_path: Đường dẫn file ảnh
            
        Returns:
            Base64 string hoặc None nếu lỗi
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                return base64_string
        except Exception as e:
            print(f"✗ Lỗi chuyển ảnh sang base64: {e}")
            return None
    
    @staticmethod
    def base64_to_image(base64_string: str, output_path: str = None) -> Optional[np.ndarray]:
        """
        Chuyển base64 string thành ảnh (numpy array hoặc file)
        
        Args:
            base64_string: Base64 string từ database
            output_path: Đường dẫn lưu file (optional)
            
        Returns:
            Numpy array (OpenCV format) hoặc None nếu lỗi
        """
        try:
            # Decode base64 thành bytes
            image_data = base64.b64decode(base64_string)
            
            # Chuyển bytes thành numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Lưu file nếu cần
            if output_path:
                cv2.imwrite(output_path, image)
            
            return image
        except Exception as e:
            print(f"✗ Lỗi chuyển base64 sang ảnh: {e}")
            return None
    
    @staticmethod
    def numpy_to_base64(image_array: np.ndarray, format: str = '.jpg') -> Optional[str]:
        """
        Chuyển numpy array (OpenCV) thành base64 string
        
        Args:
            image_array: Numpy array từ OpenCV
            format: Format ảnh (.jpg, .png)
            
        Returns:
            Base64 string hoặc None nếu lỗi
        """
        try:
            # Encode numpy array thành bytes
            success, buffer = cv2.imencode(format, image_array)
            if not success:
                return None
            
            # Chuyển bytes thành base64
            base64_string = base64.b64encode(buffer).decode('utf-8')
            return base64_string
        except Exception as e:
            print(f"✗ Lỗi chuyển numpy sang base64: {e}")
            return None
    
    @staticmethod
    def compress_image(image_array: np.ndarray, max_width: int = 800, 
                      quality: int = 85) -> np.ndarray:
        """
        Nén ảnh để giảm kích thước trước khi lưu vào database
        
        Args:
            image_array: Numpy array từ OpenCV
            max_width: Chiều rộng tối đa
            quality: Chất lượng JPEG (0-100)
            
        Returns:
            Numpy array đã nén
        """
        try:
            height, width = image_array.shape[:2]
            
            # Resize nếu ảnh quá lớn
            if width > max_width:
                ratio = max_width / width
                new_width = max_width
                new_height = int(height * ratio)
                image_array = cv2.resize(image_array, (new_width, new_height))
            
            # Nén JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', image_array, encode_param)
            image_array = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            
            return image_array
        except Exception as e:
            print(f"✗ Lỗi nén ảnh: {e}")
            return image_array
    
    @staticmethod
    def validate_image(image_path: str) -> Tuple[bool, str]:
        """
        Kiểm tra ảnh có hợp lệ không
        
        Args:
            image_path: Đường dẫn file ảnh
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Kiểm tra file tồn tại
            import os
            if not os.path.exists(image_path):
                return False, "File không tồn tại"
            
            # Kiểm tra kích thước file (max 5MB)
            file_size = os.path.getsize(image_path)
            if file_size > 5 * 1024 * 1024:
                return False, "File quá lớn (tối đa 5MB)"
            
            # Kiểm tra format
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            _, ext = os.path.splitext(image_path.lower())
            if ext not in valid_extensions:
                return False, f"Format không hỗ trợ (chỉ {', '.join(valid_extensions)})"
            
            # Thử đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                return False, "Không thể đọc ảnh"
            
            # Kiểm tra kích thước ảnh
            height, width = image.shape[:2]
            if width < 100 or height < 100:
                return False, "Ảnh quá nhỏ (tối thiểu 100x100)"
            
            if width > 4000 or height > 4000:
                return False, "Ảnh quá lớn (tối đa 4000x4000)"
            
            return True, ""
        except Exception as e:
            return False, f"Lỗi kiểm tra ảnh: {str(e)}"
    
    @staticmethod
    def get_image_info(base64_string: str) -> dict:
        """
        Lấy thông tin ảnh từ base64 string
        
        Args:
            base64_string: Base64 string
            
        Returns:
            Dict chứa thông tin ảnh
        """
        try:
            image = ImageHandler.base64_to_image(base64_string)
            if image is None:
                return {}
            
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1
            
            # Tính kích thước base64
            size_bytes = len(base64_string.encode('utf-8'))
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            
            return {
                'width': width,
                'height': height,
                'channels': channels,
                'size_bytes': size_bytes,
                'size_kb': round(size_kb, 2),
                'size_mb': round(size_mb, 2)
            }
        except Exception as e:
            print(f"✗ Lỗi lấy thông tin ảnh: {e}")
            return {}


class FaceImageDB:
    """Quản lý ảnh khuôn mặt trong database"""
    
    def __init__(self, db):
        self.db = db
    
    def save_face_image(self, student_id: int, image_path: str, 
                       compress: bool = True) -> Tuple[bool, str]:
        """
        Lưu ảnh khuôn mặt vào database
        
        Args:
            student_id: ID sinh viên
            image_path: Đường dẫn file ảnh
            compress: Có nén ảnh không
            
        Returns:
            (success, message)
        """
        try:
            # Validate ảnh
            is_valid, msg = ImageHandler.validate_image(image_path)
            if not is_valid:
                return False, msg
            
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                return False, "Không thể đọc ảnh"
            
            # Nén ảnh nếu cần
            if compress:
                image = ImageHandler.compress_image(image, max_width=800, quality=85)
            
            # Chuyển thành base64
            base64_string = ImageHandler.numpy_to_base64(image)
            if not base64_string:
                return False, "Không thể chuyển ảnh sang base64"
            
            # Lưu vào database
            cursor = self.db.connection.cursor()
            try:
                # Kiểm tra xem đã có ảnh chưa
                cursor.execute("""
                    SELECT face_image FROM students WHERE student_id = %s
                """, (student_id,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    # Cập nhật ảnh cũ
                    cursor.execute("""
                        UPDATE students 
                        SET face_image = %s, face_encoding_path = 'database'
                        WHERE student_id = %s
                    """, (base64_string, student_id))
                else:
                    # Thêm ảnh mới
                    cursor.execute("""
                        UPDATE students 
                        SET face_image = %s, face_encoding_path = 'database'
                        WHERE student_id = %s
                    """, (base64_string, student_id))
                
                self.db.connection.commit()
                
                # Lấy thông tin ảnh
                info = ImageHandler.get_image_info(base64_string)
                return True, f"Đã lưu ảnh ({info.get('size_kb', 0)} KB)"
            finally:
                cursor.close()
                
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Lỗi lưu ảnh: {str(e)}"
    
    def get_face_image(self, student_id: int, as_array: bool = True):
        """
        Lấy ảnh khuôn mặt từ database
        
        Args:
            student_id: ID sinh viên
            as_array: True = numpy array, False = base64 string
            
        Returns:
            Numpy array hoặc base64 string hoặc None
        """
        try:
            cursor = self.db.connection.cursor()
            try:
                cursor.execute("""
                    SELECT face_image FROM students WHERE student_id = %s
                """, (student_id,))
                result = cursor.fetchone()
                
                if not result or not result[0]:
                    return None
                
                base64_string = result[0]
                
                if as_array:
                    return ImageHandler.base64_to_image(base64_string)
                else:
                    return base64_string
            finally:
                cursor.close()
        except Exception as e:
            print(f"✗ Lỗi lấy ảnh: {e}")
            return None
    
    def delete_face_image(self, student_id: int) -> Tuple[bool, str]:
        """
        Xóa ảnh khuôn mặt khỏi database
        
        Args:
            student_id: ID sinh viên
            
        Returns:
            (success, message)
        """
        try:
            cursor = self.db.connection.cursor()
            try:
                cursor.execute("""
                    UPDATE students 
                    SET face_image = NULL, face_encoding_path = NULL
                    WHERE student_id = %s
                """, (student_id,))
                self.db.connection.commit()
                return True, "Đã xóa ảnh"
            finally:
                cursor.close()
        except Exception as e:
            self.db.connection.rollback()
            return False, f"Lỗi xóa ảnh: {str(e)}"
    
    def get_all_face_images(self) -> list:
        """
        Lấy tất cả ảnh khuôn mặt từ database
        
        Returns:
            List of (student_id, student_code, image_array)
        """
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT student_id, student_code, face_image 
                    FROM students 
                    WHERE face_image IS NOT NULL
                """)
                results = cursor.fetchall()
                
                face_images = []
                for row in results:
                    image = ImageHandler.base64_to_image(row['face_image'])
                    if image is not None:
                        face_images.append((
                            row['student_id'],
                            row['student_code'],
                            image
                        ))
                
                return face_images
            finally:
                cursor.close()
        except Exception as e:
            print(f"✗ Lỗi lấy tất cả ảnh: {e}")
            return []
