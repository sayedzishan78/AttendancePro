# Backend — Full Explanation (Simple Language)

This document explains **every part** of the backend in depth, in simple and easy-to-understand language. Read it section by section.

---

## 1. What Is the Backend?

The **backend** is the **server side** of the Multiface Recognition app. It:

- Receives HTTP requests from the **frontend** (React app in the browser).
- Does the **business logic**: login, face training, face recognition, attendance, webcam.
- Talks to the **MySQL database** to store and read data.
- Uses **DeepFace** and **OpenCV** for face detection and encoding.
- Sends back **JSON** or **files** (e.g. image) as the response.

So: **Frontend → Backend (FastAPI) → Database + Face recognition**. The backend is written in **Python** using **FastAPI**.

---

## 2. Backend Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              ← Entry point: creates the app, CORS, includes routes
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py        ← All main API routes (auth, persons, train, recognize, attendance, settings, health)
│   │   ├── webcam.py        ← Webcam-specific routes (start, stop, preview, capture, etc.)
│   │   └── deps.py          ← Auth dependencies (who is logged in, admin vs staff vs student)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        ← Settings from .env (database URL, secret key, threshold, etc.)
│   │   ├── database.py      ← MySQL connection, session, create tables, default admin
│   │   └── security.py      ← Password hashing and JWT creation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── attendance.py    ← Person, Attendance, AttendanceSession, DailyAttendanceSummary
│   │   └── user.py          ← AdminUser, AppUser
│   └── services/
│       ├── __init__.py
│       ├── face_encoder.py  ← DeepFace: encode one face, detect and encode many faces
│       └── webcam_service.py ← Camera loop, recognition per frame, attendance recording
├── outputs/                 ← Saved images (recognized faces, attendance photos)
├── .env                     ← Your config (create from .env.example)
├── .env.example
├── requirements.txt
└── README.md
```

- **main.py** = start here; it builds the app and mounts the API.
- **api/** = all HTTP endpoints and auth checks.
- **core/** = config, database, security (no business logic, just infrastructure).
- **models/** = database tables (Python classes that map to MySQL tables).
- **services/** = face encoding and webcam logic (used by the API).

---

## 3. main.py — How the App Starts

**What it does:**

1. **Imports** the FastAPI app, config, database, and the main router.
2. **Calls `init_database()`** so that when the server starts, the database and tables are created (if they don’t exist) and the default admin user is created (if missing).
3. **Creates the FastAPI app** with a title, version, description, and turns on **Swagger** (`/docs`) and **ReDoc** (`/redoc`) for API documentation.
4. **Adds CORS middleware** so the React frontend (running on another port, e.g. 5173) can call this backend (e.g. 8000) without the browser blocking requests. `allow_origins=["*"]` means any origin is allowed (in production you would restrict this).
5. **Includes the router** from `routes.py` with prefix **`/api`**, so all routes live under `http://localhost:8000/api/...`.
6. Defines a **root route** `GET /` that returns a welcome message and links to docs and health.
7. When you run the file with `python -m app.main` or `uvicorn app.main:app`, it runs **uvicorn** with host and port from config.

**In short:** main.py = create app → init DB → add CORS → mount all API routes under `/api` → run server.

---

## 4. core/config.py — All Settings in One Place

**What it does:**

All **configuration** is in a single `Settings` class. It uses **Pydantic** and reads from **environment variables** and from a **.env** file (so you don’t hardcode secrets).

**Meaning of each setting:**

