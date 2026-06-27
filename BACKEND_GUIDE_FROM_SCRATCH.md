# Backend Complete Guide — From Scratch to Finish

This guide explains **every part** of the backend so you can understand it fully and explain it to your team. Each **PART** is clearly separated: you can say “Part 4 is Configuration” or “From Part 7 to Part 9 we cover the API.”

**Simple language only.** No step is skipped.

---

# PART 1 — What Is the Backend and What Does It Do?

**Where this part starts:** Understanding the role of the backend in the project.

---

## 1.1 What Is a Backend?

In a web application we have two main sides:

- **Frontend** — What the user sees and clicks in the browser (our React app). It sends requests and shows data.
- **Backend** — The server that runs on a machine (or your computer during development). It receives those requests, does the work (like face recognition or saving to a database), and sends back a response.

So: **User → Browser (Frontend) → HTTP Request → Backend → Database / Face Recognition → Response → Frontend shows result.**

Our backend is a **REST API**: the frontend calls **URLs** (endpoints) with **GET**, **POST**, **PATCH**, **DELETE** and sends or receives **JSON** or **files** (e.g. images).

---

## 1.2 What Does Our Backend Do?

Our backend does the following:

1. **Authentication** — Login and registration. Checks username/email and password, creates a **token** (JWT) so the frontend can prove who is logged in on every request.
2. **User roles** — Different access for **admin**, **staff**, and **student**. Some routes only admin can call; some staff or admin; some any logged-in user.
3. **People management** — Add, edit, delete, and list **persons** (people we can recognize). Each person has name, email, department, type (student/staff), and later their **face data**.
4. **Face training** — Admin uploads several photos of a person. Backend uses **DeepFace** to extract a **face vector (embedding)** from each photo, **averages** them, and saves that vector in the database for that person. This is “enrollment.”
5. **Face recognition** — Admin (or system) sends an image. Backend detects all faces in the image, gets an embedding for each, **compares** with stored embeddings, and returns the same image with **names** (or “Unknown”) drawn on it. It can also **record attendance** when a known face is seen.
6. **Attendance** — Store and retrieve **attendance records**: who was present on which date, check-in and check-out time, confidence, optional proof image. We can filter by date, person, or type (student/staff) and get a **summary** (e.g. how many were present today).
7. **Webcam monitoring** — Start a **live camera** (e.g. laptop webcam). Backend reads frames in a loop, runs face recognition every few frames, and **records attendance** when it recognizes someone (with a cooldown so the same person is not recorded every second). Frontend can get a **preview** (current frame) and **start/stop** monitoring.
8. **Settings** — Admin can change **recognition threshold**, **stride** (how often we run recognition in webcam), and **image width** for recognition. These affect accuracy and performance.
9. **Health check** — A simple endpoint that says the server is running and whether face recognition is ready.

So the backend = **API + Database + Face recognition (DeepFace/OpenCV) + Webcam loop**. Everything the user does in the UI that needs data or face processing goes through this backend.

---

## 1.3 What Technology Do We Use?

- **Language:** Python  
- **Framework:** FastAPI (to define routes, validate input, and return JSON/files)  
- **Server:** Uvicorn (runs the FastAPI app and handles HTTP)  
- **Database:** MySQL (stores persons, attendance, users)  
- **ORM:** SQLAlchemy (we use Python classes instead of writing raw SQL)  
- **Face recognition:** DeepFace (VGG-Face model) and OpenCV (images and camera)  
- **Security:** Passlib (password hashing), python-jose (JWT creation and verification)  
- **Config:** Pydantic Settings (read from .env and environment variables)

---

**End of PART 1.**  
**Next: PART 2 — Prerequisites and First-Time Setup.**

---

# PART 2 — Prerequisites and First-Time Setup

**Where this part starts:** What you need installed and how to run the backend from scratch.

---

## 2.1 What You Need on Your Computer

1. **Python** — Version 3.8 or higher. We use Python to run the backend.  
   - Check: open terminal and type `python --version` or `python3 --version`.

2. **MySQL** — The database server must be installed and running.  
   - Our backend connects to MySQL to create and use a database (e.g. `attendance_system`).  
   - You need the **root** password (or another user/password) to put in the connection string.

3. **pip** — Python’s package installer. Usually comes with Python.  
   - We use it to install packages from `requirements.txt`.

---

## 2.2 Backend Folder

The backend code lives inside the project folder, in a folder named **`backend`**.  
Path example: `multiface-recognition-app/backend/`

Everything we describe from now on is inside this **backend** folder unless we say otherwise.

---

## 2.3 Virtual Environment (Recommended)

A **virtual environment** is an isolated Python environment for this project. We install packages only there, so they don’t mix with other projects.

**Create (one time):**

- Windows: `python -m venv venv`  
- Linux/Mac: `python3 -m venv venv`

This creates a folder **`venv`** inside the backend folder.

**Activate (every time you open a new terminal to work on the backend):**

- Windows (Command Prompt): `venv\Scripts\activate`  
- Windows (PowerShell): `venv\Scripts\Activate.ps1`  
- Linux/Mac: `source venv/bin/activate`

When activated, your prompt usually shows `(venv)`. Then any `pip install` will install into this environment.

---

## 2.4 Install Dependencies

With the virtual environment activated and your current directory set to **backend**, run:

```bash
pip install -r requirements.txt
```

This installs everything listed in **requirements.txt**:

- **fastapi** — Web framework for the API  
- **uvicorn** — Runs the FastAPI app  
- **python-multipart** — Needed for uploading files (e.g. images)  
- **sqlalchemy** — Talks to the database using Python classes  
- **pymysql** — MySQL driver for Python  
- **cryptography** — Used by PyMySQL  
- **pydantic-settings**, **pydantic** — Configuration and validation  
- **python-jose** — Create and decode JWT tokens  
- **passlib** — Hash and verify passwords  
- **deepface** — Face detection and embedding (uses VGG-Face)  
- **tf-keras** — Used by DeepFace  
- **opencv-python** — Read images and camera  
- **numpy** — Arrays and math (embeddings)  
- **Pillow** — Image handling  
- **python-dotenv** — Load .env file

**First run:** DeepFace may download its model (about 500 MB) the first time we use it. That is normal.

---

## 2.5 Environment Variables and .env File

The backend does **not** hardcode things like database password or secret key. It reads them from **environment variables**. The easiest way is to use a **.env** file in the **backend** folder.

**Step 1:** Copy the example file:

