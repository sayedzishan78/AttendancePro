"""
Webcam service for real-time face recognition and attendance monitoring.
"""
import cv2
import numpy as np
import time
import threading
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import json

from app.services.face_encoder import FaceEncoder
from app.core.config import settings


class AttendanceRecord:
    """Attendance record for a person."""
    
    def __init__(self, person_id: int, name: str, timestamp: datetime, confidence: float):
        self.person_id = person_id
        self.name = name
        self.timestamp = timestamp
        self.confidence = confidence
        self.image_path = None  # Path to captured image


class WebcamService:
    """Service for real-time webcam face recognition and attendance tracking."""
    
    def __init__(self, encoder: FaceEncoder):
        self.encoder = encoder
        self.camera = None
        self.is_running = False
        self.attendance_records: List[AttendanceRecord] = []
        self.recognition_cooldown = {}  # Prevent duplicate records
        self.cooldown_seconds = 30  # 30 seconds between same person recognition
        self.output_dir = settings.output_path
        self.current_frame = None
        self.current_annotated_frame = None
        self.recognition_results = []
        self.frame_index = 0
        self.recognition_stride = max(1, settings.LIVE_RECOGNITION_STRIDE)
        
    def initialize_camera(self, camera_id: int = 0) -> bool:
        """Initialize webcam camera."""
        try:
            self.camera = cv2.VideoCapture(camera_id)
            if not self.camera.isOpened():
                print(f"❌ Could not open camera {camera_id}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"✅ Camera {camera_id} initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing camera: {e}")
            return False
    
    def release_camera(self):
        """Release camera resources."""
        if self.camera:
            self.camera.release()
            self.camera = None
            print("📷 Camera released")
    
    def get_known_faces(self, db) -> tuple:
        """Get all known faces from database."""
        from app.models.attendance import Person
        import pickle
        
        persons = db.query(Person).all()
        
        if not persons:
            return [], [], []
        
        known_embeddings = []
        known_names = []
        known_ids = []
        
        for p in persons:
            if not p.embedding:
                continue
            try:
                emb = pickle.loads(p.embedding)
                emb = self.encoder.l2_normalize(emb)
            except Exception:
                continue
            known_embeddings.append(emb)
            known_names.append(p.name)
            known_ids.append(p.id)
        
        known_embeddings = np.array(known_embeddings)
        return known_embeddings, known_names, known_ids
    
    def recognize_faces_in_frame(
        self,
        frame: np.ndarray,
        known_embeddings: np.ndarray,
        known_names: List[str],
        known_ids: List[int],
        db,
    ) -> List[Dict]:
        """Recognize faces in a single frame."""
        if not self.encoder.initialized or known_embeddings.size == 0:
            return []
        
        frame_for_recognition, scale = self._resize_for_recognition(frame)
        detected_faces = self.encoder.detect_and_encode_faces(frame_for_recognition)
        
        results = []
        current_time = datetime.now()
        
        for face_embedding, bbox in detected_faces:
            if scale != 1.0:
                x1, y1, x2, y2 = bbox
                bbox = (
                    int(x1 / scale),
                    int(y1 / scale),
                    int(x2 / scale),
                    int(y2 / scale),
                )
            # Calculate cosine similarity with all known faces
            cos_sim = np.dot(known_embeddings, face_embedding)
            idx = np.argmax(cos_sim)
            max_sim = cos_sim[idx]
            
            # Determine if face is recognized
            name = "Unknown"
            person_id = None
            
            if max_sim > settings.RECOGNITION_THRESHOLD:
                name = known_names[idx]
                person_id = known_ids[idx]
                
                # Check cooldown to prevent duplicate attendance records
                cooldown_key = f"{person_id}_{name}"
                last_recognition = self.recognition_cooldown.get(cooldown_key)
                
                if (last_recognition is None or 
                    current_time - last_recognition > timedelta(seconds=self.cooldown_seconds)):
                    
                    # Create attendance record (in-memory + DB)
                    record = AttendanceRecord(
                        person_id=person_id,
                        name=name,
                        timestamp=current_time,
                        confidence=float(max_sim)
                    )
                    self.attendance_records.append(record)
                    self.recognition_cooldown[cooldown_key] = current_time
                    self.record_attendance(db, record)
                    
                    print(f"✅ Attendance recorded: {name} (ID: {person_id}) at {current_time.strftime('%H:%M:%S')}")
            
            results.append({
                'name': name,
                'person_id': person_id,
                'confidence': float(max_sim),
                'bbox': bbox,
                'recognized': person_id is not None
            })
        
        return results

    def _resize_for_recognition(self, frame: np.ndarray) -> tuple:
        """Resize frame for faster recognition while preserving aspect ratio."""
        target_width = settings.LIVE_RECOGNITION_WIDTH
        if not target_width or frame.shape[1] <= target_width:
            return frame, 1.0
        scale = target_width / frame.shape[1]
        new_height = int(frame.shape[0] * scale)
        resized = cv2.resize(frame, (target_width, new_height))
        return resized, scale
    
    def draw_recognition_results(self, frame: np.ndarray, results: List[Dict]) -> np.ndarray:
        """Draw recognition results on frame."""
        annotated_frame = frame.copy()
        
        for result in results:
            x1, y1, x2, y2 = result['bbox']
            color = (0, 255, 0) if result['recognized'] else (0, 0, 255)
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Add label with name and confidence
            label = f"{result['name']} ({result['confidence']:.2f})"
            cv2.putText(
                annotated_frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )
        
        return annotated_frame
    
    def save_attendance_image(self, frame: np.ndarray, results: List[Dict]) -> Optional[str]:
        """Save frame with recognition annotations."""
        if not results:
            return None
        
        # Only save if at least one person is recognized
        recognized_faces = [r for r in results if r['recognized']]
        if not recognized_faces:
            return None
        
        # Draw results on frame
        annotated_frame = self.draw_recognition_results(frame, results)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = self.output_dir / filename
        
        # Save image
        cv2.imwrite(str(filepath), annotated_frame)
        
        # Update attendance records with image path
        for record in self.attendance_records:
            if not record.image_path:
                record.image_path = str(filepath)
        
        return str(filepath)

    def update_attendance_image(self, db, results: List[Dict], image_path: Optional[str]):
        """Attach saved image to latest attendance records."""
        if not image_path:
            return
        from app.models.attendance import Attendance
        
        attendance_date = datetime.now().date()
        updated = False
        for result in results:
            if not result.get("recognized"):
                continue
            record = (
                db.query(Attendance)
                .filter(
                    Attendance.person_id == result["person_id"],
                    Attendance.date == attendance_date,
                )
                .order_by(Attendance.check_in_time.desc())
                .first()
            )
            if record and not record.image_path:
                record.image_path = image_path
                updated = True
        if updated:
            db.commit()

    def record_attendance(self, db, record: AttendanceRecord):
        """Persist attendance record to database."""
        from app.models.attendance import Attendance, AttendanceSession
        
        attendance_date = record.timestamp.date()
        existing = (
            db.query(Attendance)
            .filter(Attendance.person_id == record.person_id, Attendance.date == attendance_date)
            .first()
        )
        if existing is None:
            existing = Attendance(
                person_id=record.person_id,
                date=attendance_date,
                check_in_time=record.timestamp,
                check_out_time=record.timestamp,
                confidence=record.confidence,
                image_path=record.image_path,
                total_detections=1,
            )
            db.add(existing)
        else:
            existing.check_out_time = record.timestamp
            existing.total_detections += 1
            existing.confidence = max(existing.confidence, record.confidence)
            existing.duration_minutes = int(
                (existing.check_out_time - existing.check_in_time).total_seconds() / 60
            )
            if record.image_path and not existing.image_path:
                existing.image_path = record.image_path
        
        session = (
            db.query(AttendanceSession)
            .filter(
                AttendanceSession.person_id == record.person_id,
                AttendanceSession.status == "active",
            )
            .first()
        )
        if session is None:
            session = AttendanceSession(
                person_id=record.person_id,
                session_start=record.timestamp,
                session_end=record.timestamp,
                confidence=record.confidence,
                image_count=1,
                status="active",
            )
            db.add(session)
        else:
            session.session_end = record.timestamp
            session.image_count += 1
            session.confidence = max(session.confidence, record.confidence)
        
        db.commit()
    
    def start_monitoring(
        self,
        db,
        save_images: bool = True,
        callback: Optional[Callable] = None,
        show_window: bool = False,
    ) -> bool:
        """Start real-time attendance monitoring."""
        if not self.camera or not self.camera.isOpened():
            print("❌ Camera not initialized")
            return False
        
        # Get known faces
        known_embeddings, known_names, known_ids = self.get_known_faces(db)
        
        if known_embeddings.size == 0:
            print("❌ No trained faces found. Please train some faces first.")
            return False
        
        self.is_running = True
        print("🎥 Starting attendance monitoring...")
        print("Press 'q' to stop monitoring")
        
        try:
            while self.is_running:
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to read from camera")
                    break
                
                self.current_frame = frame.copy()
                self.frame_index += 1
                performed_recognition = False
                
                # Recognize faces every N frames to reduce load
                if self.frame_index % self.recognition_stride == 0:
                    results = self.recognize_faces_in_frame(
                        frame, known_embeddings, known_names, known_ids, db
                    )
                    self.recognition_results = results
                    performed_recognition = True
                else:
                    results = self.recognition_results or []
                
                # Draw results on frame
                annotated_frame = self.draw_recognition_results(frame, results)
                self.current_annotated_frame = annotated_frame.copy()
                
                # Save attendance image if people are recognized
                if save_images and results and performed_recognition:
                    image_path = self.save_attendance_image(frame, results)
                    if image_path:
                        for record in self.attendance_records[::-1]:
                            if record.image_path is None:
                                record.image_path = image_path
                                break
                        self.update_attendance_image(db, results, image_path)
                
                # Call callback if provided
                if callback:
                    callback(annotated_frame, results)
                
                # Display frame in a local window only when explicitly enabled
                if show_window:
                    cv2.imshow('Attendance Monitoring', annotated_frame)
                    # Check for quit key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
        finally:
            self.is_running = False
            if show_window:
                cv2.destroyAllWindows()
        
        return True
    
    def stop_monitoring(self):
        """Stop attendance monitoring."""
        self.is_running = False
        print("⏹️ Stopping monitoring...")
    
    def get_attendance_summary(self) -> Dict:
        """Get attendance summary."""
        if not self.attendance_records:
            return {
                'total_records': 0,
                'unique_persons': 0,
                'persons': [],
                'time_range': None
            }
        
        # Group by person
        person_records = {}
        for record in self.attendance_records:
            if record.person_id not in person_records:
                person_records[record.person_id] = {
                    'name': record.name,
                    'first_seen': record.timestamp,
                    'last_seen': record.timestamp,
                    'detections': 0,
                    'avg_confidence': 0.0
                }
            
            person = person_records[record.person_id]
            person['detections'] += 1
            person['avg_confidence'] = (
                (person['avg_confidence'] * (person['detections'] - 1) + record.confidence) 
                / person['detections']
            )
            
            if record.timestamp < person['first_seen']:
                person['first_seen'] = record.timestamp
            if record.timestamp > person['last_seen']:
                person['last_seen'] = record.timestamp
        
        # Get time range
        timestamps = [r.timestamp for r in self.attendance_records]
        time_range = {
            'start': min(timestamps),
            'end': max(timestamps)
        }
        
        return {
            'total_records': len(self.attendance_records),
            'unique_persons': len(person_records),
            'persons': list(person_records.values()),
            'time_range': time_range
        }
    
    def export_attendance_json(self, filepath: Optional[str] = None) -> str:
        """Export attendance records to JSON."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = str(self.output_dir / f"attendance_{timestamp}.json")
        
        # Convert records to dict
        records_data = []
        for record in self.attendance_records:
            records_data.append({
                'person_id': record.person_id,
                'name': record.name,
                'timestamp': record.timestamp.isoformat(),
                'confidence': record.confidence,
                'image_path': record.image_path
            })
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump({
                'export_time': datetime.now().isoformat(),
                'total_records': len(records_data),
                'records': records_data
            }, f, indent=2)
        
        print(f"📊 Attendance exported to: {filepath}")
        return filepath
    
    def clear_attendance_records(self):
        """Clear all attendance records."""
        self.attendance_records.clear()
        self.recognition_cooldown.clear()
        print("🗑️ Attendance records cleared")