- **APP_NAME, APP_VERSION** — Name and version of the API (used in docs and root response).
- **DEBUG** — If True, SQLAlchemy can log SQL queries; useful during development.
- **DATABASE_URL** — MySQL connection string, e.g. `mysql+pymysql://user:password@host:port/database_name`. The backend uses this to connect to MySQL.
- **HOST, PORT** — Where the server listens (e.g. `0.0.0.0` and `8000`).
- **SECRET_KEY** — Used to **sign** JWT tokens. Anyone with this key can create valid tokens, so in production it must be a long random string and kept secret.
- **ACCESS_TOKEN_EXPIRE_MINUTES** — How long a login token is valid (e.g. 12 hours = 720 minutes).
- **JWT_ALGORITHM** — Algorithm used to sign the token (e.g. HS256).
- **ADMIN_USERNAME, ADMIN_PASSWORD** — Used to create the **default admin** user when the database is first set up (only if no admin exists yet).
- **RECOGNITION_THRESHOLD** — Minimum cosine similarity (e.g. 0.4) to consider a face “recognized”. Lower = stricter, higher = looser.
- **DETECTION_SIZE** — Not used in the current code path but could be used for image size in detection.
- **LIVE_RECOGNITION_STRIDE** — In webcam mode, run face recognition every **Nth** frame (e.g. 2 = every 2nd frame) to reduce CPU load.
- **LIVE_RECOGNITION_WIDTH** — Resize the webcam frame to this width (e.g. 480) before running recognition, again to save CPU.
- **OUTPUT_DIR** — Folder name where we save images (e.g. recognized images, attendance photos). It lives under the project (e.g. `backend/outputs`).
- **MAX_FILE_SIZE_MB** — Maximum allowed size (in MB) for an uploaded image; bigger files are rejected.
- **BASE_DIR** — Project root path. **output_path** is a property that returns `BASE_DIR / OUTPUT_DIR` and creates that folder if it doesn’t exist.

**In short:** config = one place for all env-based settings; the rest of the app imports `settings` from here.

---

## 5. core/database.py — Connection and Tables

**What it does:**

- **Engine** — SQLAlchemy’s `create_engine` uses `DATABASE_URL` to know how to connect to MySQL. `pool_pre_ping=True` means we check that the connection is still valid before use. `pool_recycle=3600` recycles connections every hour so they don’t go stale. `echo=settings.DEBUG` prints SQL in debug mode.
- **SessionLocal** — A **session factory**: each time we call `SessionLocal()` we get a new **database session** (like a “conversation” with the DB). We use it to run queries and commits. We don’t use the engine directly for queries; we use sessions.
- **Base** — Declarative base for all **models**. Every table (Person, Attendance, etc.) is a class that **inherits** from `Base` and defines columns. SQLAlchemy then knows how to create tables and run queries from these classes.

**get_db():**  
This is a **dependency** used by FastAPI. It:

1. Creates a new session with `SessionLocal()`.
2. **Yields** it to the route function so the route can use `db` to query and commit.
3. In a `finally` block it **closes** the session when the request is done. So every request gets a fresh session and we never forget to close it.

**init_database():**  
Called once at startup (from main.py). It:

1. Imports the **models** (attendance, user) so that their tables are **registered** with `Base.metadata`.
2. Parses `DATABASE_URL` to get the database name.
3. If the driver is MySQL, it connects **without** selecting a database and runs `CREATE DATABASE IF NOT EXISTS <name>` so the database exists.
4. Calls **`Base.metadata.create_all(bind=engine)`** so all tables (persons, attendance, attendance_sessions, admin_users, app_users, daily_attendance_summary) are created if they don’t exist.
5. Opens a session, checks if an **admin user** with `ADMIN_USERNAME` exists; if not, it creates one with `hash_password(ADMIN_PASSWORD)` and saves it. So on first run you get a default admin (e.g. admin / admin123).

**In short:** database.py = create engine and session factory, define how to get a DB session per request, and create DB + tables + default admin on startup.

---

## 6. core/security.py — Passwords and JWT

**What it does:**

- **pwd_context** — Passlib’s `CryptContext` with scheme **pbkdf2_sha256**. It hashes passwords in a safe way (with salt and many iterations).

**hash_password(plain_password):**  
Takes the plain-text password, hashes it, and returns the hash string. We **store only this hash** in the database, never the real password.

