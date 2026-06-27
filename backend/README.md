# Multiface Recognition API - Backend

A FastAPI-based backend service for multi-face recognition using DeepFace library.

## Features

- 🧠 High-accuracy face recognition using DeepFace (VGG-Face model)
- 👥 Bulk face recognition in single images
- ⚡ Asynchronous FastAPI backend
- 🗄️ MySQL database for storing face embeddings
- 🔒 RESTful API with comprehensive error handling
- 📊 Health check and monitoring endpoints

## Tech Stack

- **Framework**: FastAPI
- **Face Recognition**: DeepFace (VGG-Face model)
- **Database**: MySQL (via SQLAlchemy)
- **Image Processing**: OpenCV
- **Python**: 3.8+ (compatible with multiple versions)

## Installation

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv


# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and configure:

```bash
copy .env.example .env
# or on Linux/Mac: cp .env.example .env
```

Edit `.env` file if needed (defaults should work fine).

### 4. Initialize Database

The database schema will be created automatically on first run.

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  python -m uvicorn app.main:app --reload

```

Or use Python:

```bash
python -m app.main
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```
GET /api/health/
```

#### 2. Train Face
```
POST /api/train/
```
**Form Data:**
- `person_id` (int): Unique ID for the person
- `name` (string): Name of the person
- `files` (files): Multiple image files containing the person's face

**Response:**
```json
{
  "message": "✅ John Doe (ID=1) trained successfully with 3 face(s)!",
  "person_id": 1,
  "name": "John Doe",
  "faces_processed": 3
}
```

#### 3. Recognize Faces
```
POST /api/recognize/
```
**Form Data:**
- `file` (file): Image file containing faces to recognize

**Response:**
- Returns image file (JPEG) with recognized faces marked

#### 4. List All Persons
```
GET /api/persons/
```

**Response:**
```json
{
  "count": 2,
  "persons": [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Smith"}
  ]
}
```

#### 5. Delete Person
```
DELETE /api/persons/{person_id}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Frontend (React + Vite)

The frontend is located in `frontend/` and provides the professional attendance UI.

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

### Connect Frontend to Backend

- Default API base is `http://localhost:8000/api`
- You can change it from the UI in **Settings → API Base URL**
- Keep the backend running on port 8000 for local development

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration settings
│   │   └── database.py      # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── person.py        # Person model
│   └── services/
│       ├── __init__.py
│       └── face_encoder.py  # Face encoding service
├── outputs/                 # Output directory for recognized images
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Example environment file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

Edit `.env` file to configure:

- `DATABASE_URL`: Database connection string
- `RECOGNITION_THRESHOLD`: Face recognition threshold (0.0-1.0)
- `DETECTION_SIZE`: Face detection size
- `MAX_FILE_SIZE_MB`: Maximum upload file size
- `DEBUG`: Enable/disable debug mode

## Dataset and Training

This project does not ship with a fixed dataset. It uses **your uploaded images** to build face embeddings.

**Best practice for training images (per person):**
- 3–5 photos, clear and sharp
- different angles (front, slight left/right)
- different lighting conditions
- avoid heavy filters or occlusions (masks, sunglasses)

## Troubleshooting

### Issue: DeepFace model download

**Note**: DeepFace will automatically download model files on first use (VGG-Face model, ~500MB). This is a one-time download.

If download fails:
1. Check your internet connection
2. Models are stored in `~/.deepface/weights/` directory
3. You can manually download models if needed

### Issue: Face recognition not initializing

If you encounter issues with face recognition initialization:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Verify DeepFace is working:
   ```python
   from deepface import DeepFace
   print("DeepFace library loaded successfully")
   ```
3. On first run, DeepFace will download the model (this may take a few minutes)

### Issue: No faces detected

- Ensure images contain clear, front-facing faces
- Check image quality and lighting
- Try adjusting `DETECTION_SIZE` in `.env`

### Issue: Recognition accuracy is low

- Train with multiple images (3-5 recommended) per person
- Ensure training images have good quality and different angles
- Adjust `RECOGNITION_THRESHOLD` in `.env` (lower = more strict)

## License

This project is open source and available for use.
