# Code Reference — Which Code Is Used for Which Part

This document maps **each part/feature** of the project to the **exact code** that implements it: file path, function/component name, and a short description. Use it to explain “this part is done by this file / this function.”

---

## 1. Backend — API and Business Logic

### 1.1 App entry and routing

| Part | File | Code | What it does |
|------|------|------|----------------|
| Backend app start | `backend/app/main.py` | `app = FastAPI(...)` | Creates FastAPI app, CORS, includes routers |
| Mount API under `/api` | `backend/app/main.py` | `app.include_router(..., prefix="/api")` | All API routes live under `/api` |
| Database init on startup | `backend/app/main.py` | `init_database()` | Creates tables and bootstrap admin user |

---

### 1.2 Authentication

| Part | File | Code | What it does |
|------|------|------|--------------|
| Admin login | `backend/app/api/routes.py` | `login(payload: LoginPayload, db)` | POST `/api/auth/login` — checks AdminUser, returns JWT |
| User (staff/student) register | `backend/app/api/routes.py` | `register(payload: RegisterPayload, db)` | POST `/api/auth/register` — creates AppUser, hashes password |
| Get current user (JWT) | `backend/app/api/routes.py` | `me(current=Depends(get_current_any_user))` | GET `/api/auth/me` — returns who is logged in |
| Password hashing | `backend/app/core/security.py` | `hash_password()`, `verify_password()` | Hashing and checking passwords |
| JWT token creation | `backend/app/core/security.py` | `create_access_token(username, role)` | Creates Bearer token for login response |
| “Require admin” dependency | `backend/app/api/deps.py` | `get_current_admin()` | Use on routes that only admin can call |
| “Require staff or admin” | `backend/app/api/deps.py` | `get_current_staff_or_admin()` | Use on routes for staff/admin (e.g. webcam) |
| “Any logged-in user” | `backend/app/api/deps.py` | `get_current_any_user()` | Use on routes that need any role |

---

### 1.3 Persons (people to be recognized)

| Part | File | Code | What it does |
|------|------|------|--------------|
| List persons | `backend/app/api/routes.py` | `list_persons(person_type, db)` | GET `/api/persons` — list all/filter by type |
| Create person | `backend/app/api/routes.py` | `create_person(payload: PersonCreate, db)` | POST `/api/persons` — add new person (no face yet) |
| Update person | `backend/app/api/routes.py` | `update_person(person_id, payload: PersonUpdate, db)` | PATCH `/api/persons/{id}` |
| Delete/deactivate person | `backend/app/api/routes.py` | `delete_person(person_id, db)` | DELETE `/api/persons/{id}` (soft deactivate) |
| Train person (face photos) | `backend/app/api/routes.py` | `train_person(person_id, files, db)` | POST `/api/train/` — encode faces, average embedding, save to DB |

---

### 1.4 Face encoding and recognition

| Part | File | Code | What it does |
|------|------|------|--------------|
| Load VGG-Face model | `backend/app/services/face_encoder.py` | `FaceEncoder.preload_model()` | Loads DeepFace model once at startup |
| Encode one image to embedding | `backend/app/services/face_encoder.py` | `FaceEncoder.encode_image(image)` | Detects face, returns 2624-d vector (L2 normalized) |
| Detect and encode all faces in image | `backend/app/services/face_encoder.py` | `FaceEncoder.detect_and_encode_faces(image)` | Multiple faces → list of embeddings |
| L2 normalize vector | `backend/app/services/face_encoder.py` | `l2_normalize(vec)` | Makes embedding unit length for cosine similarity |
| Single-image recognition | `backend/app/api/routes.py` | `recognize_faces(file, db)` | POST `/api/recognize/` — compare uploaded image to all persons, return matches |

---

### 1.5 Webcam live monitoring

| Part | File | Code | What it does |
|------|------|------|--------------|
| Start webcam monitoring | `backend/app/api/webcam.py` | `start_webcam_monitoring(camera_id, save_images)` | POST `/api/webcam/start/` — starts background thread |
| Stop monitoring | `backend/app/api/webcam.py` | `stop_webcam_monitoring()` | POST `/api/webcam/stop/` |
| Get monitoring status | `backend/app/api/webcam.py` | `get_webcam_status()` | GET `/api/webcam/status/` |
| Get live preview (base64 frame) | `backend/app/api/webcam.py` | `get_webcam_preview()` | GET `/api/webcam/preview/` — for frontend video feed |
| Capture current frame & recognize | `backend/app/api/webcam.py` | `capture_current_frame(db)` | GET `/api/webcam/capture/` — one-shot capture + recognition |
| Background loop (read frame, recognize, attendance) | `backend/app/services/webcam_service.py` | `WebcamService` (e.g. loop that reads frame, calls encoder, writes attendance) | Runs in thread; stride/cooldown applied here |
| List attendance from session | `backend/app/api/webcam.py` | `get_attendance_records()` | GET `/api/webcam/attendance/` |
| Export attendance | `backend/app/api/webcam.py` | `export_attendance()` | POST `/api/webcam/export/` |
| Clear session attendance | `backend/app/api/webcam.py` | `clear_attendance_records()` | DELETE `/api/webcam/attendance/` |
| Attendance summary for session | `backend/app/api/webcam.py` | `get_attendance_summary()` | GET `/api/webcam/summary/` |