**verify_password(plain_password, hashed_password):**  
Hashes the plain password and compares it with the stored hash. Returns True if they match (so the login password is correct).

**create_access_token(subject, role, expires_minutes):**  
Creates a **JWT**:

- **subject** — Who the user is (e.g. admin username or user email).
- **role** — admin, staff, or student.
- **expires_minutes** — Token validity (default from config).
- Encodes a dict like `{"sub": subject, "exp": expiry_time, "role": role}` and **signs** it with `SECRET_KEY` and the chosen algorithm. The frontend gets this string and sends it back in the `Authorization: Bearer <token>` header. The backend can then decode and verify the token to know who is calling.

**In short:** security.py = hash/verify passwords and create signed JWT tokens for login.

---

## 7. api/deps.py — Who Is Logged In and What Role They Have

**What it does:**

These are **FastAPI dependencies**. A dependency runs **before** the route function and can return a value (e.g. the current user) or **raise an exception** (e.g. 401 Unauthorized, 403 Forbidden).

**HTTPBearer()** — Expects the client to send a header: `Authorization: Bearer <token>`.

**get_current_user(credentials, db):**

1. Takes the **token** from the Bearer credentials.
2. **Decodes** the JWT with `SECRET_KEY` and the configured algorithm. If the token is invalid or expired, `jwt.decode` raises and we return **401 Unauthorized**.
3. Reads **subject** (username or email) and **role** from the token.
4. If role is **admin**, looks up the user in **admin_users** by username. If role is staff/student, looks up in **app_users** by email. User must be **is_active**.
5. If no user is found, returns 401. Otherwise returns a dict: `{"role": role, "user": user}`. So every protected route that uses this dependency gets the **current user** and **role**.

**get_current_admin(current):**  
Uses `get_current_user`. If `current["role"] != "admin"` it raises **403 Forbidden**. Otherwise returns `current["user"]`. So only **admin** can access routes that depend on this.

**get_current_staff_or_admin(current):**  
Same idea: if role is not **admin** or **staff**, returns 403. So **staff** and **admin** can access these routes (e.g. webcam, attendance).

**get_current_any_user(current):**  
If role is not admin, staff, or student, returns 403. So any **logged-in** user (any role) can access (e.g. /auth/me, /attendance list).

**In short:** deps.py = read JWT → get user from DB → enforce role (admin only, staff or admin, or any logged-in user).

---

## 8. models/attendance.py — Person and Attendance Tables

**What it does:**

Each class is a **SQLAlchemy model**: it defines a **table** and its **columns**. The table name is set with `__tablename__`.

**Person:**

- **persons** table. Stores everyone we can recognize.
- **id** — Primary key.
- **name** — Full name, unique.
- **email** — Optional, unique.
- **department** — Optional (e.g. CS, HR).
- **person_code** — Optional, unique (e.g. student ID, employee ID).
- **person_type** — "student" or "staff".
- **embedding** — **LargeBinary**: the face embedding (vector) stored as bytes (we pickle the numpy array and save it here). This is the “face data” we use for recognition.
- **created_at** — When the row was created.
- **is_active** — Can be used to soft-delete.
- **attendance_records** — Relationship: one Person has many Attendance rows. So we can do `person.attendance_records` in code.

**Attendance:**

- **attendance** table. One row = one person’s attendance for **one day**.
- **person_id** — Foreign key to persons.id.
- **date** — The calendar date.
- **check_in_time** — First time we saw them that day.
- **check_out_time** — Last time we saw them (updated on each new detection).
- **confidence** — Recognition confidence (e.g. similarity score).
- **image_path** — Optional path to a saved proof image.
- **total_detections** — How many times they were detected that day.
- **duration_minutes** — Time between first and last detection.
- **person** — Relationship back to Person.

So we have **one row per person per day**; we update the same row when we see them again (check_out, total_detections, duration).

