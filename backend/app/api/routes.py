"""
API routes for face recognition and attendance monitoring.
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
import numpy as np
import pickle
import uuid
import cv2

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, hash_password
from app.api.deps import get_current_admin, get_current_any_user, get_current_staff_or_admin
from app.models.attendance import Person, Attendance, AttendanceSession
from app.models.user import AdminUser, AppUser
from app.services.face_encoder import FaceEncoder
from app.api import webcam

router = APIRouter()
encoder = FaceEncoder()

# Preload model on startup
encoder.preload_model()


class LoginPayload(BaseModel):
    username: str
    password: str


class RegisterPayload(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = Field(pattern="^(staff|student)$")
    department: Optional[str] = None
    note: Optional[str] = None


class PersonCreate(BaseModel):
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    person_code: Optional[str] = None
    person_type: str = Field(default="student", pattern="^(student|staff)$")


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    person_code: Optional[str] = None
    person_type: Optional[str] = Field(default=None, pattern="^(student|staff)$")


class AttendanceQuery(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    person_id: Optional[int] = None
    person_type: Optional[str] = Field(default=None, pattern="^(student|staff)$")


class RecognitionSettings(BaseModel):
    recognition_threshold: float = Field(ge=0.0, le=1.0)
    live_recognition_stride: int = Field(ge=1, le=10)
    live_recognition_width: int = Field(ge=160, le=1280)


@router.post("/auth/login", status_code=status.HTTP_200_OK)
async def login(payload: LoginPayload, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if admin and admin.is_active and verify_password(payload.password, admin.password_hash):
        token = create_access_token(admin.username, role="admin")
        return {"access_token": token, "token_type": "bearer", "role": "admin"}

    user = db.query(AppUser).filter(AppUser.email == payload.username).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role}


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    if db.query(AppUser).filter(AppUser.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = AppUser(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
        note=payload.note,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Registration successful", "id": user.id, "role": user.role}


@router.get("/auth/me")
async def me(current=Depends(get_current_any_user)):
    role = current["role"]
    user = current["user"]
    if role == "admin":
        return {"username": user.username, "role": role, "is_active": user.is_active}
    return {"email": user.email, "full_name": user.full_name, "role": role, "is_active": user.is_active}


@router.get("/settings/recognition", dependencies=[Depends(get_current_admin)])
async def get_recognition_settings():
    return {
        "recognition_threshold": settings.RECOGNITION_THRESHOLD,
        "live_recognition_stride": settings.LIVE_RECOGNITION_STRIDE,
        "live_recognition_width": settings.LIVE_RECOGNITION_WIDTH,
    }


@router.put("/settings/recognition", dependencies=[Depends(get_current_admin)])
async def update_recognition_settings(payload: RecognitionSettings):
    settings.RECOGNITION_THRESHOLD = payload.recognition_threshold
    settings.LIVE_RECOGNITION_STRIDE = payload.live_recognition_stride
    settings.LIVE_RECOGNITION_WIDTH = payload.live_recognition_width

    webcam.webcam_service.recognition_stride = max(1, settings.LIVE_RECOGNITION_STRIDE)

    return {
        "message": "Recognition settings updated",
        "recognition_threshold": settings.RECOGNITION_THRESHOLD,
        "live_recognition_stride": settings.LIVE_RECOGNITION_STRIDE,
        "live_recognition_width": settings.LIVE_RECOGNITION_WIDTH,
    }


@router.post("/persons", dependencies=[Depends(get_current_admin)])
async def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    if db.query(Person).filter(Person.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Name already exists")
    if payload.email and db.query(Person).filter(Person.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if payload.person_code and db.query(Person).filter(Person.person_code == payload.person_code).first():
        raise HTTPException(status_code=400, detail="Person code already exists")

    person = Person(
        name=payload.name,
        email=payload.email,
        department=payload.department,
        person_code=payload.person_code,
        person_type=payload.person_type,
        embedding=b"",  # placeholder until training
    )
    db.add(person)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate person data")
    db.refresh(person)
    return {"id": person.id, "name": person.name}


@router.get("/persons", dependencies=[Depends(get_current_admin)])
async def list_persons(person_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Person)
    if person_type:
        query = query.filter(Person.person_type == person_type)
    persons = query.all()
    
    return {
        "count": len(persons),
        "persons": [
            {
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "department": p.department,
                "person_code": p.person_code,
                "person_type": p.person_type,
            }
            for p in persons
        ],
    }


@router.patch("/persons/{person_id}", dependencies=[Depends(get_current_admin)])
async def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    incoming = payload.model_dump(exclude_unset=True)
    if "name" in incoming:
        existing = db.query(Person).filter(Person.name == incoming["name"], Person.id != person_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Name already exists")
    if "email" in incoming and incoming["email"]:
        existing = db.query(Person).filter(Person.email == incoming["email"], Person.id != person_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
    if "person_code" in incoming and incoming["person_code"]:
        existing = db.query(Person).filter(Person.person_code == incoming["person_code"], Person.id != person_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Person code already exists")
    
    for key, value in incoming.items():
        setattr(person, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate person data")
    return {"message": "Person updated", "id": person.id}


@router.delete("/persons/{person_id}", dependencies=[Depends(get_current_admin)])
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.query(AttendanceSession).filter(AttendanceSession.person_id == person_id).delete()
    db.query(Attendance).filter(Attendance.person_id == person_id).delete()
    db.delete(person)
    db.commit()
    return {"message": "Person deleted", "id": person.id}


@router.post("/train/", dependencies=[Depends(get_current_admin)])
async def train_person(
    person_id: int = Form(...),
    name: str = Form(...),
    person_type: str = Form("student"),
    email: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    person_code: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Train the system with face images for a person.
    
    Args:
        person_id: Unique ID for the person
        name: Name of the person
        files: List of image files containing the person's face
        
    Returns:
        Success message or error
    """
    if not encoder.initialized:
        raise HTTPException(
            status_code=503,
            detail="Face recognition service is not initialized. Please check dependencies."
        )
    
    embeddings = []
    
    # Process each uploaded file
    for file in files:
        # Check file size
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Encode face from image
        emb = encoder.encode_image(contents)
        if emb is not None:
            embeddings.append(emb)
    
    if not embeddings:
        raise HTTPException(
            status_code=400,
            detail=f"No valid faces found in uploaded images for {name}"
        )
    
    # Calculate average embedding and normalize
    avg_embedding = np.mean(embeddings, axis=0)
    avg_embedding = encoder.l2_normalize(avg_embedding)
    serialized = pickle.dumps(avg_embedding)
    
    # Store or update person in database
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        person = Person(
            id=person_id,
            name=name,
            email=email,
            department=department,
            person_code=person_code,
            person_type=person_type,
            embedding=serialized,
        )
        db.add(person)
    else:
        person.name = name
        person.email = email
        person.department = department
        person.person_code = person_code
        person.person_type = person_type
        person.embedding = serialized
    db.commit()
    
    return {
        "message": f"✅ {name} (ID={person_id}) trained successfully with {len(embeddings)} face(s)!",
        "person_id": person_id,
        "name": name,
        "faces_processed": len(embeddings)
    }