---

### 1.6 Attendance (database records)

| Part | File | Code | What it does |
|------|------|------|--------------|
| List attendance (filters) | `backend/app/api/routes.py` | `list_attendance(start_date, end_date, person_id, person_type, db)` | GET `/api/attendance` — used by Attendance page |
| Attendance summary (e.g. by date) | `backend/app/api/routes.py` | `attendance_summary(target_date, db)` | GET `/api/attendance/summary` — used by Dashboard |

---

### 1.7 Settings

| Part | File | Code | What it does |
|------|------|------|--------------|
| Get recognition settings | `backend/app/api/routes.py` | `get_recognition_settings()` | GET `/api/settings/recognition` — threshold, stride, width |
| Update recognition settings | `backend/app/api/routes.py` | `update_recognition_settings(payload: RecognitionSettings)` | PUT `/api/settings/recognition` |

---

### 1.8 Database and config

| Part | File | Code | What it does |
|------|------|------|--------------|
| DB connection and session | `backend/app/core/database.py` | `engine`, `SessionLocal`, `get_db()` | SQLAlchemy + MySQL; `get_db` used in route dependencies |
| Create tables & bootstrap | `backend/app/core/database.py` | `init_database()` | Creates all tables; creates default admin if none |
| Config (env vars) | `backend/app/core/config.py` | `Settings` (Pydantic) | DATABASE_URL, SECRET_KEY, RECOGNITION_THRESHOLD, STRIDE, etc. |
| Person, Attendance models | `backend/app/models/attendance.py` | `Person`, `Attendance`, etc. | ORM models for persons and attendance rows |
| Admin and app users | `backend/app/models/user.py` | `AdminUser`, `AppUser` | Admin (login) and staff/student users |

---

### 1.9 Health check

| Part | File | Code | What it does |
|------|------|------|--------------|
| Health endpoint | `backend/app/api/routes.py` | `health_check()` | GET `/api/health/` — simple “backend is up” |

---

## 2. Frontend — Pages and Features

### 2.1 Routing and layout

| Part | File | Code | What it does |
|------|------|------|--------------|
| Define all routes | `frontend/src/App.tsx` | `<Routes>`, `<Route path="..." element={...} />` | `/` → Welcome, `/auth` → Login, `/app` → layout with nested routes |
| “Must be logged in” | `frontend/src/App.tsx` | `RequireAuth` | Wraps `/app`; redirects to `/login` if not authenticated |
| “Must be admin/staff” | `frontend/src/App.tsx` | `RequireRole allowed={["admin","staff"]}` | Used for Live Monitoring, Attendance |
| “Admin only” | `frontend/src/App.tsx` | `RequireRole allowed={["admin"]}` | Used for People, Settings |
| App shell (sidebar + content) | `frontend/src/components/AppLayout.tsx` | `AppLayout` | Sidebar nav + `<Outlet />` for Dashboard, People, etc. |
| Sidebar links by role | `frontend/src/components/AppLayout.tsx` | Nav links filtered by `role` | Shows Dashboard, Monitoring, People (admin), Attendance, Settings (admin) |

---

### 2.2 Auth and global state

| Part | File | Code | What it does |
|------|------|------|--------------|
| Auth state (token, role) | `frontend/src/state/AuthContext.tsx` | `AuthProvider`, `useAuth()` | Holds token & role; reads from localStorage |
| Login/Register UI | `frontend/src/pages/Login.tsx` | `Login` component | Forms; calls login/register API; saves token and role |
| API client (base URL, auth header) | `frontend/src/api/http.ts` | Axios instance + interceptor | Adds `Authorization: Bearer <token>`; baseURL from env or settings |
| Login/register API calls | `frontend/src/api/auth.ts` | `login()`, `register()`, `me()` | POST login/register, GET me |

---

### 2.3 Welcome and landing

| Part | File | Code | What it does |
|------|------|------|--------------|
| Landing page | `frontend/src/pages/Welcome.tsx` | `Welcome` | “Enter System” button; sets `isTransitioning` for split/flash animation, then navigates to `/auth` |
| Honeycomb split + flash | `frontend/src/pages/Welcome.tsx` | Classes `honeycomb-split active`, `bright-flash active` | Triggers CSS animations in `styles.css` when leaving |

---

### 2.4 Dashboard

