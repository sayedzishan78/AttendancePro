"""
API routes for webcam-based attendance monitoring.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import threading
import time
import base64
import numpy as np
import cv2

from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.services.face_encoder import FaceEncoder
from app.services.webcam_service import WebcamService
from app.api.deps import get_current_staff_or_admin

router = APIRouter()
encoder = FaceEncoder()
webcam_service = WebcamService(encoder)

# Global monitoring thread
monitoring_thread = None
monitoring_active = False


@router.post("/start/", dependencies=[Depends(get_current_staff_or_admin)])
async def start_webcam_monitoring(
    background_tasks: BackgroundTasks,
    camera_id: int = 0,
    save_images: bool = True,
):
    """
    Start webcam-based attendance monitoring.
    
    Args:
        camera_id: Camera device ID (default: 0)
        save_images: Whether to save attendance images
        db: Database session
        
    Returns:
        Monitoring status
    """
    global monitoring_thread, monitoring_active
    
    if monitoring_active:
        raise HTTPException(
            status_code=400,
            detail="Webcam monitoring is already active"
        )
    
    # Initialize camera
    if not webcam_service.initialize_camera(camera_id):
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize camera"
        )
    
    # Start monitoring in background
    def monitor_in_background():
        global monitoring_active
        monitoring_active = True
        db = SessionLocal()
        try:
            webcam_service.start_monitoring(db, save_images=save_images, show_window=False)
        finally:
            monitoring_active = False
            webcam_service.release_camera()
            db.close()
    
    monitoring_thread = threading.Thread(target=monitor_in_background, daemon=True)
    monitoring_thread.start()
    
    return {
        "message": "🎥 Webcam monitoring started",
        "camera_id": camera_id,
        "save_images": save_images,
        "status": "active"
    }


@router.post("/stop/", dependencies=[Depends(get_current_staff_or_admin)])
async def stop_webcam_monitoring():
    """
    Stop webcam-based attendance monitoring.
    
    Returns:
        Monitoring status
    """
    global monitoring_active
    
    if not monitoring_active:
        raise HTTPException(
            status_code=400,
            detail="Webcam monitoring is not active"
        )
    
    webcam_service.stop_monitoring()
    
    # Wait for thread to finish
    if monitoring_thread and monitoring_thread.is_alive():
        monitoring_thread.join(timeout=5)
    
    return {
        "message": "⏹️ Webcam monitoring stopped",
        "status": "stopped"
    }


@router.get("/status/", dependencies=[Depends(get_current_staff_or_admin)])
async def get_webcam_status():
    """
    Get current webcam monitoring status.
    
    Returns:
        Monitoring status and statistics
    """
    global monitoring_active
    
    attendance_summary = webcam_service.get_attendance_summary()
    
    return {
        "monitoring_active": monitoring_active,
        "camera_initialized": webcam_service.camera is not None,
        "attendance_summary": attendance_summary,
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/attendance/", dependencies=[Depends(get_current_staff_or_admin)])
async def get_attendance_records():
    """
    Get all attendance records.
    
    Returns:
        List of attendance records
    """
    records = []
    for record in webcam_service.attendance_records:
        records.append({
            "person_id": record.person_id,
            "name": record.name,
            "timestamp": record.timestamp.isoformat(),
            "confidence": record.confidence,
            "image_path": record.image_path
        })
    
    return {
        "total_records": len(records),
        "records": records
    }


@router.post("/export/", dependencies=[Depends(get_current_staff_or_admin)])
async def export_attendance():
    """
    Export attendance records to JSON file.
    
    Returns:
        Export file path and summary
    """
    if not webcam_service.attendance_records:
        raise HTTPException(
            status_code=404,
            detail="No attendance records to export"
        )
    
    filepath = webcam_service.export_attendance_json()
    summary = webcam_service.get_attendance_summary()
    
    return {
        "message": "📊 Attendance exported successfully",
        "filepath": filepath,
        "summary": summary
    }


@router.delete("/attendance/", dependencies=[Depends(get_current_staff_or_admin)])
async def clear_attendance_records():
    """
    Clear all attendance records.
    
    Returns:
        Confirmation message
    """
    webcam_service.clear_attendance_records()
    
    return {
        "message": "🗑️ Attendance records cleared",
        "records_remaining": 0
    }


@router.get("/capture/", dependencies=[Depends(get_current_staff_or_admin)])
async def capture_current_frame(db: Session = Depends(get_db)):
    """
    Capture and process a single frame from webcam.
    
    Returns:
        Processed frame with face recognition results
    """
    if not webcam_service.camera or not webcam_service.camera.isOpened():
        # Initialize camera temporarily
        if not webcam_service.initialize_camera():
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize camera"
            )
    
    try:
        # Capture frame
        ret, frame = webcam_service.camera.read()
        if not ret:
            raise HTTPException(
                status_code=500,
                detail="Failed to capture frame from camera"
            )
        
        # Get known faces
        known_embeddings, known_names, known_ids = webcam_service.get_known_faces(db)
        
        if known_embeddings.size == 0:
            raise HTTPException(
                status_code=404,
                detail="No trained faces found. Please train some faces first."
            )
        
        # Recognize faces
        results = webcam_service.recognize_faces_in_frame(
            frame, known_embeddings, known_names, known_ids, db
        )
        
        # Draw results on frame
        annotated_frame = webcam_service.draw_recognition_results(frame, results)
        
        # Save attendance image if people are recognized
        image_path = webcam_service.save_attendance_image(frame, results)
        webcam_service.update_attendance_image(db, results, image_path)
        
        # Convert frame to base64 for response
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "message": "📸 Frame captured and processed",
            "faces_detected": len(results),
            "faces_recognized": len([r for r in results if r['recognized']]),
            "image_saved": image_path is not None,
            "image_path": image_path,
            "frame_base64": frame_base64,
            "results": results
        }
        
    finally:
        # Release camera if it was initialized temporarily
        if not monitoring_active:
            webcam_service.release_camera()


@router.get("/preview/", dependencies=[Depends(get_current_staff_or_admin)])
async def get_webcam_preview():
    """
    Get current webcam preview as base64 image.
    
    Returns:
        Base64 encoded current frame
    """
    if not webcam_service.camera or not webcam_service.camera.isOpened():
        raise HTTPException(
            status_code=400,
            detail="Camera not initialized. Start monitoring first."
        )
    
    if webcam_service.current_frame is None and webcam_service.current_annotated_frame is None:
        raise HTTPException(
            status_code=404,
            detail="No frame available yet"
        )
    
    # Convert current frame to base64
    frame = (
        webcam_service.current_annotated_frame
        if webcam_service.current_annotated_frame is not None
        else webcam_service.current_frame
    )
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "frame_base64": frame_base64,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "recognition_results": webcam_service.recognition_results
    }


@router.get("/summary/", dependencies=[Depends(get_current_staff_or_admin)])
async def get_attendance_summary():
    """
    Get detailed attendance summary.
    
    Returns:
        Detailed attendance statistics
    """
    summary = webcam_service.get_attendance_summary()
    
    return {
        "summary": summary,
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring_active": monitoring_active
    }