**AttendanceSession:**

- **attendance_sessions** table. Used during **continuous webcam** monitoring to track a “session” (start/end, how many images, status).
- **person_id**, **session_start**, **session_end**, **confidence**, **image_count**, **status** (e.g. active, completed). Helps with detailed session reporting.

**DailyAttendanceSummary:**

- **daily_attendance_summary** table. Can store per-day summary (total present, expected, rate, first check-in, last check-out). Defined in the model; you can use it later for reporting.

**In short:** attendance.py = define Person (with face embedding), Attendance (one per person per day), AttendanceSession (for webcam sessions), and optional daily summary.

---

## 9. models/user.py — Who Can Log In

**AdminUser:**

- **admin_users** table. For **admin** login only.
- **username** — Unique. Admin logs in with username + password.
- **password_hash** — Hashed password (from security.hash_password).
- **is_active** — Can disable an admin without deleting.

**AppUser:**

- **app_users** table. For **staff** and **student** login.
- **full_name**, **email** (unique), **password_hash**, **role** ("staff" or "student"), **department**, **note**, **is_active**. They log in with **email** and password. The JWT’s subject is the email; the role is stored in the token and checked in deps.

**In short:** user.py = two separate tables for admin (username) vs staff/student (email), both with hashed passwords.

---

## 10. services/face_encoder.py — Face Detection and Embedding

**What it does:**

This service uses **DeepFace** to turn a face image into a **vector (embedding)** and to **detect all faces** in an image. We don’t store raw images for recognition; we store and compare these vectors.

**FaceEncoder class:**

- **__init__:** Sets `model_name = "VGG-Face"` (the DeepFace model we use). Does not load the model yet; DeepFace will load or download it on first use.
- **l2_normalize(x):** Takes a vector, divides by its length (L2 norm), so the length becomes 1. After this, **dot product = cosine similarity**, which we use to compare two faces.
- **preload_model():** Optional. Creates a dummy image, runs DeepFace.represent on it so the model is downloaded/loaded once at startup. Avoids a long delay on the first real request.
- **encode_image(file_bytes):**  
  - Saves the bytes to a **temporary file** (DeepFace expects a file path).  
  - Calls **DeepFace.represent** with that path, model VGG-Face, **enforce_detection=True** (so it fails if no face is found), and detector_backend **opencv**.  
  - Gets back a list of face results; each has an **embedding** (list of numbers). We take the first face’s embedding, convert to numpy array, **L2-normalize**, and return it. If no face, returns None.  
  - Deletes the temp file.  
  Used during **training**: one face per image → one embedding per image.
- **detect_and_encode_faces(img):**  
  - **img** is an OpenCV image (numpy array, BGR).  
  - Writes it to a temp file and calls **DeepFace.represent** with **enforce_detection=False** (so it doesn’t fail if there are no faces).  
  - For **each** detected face we get an embedding and the face region (**facial_area**: x, y, w, h). We convert that to (x1, y1, x2, y2) and return a list of **(embedding, bbox)**.  
  Used during **recognition** and **webcam**: one image → many faces → many (embedding, bbox) pairs.

**In short:** face_encoder.py = use DeepFace to get one embedding from one image (training) or many (embedding, bbox) from one image (recognition), and L2-normalize for consistent comparison.

---

## 11. api/routes.py — Main API Endpoints

All routes are under **/api** because of the prefix in main.py.

**Pydantic models (request bodies):**

- **LoginPayload** — username, password.
- **RegisterPayload** — full_name, email, password, role (staff|student), optional department, note.
- **PersonCreate** — name, optional email, department, person_code, person_type (student|staff).
- **PersonUpdate** — same fields, all optional (for PATCH).
- **RecognitionSettings** — recognition_threshold, live_recognition_stride, live_recognition_width (with min/max checks).

**Auth (no token required):**

