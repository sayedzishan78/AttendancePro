# MultiFace Recognition App – Complete Explanation Guide

This guide explains the **MultiFace Recognition App** from scratch in simple language, as if you are new to programming. Read it section by section to understand what the project does and how it works.

---

## 1. PROJECT OVERVIEW

### What is MultiFace Recognition App?

**MultiFace Recognition App** is a software system that:

1. **Detects faces** in images or from a camera (webcam).
2. **Recognizes who each face belongs to** by comparing it with faces the system was "trained" on (students or staff).
3. **Marks attendance** automatically when a known person is seen (e.g. "John checked in at 9:00 AM").
4. **Shows reports** so admins or staff can see who was present and when.

Think of it like a digital register: instead of calling names, the camera "sees" who is in front of it and records their attendance.

### What problem does it solve?

- **Manual attendance** (paper or clicking names) is slow and can be faked.
- This app automates attendance using the camera: when a trained person's face is detected, the system records them as present for that day.
- It saves time, reduces human error, and gives a clear record (who, when, and optionally a photo).

### What makes it different from single-face systems?

- **Single-face:** Only one face is processed at a time (e.g. one person per photo).
- **MultiFace:** In one image or one camera frame, the system can detect **many faces at once**, recognize each person, and mark attendance for all of them in that same moment. So a group photo or a classroom camera view can record several people in one go.

### What is the main goal of this project?

The main goal is to provide a **professional attendance monitoring system** that:

- Uses **face recognition** (not just face detection) to know *who* is present.
- Works in **real time** with a webcam (live monitoring).
- Supports **multiple people** in the same frame.
- Stores data in a **database** and shows it on a **web dashboard** with roles (admin, staff, student).

---

## 2. SYSTEM ARCHITECTURE

### Complete architecture (big picture)

The app has three main parts:

1. **Frontend (React + Vite)**  
   - The website you open in the browser (login, dashboard, live monitoring, people management, attendance reports, settings).  
   - Runs on your computer; talks to the backend over HTTP.

2. **Backend (FastAPI)**  
   - The "server" that does the real work: face detection, face recognition, saving attendance, user auth, and API.  
   - Runs on a port (e.g. 8000). The frontend sends requests here.

3. **Database (MySQL)**  
   - Stores: persons (names, face embeddings), attendance records, users (admin, staff, student).  
   - The backend reads and writes here; the frontend never talks to the database directly.

So: **Browser → Frontend (React) → Backend (FastAPI) → Database (MySQL)**.  
Face recognition runs **inside the backend** (Python + DeepFace + OpenCV).

### How camera input is handled

- The **camera is opened by the backend**, not by the browser.
- When you click "Start" on the Live Monitoring page, the frontend calls the backend API: "Start webcam."
- The backend uses **OpenCV** (`cv2.VideoCapture`) to open the camera (e.g. device 0), then runs a loop that:
  - Reads a **frame** (one image) from the camera.
  - Runs face detection and recognition on that frame.
  - Stores the latest frame (and optional annotated image) in memory.
- The frontend **does not get a live video stream**. It repeatedly asks the backend: "Give me the latest preview image." The backend sends back the last processed frame as a **base64 image**. So the "live" feeling is achieved by polling (e.g. every 1.5 seconds) the `/api/webcam/preview/` endpoint.

### How multiple faces are processed at the same time

- One frame from the camera can contain many faces.
- The backend uses **DeepFace** with `enforce_detection=False` so it returns **all faces** in the image.
- For each face, DeepFace gives:
  - A **face region** (bounding box: x, y, width, height).
  - An **embedding** (a list of numbers describing that face).
- The code loops over **each detected face**, computes similarity with every stored person's embedding, and decides "this face is Person A," "this face is Person B," etc. So in one frame, many people can be recognized and attendance can be updated for each of them (subject to cooldown and "one record per person per day" logic).

### How backend, database, and frontend are connected

- **Frontend ↔ Backend:**  
  - Frontend uses **Axios** with a base URL (e.g. `http://localhost:8000/api`).  
  - Every button or page that needs data calls an API (e.g. `GET /api/attendance`, `POST /api/webcam/start/`).  
  - The backend returns JSON (or files/images).  
  - Auth: frontend stores a JWT in `localStorage` and sends it as `Authorization: Bearer <token>`.

- **Backend ↔ Database:**  
  - Backend uses **SQLAlchemy** with **PyMySQL** to connect to MySQL.  
  - Connection string is in config (e.g. `.env`: `DATABASE_URL`).  
  - Each API that needs data uses a **database session** (e.g. `get_db()`) to run queries and commit.

So the **full data flow** is: User action in browser → Frontend HTTP request → Backend API → Database (read/write) and/or face recognition → Backend response → Frontend updates the UI.

### Full data flow from camera capture to attendance marking