| Part | File | Code | What it does |
|------|------|------|--------------|
| Dashboard page | `frontend/src/pages/Dashboard.tsx` | `Dashboard` | Shows attendance summary and recent list; quick links to Monitoring, People, Attendance |
| Fetch summary | `frontend/src/api/attendance.ts` | `fetchAttendanceSummary()` | GET `/api/attendance/summary` |
| Fetch recent attendance | `frontend/src/api/attendance.ts` | `fetchAttendance()` | GET `/api/attendance` (optional params) |

---

### 2.5 People (admin)

| Part | File | Code | What it does |
|------|------|------|--------------|
| People CRUD page | `frontend/src/pages/People.tsx` | `People` | List persons; add/edit/delete; upload photos and “Train” |
| List/create/update/delete persons | `frontend/src/api/persons.ts` | `fetchPersons()`, `createPerson()`, `updatePerson()`, `deactivatePerson()` | GET/POST/PATCH/DELETE `/api/persons` |
| Train person (upload photos) | `frontend/src/api/persons.ts` | `trainPerson(personId, files)` | POST `/api/train/` with FormData (files) |

---

### 2.6 Live monitoring

| Part | File | Code | What it does |
|------|------|------|--------------|
| Live monitoring page | `frontend/src/pages/LiveMonitoring.tsx` | `LiveMonitoring` | Start/Stop buttons; shows preview image (from base64); can show last recognition / status |
| Start/stop and status | `frontend/src/api/webcam.ts` | `startMonitoring()`, `stopMonitoring()`, `fetchStatus()` | POST start/stop, GET `/api/webcam/status/` |
| Preview image | `frontend/src/api/webcam.ts` | `fetchPreview()` | GET `/api/webcam/preview/` — frontend polls and sets as img src |

---

### 2.7 Attendance history

| Part | File | Code | What it does |
|------|------|------|--------------|
| Attendance page | `frontend/src/pages/Attendance.tsx` | `Attendance` | Date range and filters; table of attendance records |
| Fetch attendance list | `frontend/src/api/attendance.ts` | `fetchAttendance(params)` | GET `/api/attendance` with query params |

---

### 2.8 Settings (admin)

| Part | File | Code | What it does |
|------|------|------|--------------|
| Settings page | `frontend/src/pages/Settings.tsx` | `Settings` | API base URL, recognition threshold, stride, width |
| Get/update recognition settings | `frontend/src/api/settings.ts` | `fetchRecognitionSettings()`, `updateRecognitionSettings()` | GET/PUT `/api/settings/recognition` |

---

### 2.9 Access denied and styles

| Part | File | Code | What it does |
|------|------|------|--------------|
| Access denied screen | `frontend/src/pages/AccessDenied.tsx` | `AccessDenied` | Shown when user hits a route their role cannot access |
| All global and component styles | `frontend/src/styles.css` | Classes used in TSX (e.g. `.page`, `.card`, `.auth-panel-slide`) | Layout, colors, **all animations** (see ANIMATIONS_AND_WHERE_THEY_ARE.md) |

---

## 3. Quick lookup: “I want to change…”

| If you want to… | Backend | Frontend |
|------------------|--------|----------|
| Change login logic | `backend/app/api/routes.py` → `login`, `backend/app/core/security.py` | `frontend/src/pages/Login.tsx`, `frontend/src/api/auth.ts` |
| Change how faces are encoded | `backend/app/services/face_encoder.py` | — |
| Change recognition threshold / stride | `backend/app/core/config.py`, `backend/app/api/routes.py` (settings endpoints) | `frontend/src/pages/Settings.tsx`, `frontend/src/api/settings.ts` |
| Change webcam loop (stride, cooldown) | `backend/app/services/webcam_service.py`, `backend/app/core/config.py` | — |
| Change attendance list or summary | `backend/app/api/routes.py` → `list_attendance`, `attendance_summary` | `frontend/src/pages/Attendance.tsx`, `Dashboard.tsx`, `frontend/src/api/attendance.ts` |
| Change sidebar or app layout | — | `frontend/src/components/AppLayout.tsx` |
| Change any animation | — | `frontend/src/styles.css` (and component classNames); see ANIMATIONS_AND_WHERE_THEY_ARE.md |
| Add a new API endpoint | `backend/app/api/routes.py` or `backend/app/api/webcam.py` | Add call in corresponding `frontend/src/api/*.ts` and use in page |

---

## 4. Summary

- **Backend:** `main.py` wires the app; `routes.py` has auth, persons, train, recognize, attendance, settings, health; `webcam.py` has all webcam endpoints; `face_encoder.py` does face encoding; `webcam_service.py` does the webcam loop; `database.py` and `config.py` handle DB and config; `deps.py` handles “who is allowed” for each route.
- **Frontend:** `App.tsx` defines routes and guards; `AuthContext.tsx` holds auth state; `AppLayout.tsx` is the shell; each page in `pages/` uses API functions from `api/`; all animations and transitions are in `styles.css` and are referenced in ANIMATIONS_AND_WHERE_THEY_ARE.md.

Use this document to say exactly “this part is implemented in this file, in this function/component.”