@router.post("/recognize/", dependencies=[Depends(get_current_admin)])
async def recognize_faces(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recognize faces in an uploaded image.
    
    Args:
        file: Image file containing faces to recognize
        
    Returns:
        Image file with recognized faces marked
    """
    if not encoder.initialized:
        raise HTTPException(
            status_code=503,
            detail="Face recognition service is not initialized. Please check dependencies."
        )
    
    # Read and decode image
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    
    # Get all known embeddings from database
    persons = db.query(Person).all()
    
    if not persons:
        raise HTTPException(
            status_code=404,
            detail="No trained faces found. Please train some faces first."
        )
    
    known_embeddings = []
    known_names = []
    known_ids = []
    
    for p in persons:
        if not p.embedding:
            continue
        try:
            emb = pickle.loads(p.embedding)
            emb = encoder.l2_normalize(emb)
        except Exception:
            continue
        known_embeddings.append(emb)
        known_names.append(p.name)
        known_ids.append(p.id)
    
    if not known_embeddings:
        raise HTTPException(
            status_code=404,
            detail="No trained faces found. Please train some faces first."
        )
    
    known_embeddings = np.array(known_embeddings)
    
    # Detect and encode faces in the uploaded image
    detected_faces = encoder.detect_and_encode_faces(img)
    
    if not detected_faces:
        raise HTTPException(
            status_code=400,
            detail="No faces detected in the uploaded image"
        )
    
    # Recognize each detected face
    recognized_count = 0
    
    for face_embedding, bbox in detected_faces:
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
            recognized_count += 1
        
        # Draw bounding box and label
        x1, y1, x2, y2 = bbox
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Add label with name and confidence
        label = f"{name} ({max_sim:.2f})" if person_id else f"{name}"
        cv2.putText(
            img, label, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
        )
    
    # Save result image
    output_filename = f"recognized_{uuid.uuid4().hex}.jpg"
    output_path = settings.output_path / output_filename
    cv2.imwrite(str(output_path), img)
    
    return FileResponse(
        str(output_path),
        media_type="image/jpeg",
        headers={
            "X-Recognized-Count": str(recognized_count),
            "X-Total-Faces": str(len(detected_faces))
        }
    )


@router.get("/attendance", dependencies=[Depends(get_current_any_user)])
async def list_attendance(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    person_id: Optional[int] = None,
    person_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Attendance, Person).join(Person, Attendance.person_id == Person.id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    if person_id:
        query = query.filter(Attendance.person_id == person_id)
    if person_type:
        query = query.filter(Person.person_type == person_type)
    
    rows = query.order_by(Attendance.date.desc(), Attendance.check_in_time.desc()).all()
    records = []
    for attendance, person in rows:
        records.append({
            "id": attendance.id,
            "person_id": person.id,
            "name": person.name,
            "person_type": person.person_type,
            "date": attendance.date.isoformat(),
            "check_in_time": attendance.check_in_time.isoformat(),
            "check_out_time": attendance.check_out_time.isoformat() if attendance.check_out_time else None,
            "confidence": attendance.confidence,
            "total_detections": attendance.total_detections,
            "duration_minutes": attendance.duration_minutes,
            "image_path": attendance.image_path,
        })
    
    return {"count": len(records), "records": records}


@router.get("/attendance/summary", dependencies=[Depends(get_current_any_user)])
async def attendance_summary(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    if target_date is None:
        target_date = datetime.utcnow().date()
    total_people = db.query(Person).count()
    present = db.query(Attendance).filter(Attendance.date == target_date).count()
    
    attendance_rate = 0.0 if total_people == 0 else round((present / total_people) * 100.0, 2)
    return {
        "date": target_date.isoformat(),
        "total_people": total_people,
        "present": present,
        "attendance_rate": attendance_rate,
    }


@router.get("/health/")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "Multiface Recognition API",
        "face_encoder_initialized": encoder.initialized
    }


# Include webcam routes
router.include_router(webcam.router, prefix="/webcam", tags=["Webcam Attendance"])