1. User starts monitoring from the frontend → `POST /api/webcam/start/`.
2. Backend opens the camera and starts a **background thread** that runs a loop:
   - Read frame from camera.
   - Every N-th frame (stride), run face detection + encoding (DeepFace), then compare each face's embedding to all stored person embeddings (cosine similarity).
   - If similarity > threshold for a person and cooldown allows, create/update an **attendance record** for that person for today and commit to DB.
   - Optionally save an image and attach path to the attendance row.
3. Stored data: **Person** (id, name, embedding, etc.) and **Attendance** (person_id, date, check_in_time, check_out_time, confidence, image_path, etc.).
4. Frontend shows "latest detections" by polling `/api/webcam/preview/` (which returns the last annotated frame and recognition results) and shows "attendance" via `/api/attendance` and dashboard summary via `/api/attendance/summary`.

So: **Camera → Frame → Detect faces → Encode faces → Match to DB persons → Update attendance in DB → Frontend reads attendance and preview.**

---

## 3. PROJECT STRUCTURE

### Root folder

- **backend/** – Python FastAPI server (APIs, face recognition, DB).
- **frontend/** – React + Vite web app (UI, pages, API client).

### Backend folders and important files

- **backend/app/**  
  - **main.py** – Entry point of the backend. Creates the FastAPI app, CORS, includes the API router. When you run the server, execution starts here.  
  - **api/**  
    - **routes.py** – Main API routes: auth (login, register), persons (CRUD), train, recognize, attendance, health, recognition settings.  
    - **webcam.py** – Webcam-specific routes: start/stop monitoring, status, preview, capture, attendance list, export, clear.  
    - **deps.py** – Auth dependencies: get current user (JWT), get_current_admin, get_current_staff_or_admin, get_current_any_user.  
  - **core/**  
    - **config.py** – Settings (DB URL, threshold, ports, secrets) from environment/.env.  
    - **database.py** – SQLAlchemy engine, session factory, `get_db`, `init_database` (create DB if missing, create tables, optional admin bootstrap).  
    - **security.py** – Password hashing and JWT creation.  
  - **models/**  
    - **attendance.py** – Person, Attendance, AttendanceSession, DailyAttendanceSummary (SQLAlchemy models).  
    - **user.py** – AdminUser, AppUser.  
  - **services/**  
    - **face_encoder.py** – FaceEncoder class: DeepFace (VGG-Face), encode one image, detect and encode all faces in an image, L2 normalize. This is the "brain" of face recognition.  
    - **webcam_service.py** – WebcamService: camera open/close, loop that reads frames, runs recognition, cooldown to avoid duplicate attendance, saving to DB and optional images.

### Frontend folders and important files

- **frontend/src/**  
  - **main.tsx** – Entry point: renders the app inside `BrowserRouter` and `AuthProvider`.  
  - **App.tsx** – Defines routes (login, dashboard, monitoring, people, attendance, settings), `RequireAuth` and `RequireRole` so only logged-in and allowed roles see certain pages.  
  - **state/AuthContext.tsx** – Auth state (token, role, login/logout); used across the app.  
  - **api/http.ts** – Axios instance: base URL from env or localStorage, adds `Authorization: Bearer <token>` to every request.  
  - **api/auth.ts**, **persons.ts**, **attendance.ts**, **webcam.ts**, **settings.ts** – Functions that call backend APIs.  
  - **pages/** – Login, Dashboard, LiveMonitoring, People, Attendance, Settings, AccessDenied.  
  - **components/AppLayout.tsx** – Layout (sidebar/nav + outlet for the current page).  
  - **styles.css** – Global styles.

### Which files are essential

- **Backend:** `main.py` (start), `routes.py` and `webcam.py` (APIs), `face_encoder.py` (recognition), `webcam_service.py` (camera + attendance loop), `database.py`, `config.py`, `models/attendance.py` and `user.py`.  
- **Frontend:** `main.tsx`, `App.tsx`, `AuthContext`, `http.ts`, and the page components that use the APIs.  
- **Config:** Backend `.env` (e.g. `DATABASE_URL`, `RECOGNITION_THRESHOLD`).

### What happens when the project starts

- **Backend:**  
  - Running `uvicorn app.main:app` (or `python -m app.main`) loads `main.py`.  
  - `init_database()` runs (creates DB if needed, tables, default admin).  
  - FastAPI app is created, router included.  
  - When the first request that uses face recognition happens (or at startup if preload is called), the FaceEncoder preloads the DeepFace model (downloads weights once if needed).

- **Frontend:**  
  - Running `npm run dev` starts Vite and serves the React app.  
  - User opens the app in the browser; `main.tsx` mounts the app; if not logged in, they are sent to `/login`. After login, they see the dashboard and can open other pages based on role.

### Entry points

- **Backend:** `backend/app/main.py` – the `app` object is the FastAPI application; `if __name__ == "__main__"` runs uvicorn.  
- **Frontend:** `frontend/src/main.tsx` – `ReactDOM.createRoot(...).render(...)` mounts the root component (App inside Router and AuthProvider).

---

## 4. TECHNOLOGIES USED

- **Programming languages:**  
  - Backend: **Python 3.8+**.  
  - Frontend: **TypeScript** (and JSX for React).

- **Frameworks:**  
  - Backend: **FastAPI** (async web framework, automatic OpenAPI docs).  
  - Frontend: **React 18** with **React Router**; build tool: **Vite**.

- **Database:** **MySQL**. Access from Python via **SQLAlchemy** (ORM) and **PyMySQL** (driver).

- **Face detection:** Handled inside **DeepFace**; DeepFace can use different detectors; in this project the code uses **OpenCV** as the detector backend (`detector_backend='opencv'`). So OpenCV is used for the "find face regions" step.

- **Face recognition model:** **VGG-Face** via **DeepFace** (`model_name="VGG-Face"`). This model turns a face image into a fixed-size vector (embedding). Recognition is done by comparing these embeddings (cosine similarity), not by "face detection" alone.

- **Why these choices:**  
  - FastAPI: fast, easy APIs and docs.  
  - React + Vite: modern UI and fast dev experience.  
  - MySQL: reliable, good for structured data (persons, attendance, users).  
  - DeepFace + VGG-Face: good accuracy without writing low-level neural network code; DeepFace handles detection and embedding in one library.

---

## 5. ALGORITHMS USED IN THE PROJECT

This section describes every **algorithm** (the mathematical or logical method) used in the MultiFace Recognition App. Algorithms are the "how" behind the features.

### Main algorithm used in this project

The **main algorithm** in the MultiFace Recognition App is **VGG-Face**. It is the one that makes “who is this person?” possible.

- **VGG-Face** is the **face recognition** model. It converts a face image into a fixed-length vector (embedding). That embedding is what allows the system to identify the person. Without VGG-Face you would only know “there is a face,” not “this is John” or “this is Mary.”
- **Cosine similarity** is used for **matching**: it compares the new face’s embedding to all stored embeddings and picks the best match. It is important but secondary; the algorithm that is specific to your app’s core purpose (recognizing who someone is) is **VGG-Face**.

So in short: **VGG-Face is the main algorithm**; cosine similarity is the comparison method used on top of it.

### 5.1 Face detection algorithm

- **What is used:** **OpenCV-based face detector** (configured in the project as `detector_backend='opencv'` inside DeepFace).
- **What it does:** Scans an image and finds rectangular regions that contain a human face. It does **not** identify who the person is; it only answers "where is a face?"
- **How it works (simple idea):** The detector slides a window over the image and uses pre-trained classifiers (e.g. Haar-like features or similar) to decide whether that region looks like a face. It returns one or more bounding boxes (x, y, width, height) for each face found.
- **Where in code:** DeepFace’s `represent()` is called with `detector_backend='opencv'`; DeepFace uses OpenCV under the hood for this step. So the **algorithm** is the OpenCV face detection algorithm (Haar cascades or the default OpenCV detector used by DeepFace).

### 5.2 Face recognition (embedding) algorithm

- **What is used:** **VGG-Face** – a deep convolutional neural network (CNN) for face recognition.
- **What it does:** Takes a cropped face image and outputs a fixed-length vector of numbers called an **embedding** (or **face embedding**). This vector is like a numerical "fingerprint" of that face. The same person in different photos should get similar vectors; different people should get different vectors.
- **How it works (simple idea):** The image is passed through many layers of convolutions and other operations. The final layer produces a high-dimensional vector (e.g. 2622 dimensions for VGG-Face). That vector is then **L2-normalized** in our project (see below). We do **not** train this network ourselves; we use the pre-trained VGG-Face model provided by DeepFace.
- **Where in code:** `face_encoder.py` – `model_name = "VGG-Face"` and `DeepFace.represent(..., model_name=self.model_name)`.

### 5.3 Similarity / matching algorithm

- **What is used:** **Cosine similarity** implemented as a dot product on **L2-normalized** vectors.
- **What it does:** Compares a new face embedding (from the camera or uploaded image) with every stored person’s embedding and finds the **most similar** stored person. If that similarity is above a threshold, the face is "recognized" as that person.
- **How it works (simple idea):**
  - **L2 normalization:** Each embedding vector is scaled so that its length (Euclidean norm) is 1. So we work with unit-length vectors.
  - **Cosine similarity:** For two unit-length vectors **a** and **b**, the cosine of the angle between them is exactly the **dot product**: `cos_sim = a · b`. In the code this is `np.dot(known_embeddings, face_embedding)`. Values range from -1 to 1; **closer to 1** means more similar.
  - **Matching:** For the new face embedding, we compute dot product with all known embeddings, take the **maximum** value and the corresponding person. If `max_sim > RECOGNITION_THRESHOLD` (e.g. 0.4), we say the face is recognized as that person.
- **Where in code:** `face_encoder.py` – `l2_normalize()`; `webcam_service.py` and `routes.py` – `cos_sim = np.dot(known_embeddings, face_embedding)`, `idx = np.argmax(cos_sim)`.

### 5.4 Password hashing algorithm

- **What is used:** **PBKDF2-SHA256** (configured in Passlib as `pbkdf2_sha256`).
- **What it does:** When a user registers or when the admin account is created, the password is not stored in plain text. It is **hashed**: turned into a fixed-length string that cannot be reversed. When the user logs in, the entered password is hashed the same way and compared with the stored hash.
- **How it works (simple idea):** PBKDF2 (Password-Based Key Derivation Function 2) applies a hash function (here SHA-256) many times, with a salt, to make brute-force attacks slow. So even if someone gets the database, they cannot recover the actual passwords.
- **Where in code:** `core/security.py` – `CryptContext(schemes=["pbkdf2_sha256"], ...)`, `hash_password()`, `verify_password()`.

### 5.5 Token (authentication) algorithm

- **What is used:** **JWT (JSON Web Token)** with **HS256** (HMAC-SHA256) for signing.
- **What it does:** After a successful login, the backend creates a token that encodes the user’s identity (e.g. username/email) and role. The frontend sends this token with every API request. The backend verifies the token and knows who is making the request without storing sessions on the server.
- **How it works (simple idea):** The token has three parts (header, payload, signature). The payload contains claims like `sub` (subject = username/email) and `role`. The signature is computed with HS256 using a secret key; the backend verifies it with the same key. If the signature is valid and the token is not expired, the user is considered authenticated.
- **Where in code:** `core/security.py` – `jwt.encode(..., algorithm=settings.JWT_ALGORITHM)` (JWT_ALGORITHM is `"HS256"`); `api/deps.py` – `jwt.decode()` to validate the token and load the current user.

### 5.6 Summary table of algorithms

| Area              | Algorithm / method        | Purpose                                      |
|-------------------|---------------------------|----------------------------------------------|
| Face detection    | OpenCV face detector      | Find face regions in image                  |
| Face recognition  | VGG-Face (CNN)            | Convert face image → embedding vector       |
| Matching          | Cosine similarity (L2 + dot product) | Compare embeddings, find best match  |
| Password storage  | PBKDF2-SHA256             | Hash passwords safely                        |
| Authentication    | JWT with HS256            | Stateless login and API auth                 |

---

## 6. LIBRARIES USED IN THE PROJECT

A **library** is pre-written code that you use in your project so you don’t have to implement everything from scratch. Below is a detailed list of every library used in the MultiFace Recognition App, with counts and short descriptions.

### 6.1 Backend libraries (Python)

The backend uses **14 direct dependencies** listed in `backend/requirements.txt`. Each line is one library (or a group like `uvicorn[standard]`).

| # | Library            | Version (min) | Purpose |
|---|--------------------|---------------|--------|
| 1 | **fastapi**        | 0.104.0      | Web framework: defines API routes, request/response, validation, OpenAPI docs. |
| 2 | **uvicorn**        | 0.24.0       | ASGI server: runs the FastAPI app and handles HTTP requests. The `[standard]` extra adds performance and compatibility. |
| 3 | **python-multipart**| 0.0.6        | Parses multipart form data (e.g. file uploads for training and recognize). |
| 4 | **sqlalchemy**     | 2.0.0        | ORM (Object-Relational Mapping): defines database models (Person, Attendance, etc.) and runs queries without writing raw SQL. |
| 5 | **pymysql**        | 1.0.2        | MySQL driver: connects Python to the MySQL database server. |
| 6 | **cryptography**   | 41.0.0       | Used by PyMySQL (and python-jose) for secure connections and crypto operations. |
| 7 | **pydantic-settings** | 2.1.0     | Loads configuration from environment variables and `.env` (used in `config.py`). |
| 8 | **pydantic**       | 2.5.0        | Data validation and settings; FastAPI uses it for request/response models. |
| 9 | **python-jose**    | 3.3.0        | Creates and decodes JWT tokens (with `[cryptography]` for security). |
|10 | **passlib**        | 1.7.4        | Password hashing and verification (PBKDF2-SHA256). The `[bcrypt]` extra is optional; this project uses pbkdf2_sha256. |
|11 | **deepface**       | 0.0.79       | Face detection and face recognition: wraps VGG-Face and other models, and the OpenCV detector. |
|12 | **tf-keras**       | 2.15.0       | TensorFlow/Keras: required by DeepFace to run the VGG-Face neural network. |
|13 | **opencv-python**  | 4.8.0        | OpenCV: camera capture (`cv2.VideoCapture`), image read/write, and used by DeepFace as the face detector backend. |
|14 | **numpy**          | 1.24.0       | Numerical arrays and math (e.g. embeddings, dot product, normalization). |
|15 | **Pillow**         | 10.0.0       | Image handling; may be used by DeepFace or image processing in the stack. |
|16 | **python-dotenv**  | 1.0.0        | Loads `.env` file into environment variables (used with pydantic-settings). |

**Total: 16 backend libraries** (all from `requirements.txt`; some packages pull in additional transitive dependencies such as TensorFlow, which are not listed here but are installed automatically).

### 6.2 Frontend libraries (JavaScript/TypeScript)

The frontend has **dependencies** (used at run time) and **devDependencies** (used only during build and development).

**Dependencies (4 libraries):**

| # | Library             | Version  | Purpose |
|---|---------------------|----------|--------|
| 1 | **react**           | ^18.2.0  | UI library: components, state, and rendering. |
| 2 | **react-dom**       | ^18.2.0  | Renders React components into the browser DOM. |
| 3 | **react-router-dom**| ^6.22.3  | Routing: URLs like `/login`, `/monitoring`, `/attendance`, and protected routes. |
| 4 | **axios**           | ^1.7.2   | HTTP client: sends GET/POST etc. to the backend API and receives JSON (or files). |

**DevDependencies (5 libraries):**

| # | Library              | Version  | Purpose |
|---|----------------------|----------|--------|
| 1 | **vite**             | ^5.1.6   | Build tool: dev server, bundling, and production build. |
| 2 | **typescript**       | ^5.4.2   | TypeScript compiler: type checking and compiling TS to JS. |
| 3 | **@vitejs/plugin-react** | ^4.2.1 | Vite plugin to compile React (JSX) and enable fast refresh. |
| 4 | **@types/react**     | ^18.2.48 | TypeScript type definitions for React. |
| 5 | **@types/react-dom** | ^18.2.18 | TypeScript type definitions for React DOM. |

**Total: 4 dependencies + 5 devDependencies = 9 frontend libraries** in `package.json`.

### 6.3 Total library count

- **Backend:** 16 libraries (from `requirements.txt`).  
- **Frontend:** 9 libraries (4 runtime + 5 dev).  
- **Overall project:** **25 distinct libraries** (backend + frontend; not counting transitive dependencies like TensorFlow, which are installed automatically by pip/npm).

### 6.4 Where each part of the app uses libraries

- **Face detection & recognition:** DeepFace, OpenCV, TensorFlow/Keras (via DeepFace), NumPy.  
- **Database:** SQLAlchemy, PyMySQL, Cryptography.  
- **API & server:** FastAPI, Uvicorn, Pydantic, python-multipart.  
- **Auth:** python-jose (JWT), Passlib (password hashing).  
- **Config:** pydantic-settings, python-dotenv.  
- **Frontend UI & API calls:** React, React DOM, React Router, Axios; build and types: Vite, TypeScript, Vite React plugin, React type definitions.

---

## 7. FACE DETECTION & RECOGNITION PIPELINE

Step-by-step in simple terms:

1. **Camera captures a frame**  
   - OpenCV `cv2.VideoCapture(camera_id).read()` returns one image (frame) as a numpy array (height × width × 3, BGR).

2. **Face detection**  
   - The frame (or a resized version for speed) is passed to DeepFace. With `enforce_detection=False`, DeepFace uses its detector (here OpenCV) to find all face regions. Each region is given as a bounding box (e.g. x, y, w, h).

3. **Multiple faces**  
   - DeepFace's `represent()` returns a list of objects: one per detected face. So one frame → list of faces.

4. **Face embeddings**  
   - For each face, DeepFace runs the VGG-Face model and returns an **embedding** (a vector of numbers). This vector is a "fingerprint" of that face. Same person in different photos should get similar vectors.

5. **Storing embeddings**  
   - When you "train" a person, you upload 2–5 images. The backend gets one embedding per image, averages them, L2-normalizes, then stores the result in the `Person.embedding` column (as binary/pickle) in the database. So each person has one stored embedding.

6. **Matching**  
   - For a new face embedding from the camera, the backend loads all persons' embeddings from the DB, L2-normalizes them, then compares the new embedding to each stored one.

7. **Similarity metric**  
   - **Cosine similarity** is used: `np.dot(known_embeddings, face_embedding)`. Because vectors are L2-normalized, this dot product is the cosine of the angle between them. Higher value = more similar. The code takes the **maximum** similarity and the corresponding person.

8. **Threshold**  
   - `RECOGNITION_THRESHOLD` (default 0.4 in config). If `max_sim > threshold`, the face is considered "recognized" as that person. So 0.4 is a balance: lower = stricter (fewer false positives, might miss some), higher = looser (more false positives). It's configurable in Settings.

9. **Avoiding duplicate attendance**  
   - **Per person per day:** The backend checks if there is already an `Attendance` row for that `person_id` and today's date. If yes, it updates that row (e.g. check_out_time, total_detections) instead of creating a new one. So at most one attendance "record" per person per day.  
   - **Cooldown:** In live monitoring, a **recognition cooldown** (e.g. 30 seconds) per person means that after the system records attendance for "John," it won't create another record for John for 30 seconds even if he appears in every frame. So you get one "first seen" and then updates (check_out, detections) without flooding the DB.

10. **Real-time processing**  
    - The camera loop runs in a **background thread**. It doesn't run recognition on every frame; it uses a **stride** (e.g. every 2nd frame) to reduce CPU load. So: capture every frame, but run heavy face detection + encoding only every N frames. The rest of the time it can reuse the last recognition results for drawing. The frontend gets the "latest" result by polling the preview endpoint every 1.5 seconds.

---

## 8. DATABASE EXPLANATION

### Tables (from the models)

- **persons**  
  - id, name (unique), email (unique, optional), department, person_code (unique, optional), person_type (student/staff), **embedding** (binary: stored face embedding), created_at, is_active.  
  - One row per person who can be recognized; the embedding is used for matching.

- **attendance**  
  - id, person_id (FK to persons), date, check_in_time, check_out_time, confidence, image_path, total_detections, duration_minutes.  
  - One row per person per day (first detection creates it, later detections update check_out and total_detections).

- **attendance_sessions**  
  - id, person_id, session_start, session_end, confidence, image_count, status (e.g. active/completed).  
  - More granular "sessions" for the same person; used by the webcam service to track continuous presence.

- **daily_attendance_summary**  
  - id, date, total_persons_present, total_persons_expected, attendance_rate, first_check_in, last_check_out.  
  - Can be used for quick daily stats (the app also computes summary on the fly in the API).

- **admin_users**  
  - id, username, password_hash, created_at, is_active.  
  - For admin login (JWT).

- **app_users**  
  - id, full_name, email, password_hash, role (staff/student), department, note, created_at, is_active.  
  - For staff/student login and role-based access.

### Relationships

- **Person** has many **Attendance** (person_id → persons.id).  
- **Person** has many **AttendanceSession** (person_id → persons.id).  
- No direct FK from users to persons; they are separate (users log in to the app, persons are the ones whose faces are trained and whose attendance is recorded).

### How student/person data is stored

- In **persons**: name, email, department, person_code, person_type, and the **embedding** (serialized numpy array). Training replaces or sets this embedding.

### How attendance is stored

- In **attendance**: one row per (person_id, date); check_in_time is the first detection time that day; check_out_time and total_detections are updated on later detections; confidence and optional image_path are stored.

### How duplicate attendance is prevented

- **Same day:** Before inserting, the code checks for an existing row with same `person_id` and `date`. If found, it updates that row instead of inserting. So at most one row per person per day.  
- **Spam in one session:** The 30-second cooldown in `WebcamService` prevents recording a new "attendance event" for the same person within 30 seconds; only the first in that window triggers a DB update (or the first of the day creates the row, subsequent ones update it).

---

## 9. BACKEND EXPLANATION

### API endpoints (summary)

- **Auth:**  
  - `POST /api/auth/login` – body: username, password → returns JWT and role.  
  - `POST /api/auth/register` – body: full_name, email, password, role (staff|student), optional department, note → creates AppUser.  
  - `GET /api/auth/me` – returns current user info (needs Bearer token).

- **Settings (admin):**  
  - `GET /api/settings/recognition` – get threshold, stride, width.  
  - `PUT /api/settings/recognition` – update them (and sync webcam_service stride).

- **Persons (admin):**  
  - `POST /api/persons` – create person (name, email, department, person_code, person_type).  
  - `GET /api/persons` – list all (optional ?person_type=).  
  - `PATCH /api/persons/{id}` – update person.  
  - `DELETE /api/persons/{id}` – delete person and their attendance/sessions.

- **Train:**  
  - `POST /api/train/` – form: person_id, name, person_type, optional email/department/person_code, **files** (images). Backend encodes each image's face, averages embeddings, L2-normalizes, then saves/updates that person's embedding in DB.

- **Recognize (single image):**  
  - `POST /api/recognize/` – upload one image file. Backend detects all faces, encodes them, compares to DB, draws boxes and labels on image, saves image, returns the image (and headers with counts).

- **Attendance (any authenticated user with permission):**  
  - `GET /api/attendance` – query params: start_date, end_date, person_id, person_type. Returns list of attendance records (joined with person name/type).  
  - `GET /api/attendance/summary` – query param: target_date. Returns total_people, present, attendance_rate for that date.

- **Webcam:**  
  - `POST /api/webcam/start/` – start camera and background monitoring (params: camera_id, save_images).  
  - `POST /api/webcam/stop/` – stop monitoring.  
  - `GET /api/webcam/status/` – monitoring_active, camera_initialized, attendance_summary.  
  - `GET /api/webcam/preview/` – latest frame as base64 + recognition_results.  
  - `GET /api/webcam/capture/` – capture one frame, run recognition, save attendance if any, return frame + results.  
  - `GET /api/webcam/attendance/` – list in-memory attendance records from current session.  
  - `GET /api/webcam/summary/` – detailed summary.  
  - `POST /api/webcam/export/` – export attendance to JSON file.  
  - `DELETE /api/webcam/attendance/` – clear in-memory records (DB records stay).

- **Health:**  
  - `GET /api/health/` – status, face_encoder_initialized.

### Request/response format

- Login/register: JSON body; response JSON with token or message.  
- Persons: JSON body for create/update; list returns `{ count, persons: [...] }`.  
- Train: multipart form (person_id, name, files, ...); response JSON with message, person_id, name, faces_processed.  
- Recognize: multipart file upload; response is image/jpeg with optional headers.  
- Attendance: GET with query params; response `{ count, records: [...] }`.  
- Webcam preview/capture: response JSON with `frame_base64`, `recognition_results`, etc.

### How backend talks to the database

- **Session:** Each request that needs DB gets a session via `Depends(get_db)`. `get_db()` yields a SQLAlchemy session and closes it after the request.  
- **Queries:** Code uses `db.query(Model).filter(...).all()` or `.first()`, then `db.add()`, `db.commit()`, `db.refresh()` as needed.  
- **Recognition results saved:** In webcam flow, `WebcamService.record_attendance()` is called when a face is recognized and cooldown allows; it creates or updates `Attendance` and `AttendanceSession` and calls `db.commit()`.

---

## 10. FRONTEND EXPLANATION

### Pages

- **Login** – Form: username (email for non-admin), password. Calls login API, stores token and role, redirects to "/".  
- **Dashboard** – Shows welcome, "Total People," "Present Today," "Attendance Rate," latest attendance table, quick links (Monitoring, Attendance, People, Settings) based on role.  
- **Live Monitoring** – Start/Stop buttons for webcam; status indicator; preview image (from polling `/api/webcam/preview/`); table of "latest detections" (name, recognized/unknown).  
- **People** – List of persons (students/staff) with filter; form to add/edit person and upload 2–5 face images to train; calls create/update person and train API.  
- **Attendance** – Filters (start date, end date, person type); table of attendance records (name, type, date, check-in, check-out, confidence); data from `GET /api/attendance`.  
- **Settings** – (Admin) Recognition settings: threshold, stride, width; calls get/update settings API.  
- **Access Denied** – Shown when the user's role is not allowed for the current route.

### How frontend connects to backend

- **Base URL:** From `localStorage` key `attendance_api_base` or env `VITE_API_BASE_URL` or default `http://localhost:8000/api` (see `http.ts`).  
- **Auth:** After login, token is stored; `http.ts` interceptor adds `Authorization: Bearer <token>` to every request.  
- **Calls:** Each page or component uses the `api/*` functions (e.g. `fetchAttendance()`, `startMonitoring()`) which use the `http` Axios instance, so all requests go to the backend and responses are JSON (or file).

### How attendance is displayed

- **Dashboard:** Fetches `fetchAttendanceSummary()` and `fetchAttendance()` and shows summary (total, present, rate) and a table of latest 5 records.  
- **Attendance page:** Fetches `fetchAttendance({ start_date, end_date, person_type })` and renders a table of records (name, type, date, check-in, check-out, confidence).  
- **Live Monitoring:** Shows "latest detections" from the preview response (recognition_results); "Attendance marked" is shown when `recognized === true`.

---

## 11. PROGRAM FLOW (STEP BY STEP)

1. **System starts** – Backend runs `init_database()` (DB + tables + default admin), FastAPI app is ready. Frontend dev server serves the React app.  
2. **User opens app** – Not logged in → redirect to Login.  
3. **User logs in** – Frontend sends credentials to `POST /api/auth/login`; backend checks AdminUser or AppUser, returns JWT; frontend stores token and role.  
4. **User goes to Live Monitoring and clicks Start** – Frontend calls `POST /api/webcam/start/`. Backend opens camera, starts a thread that runs the monitoring loop.  
5. **Camera activates** – `cv2.VideoCapture(0)` opens; loop runs.  
6. **Frame captured** – `camera.read()` gives one frame (numpy array).  
7. **Multiple faces detected** – Every N frames, frame is resized (optional), then `encoder.detect_and_encode_faces(frame)` runs; DeepFace returns list of (embedding, bbox) per face.  
8. **Embeddings generated** – Each face's embedding is L2-normalized.  
9. **Compared with stored embeddings** – Known embeddings loaded from DB (Person table); cosine similarity between each detected embedding and all known; for each face, take argmax and max similarity.  
10. **Identity matched** – If max_sim > threshold, that face is "recognized" as the corresponding person.  
11. **Attendance marked** – If cooldown allows, `record_attendance()` is called: find or create Attendance row for that person_id and today, update check_out_time and total_detections; optionally create/update AttendanceSession; commit.  
12. **Data saved to database** – Attendance and AttendanceSession tables updated in the same request/session.  
13. **Dashboard updated** – Frontend polls preview and/or user opens Dashboard or Attendance page; those pages call `GET /api/attendance` and `GET /api/attendance/summary` and re-render with new data.

---

## 12. IMPORTANT CODE

### Backend "brain" of recognition: `app/services/face_encoder.py`

- **FaceEncoder**  
  - Uses DeepFace with **VGG-Face** and **OpenCV** detector.  
  - **l2_normalize(x):** `x / np.linalg.norm(x)` so that cosine similarity is just the dot product.  
  - **encode_image(file_bytes):** Writes bytes to a temp file, calls `DeepFace.represent(..., enforce_detection=True)`, returns normalized embedding of the first face or None.  
  - **detect_and_encode_faces(img):** Same but `enforce_detection=False`; returns list of (normalized_embedding, bbox (x1,y1,x2,y2)) for every face.  
  - **preload_model():** Runs DeepFace on a dummy image so the model is downloaded/loaded once at startup.

### Where recognition and attendance meet: `app/services/webcam_service.py`

- **get_known_faces(db):** Loads all Person rows, unpickles embeddings, L2-normalizes, returns arrays of embeddings, names, ids.  
- **recognize_faces_in_frame(frame, known_embeddings, known_names, known_ids, db):** Resizes frame, calls `encoder.detect_and_encode_faces()`, for each face computes `cos_sim = np.dot(known_embeddings, face_embedding)`, finds argmax and max_sim; if max_sim > threshold, checks cooldown; if OK, creates AttendanceRecord, appends to list, calls `record_attendance(db, record)`, updates cooldown. Returns list of dicts (name, person_id, confidence, bbox, recognized).  
- **record_attendance(db, record):** Ensures one Attendance row per (person_id, date): if none exists, create with check_in and check_out = record.timestamp; else update check_out, total_detections, duration_minutes, confidence, image_path. Also creates/updates AttendanceSession. Then `db.commit()`.  
- **start_monitoring(db, save_images, ...):** Loop: read frame, every `recognition_stride` frames call `recognize_faces_in_frame`, draw results, optionally save image and update attendance image path; set `current_frame` and `current_annotated_frame` so preview endpoint can return them.

### Main API: `app/api/routes.py` and `app/api/webcam.py`

- **routes.py:** Defines login, register, persons CRUD, train, recognize, attendance list/summary, health. Train uses `encoder.encode_image()` per file, averages and normalizes, then saves to Person. Recognize loads known embeddings, calls `encoder.detect_and_encode_faces(img)`, then same cosine similarity and threshold logic, draws on image, returns image.  
- **webcam.py:** Start/stop use WebcamService (camera + background thread); preview returns current_annotated_frame (or current_frame) as base64 and recognition_results; capture runs one frame through recognize_faces_in_frame and returns results + image.

So the **brain** of the system is the **FaceEncoder** (face → embedding) plus the **WebcamService** (camera loop + matching + cooldown + DB attendance). The **entry** to the app is **main.py** (backend) and **main.tsx** (frontend).

---

## 13. RUNNING & DEPLOYMENT

### Install dependencies

- **Backend:**  
  `cd backend`  
  `python -m venv venv`  
  `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)  
  `pip install -r requirements.txt`  

- **Frontend:**  
  `cd frontend`  
  `npm install`  

### Configure database

- Create a MySQL server.  
- Copy `backend/.env.example` to `backend/.env`.  
- Set `DATABASE_URL`, e.g. `mysql+pymysql://user:password@host:3306/database_name`.  
- On first backend run, `init_database()` will create the database (if missing) and all tables.

### Run backend

- From backend folder (with venv active):  
  `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`  
  Or: `python -m app.main`  
- API: `http://localhost:8000`, docs: `http://localhost:8000/docs`.

### Run frontend

- From frontend folder:  
  `npm run dev`  
- Open the URL Vite prints (e.g. `http://localhost:5173`). Set API base in Settings if backend is not at `http://localhost:8000/api`.

### Deploy to cloud (high level)

- **Backend:** Run FastAPI on a cloud VM or container (e.g. Gunicorn/Uvicorn behind Nginx). Use a cloud MySQL instance or managed DB; set `DATABASE_URL` and `SECRET_KEY` in environment.  
- **Frontend:** Run `npm run build`, then serve the `dist/` folder with a static server or CDN; set `VITE_API_BASE_URL` to your backend's public API URL.  
- **Camera:** For live monitoring, the backend must have access to a camera (e.g. USB on the server or a camera service the server can call). For "upload image only" (recognize), no camera is needed in production.

---

This guide covers the whole MultiFace Recognition App from concept to code and deployment. If you want to change behavior, start from the section that matches what you want (e.g. "avoid duplicate attendance" → Section 8 and 7; "change recognition sensitivity" → config and Section 7 threshold; "add a new API" → Section 9 and routes/webcam code).