- Windows: `copy .env.example .env`  
- Linux/Mac: `cp .env.example .env`

**Step 2:** Open **.env** and set at least:

- **DATABASE_URL** — How to connect to MySQL.  
  Format: `mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE_NAME`  
  Example: `mysql+pymysql://root:YourPassword@localhost:3306/attendance_system`  
  If your password has special characters (e.g. `@`), encode them (e.g. `%40` for `@`).

You can also set (or leave as default in code):

- **SECRET_KEY** — A long random string for signing JWTs. In production use a strong secret.  
- **ADMIN_USERNAME**, **ADMIN_PASSWORD** — Used to create the default admin when the database is first created (e.g. admin / admin123).  
- **RECOGNITION_THRESHOLD** — e.g. 0.4 (minimum similarity to say “recognized”).  
- **LIVE_RECOGNITION_STRIDE** — e.g. 2 (run recognition every 2nd frame in webcam).  
- **LIVE_RECOGNITION_WIDTH** — e.g. 480 (resize frame to this width before recognition).  
- **MAX_FILE_SIZE_MB** — e.g. 10 (reject uploaded images larger than this).  
- **OUTPUT_DIR** — e.g. outputs (folder where we save images).  
- **HOST** — e.g. 0.0.0.0.  
- **PORT** — e.g. 8000.  
- **ACCESS_TOKEN_EXPIRE_MINUTES** — e.g. 720 (12 hours).  
- **JWT_ALGORITHM** — e.g. HS256.  
- **DEBUG** — True or False (if True, SQL can be logged).

The file **config.py** (Part 4) reads these and gives default values for anything not set.

---

## 2.6 Run the Backend

Make sure:

1. MySQL is running.  
2. You are in the **backend** folder.  
3. Virtual environment is activated (if you use one).  
4. **.env** has at least **DATABASE_URL** correct.

Then run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python -m uvicorn app.main:app --reload
```

- **app.main** — Python module `app.main`.  
- **app** — The FastAPI application object inside `main.py`.  
- **--reload** — Server restarts when you change code (good for development).  
- **--host 0.0.0.0** — Listen on all interfaces (so frontend on another machine/port can call it).  
- **--port 8000** — Port number (must match what frontend uses, e.g. `http://localhost:8000`).

When it starts you should see:

