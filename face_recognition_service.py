# face_recognition_service.py - Face Recognition cho Desktop App
import cv2
import numpy as np
import pickle
import os
from config import Config

class FaceRecognitionService:
    def __init__(self):
        self.model_path = Config.FACE_MODEL_PATH
        self.labels_path = Config.LABELS_PATH
        self.recognizer = None
        self.labels = {}
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
        # Load model nếu đã tồn tại
        if os.path.exists(self.model_path) and os.path.exists(self.labels_path):
            self.load_model()
    
    def train_model(self, db):
        """
        Train model từ ảnh trong database
        
        Args:
            db: Database instance
        
        Returns:
            dict: Kết quả training
        """
        faces = []
        labels_list = []
        label_ids = {}
        current_id = 0
        
        # Lấy danh sách sinh viên có ảnh
        students = db.get_all_students()
        
        trained_count = 0
        
        for student in students:
            student_code = student['student_code']
            face_folder = student['face_encoding_path']
            
            if not face_folder or not os.path.exists(face_folder):
                continue
            
            # Gán ID cho sinh viên
            if student_code not in label_ids:
                label_ids[student_code] = current_id
                current_id += 1
            
            label_id = label_ids[student_code]
            
            # Đọc tất cả ảnh
            image_count = 0
            for image_name in os.listdir(face_folder):
                image_path = os.path.join(face_folder, image_name)
                
                try:
                    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        continue
                    
                    # Detect face trong ảnh
                    detected_faces = self.face_cascade.detectMultiScale(
                        img, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
                    )
                    
                    if len(detected_faces) == 0:
                        # Nếu không detect được, dùng toàn bộ ảnh
                        img_resized = cv2.resize(img, (200, 200))
                        faces.append(img_resized)
                        labels_list.append(label_id)
                        image_count += 1
                    else:
                        # Crop face đầu tiên
                        x, y, w, h = detected_faces[0]
                        face_roi = img[y:y+h, x:x+w]
                        face_resized = cv2.resize(face_roi, (200, 200))
                        faces.append(face_resized)
                        labels_list.append(label_id)
                        image_count += 1
                        
                except Exception as e:
                    print(f"Lỗi đọc ảnh {image_path}: {e}")
                    continue
            
            if image_count > 0:
                trained_count += 1
        
        if len(faces) == 0:
            return {
                'success': False,
                'error': 'Không tìm thấy ảnh khuôn mặt nào'
            }
        
        # Train model LBPH
        faces_array = np.array(faces)
        labels_array = np.array(labels_list)
        
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.train(faces_array, labels_array)
        
        # Lưu model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.recognizer.save(self.model_path)
        
        # Lưu labels
        with open(self.labels_path, 'wb') as f:
            pickle.dump(label_ids, f)
        
        self.labels = {v: k for k, v in label_ids.items()}
        
        return {
            'success': True,
            'total_students': trained_count,
            'total_images': len(faces),
            'students': list(label_ids.keys())
        }
    
    def load_model(self):
        """Load model đã train"""
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read(self.model_path)
            
            with open(self.labels_path, 'rb') as f:
                label_ids = pickle.load(f)
                self.labels = {v: k for k, v in label_ids.items()}
            
            return True
        except Exception as e:
            print(f"Lỗi load model: {e}")
            return False
    
    def recognize_faces(self, frame):
        """
        Nhận diện khuôn mặt trong frame
        
        Args:
            frame: OpenCV BGR image
        
        Returns:
            list: [{student_code, confidence, bbox, label_text}]
        """
        if self.recognizer is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.2, 
            minNeighbors=5,
            minSize=(50, 50)
        )
        
        results = []
        
        for (x, y, w, h) in faces:
            roi_gray = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            
            try:
                label_id, confidence = self.recognizer.predict(roi_gray)
                student_code = self.labels.get(label_id, 'Unknown')
                
                # Chuyển confidence (càng thấp càng tốt) sang % tin cậy
                confidence_percent = max(0, 100 - confidence)
                
                label_text = f"{student_code} ({confidence_percent:.1f}%)"
                
                results.append({
                    'student_code': student_code,
                    'confidence': confidence_percent,
                    'bbox': (x, y, w, h),
                    'label_text': label_text,
                    'raw_confidence': confidence
                })
            except Exception as e:
                print(f"Lỗi nhận diện: {e}")
                continue
        
        return results
    
    def mark_attendance_from_camera(self, db, session_id, frame, confidence_threshold=None):
        """
        Điểm danh tự động từ camera
        
        Args:
            db: Database instance
            session_id: ID buổi học
            frame: Camera frame
            confidence_threshold: Ngưỡng tin cậy (mặc định từ config)
        
        Returns:
            dict: Kết quả điểm danh
        """
        if confidence_threshold is None:
            confidence_threshold = Config.CONFIDENCE_THRESHOLD
        
        # Nhận diện khuôn mặt
        recognized = self.recognize_faces(frame)
        
        results = {
            'total_detected': len(recognized),
            'marked': [],
            'rejected': [],
            'already_marked': []
        }
        
        for face in recognized:
            student_code = face['student_code']
            confidence = face['confidence']
            
            # Kiểm tra confidence
            if confidence < confidence_threshold:
                results['rejected'].append({
                    'student_code': student_code,
                    'confidence': confidence,
                    'reason': 'Độ tin cậy thấp'
                })
                continue
            
            # Lấy student_id từ student_code
            student = db.get_student_by_code(student_code)
            if not student:
                results['rejected'].append({
                    'student_code': student_code,
                    'confidence': confidence,
                    'reason': 'Không tìm thấy sinh viên'
                })
                continue
            
            student_id = student['student_id']
            
            # Kiểm tra đã điểm danh chưa
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE session_id = %s AND student_id = %s
            """, (session_id, student_id))
            existing = cursor.fetchone()
            cursor.close()
            
            if existing:
                results['already_marked'].append({
                    'student_code': student_code,
                    'student_name': student['full_name'],
                    'confidence': confidence,
                    'time': existing['check_in_time']
                })
                continue
            
            # Điểm danh
            success = db.mark_attendance(
                session_id=session_id,
                student_id=student_id,
                status='present',
                confidence_score=confidence
            )
            
            if success:
                results['marked'].append({
                    'student_code': student_code,
                    'student_name': student['full_name'],
                    'confidence': confidence
                })
        
        return results
    
    def draw_faces(self, frame, recognized_faces, confidence_threshold=None):
        """
        Vẽ khung và thông tin lên frame
        
        Args:
            frame: OpenCV BGR image
            recognized_faces: Kết quả từ recognize_faces()
            confidence_threshold: Ngưỡng tin cậy
        
        Returns:
            frame: Frame đã vẽ
        """
        if confidence_threshold is None:
            confidence_threshold = Config.CONFIDENCE_THRESHOLD
        
        for face in recognized_faces:
            x, y, w, h = face['bbox']
            confidence = face['confidence']
            label_text = face['label_text']
            
            # Màu sắc dựa trên confidence
            if confidence >= confidence_threshold:
                color = (0, 255, 0)  # Xanh lá
                status = "✓"
            else:
                color = (0, 0, 255)  # Đỏ
                status = "✗"
            
            # Vẽ khung
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Vẽ background cho text
            text_bg_height = 30
            cv2.rectangle(frame, (x, y-text_bg_height), (x+w, y), color, -1)
            
            # Vẽ text
            cv2.putText(
                frame, 
                f"{status} {label_text}", 
                (x+5, y-8), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (255, 255, 255), 
                1
            )
        
        return frame

# Global instance
face_service = FaceRecognitionService()