- **POST /auth/login** — Receives username (or email) and password. Looks up **AdminUser** by username; if found and password matches, returns JWT with role "admin". Else looks up **AppUser** by email; if found and password matches, returns JWT with that user’s role. Else 401.
- **POST /auth/register** — Creates a new **AppUser** (staff or student). Checks email not already used. Hashes password, saves user, returns id and role.

**Auth (token required):**

- **GET /auth/me** — Uses `get_current_any_user`. Returns current user info (username or email, full_name, role, is_active) depending on admin vs app user.

**Settings (admin only):**

- **GET /settings/recognition** — Returns current threshold, stride, width from config.
- **PUT /settings/recognition** — Updates those values in config and updates the webcam service’s stride so the running loop uses the new value.

**Persons (admin only):**

- **POST /persons** — Creates a **Person** with name, email, department, person_code, person_type. Embedding is empty at first (filled when we train). Checks name/email/person_code uniqueness.
- **GET /persons** — Lists all persons; optional query param **person_type** to filter. Returns id, name, email, department, person_code, person_type (no embedding).
- **PATCH /persons/{person_id}** — Updates only the fields sent in the body. Same uniqueness checks for name, email, person_code.
- **DELETE /persons/{person_id}** — Deletes attendance_sessions and attendance for that person, then deletes the person.

**Training (admin only):**

- **POST /train/** — **Form data**: person_id, name, person_type, optional email, department, person_code, and **files** (multiple image files). For each file: check size, call **encoder.encode_image(contents)** to get one embedding per face (skips if no face). Collects all embeddings, **averages** them, **L2-normalizes**, then **pickles** and stores in **persons.embedding** (creates or updates the person). So after training, that person has one “average face” vector.

**Recognition (admin only):**

- **POST /recognize/** — One **file** (image). Reads bytes, decodes with OpenCV. Loads all persons from DB, unpickles their embeddings, L2-normalizes. Calls **encoder.detect_and_encode_faces(img)** to get all (embedding, bbox) in the image. For each face: **cos_sim = np.dot(known_embeddings, face_embedding)**, find **argmax** and **max_sim**. If max_sim > **RECOGNITION_THRESHOLD**, assign that person’s name and id; else "Unknown". Draws **rectangle** and **label** on the image (green = recognized, red = unknown), saves image under **output_path**, returns it as **FileResponse** (JPEG). Also returns headers with recognized count and total face count.

**Attendance (any logged-in user):**

- **GET /attendance** — Query params: start_date, end_date, person_id, person_type. Joins Attendance and Person, applies filters, orders by date and check_in_time, returns list of records (id, person_id, name, person_type, date, check_in_time, check_out_time, confidence, total_detections, duration_minutes, image_path).
- **GET /attendance/summary** — Optional **target_date** (default today). Counts total persons and how many have an attendance row for that date; computes **attendance_rate** (present/total * 100). Returns date, total_people, present, attendance_rate.

**Health (no auth):**

- **GET /health/** — Returns status "healthy", service name, and whether **encoder.initialized** is True (so we know if face recognition is ready).

**Webcam:**

- **router.include_router(webcam.router, prefix="/webcam")** — So all webcam routes are under **/api/webcam/...** (see next section).

**In short:** routes.py = auth, persons CRUD, train (average embeddings → save to Person), recognize (detect faces → compare with DB → return marked image), attendance list/summary, recognition settings, health, and webcam sub-routes.

---

## 12. api/webcam.py — Webcam Routes and Background Thread

**What it does:**

- Uses the same **FaceEncoder** and a **WebcamService** (see next section). Keeps a **global** monitoring thread and **monitoring_active** flag so only one monitoring loop runs at a time.

