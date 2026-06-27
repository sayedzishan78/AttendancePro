"""
Flask Backend for Webcam Attendance System
Alternative to FastAPI if you prefer Flask
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import threading
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import sqlite3
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['OUTPUT_DIR'] = 'outputs'
app.config['DATABASE'] = 'face_recognition.db'
app.config['RECOGNITION_THRESHOLD'] = 0.4

# Ensure output directory exists
Path(app.config['OUTPUT_DIR']).mkdir(exist_ok=True)

# Global variables for webcam monitoring
camera = None
monitoring_active = False
monitoring_thread = None
attendance_records = []
recognition_cooldown = {}
current_frame = None

class SimpleFaceEncoder:
    """Simple face encoder using OpenCV (placeholder for DeepFace)"""
    
    def __init__(self):
        self.initialized = True
        self._model_preloaded = True
    
    def encode_image(self, image_bytes):
        """Placeholder - in real implementation, use DeepFace"""
        # Return dummy embedding for demo
        return np.random.rand(512).astype(np.float32)
    
    def detect_and_encode_faces(self, img):
        """Placeholder - in real implementation, use DeepFace"""
        # Return dummy face detection for demo
        return [(np.random.rand(512).astype(np.float32), (100, 100, 200, 200))]

encoder = SimpleFaceEncoder()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            department TEXT,
            employee_id TEXT UNIQUE,
            embedding BLOB NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            date DATE NOT NULL,
            check_in_time DATETIME NOT NULL,
            check_out_time DATETIME,
            confidence REAL NOT NULL,
            image_path TEXT,
            total_detections INTEGER DEFAULT 1,
            duration_minutes INTEGER,
            FOREIGN KEY (person_id) REFERENCES persons(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_known_faces():
    """Get all known faces from database"""
    conn = get_db_connection()
    persons = conn.execute('SELECT * FROM persons WHERE is_active = 1').fetchall()
    conn.close()
    
    if not persons:
        return [], [], []
    
    known_embeddings = []
    known_names = []
    known_ids = []
    
    for person in persons:
        try:
            emb = pickle.loads(person['embedding'])
            known_embeddings.append(emb)
            known_names.append(person['name'])
            known_ids.append(person['id'])
        except:
            continue
    
    return np.array(known_embeddings), known_names, known_ids

def recognize_faces_in_frame(frame, known_embeddings, known_names, known_ids):
    """Recognize faces in frame"""
    if known_embeddings.size == 0:
        return []
    
    # Detect faces
    detected_faces = encoder.detect_and_encode_faces(frame)
    
    results = []
    current_time = datetime.now()
    
    for face_embedding, bbox in detected_faces:
        # Calculate similarity (placeholder)
        if known_embeddings.size > 0:
            similarities = np.dot(known_embeddings, face_embedding)
            idx = np.argmax(similarities)
            max_sim = similarities[idx]
            
            name = "Unknown"
            person_id = None
            
            if max_sim > app.config['RECOGNITION_THRESHOLD']:
                name = known_names[idx]
                person_id = known_ids[idx]
                
                # Check cooldown
                cooldown_key = f"{person_id}_{name}"
                last_recognition = recognition_cooldown.get(cooldown_key)
                
                if (last_recognition is None or 
                    current_time - last_recognition > timedelta(seconds=30)):
                    
                    # Create attendance record
                    record = {
                        'person_id': person_id,
                        'name': name,
                        'timestamp': current_time,
                        'confidence': float(max_sim),
                        'image_path': None
                    }
                    attendance_records.append(record)
                    recognition_cooldown[cooldown_key] = current_time
            
            results.append({
                'name': name,
                'person_id': person_id,
                'confidence': float(max_sim),
                'bbox': bbox,
                'recognized': person_id is not None
            })
    
    return results

def draw_recognition_results(frame, results):
    """Draw recognition results on frame"""
    annotated_frame = frame.copy()
    
    for result in results:
        x1, y1, x2, y2 = result['bbox']
        color = (0, 255, 0) if result['recognized'] else (0, 0, 255)
        
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
        
        label = f"{result['name']} ({result['confidence']:.2f})"
        cv2.putText(
            annotated_frame, label, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
        )
    
    return annotated_frame

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Webcam Attendance API (Flask)',
        'face_encoder_initialized': encoder.initialized
    })

@app.route('/api/webcam/start', methods=['POST'])
def start_monitoring():
    """Start webcam monitoring"""
    global monitoring_active, monitoring_thread, camera
    
    if monitoring_active:
        return jsonify({'error': 'Monitoring already active'}), 400
    
    try:
        # Initialize camera
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'error': 'Failed to initialize camera'}), 500
        
        monitoring_active = True
        
        def monitor():
            global current_frame
            known_embeddings, known_names, known_ids = get_known_faces()
            
            while monitoring_active:
                ret, frame = camera.read()
                if not ret:
                    break
                
                current_frame = frame.copy()
                
                # Recognize faces
                results = recognize_faces_in_frame(
                    frame, known_embeddings, known_names, known_ids
                )
                
                time.sleep(0.03)  # ~30 FPS
        
        monitoring_thread = threading.Thread(target=monitor, daemon=True)
        monitoring_thread.start()
        
        return jsonify({
            'message': '🎥 Webcam monitoring started',
            'status': 'active'
        })
        
    except Exception as e:
        monitoring_active = False
        return jsonify({'error': str(e)}), 500

@app.route('/api/webcam/stop', methods=['POST'])
def stop_monitoring():
    """Stop webcam monitoring"""
    global monitoring_active, camera
    
    if not monitoring_active:
        return jsonify({'error': 'Monitoring not active'}), 400
    
    monitoring_active = False
    
    if camera:
        camera.release()
        camera = None
    
    return jsonify({
        'message': '⏹️ Webcam monitoring stopped',
        'status': 'stopped'
    })

@app.route('/api/webcam/status', methods=['GET'])
def get_status():
    """Get monitoring status"""
    global monitoring_active, attendance_records
    
    # Calculate summary
    unique_persons = len(set(r['person_id'] for r in attendance_records if r['person_id']))
    
    summary = {
        'total_records': len(attendance_records),
        'unique_persons': unique_persons,
        'persons': []
    }
    
    return jsonify({
        'monitoring_active': monitoring_active,
        'camera_initialized': camera is not None,
        'attendance_summary': summary
    })

@app.route('/api/webcam/attendance', methods=['GET'])
def get_attendance():
    """Get attendance records"""
    global attendance_records
    
    records = []
    for record in attendance_records:
        records.append({
            'person_id': record['person_id'],
            'name': record['name'],
            'timestamp': record['timestamp'].isoformat(),
            'confidence': record['confidence'],
            'image_path': record['image_path']
        })
    
    return jsonify({
        'total_records': len(records),
        'records': records
    })

@app.route('/api/webcam/capture', methods=['GET'])
def capture_frame():
    """Capture and process single frame"""
    global camera, current_frame
    
    if not camera or not camera.isOpened():
        # Initialize camera temporarily
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'error': 'Failed to initialize camera'}), 500
    
    try:
        ret, frame = camera.read()
        if not ret:
            return jsonify({'error': 'Failed to capture frame'}), 500
        
        # Get known faces
        known_embeddings, known_names, known_ids = get_known_faces()
        
        # Recognize faces
        results = recognize_faces_in_frame(frame, known_embeddings, known_names, known_ids)
        
        # Draw results
        annotated_frame = draw_recognition_results(frame, results)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'message': '📸 Frame captured and processed',
            'faces_detected': len(results),
            'faces_recognized': len([r for r in results if r['recognized']]),
            'frame_base64': frame_base64,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webcam/export', methods=['POST'])
def export_attendance():
    """Export attendance records"""
    global attendance_records
    
    if not attendance_records:
        return jsonify({'error': 'No attendance records to export'}), 404
    
    # Create export data
    export_data = {
        'export_time': datetime.now().isoformat(),
        'total_records': len(attendance_records),
        'records': []
    }
    
    for record in attendance_records:
        export_data['records'].append({
            'person_id': record['person_id'],
            'name': record['name'],
            'timestamp': record['timestamp'].isoformat(),
            'confidence': record['confidence'],
            'image_path': record['image_path']
        })
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(app.config['OUTPUT_DIR'], f"attendance_{timestamp}.json")
    
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return jsonify({
        'message': '📊 Attendance exported successfully',
        'filepath': filepath
    })

@app.route('/api/webcam/attendance', methods=['DELETE'])
def clear_attendance():
    """Clear attendance records"""
    global attendance_records, recognition_cooldown
    
    attendance_records.clear()
    recognition_cooldown.clear()
    
    return jsonify({
        'message': '🗑️ Attendance records cleared'
    })

@app.route('/api/webcam/preview', methods=['GET'])
def get_preview():
    """Get current webcam preview"""
    global current_frame
    
    if current_frame is None:
        return jsonify({'error': 'No frame available'}), 404
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', current_frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        'frame_base64': frame_base64,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/webcam/summary', methods=['GET'])
def get_summary():
    """Get attendance summary"""
    global attendance_records, monitoring_active
    
    # Calculate summary
    unique_persons = len(set(r['person_id'] for r in attendance_records if r['person_id']))
    
    summary = {
        'total_records': len(attendance_records),
        'unique_persons': unique_persons,
        'persons': []
    }
    
    return jsonify({
        'summary': summary,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'monitoring_active': monitoring_active
    })

# Training endpoints (simplified)
@app.route('/api/train', methods=['POST'])
def train_person():
    """Train a person (simplified)"""
    data = request.get_json()
    
    person_id = data.get('person_id')
    name = data.get('name')
    
    if not person_id or not name:
        return jsonify({'error': 'person_id and name required'}), 400
    
    # Create dummy embedding
    embedding = pickle.dumps(np.random.rand(512).astype(np.float32))
    
    # Save to database
    conn = get_db_connection()
    conn.execute(
        'INSERT OR REPLACE INTO persons (id, name, embedding) VALUES (?, ?, ?)',
        (person_id, name, embedding)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f'✅ {name} (ID={person_id}) trained successfully',
        'person_id': person_id,
        'name': name,
        'faces_processed': 1
    })

@app.route('/api/persons', methods=['GET'])
def list_persons():
    """List all trained persons"""
    conn = get_db_connection()
    persons = conn.execute('SELECT id, name FROM persons WHERE is_active = 1').fetchall()
    conn.close()
    
    return jsonify({
        'count': len(persons),
        'persons': [dict(p) for p in persons]
    })

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    print("🚀 Flask Webcam Attendance API starting...")
    print("📖 API Documentation: http://localhost:5000/api/health")
    print("🎥 Webcam frontend: Open webcam_attendance_fixed.html")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