- Database and tables being created (if first run).  
- Default admin user created (if none existed).  
- Maybe “Preloading DeepFace model…” on first run.  
- A message that the server is running (e.g. http://0.0.0.0:8000).

**Useful URLs:**

- **http://localhost:8000/** — Welcome message and links.  
- **http://localhost:8000/docs** — Swagger UI: list of all API endpoints and “Try it out.”  
- **http://localhost:8000/redoc** — ReDoc: same API in another format.  
- **http://localhost:8000/api/health/** — Health check (no login needed).

---

**End of PART 2.**  
**Next: PART 3 — Project Structure (Folders and Files).**

---

# PART 3 — Project Structure (Folders and Files)

**Where this part starts:** Knowing where every file lives and what it is for.

---

## 3.1 Folder Tree

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── webcam.py
│   │   └── deps.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── attendance.py
│   │   └── user.py
│   └── services/
│       ├── __init__.py
│       ├── face_encoder.py
│       └── webcam_service.py
├── outputs/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## 3.2 What Each Part Is For

| Path | Purpose |
|------|--------|
| **app/** | Main Python package. All backend code is under `app`. |
| **app/main.py** | Entry point. Creates the FastAPI app, connects database, adds CORS, mounts all API routes. When we run `uvicorn app.main:app`, this is what runs. |
| **app/api/** | Everything related to **HTTP endpoints** and **who can call them**. |
| **app/api/routes.py** | Defines most routes: login, register, persons CRUD, train, recognize, attendance, settings, health. Also includes the webcam router. |
| **app/api/webcam.py** | Routes only for webcam: start, stop, status, capture, preview, attendance list, export, clear. |
| **app/api/deps.py** | **Dependencies** for authentication: read JWT, load user, check role (admin / staff / student). Used by routes to protect endpoints. |
| **app/core/** | **Core** = config, database connection, and security helpers. No business logic, only setup and utilities. |
| **app/core/config.py** | Reads .env and environment variables; exposes one `settings` object (database URL, secret key, threshold, etc.). |
| **app/core/database.py** | Creates the MySQL engine and session factory; defines how to get a DB session per request; creates database and tables and default admin on startup. |
| **app/core/security.py** | Password hashing (Passlib) and JWT creation (python-jose). |
| **app/models/** | **Models** = database tables defined as Python classes (SQLAlchemy). |
| **app/models/attendance.py** | Tables: Person, Attendance, AttendanceSession, DailyAttendanceSummary. |
| **app/models/user.py** | Tables: AdminUser, AppUser. |
| **app/services/** | **Services** = business logic that is not HTTP. Used by the API. |
| **app/services/face_encoder.py** | Uses DeepFace to get face embeddings from images (one face or many faces). |
| **app/services/webcam_service.py** | Opens camera, runs the frame loop, runs face recognition every N frames, records attendance, saves images. |
| **outputs/** | Folder where we save images (recognized faces, attendance photos). Created automatically if missing. |
| **.env** | Your local config (not committed to git). Copy from .env.example. |
| **.env.example** | Example of which variables you can set. |
| **requirements.txt** | List of Python packages to install with `pip install -r requirements.txt`. |

---

## 3.3 How the Pieces Connect

- **main.py** imports **config**, **database**, and **routes**. It calls **init_database()** once, then mounts the **router** from routes with prefix **/api**. So every route in routes.py and webcam.py is under **http://localhost:8000/api/...**.
- **routes.py** imports **database** (get_db), **config** (settings), **security** (hash, verify, create_access_token), **deps** (get_current_admin, etc.), **models** (Person, Attendance, AdminUser, AppUser), **face_encoder** (FaceEncoder), and **webcam** (to include webcam router). So routes are the “front door”; they use core, models, and services.
- **webcam.py** imports **database** (get_db, SessionLocal), **config**, **face_encoder**, **webcam_service**. It defines webcam endpoints and calls WebcamService for camera and loop.
- **deps.py** imports **database** (get_db), **config**, **models** (AdminUser, AppUser). It uses the JWT and DB to know “current user” and “role.”
- **face_encoder** is used by **routes.py** (train, recognize) and by **webcam_service** (inside the frame loop). **webcam_service** is used only by **webcam.py**.

So: **main** → **routes** (+ webcam router) → **deps** for auth; **routes** and **webcam** use **core**, **models**, and **services**.

---

**End of PART 3.**  
**Next: PART 4 — Configuration (config.py).**

---

# PART 4 — Configuration (config.py)

**Where this part starts:** How the backend gets all its settings from one place.

---

## 4.1 Why We Need Config

We need to change things without editing code: database password, secret key, port, threshold, etc. So we put them in **environment variables** or a **.env** file and read them in **config.py**. The rest of the app imports **settings** from config and uses `settings.DATABASE_URL`, `settings.RECOGNITION_THRESHOLD`, etc.

---

## 4.2 How config.py Works

- We use **Pydantic** and **pydantic-settings**. The class **Settings** extends **BaseSettings**.
- We tell it: read from a **.env** file, be **case-sensitive**, and **ignore** extra keys in .env.
- Each attribute is a **setting**: name, type, and **default value** if not set in .env.

Example:

- `DATABASE_URL: str = "mysql+pymysql://..."` — Default connection string; you override in .env.
- `SECRET_KEY: str = "change-me-please"` — You must set a strong secret in production.
- `RECOGNITION_THRESHOLD: float = 0.4` — Minimum similarity to consider a face recognized.

At the bottom we create one instance: **settings = Settings()**. So everywhere we do `from app.core.config import settings` and then use `settings.PORT`, `settings.RECOGNITION_THRESHOLD`, etc.

---

## 4.3 Every Setting Explained

| Setting | Type | Meaning |
|--------|------|--------|
| APP_NAME | str | Name of the API (e.g. in docs and health). |
| APP_VERSION | str | Version string. |
| DEBUG | bool | If True, SQLAlchemy can echo SQL (helpful in development). |
| DATABASE_URL | str | Full MySQL connection: user, password, host, port, database name. |
| HOST | str | Where the server listens (0.0.0.0 = all interfaces). |
| PORT | int | Port number (e.g. 8000). |
| SECRET_KEY | str | Secret used to **sign** JWT. Keep it secret in production. |
| ACCESS_TOKEN_EXPIRE_MINUTES | int | How many minutes the login token is valid (e.g. 720 = 12 hours). |
| JWT_ALGORITHM | str | Algorithm for JWT (e.g. HS256). |
| ADMIN_USERNAME | str | Username of the default admin created on first run. |
| ADMIN_PASSWORD | str | Password of that default admin (only used once to create the user). |
| RECOGNITION_THRESHOLD | float | Min cosine similarity to say “recognized” (0.0–1.0). Lower = stricter. |
| DETECTION_SIZE | int | Can be used for image size in detection (current code may not use it everywhere). |
| LIVE_RECOGNITION_STRIDE | int | In webcam, run recognition every Nth frame (e.g. 2 = every 2nd frame). |
| LIVE_RECOGNITION_WIDTH | int | Resize webcam frame to this width (pixels) before recognition. |
| OUTPUT_DIR | str | Folder name for saved images (under project root). |
| MAX_FILE_SIZE_MB | int | Reject uploaded images larger than this (MB). |
| BASE_DIR | Path | Project root path (backend folder). |

---

## 4.4 output_path Property

In Settings we have a **property** called **output_path**. It returns **BASE_DIR / OUTPUT_DIR** (e.g. `backend/outputs`). Before returning, it creates that folder if it doesn’t exist (**mkdir(exist_ok=True)**). So the rest of the app uses **settings.output_path** to save recognized images and attendance photos.

---

**End of PART 4.**  
**Next: PART 5 — Database (database.py and Models).**

---

# PART 5 — Database (database.py and Models)

**Where this part starts:** How we connect to MySQL and how each table is defined.

---

## 5.1 database.py — Connection and Session

**Engine:**  
We call **create_engine(settings.DATABASE_URL)**. This tells SQLAlchemy how to connect to MySQL. We use:

- **pool_pre_ping=True** — Before using a connection we check it’s still alive.  
- **pool_recycle=3600** — Recycle connections every hour so they don’t go stale.  
- **echo=settings.DEBUG** — If DEBUG is True, print every SQL query (for debugging).

**SessionLocal:**  
**sessionmaker** creates a **factory**: when we call **SessionLocal()** we get a **new session**. A session is like a “conversation” with the database: we add, query, update, delete, and then **commit**. We set **autocommit=False** and **autoflush=False** and bind it to the engine. So every request that needs the DB will create one session, use it, and close it.

**Base:**  
**declarative_base()** gives us a **Base** class. Every **model** (table) is a class that **inherits** from Base and has **Column(...)** attributes. SQLAlchemy then knows how to create tables and run queries from these classes.

**get_db():**  
This is a **generator** function used as a **FastAPI dependency**. It:

1. Creates **db = SessionLocal()**.  
2. **Yields** db so the route function can use it (e.g. `db.query(Person).all()`).  
3. In a **finally** block it **closes** the session. So we never forget to close, and every request gets a fresh session.

Routes that need the database declare **db: Session = Depends(get_db)** and FastAPI injects the session.

**init_database():**  
Called **once** when the app starts (from main.py). It:

1. Imports the **models** (attendance, user) so that their tables are **registered** with Base.metadata.  
2. Parses **DATABASE_URL** to get the database name.  
3. If the driver is MySQL, connects **without** selecting a database and runs **CREATE DATABASE IF NOT EXISTS &lt;name&gt;** so the database exists.  
4. Runs **Base.metadata.create_all(bind=engine)** so **all** tables (persons, attendance, attendance_sessions, admin_users, app_users, daily_attendance_summary) are created if they don’t exist.  
5. Opens a session, checks if an **AdminUser** with **ADMIN_USERNAME** exists. If **not**, it creates one with **hash_password(ADMIN_PASSWORD)** and commits. So on first run you get a default admin (e.g. admin / admin123).

---

## 5.2 Models — Tables as Python Classes

**persons (Person)**  
- **id** — Primary key.  
- **name** — Full name, unique, not null.  
- **email** — Optional, unique.  
- **department** — Optional.  
- **person_code** — Optional, unique (e.g. student ID).  
- **person_type** — "student" or "staff", default "student".  
- **embedding** — **LargeBinary**: we store the **face vector** here as bytes (we pickle the numpy array). This is what we use for recognition.  
- **created_at** — When the row was created.  
- **is_active** — Can be used to soft-delete.  
- **attendance_records** — Relationship: one Person has many Attendance rows.

**attendance (Attendance)**  
- **id** — Primary key.  
- **person_id** — Foreign key to persons.id.  
- **date** — Calendar date (one row per person per day).  
- **check_in_time** — First detection time that day.  
- **check_out_time** — Last detection time (updated when we see them again).  
- **confidence** — Recognition confidence (e.g. similarity score).  
- **image_path** — Optional path to proof image.  
- **total_detections** — How many times detected that day.  
- **duration_minutes** — Minutes between first and last detection.  
- **person** — Relationship back to Person.

**attendance_sessions (AttendanceSession)**  
- **person_id**, **session_start**, **session_end**, **confidence**, **image_count**, **status** (e.g. active, completed). Used for continuous webcam session tracking.

**daily_attendance_summary (DailyAttendanceSummary)**  
- **date**, **total_persons_present**, **total_persons_expected**, **attendance_rate**, **first_check_in**, **last_check_out**. For daily reports (model is defined; you can use it in reports later).

**admin_users (AdminUser)**  
- **id**, **username** (unique), **password_hash**, **created_at**, **is_active**. Admin logs in with username + password.

**app_users (AppUser)**  
- **id**, **full_name**, **email** (unique), **password_hash**, **role** (staff or student), **department**, **note**, **created_at**, **is_active**. Staff/student log in with email + password.

---

## 5.3 Why One Attendance Row per Person per Day

We **do not** create a new attendance row every time we see a person. We have **one row per person per day**. The first time we see them we **create** the row and set check_in_time and check_out_time. When we see them again the same day we **update** that row: check_out_time, total_detections, duration_minutes. So we avoid duplicates and always have one record per person per day.

---

**End of PART 5.**  
**Next: PART 6 — Security (Passwords and JWT).**

---

# PART 6 — Security (Passwords and JWT)

**Where this part starts:** How we store passwords and how we create and use login tokens.

---

## 6.1 Password Hashing (Passlib)

We **never** store the real password. We store a **hash**.

**pwd_context** — We use **CryptContext** with scheme **pbkdf2_sha256**. It hashes in a safe way (salt + many iterations).

**hash_password(password):**  
Takes the plain password, hashes it, and returns the hash string. We call this when we **create** a user (admin or app user) and save the result in **password_hash**.

**verify_password(plain_password, hashed_password):**  
Hashes the plain password and compares with the stored hash. Returns **True** if they match. We call this on **login** to check if the password is correct.

So even if someone gets the database, they cannot get back the original passwords from the hashes.

---

## 6.2 JWT (JSON Web Token)

After a successful login we need to tell the frontend “this user is logged in” and “their role is admin/staff/student.” We don’t want to store a session in the database for every request. So we use a **token** that carries this information and is **signed** by the server.

**create_access_token(subject, role, expires_minutes):**  
- **subject** — Who the user is: for admin we use **username**, for app users we use **email**.  
- **role** — "admin", "staff", or "student".  
- **expires_minutes** — How long the token is valid (default from settings, e.g. 720 = 12 hours).  
- We build a dict: **sub** = subject, **exp** = current time + expiry, **role** = role.  
- We **sign** it with **SECRET_KEY** and the chosen **JWT_ALGORITHM** (e.g. HS256) and return the token string.  
- The frontend stores this string and sends it in the header **Authorization: Bearer &lt;token&gt;** on every request. The backend can then **decode** the token and verify the signature to know who is calling and their role.

---

**End of PART 6.**  
**Next: PART 7 — Authentication and Dependencies (deps.py).**

---

# PART 7 — Authentication and Dependencies (deps.py)

**Where this part starts:** How the backend knows “who is calling” and “are they allowed?”

---

## 7.1 What Is a Dependency?

In FastAPI, a **dependency** is a function that runs **before** the route function. It can:

- Return a value that is passed into the route (e.g. the current user).  
- Raise an exception (e.g. 401 Unauthorized or 403 Forbidden) so the route is not run.

So we use dependencies to **protect** routes: only logged-in users, or only admin, etc.

---

## 7.2 HTTPBearer()

We use **HTTPBearer()** so FastAPI expects the request to have the header **Authorization: Bearer &lt;token&gt;**. If the header is missing, FastAPI returns 403 before our code runs. If it is present, our dependency receives the **credentials** (the token string).

---

## 7.3 get_current_user(credentials, db)

1. Takes the **token** from the Bearer credentials.  
2. **Decodes** the JWT with **SECRET_KEY** and the configured algorithm. If the token is invalid or expired, **jwt.decode** raises; we catch and return **401 Unauthorized** with message like "Invalid token".  
3. From the payload we read **sub** (subject = username or email) and **role**. If either is missing we return 401.  
4. If **role == "admin"** we query **AdminUser** by **username == sub** and **is_active == True**.  
5. Else we query **AppUser** by **email == sub** and **is_active == True**.  
6. If no user is found we return 401 ("Invalid user").  
7. Otherwise we return **{"role": role, "user": user}**. So any route that uses this dependency gets the **current user** and **role**.

---

## 7.4 get_current_admin(current)

- Depends on **get_current_user** (so it runs first).  
- If **current["role"] != "admin"** we raise **403 Forbidden** ("Admin access required").  
- Otherwise we return **current["user"]**. So only **admin** can access routes that use **Depends(get_current_admin)**.

---

## 7.5 get_current_staff_or_admin(current)

- Depends on **get_current_user**.  
- If role is **not** "admin" or "staff" we raise 403 ("Staff access required").  
- Otherwise we return **current**. So **staff** and **admin** can access (e.g. webcam, attendance).

---

## 7.6 get_current_any_user(current)

- Depends on **get_current_user**.  
- If role is not one of "admin", "staff", "student" we raise 403.  
- Otherwise we return **current**. So **any logged-in user** can access (e.g. /auth/me, GET /attendance).

---

## 7.7 How Routes Use These

- **POST /auth/login** and **POST /auth/register** — **No** dependency. Anyone can call.  
- **GET /auth/me** — **Depends(get_current_any_user)**.  
- **GET/PUT /settings/recognition**, **POST/GET/PATCH/DELETE /persons**, **POST /train/**, **POST /recognize/** — **Depends(get_current_admin)**.  
- **GET /attendance**, **GET /attendance/summary** — **Depends(get_current_any_user)**.  
- All **/webcam/** routes — **Depends(get_current_staff_or_admin)**.  
- **GET /health/** — No dependency.

So the **separation** is clear: admin-only, staff-or-admin, or any authenticated user.

---

**End of PART 7.**  
**Next: PART 8 — Face Recognition Service (face_encoder.py).**

---

# PART 8 — Face Recognition Service (face_encoder.py)

**Where this part starts:** How we turn a face image into a vector and how we detect multiple faces.

---

## 8.1 Why a Separate Service?

Face encoding uses **DeepFace** and **OpenCV**. We put this in a **service** (face_encoder.py) so that:

- Both **routes.py** (train, recognize) and **webcam_service** can use the same logic.  
- The API layer stays thin; the “how to get an embedding” is in one place.

---

## 8.2 FaceEncoder Class

**__init__:**  
We set **model_name = "VGG-Face"** (the DeepFace model we use). We set **initialized = True** and **_model_preloaded = False**. We don’t load the model here; DeepFace loads or downloads it on first use.

**l2_normalize(x):**  
Takes a numpy vector **x**, computes its **L2 norm** (length). If the norm is 0 we return x; else we return **x / norm** so the vector has length 1. After this, **dot product between two vectors = cosine similarity**, which we use to compare faces.

**preload_model():**  
Optional. We create a small dummy image, save it to a temp file, and call **DeepFace.represent** on it with **enforce_detection=False** so it doesn’t fail. This triggers model download/load once at startup. Then we delete the temp file and set **_model_preloaded = True**. routes.py calls this when the app starts so the first real request isn’t slow.

---

## 8.3 encode_image(file_bytes)

**Used for:** Training (one face per image).

**Steps:**  
1. Save **file_bytes** to a **temporary file** (DeepFace expects a path).  
2. Call **DeepFace.represent(path, model_name=VGG-Face, enforce_detection=True, detector_backend='opencv')**.  
3. If no face is found, DeepFace fails or returns empty; we return **None**.  
4. Otherwise we take the **first** face’s **embedding** (list of numbers), convert to numpy array, **L2-normalize**, and return it.  
5. We delete the temp file in a **finally** block.

So: **image bytes → temp file → DeepFace → one embedding (or None)**.

---

## 8.4 detect_and_encode_faces(img)

**Used for:** Recognition and webcam (one image, possibly many faces).

**Steps:**  
1. **img** is an OpenCV image (numpy array, BGR).  
2. We write it to a **temp file**.  
3. Call **DeepFace.represent(path, model_name=VGG-Face, enforce_detection=False, detector_backend='opencv')**.  
4. We get a **list** of face results. Each has **embedding** and **facial_area** (x, y, w, h).  
5. For each face we take the embedding, L2-normalize it, and convert (x, y, w, h) to **(x1, y1, x2, y2)** (bounding box).  
6. We return a list of **(embedding, bbox)** tuples.  
7. We delete the temp file in a **finally** block.

So: **image → temp file → DeepFace → list of (embedding, bbox)**.

---

## 8.5 Why Temp Files?

DeepFace’s **represent()** in this setup takes a **file path**, not raw bytes. So we write bytes to a temp file, call DeepFace, then delete the file. This keeps the interface simple and avoids changing DeepFace internals.

---

**End of PART 8.**  
**Next: PART 9 — Main API Routes (routes.py).**

---

# PART 9 — Main API Routes (routes.py)

**Where this part starts:** Every endpoint under /api (except webcam) and what it does step by step.

---

## 9.1 Router and Imports

- We create **router = APIRouter()**.  
- We create one **encoder = FaceEncoder()** and call **encoder.preload_model()** so the model is loaded at startup.  
- We import get_db, settings, security functions, deps, models, face_encoder, and webcam (to include its router later).

---

## 9.2 Pydantic Models (Request Bodies)

- **LoginPayload** — username, password (both strings).  
- **RegisterPayload** — full_name, email, password, role (pattern staff|student), optional department, note.  
- **PersonCreate** — name, optional email, department, person_code, person_type (student|staff).  
- **PersonUpdate** — same fields, all optional (for PATCH).  
- **RecognitionSettings** — recognition_threshold (0–1), live_recognition_stride (1–10), live_recognition_width (160–1280).

These validate the request body and give clear errors if the format is wrong.

---

## 9.3 Auth Endpoints

**POST /auth/login**  
- Body: LoginPayload (username, password).  
- We try **AdminUser** by username. If found and **verify_password** matches and user is active, we **create_access_token(username, role="admin")** and return **access_token**, **token_type**: "bearer", **role**: "admin".  
- Else we try **AppUser** by email (we use payload.username as email for app users). If not found or password wrong or inactive we raise **401 Unauthorized**.  
- Else we create_access_token(email, role=user.role) and return token and role.  
- So: one endpoint for both admin (username) and staff/student (email).

**POST /auth/register**  
- Body: RegisterPayload.  
- If **AppUser** with that email already exists we return 400.  
- We create **AppUser** with full_name, email, **hash_password(password)**, role, department, note, is_active=True, add to db, commit, refresh, and return success message, id, role.

**GET /auth/me**  
- **Depends(get_current_any_user)**.  
- We return current user info: for admin we return username, role, is_active; for app user we return email, full_name, role, is_active.

---

## 9.4 Settings Endpoints (Admin Only)

**GET /settings/recognition** — **Depends(get_current_admin)**. Returns current **recognition_threshold**, **live_recognition_stride**, **live_recognition_width** from settings.

**PUT /settings/recognition** — **Depends(get_current_admin)**. Body: RecognitionSettings. We **update** settings in memory (settings.RECOGNITION_THRESHOLD, etc.) and also set **webcam.webcam_service.recognition_stride** so the running webcam loop uses the new stride. Then we return the new values.

---

## 9.5 Persons CRUD (Admin Only)

**POST /persons** — **Depends(get_current_admin)**. Body: PersonCreate. We check name, email (if provided), person_code (if provided) are not already used. We create **Person** with name, email, department, person_code, person_type and **embedding=b""** (placeholder until training). We add, commit, and return id and name.

**GET /persons** — **Depends(get_current_admin)**. Optional query **person_type** to filter. We query Person, apply filter, return count and list of {id, name, email, department, person_code, person_type} (no embedding).

**PATCH /persons/{person_id}** — **Depends(get_current_admin)**. Body: PersonUpdate (only fields to change). We load the person; if not found 404. We check uniqueness for name, email, person_code against other persons. We update only the provided fields, commit, return message and id.

**DELETE /persons/{person_id}** — **Depends(get_current_admin)**. We delete **AttendanceSession** and **Attendance** for this person, then delete the **Person**, commit, return message and id.

---

## 9.6 Training (Admin Only)

**POST /train/** — **Depends(get_current_admin)**.  
**Form data:** person_id (int), name (str), person_type (default "student"), optional email, department, person_code, and **files** (list of image files).

**Steps:**  
1. If encoder is not initialized we return 503.  
2. We create an empty list **embeddings**.  
3. For **each file**: read contents, check size &lt; MAX_FILE_SIZE_MB (else 400), call **encoder.encode_image(contents)**. If the result is not None we append it to embeddings.  
4. If **embeddings** is empty we return 400 "No valid faces found".  
5. We **average** all embeddings: **np.mean(embeddings, axis=0)**, then **encoder.l2_normalize(avg_embedding)**.  
6. We **pickle** the result and get bytes.  
7. We look up **Person** by person_id. If **none** we create a new Person with id=person_id, name, email, department, person_code, person_type, embedding=serialized, and add it. If **exists** we update name, email, department, person_code, person_type and **embedding=serialized**.  
8. We commit and return success message with person_id, name, and faces_processed count.

So: **multiple photos → one embedding per face → average → normalize → save in Person.embedding**.

---

## 9.7 Recognition (Admin Only)

**POST /recognize/** — **Depends(get_current_admin)**.  
**Body:** one **file** (image).

**Steps:**  
1. If encoder not initialized return 503.  
2. Read file contents; if size &gt; MAX_FILE_SIZE_MB return 400.  
3. Decode image: **np.frombuffer(contents, np.uint8)** then **cv2.imdecode(..., cv2.IMREAD_COLOR)**. If None return 400.  
4. Load **all Person** from db. If no persons or no one has embedding return 404.  
5. Build lists **known_embeddings**, **known_names**, **known_ids**: for each person with embedding we pickle.loads, L2-normalize, and append. Convert known_embeddings to numpy array.  
6. Call **encoder.detect_and_encode_faces(img)** → list of (embedding, bbox). If empty return 400 "No faces detected".  
7. For **each (face_embedding, bbox)**:  
   - **cos_sim = np.dot(known_embeddings, face_embedding)** (dot product = cosine similarity after L2 norm).  
   - **idx = np.argmax(cos_sim)**, **max_sim = cos_sim[idx]**.  
   - If **max_sim &gt; settings.RECOGNITION_THRESHOLD** we set name = known_names[idx], person_id = known_ids[idx], and increment recognized_count. Else name = "Unknown", person_id = None.  
   - We **draw** rectangle (green if recognized, red if unknown) and **label** (name and max_sim) on the image with OpenCV.  
8. We **save** the image to **settings.output_path** with a unique filename (e.g. recognized_&lt;uuid&gt;.jpg).  
9. We return **FileResponse** (the image as JPEG) with headers **X-Recognized-Count** and **X-Total-Faces**.

So: **image → detect faces → compare with DB → draw boxes and names → return image**.

---

## 9.8 Attendance Endpoints (Any Logged-in User)

**GET /attendance** — **Depends(get_current_any_user)**.  
Query params: **start_date**, **end_date**, **person_id**, **person_type**. We query **Attendance** joined with **Person**, apply filters, order by date desc and check_in_time desc, and return **count** and **records** (id, person_id, name, person_type, date, check_in_time, check_out_time, confidence, total_detections, duration_minutes, image_path).

**GET /attendance/summary** — **Depends(get_current_any_user)**.  
Query param: **target_date** (default today). We count **total_people** = Person.count() and **present** = Attendance rows for that date. We compute **attendance_rate** = (present / total_people) * 100 (or 0 if no people). We return date, total_people, present, attendance_rate.

---

## 9.9 Health (No Auth)

**GET /health/** — No dependency. We return **status**: "healthy", **service**: app name, **face_encoder_initialized**: encoder.initialized. So we can check if the server and face service are ready.

---

## 9.10 Including Webcam Router

At the end of routes.py we do **router.include_router(webcam.router, prefix="/webcam", tags=[...])**. So all webcam routes are under **/api/webcam/...** (see Part 10).

---

**End of PART 9.**  
**Next: PART 10 — Webcam API (webcam.py).**

---

# PART 10 — Webcam API (webcam.py)

**Where this part starts:** All endpoints that control the camera and get preview/attendance from the current run.

---

## 10.1 What This File Does

- It defines a **router** and a **WebcamService(encoder)**.  
- It keeps **monitoring_thread** and **monitoring_active** so only one monitoring loop runs at a time.  
- All routes here use **Depends(get_current_staff_or_admin)** so only **staff** or **admin** can call them.

---

## 10.2 POST /webcam/start/

- If **monitoring_active** is already True we return 400 "already active".  
- We call **webcam_service.initialize_camera(camera_id)** (default 0). If it fails we return 500.  
- We define a function **monitor_in_background** that: sets **monitoring_active = True**, creates a **new DB session** (SessionLocal()), calls **webcam_service.start_monitoring(db, save_images=save_images, show_window=False)** (this is the **infinite loop** that reads frames and does recognition), then in **finally** sets monitoring_active False, releases the camera, and closes the session.  
- We start this function in a **thread** (daemon=True) so the API can still respond.  
- We return a message that monitoring started, camera_id, save_images, status "active".

So: **start** = open camera + run the recognition loop in a background thread.

---

## 10.3 POST /webcam/stop/

- If **monitoring_active** is False we return 400.  
- We call **webcam_service.stop_monitoring()** so the loop’s **is_running** becomes False and the loop exits.  
- We **join** the thread with a short timeout so we wait for it to finish.  
- We return message "stopped".

---

## 10.4 GET /webcam/status/

- We return **monitoring_active**, **camera_initialized** (camera is not None), **attendance_summary** from webcam_service (total_records, unique_persons, persons, time_range), and **current_time**.

---

## 10.5 GET /webcam/attendance/

- We return the **in-memory** list of **attendance_records** from webcam_service (person_id, name, timestamp, confidence, image_path) and total_records. This is the list of people recorded during the **current** monitoring run.

---

## 10.6 POST /webcam/export/

- If there are no attendance_records we return 404.  
- We call **webcam_service.export_attendance_json()** to write a JSON file to the output folder and get the filepath.  
- We return message, filepath, and summary.

---

## 10.7 DELETE /webcam/attendance/

- We call **webcam_service.clear_attendance_records()** to clear the in-memory list and cooldown.  
- We return message and records_remaining = 0.

---

## 10.8 GET /webcam/capture/

- If the camera is not open we try **webcam_service.initialize_camera()**; if it fails we return 500.  
- We **read one frame** from the camera. If read fails we return 500.  
- We get **known_embeddings, known_names, known_ids** from **webcam_service.get_known_faces(db)**. If empty we return 404.  
- We call **webcam_service.recognize_faces_in_frame(...)** to get results. We **draw** results on the frame. We **save** an attendance image if someone was recognized and **update_attendance_image** in the DB.  
- We **encode** the annotated frame as JPEG and then **base64** and return it in the response with **frame_base64**, **faces_detected**, **faces_recognized**, **image_saved**, **image_path**, **results**.  
- If we had opened the camera only for this request (monitoring was not active), we **release** the camera in a **finally** block.

So: **one frame** → recognize → draw → optionally save and update DB → return base64 image and counts.

---

## 10.9 GET /webcam/preview/

- If camera is not open we return 400.  
- If **current_frame** and **current_annotated_frame** are both None we return 404.  
- We take **current_annotated_frame** if available else **current_frame**, encode as JPEG and then base64, and return **frame_base64**, **timestamp**, **recognition_results**. So the frontend can **poll** this to show the live view.

---

## 10.10 GET /webcam/summary/

- We return **summary** from webcam_service, **current_time**, and **monitoring_active**.

---

**End of PART 10.**  
**Next: PART 11 — Webcam Service (webcam_service.py).**

---

# PART 11 — Webcam Service (webcam_service.py)

**Where this part starts:** The camera loop, recognition every N frames, cooldown, and writing attendance to the database.

---

## 11.1 AttendanceRecord (Simple Class)

- **person_id**, **name**, **timestamp**, **confidence**, **image_path**.  
- Used for the **in-memory** list of records during one monitoring run. We don’t store this in the DB directly; we use it and then call **record_attendance** to write to the **Attendance** and **AttendanceSession** tables.

---

## 11.2 WebcamService __init__(encoder)

- We store **encoder**, **camera = None**, **is_running = False**, **attendance_records = []**, **recognition_cooldown = {}** (to avoid recording the same person again within cooldown_seconds), **cooldown_seconds = 30**, **output_dir** from settings, **current_frame**, **current_annotated_frame**, **recognition_results**, **frame_index = 0**, **recognition_stride** from settings (e.g. 2).

---

## 11.3 initialize_camera(camera_id)

- We create **cv2.VideoCapture(camera_id)**. If not opened we return False. We set width, height, FPS and return True.

**release_camera()** — We release the camera and set it to None.

---

## 11.4 get_known_faces(db)

- We query **Person.all()**, and for each person with **embedding** we **pickle.loads**, L2-normalize, and collect into lists. We return **(numpy array of embeddings, list of names, list of ids)**. Used at the start of monitoring and in capture.

---

## 11.5 recognize_faces_in_frame(frame, known_embeddings, known_names, known_ids, db)

- We optionally **resize** the frame (**_resize_for_recognition**) to **LIVE_RECOGNITION_WIDTH** and get a **scale** to map bboxes back to original size.  
- We call **encoder.detect_and_encode_faces(frame_for_recognition)**.  
- For each (embedding, bbox) we scale bbox back if needed. We compute **cos_sim = np.dot(known_embeddings, face_embedding)**, **idx = argmax**, **max_sim**. If **max_sim &gt; RECOGNITION_THRESHOLD** we set name and person_id.  
- **Cooldown:** We use a key like **person_id_name**. If we haven’t recorded this person in the last **cooldown_seconds** we: create an **AttendanceRecord**, append to **attendance_records**, set **recognition_cooldown[key] = current_time**, and call **record_attendance(db, record)**. So we don’t record the same person every frame.  
- We append to **results** a dict: name, person_id, confidence, bbox, recognized (bool).  
- We return the list of results.

---

## 11.6 _resize_for_recognition(frame)

- If frame width &lt;= target width we return frame and scale 1.0. Else we resize to **LIVE_RECOGNITION_WIDTH** keeping aspect ratio and return (resized_frame, scale). Scale is used to convert bboxes back to original coordinates.

---

## 11.7 draw_recognition_results(frame, results)

- We copy the frame and for each result we draw a **rectangle** (green if recognized, red if not) and **text** (name and confidence). We return the annotated frame.

---

## 11.8 save_attendance_image(frame, results)

- If at least one face is recognized we draw results on the frame, generate a unique filename (e.g. attendance_&lt;timestamp&gt;_&lt;uuid&gt;.jpg), save under **output_dir**, update **record.image_path** for the latest records, and return the file path.

**update_attendance_image(db, results, image_path)** — For each recognized result we find the latest **Attendance** row for that person and today and set **image_path** if not set, then commit.

---

## 11.9 record_attendance(db, record)

- **Attendance:** We look for an existing row for this **person_id** and **date**. If **none** we create a new **Attendance** with check_in_time and check_out_time = record.timestamp, confidence, total_detections=1. If **exists** we **update** check_out_time, total_detections, confidence (max), duration_minutes (from check_in to check_out), and image_path if we have it. So **one row per person per day** is always maintained.  
- **AttendanceSession:** We find or create an active session for this person and update session_end, image_count, confidence.  
- We **commit**.

---

## 11.10 start_monitoring(db, save_images, callback, show_window)

- We check camera is open and get **known_embeddings, known_names, known_ids**. If empty we return False.  
- We set **is_running = True**.  
- **Loop:**  
  - **Read** a frame. If fail we break.  
  - We store **current_frame**. We increment **frame_index**.  
  - If **frame_index % recognition_stride == 0** we call **recognize_faces_in_frame(...)** and store **recognition_results**; else we reuse previous results.  
  - We **draw** results on the frame and store **current_annotated_frame**.  
  - If **save_images** and we did recognition and there are results we **save_attendance_image** and **update_attendance_image**.  
  - Optional callback and optional **cv2.imshow** (show_window).  
  - Small **sleep** (e.g. 0.03) to limit CPU.  
- When **is_running** becomes False (from **stop_monitoring**) we exit the loop, set is_running False, and optionally destroy windows.

So: **loop over frames → every Nth frame run recognition → apply cooldown → record attendance and optionally save image → keep latest frame for preview**.

---

## 11.11 stop_monitoring(), get_attendance_summary(), export_attendance_json(), clear_attendance_records()

- **stop_monitoring()** — Sets **is_running = False** so the loop exits.  
- **get_attendance_summary()** — Groups in-memory **attendance_records** by person (first_seen, last_seen, detections, avg_confidence) and returns total_records, unique_persons, persons list, time_range.  
- **export_attendance_json()** — Writes attendance_records to a JSON file in output_dir and returns the path.  
- **clear_attendance_records()** — Clears **attendance_records** and **recognition_cooldown**.

---

**End of PART 11.**  
**Next: PART 12 — How to Run and Test.**

---

# PART 12 — How to Run and Test

**Where this part starts:** Quick reference to run the backend and test each part.

---

## 12.1 Run Checklist

1. **MySQL** is running.  
2. **.env** in backend folder has **DATABASE_URL** correct (and optionally SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, etc.).  
3. In **backend** folder: **pip install -r requirements.txt** (and activate venv if you use one).  
4. Run: **uvicorn app.main:app --reload --host 0.0.0.0 --port 8000**.  
5. Open **http://localhost:8000/docs** to see all endpoints.

---

## 12.2 Test Flow (Manual)

1. **Health:** GET http://localhost:8000/api/health/ — should return healthy and face_encoder_initialized true after first load.  
2. **Login:** POST /api/auth/login with body **{"username":"admin","password":"admin123"}** (or your ADMIN_USERNAME/ADMIN_PASSWORD). Copy the **access_token** from the response.  
3. **Auth header:** In Swagger, click “Authorize” and enter **Bearer &lt;your_token&gt;** (with the word Bearer and a space).  
4. **Me:** GET /api/auth/me — should return your user and role.  
5. **Create person:** POST /api/persons with body e.g. {"name":"Test User","person_type":"student"}. Note the **id**.  
6. **Train:** POST /api/train/ with form: person_id = that id, name = "Test User", person_type = student, and **files** = 2–3 face photos. Should return success and faces_processed.  
7. **Recognize:** POST /api/recognize/ with one image file that contains a face. Should return the image with a box and name (or Unknown).  
8. **Attendance:** GET /api/attendance — optional start_date, end_date. Should return records (empty if you haven’t used webcam yet).  
9. **Webcam:** POST /api/webcam/start/ (camera_id=0, save_images=true). Then GET /api/webcam/preview/ to get the current frame. Then POST /api/webcam/stop/.

---

## 12.3 Frontend Connection

- Frontend must call **http://localhost:8000/api** (or your backend URL). Set **VITE_API_BASE_URL** in frontend .env or use Settings in the app.  
- Backend has **CORS** allow_origins=["*"] so the browser allows requests from the frontend port (e.g. 5173).

---

**End of PART 12.**  
**Next: PART 13 — End-to-End Flow Summary.**

---

# PART 13 — End-to-End Flow Summary

**Where this part starts:** One place that ties everything together for explaining to your team.

---

## 13.1 From Request to Response

1. **Request** comes to **http://localhost:8000/api/...**  
2. **main.py** has mounted the router with prefix **/api**, so the path is handled by **routes.py** or **webcam.py**.  
3. If the route has **Depends(get_db)**, FastAPI calls **get_db()** and injects a **database session**.  
4. If the route has **Depends(get_current_admin)** (or staff_or_admin or any_user), FastAPI runs **get_current_user** first: it reads **Authorization: Bearer &lt;token&gt;**, decodes the JWT, loads the user from DB, and checks role. If invalid → 401 or 403; else the route runs with **current** user.  
5. The route function uses **db** to query or update **Person**, **Attendance**, **AdminUser**, **AppUser**, etc. It may use **encoder** (FaceEncoder) or **webcam_service** for face or camera work.  
6. The route returns **JSON** or **FileResponse** (e.g. image). FastAPI sends that back as the HTTP response.  
7. **get_db**’s finally block runs and **closes** the session.

---

## 13.2 Training Flow (Explain to Team)

- Admin creates a **Person** (POST /persons).  
- Admin uploads **multiple photos** of that person (POST /train/ with person_id, name, files).  
- Backend reads each image, calls **FaceEncoder.encode_image()** → one embedding per face (or skips if no face).  
- Backend **averages** all embeddings and **L2-normalizes**.  
- Backend **pickles** and saves in **Person.embedding**.  
- So: **many photos → one average vector per person** stored in the database.

---

## 13.3 Recognition Flow (Explain to Team)

- Someone sends **one image** (POST /recognize/ or from webcam frame).  
- Backend loads **all Person** embeddings from DB and **L2-normalizes**.  
- Backend calls **FaceEncoder.detect_and_encode_faces(img)** → list of (embedding, bbox).  
- For each face: **cosine similarity** = dot product with all known embeddings; **best match** and **max_sim**. If **max_sim &gt; threshold** → recognized (name, id); else "Unknown".  
- Backend **draws** boxes and labels on the image and returns the image (or in webcam, stores the frame for preview and optionally **records attendance**).

---

## 13.4 Webcam Attendance Flow (Explain to Team)

- Staff/Admin calls **POST /webcam/start/**.  
- Backend **opens the camera** and starts a **background thread**.  
- In the thread we **loop**: read frame → every **Nth** frame run **recognize_faces_in_frame** (resize, detect, compare, **cooldown**, **record_attendance** to DB) → draw results → optionally save image → store frame for preview.  
- **record_attendance** ensures **one Attendance row per person per day** (create or update check_out_time, total_detections, duration).  
- Frontend can **GET /webcam/preview/** to show the live view and **POST /webcam/stop/** to stop.  
- So: **camera → loop → recognize every N frames → cooldown → one row per person per day**.

---

## 13.5 Part Separation for Team Explanation

You can say:

- **Part 1** — What the backend is and what it does (overview).  
- **Part 2** — How to set up and run it (prerequisites, install, .env, uvicorn).  
- **Part 3** — Folder structure and where each file lives.  
- **Part 4** — Configuration (config.py and every setting).  
- **Part 5** — Database (database.py + all models and tables).  
- **Part 6** — Security (passwords and JWT).  
- **Part 7** — Who can call what (deps.py and roles).  
- **Part 8** — Face encoding (face_encoder.py, encode_image, detect_and_encode_faces).  
- **Part 9** — Main API (auth, persons, train, recognize, attendance, settings, health).  
- **Part 10** — Webcam API (start, stop, preview, capture, attendance, export).  
- **Part 11** — Webcam service (camera loop, cooldown, record_attendance).  
- **Part 12** — How to run and test.  
- **Part 13** — End-to-end flow and how to explain training, recognition, and webcam to the team.

---

**End of PART 13.**  
**End of Backend Complete Guide.**

Use this document from **Part 1 to Part 13** to explain the backend from scratch to finish. Every part is separated so you can say “from Part X to Part Y” when explaining to a team member.