**POST /webcam/start/** (staff or admin):

- If monitoring is already active → 400. Else **initializes the camera** (e.g. camera_id=0) via WebcamService. Defines a function **monitor_in_background** that: sets monitoring_active True, creates a **new DB session** (SessionLocal), calls **webcam_service.start_monitoring(db, save_images=...)** (this runs the **infinite loop** that reads frames and does recognition), then sets monitoring_active False, releases the camera, closes the session. Starts this function in a **daemon thread** so the API can still respond. Returns a message that monitoring started.

**POST /webcam/stop/** (staff or admin):

- If not active → 400. Calls **webcam_service.stop_monitoring()** (sets is_running False so the loop exits). Waits for the thread to finish (join with timeout). Returns stopped message.

**GET /webcam/status/** — Returns monitoring_active, camera_initialized, **attendance_summary** from the service (total records, unique persons, etc.), and current time.

**GET /webcam/attendance/** — Returns the **in-memory** list of attendance records from the current monitoring run (person_id, name, timestamp, confidence, image_path).

**POST /webcam/export/** — If there are attendance records, calls **webcam_service.export_attendance_json()** to save a JSON file and returns the filepath and summary.

**DELETE /webcam/attendance/** — Clears the in-memory attendance list and cooldown in the service.

**GET /webcam/capture/** — If the camera isn’t open, initializes it. Reads **one frame**, gets known faces from DB, runs **recognize_faces_in_frame**, draws results, optionally saves an attendance image and updates DB. Returns base64 image, counts, and results. If we had to open the camera only for this request, we release it after.

**GET /webcam/preview/** — Returns the **latest frame** (or annotated frame) from the monitoring loop as **base64**, plus timestamp and recognition_results. So the frontend can poll this to show the live view.

**GET /webcam/summary/** — Returns the same attendance summary as the service and monitoring_active.

**In short:** webcam.py = start/stop the camera and background loop, expose status/preview/capture/attendance/export/clear as HTTP endpoints; the heavy work is inside WebcamService.

---

## 13. services/webcam_service.py — Camera Loop and Attendance Recording

**What it does:**

- **WebcamService** holds the **camera** (OpenCV VideoCapture), the **FaceEncoder**, and runs the **frame loop** that does recognition and writes attendance to the DB.

**AttendanceRecord** — Simple class: person_id, name, timestamp, confidence, image_path. Used for the **in-memory** list of records during a monitoring run.

**WebcamService:**

- **__init__(encoder):** Stores encoder, camera=None, is_running=False, list of attendance_records, **recognition_cooldown** dict (to avoid recording the same person again within cooldown_seconds), **cooldown_seconds** (e.g. 30), output_dir from config, current_frame, current_annotated_frame, recognition_results, frame_index, **recognition_stride** from config.
- **initialize_camera(camera_id):** Opens **cv2.VideoCapture(camera_id)**, sets width/height/FPS, returns True/False.
- **release_camera():** Releases the camera and sets it to None.
- **get_known_faces(db):** Loads all Person rows, unpickles and L2-normalizes embeddings, returns (numpy array of embeddings, list of names, list of ids). Used at the start of monitoring and in capture.
- **recognize_faces_in_frame(frame, known_embeddings, known_names, known_ids, db):**  
  - Optionally **resizes** the frame (e.g. to LIVE_RECOGNITION_WIDTH) for speed; keeps a **scale** factor to map bboxes back to original size.  
  - Calls **encoder.detect_and_encode_faces** on the (resized) frame.  
  - For each (embedding, bbox): computes **cos_sim = np.dot(known_embeddings, face_embedding)**, finds **argmax** and **max_sim**. If max_sim > **RECOGNITION_THRESHOLD**, assigns name and person_id. Then **cooldown check**: if we haven’t recorded this person in the last cooldown_seconds, we create an **AttendanceRecord**, append to attendance_records, set cooldown for this person, and call **record_attendance(db, record)** to write to the **attendance** and **attendance_sessions** tables.  
  - Returns a list of dicts: name, person_id, confidence, bbox (original size), recognized (bool).
- **_resize_for_recognition(frame):** Resizes to config width if needed; returns (resized_frame, scale).
- **draw_recognition_results(frame, results):** Draws rectangle and label (name, confidence) on the frame; green if recognized, red if unknown.
- **save_attendance_image(frame, results):** If at least one face is recognized, draws results on the frame and saves it under output_dir with a unique filename; updates record.image_path; returns the file path.
- **update_attendance_image(db, results, image_path):** Updates the **Attendance** rows for today for the recognized persons to set **image_path** if not already set.
- **record_attendance(db, record):**  
  - Finds or creates an **Attendance** row for this **person_id** and **date**. If new: sets check_in_time and check_out_time to record.timestamp, confidence, total_detections=1. If existing: updates check_out_time, total_detections, confidence (max), duration_minutes from check_in to check_out.  
  - Finds or creates an **AttendanceSession** for this person with status "active"; updates session_end, image_count, confidence.  
  - Commits. So we have **one attendance row per person per day** and update it on each new detection (with cooldown).
- **start_monitoring(db, save_images, callback, show_window):**  
  - Gets known faces from DB. If none, returns False.  
  - Sets **is_running = True**.  
  - **Loop:** read frame → store as current_frame → every **recognition_stride** frames call **recognize_faces_in_frame** and store results; else reuse previous results. Draw results on frame, store as current_annotated_frame. If save_images and we did recognition and there are results, save an attendance image and update DB. Optional callback and optional OpenCV window (show_window). Small sleep to limit CPU.  
  - When **is_running** becomes False (from stop_monitoring()), the loop exits.
- **stop_monitoring():** Sets **is_running = False**.
- **get_attendance_summary():** Groups in-memory attendance_records by person (first_seen, last_seen, detections, avg_confidence) and returns total_records, unique_persons, persons list, time_range.
- **export_attendance_json():** Writes the in-memory records to a JSON file in output_dir; returns the file path.
- **clear_attendance_records():** Clears the in-memory list and cooldown dict.

**In short:** webcam_service.py = open camera, loop over frames, every Nth frame run face detection and recognition, compare with DB embeddings, apply cooldown, write/update Attendance and AttendanceSession, optionally save images and expose the latest frame for preview.

---

## 14. How It All Fits Together

1. **Start:** main.py runs → init_database() creates DB, tables, default admin → app mounts router with prefix /api.
2. **Login:** Client POSTs to /api/auth/login → routes.py checks admin_users then app_users → security.py verifies password and creates JWT → client gets token and role.
3. **Protected request:** Client sends **Authorization: Bearer &lt;token&gt;** → deps.py decodes JWT and loads user from DB → route runs (e.g. get persons, train, recognize).
4. **Train:** POST /api/train/ with person_id, name, files → routes.py reads each file → face_encoder.encode_image() → average embeddings → L2-normalize → pickle → save in Person.embedding.
5. **Recognize:** POST /api/recognize/ with one image → routes.py loads all Person embeddings → face_encoder.detect_and_encode_faces() → for each face, dot product with all known → threshold → draw and return image.
6. **Webcam start:** POST /api/webcam/start/ → webcam.py opens camera and starts a thread → webcam_service.start_monitoring() runs the frame loop → every stride frames it uses face_encoder and record_attendance() to update the DB.
7. **Attendance:** GET /api/attendance (with optional filters) → routes.py queries Attendance joined with Person and returns records. Summary uses count of persons and count of attendance rows for the date.

**In short:** Config and database and security support the app; models define tables; face_encoder does DeepFace work; routes and webcam expose HTTP API; webcam_service does the camera loop and attendance writing. Everything is wired so that you can train faces, recognize them in images or from the webcam, and store/query attendance in MySQL.

---

Use this document as your **single place** to understand the backend from top to bottom. If you need to explain one file or one flow (e.g. “how does training work?” or “how does the webcam record attendance?”), you can use the relevant section and the “In short” lines for a quick recap.
