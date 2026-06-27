# Multiface Recognition & Attendance System — Seminar Script (A to Z)

Use this as your speaking script or convert sections into slides. Cover each part in order for a complete seminar.

---

## 1. Title & Introduction (1–2 min)

**What to say:**

> "Good morning/afternoon. Today I am presenting our project: **Multiface Recognition and Professional Attendance Monitoring System**.
>
> This is a full-stack application that uses **face recognition** to mark attendance automatically. It supports **multiple faces in a single image**, **live webcam monitoring**, and **role-based access** for admin, staff, and students. I will walk you through the problem, solution, technologies, architecture, and implementation from A to Z."

---

## 2. Problem Statement & Motivation (2–3 min)

**What to say:**

> "Manual attendance (roll call, sheets) is time-consuming, prone to proxy, and hard to analyze. We wanted:
> - **Automatic** attendance using face recognition  
> - **Multi-face** support: detect and identify several people in one image or video  
> - **Real-time** monitoring via webcam  
> - **Secure** login and different permissions for admin, staff, and students  
> - **Stored history** and reporting (who was present, when, with proof images)  
>
> Our system addresses all of these."

**Slide/point:** Problem → Manual attendance, proxy, no analytics. Solution → AI-based multi-face recognition + web app.

---

## 3. High-Level Solution Overview (2 min)

**What to say:**

> "The system has two main parts:
> 1. **Backend** — A REST API built with **FastAPI** (Python). It handles authentication, stores persons and their face data, runs face recognition (using **DeepFace**), and manages attendance and webcam monitoring.
> 2. **Frontend** — A **React** single-page app (with **Vite** and **TypeScript**) that provides login, dashboard, live monitoring, people management, attendance reports, and settings.
>
> Data is stored in **MySQL**. Face recognition uses **DeepFace** (VGG-Face model) and **OpenCV** for detection and encoding."

**Slide:** Diagram: **User (Browser)** ↔ **React Frontend** ↔ **FastAPI Backend** ↔ **MySQL**; Backend uses **DeepFace + OpenCV**.

---

## 4. Technologies Used (2–3 min)

**What to say:**

> "**Backend:**  
> - **FastAPI** — async REST API, automatic docs (Swagger/ReDoc).  
> - **SQLAlchemy** — ORM for MySQL (persons, attendance, users).  
> - **DeepFace** — face detection and 2624-dimensional embeddings (VGG-Face).  
> - **OpenCV** — image decode, resize, drawing bounding boxes.  
> - **PyMySQL** — MySQL driver.  
> - **JWT (python-jose)** — access tokens.  
> - **Passlib** — password hashing (pbkdf2_sha256).  
>
> **Frontend:**  
> - **React 18** + **TypeScript**.  
> - **Vite** — build and dev server.  
> - **React Router** — routes (/, /auth, /app/dashboard, etc.).  
> - **Axios** — HTTP client to backend API.  
>
> **Database:**  
> - **MySQL** — persons, attendance, sessions, admin users, app users (staff/student)."

**Slide:** Table: Backend | Frontend | Database | AI/ML.

---

## 5. System Architecture (3–4 min)

**What to say:**

> "**Layers:**  
> 1. **Presentation** — React UI (login, dashboard, live monitoring, people, attendance, settings).  
> 2. **API** — FastAPI routes under `/api`: auth, persons, train, recognize, attendance, webcam, settings, health.  
> 3. **Business logic** — Services: `FaceEncoder` (DeepFace), `WebcamService` (camera + recognition loop).  
> 4. **Data** — SQLAlchemy models, MySQL.  
>
> **Auth flow:** User logs in with username/email and password. Backend returns a **JWT**. Frontend stores the token and role (admin/staff/student) in localStorage and sends `Authorization: Bearer <token>` on every API call. Backend validates JWT and checks role for protected routes.  
>
> **Face flow:**  
> - **Training:** Admin uploads images for a person → backend extracts face embeddings with DeepFace → average embedding is L2-normalized and stored in DB (pickled) with person metadata.  
> - **Recognition:** Image (file or webcam frame) → detect and encode all faces → compare each embedding to stored ones using **cosine similarity** → if similarity above threshold, mark as recognized and record attendance."

**Slide:** Request flow: Browser → React → Axios → FastAPI → Service/DB; Face pipeline: Image → DeepFace (detect + encode) → Compare → Match/Unknown.

---

## 6. Database Design (2–3 min)

**What to say:**

> "We use **MySQL** with these main tables:  
>
> - **persons** — id, name, email, department, person_code, person_type (student/staff), **embedding** (BLOB: serialized face vector), created_at, is_active. This is the face gallery.  
> - **attendance** — id, person_id (FK), date, check_in_time, check_out_time, confidence, image_path, total_detections, duration_minutes. One row per person per day; check_out and duration updated on later detections.  
> - **attendance_sessions** — for continuous monitoring: person_id, session_start, session_end, confidence, image_count, status (active/completed).  
> - **admin_users** — id, username, password_hash, is_active (admin login).  
> - **app_users** — id, full_name, email, password_hash, role (staff/student), department, note, is_active (staff/student login).  
>
> Database and tables are created automatically on startup; a default admin user is bootstrapped if none exists."

**Slide:** ER diagram or table list with key columns.

---

## 7. Face Recognition Pipeline (4–5 min)

**What to say:**

> "Face recognition has two phases: **enrollment** and **recognition**.  
>
> **Enrollment (training):**  
> - Admin selects a person (or creates one) and uploads **multiple photos** of that person.  
> - For each image, we call DeepFace’s **represent** with the VGG-Face model and OpenCV detector. DeepFace returns a **2624-dimensional embedding** per face.  
> - We take the **average** of all embeddings for that person and **L2-normalize** it. That vector is **pickled** and stored in `persons.embedding`.  
> - Using 3–5 clear photos from different angles/lighting improves accuracy.  
>
> **Recognition:**  
> - Given an image (upload or webcam frame), we again use DeepFace to **detect and encode all faces** (same model and detector).  
> - For each detected face we get an embedding; we L2-normalize it.  
> - We load all stored person embeddings from the DB and compute **cosine similarity** (dot product of normalized vectors) with this face.  
> - If the **maximum similarity is above a threshold** (e.g. 0.4, configurable), we assign that person’s name and ID; otherwise we label **Unknown**.  
> - For live webcam we only run recognition every **Nth frame** (stride) and optionally resize to a smaller width to keep performance good."

**Slide:** Training: Photos → DeepFace → embeddings → average → normalize → DB. Recognition: Image → DeepFace → embeddings → cosine similarity → threshold → name/Unknown.

---

## 8. Backend API — Main Endpoints (3–4 min)

**What to say:**

> "All API routes are under `/api`.  
>
> **Auth:**  
> - `POST /api/auth/login` — username/email + password → JWT and role.  
> - `POST /api/auth/register` — register staff/student (full_name, email, password, role, department).  
> - `GET /api/auth/me` — current user info (needs token).  
>
> **People (admin only):**  
> - `GET /api/persons` — list all persons (optional filter by type).  
> - `POST /api/persons` — create person (name, email, department, person_code, person_type).  
> - `PATCH /api/persons/{id}` — update.  
> - `DELETE /api/persons/{id}` — delete (cascades to attendance).  
>
> **Training (admin):**  
> - `POST /api/train/` — form data: person_id, name, person_type, optional email/department/person_code, and **files** (multiple images). Backend encodes faces, averages, and saves embedding.  
>
> **Recognition (admin):**  
> - `POST /api/recognize/` — upload one image; returns a **JPEG with bounding boxes and labels** (name + confidence or Unknown).  
>
> **Attendance (staff/admin can view):**  
> - `GET /api/attendance` — list records with filters (date range, person_id, person_type).  
> - `GET /api/attendance/summary` — total people, present count, attendance rate for a date.  
>
> **Webcam (staff/admin):**  
> - `POST /api/webcam/start/` — start live monitoring (camera_id, save_images).  
> - `POST /api/webcam/stop/` — stop.  
> - `GET /api/webcam/status/` — monitoring active or not, camera status, attendance summary.  
> - `GET /api/webcam/capture/` — one-shot capture + recognition + optional save.  
> - `GET /api/webcam/preview/` — current frame as base64.  
> - `GET /api/webcam/attendance/` — in-memory attendance list from current run.  
> - `POST /api/webcam/export/` — export to JSON.  
>
> **Settings (admin):**  
> - `GET/PUT /api/settings/recognition` — threshold, stride, live width.  
>
> **Health:**  
> - `GET /api/health/` — status and whether face encoder is initialized.  
>
> API docs: **/docs** (Swagger) and **/redoc**."

**Slide:** List of endpoint groups and methods.

---

## 9. Authentication & Authorization (2 min)

**What to say:**

> "We use **JWT** (Bearer token). On login, backend checks either **admin_users** (username) or **app_users** (email), verifies password with Passlib, and issues a token containing subject (username/email) and **role** (admin, staff, student).  
>
> **Role-based access:**  
> - **Admin** — full access: people CRUD, train, recognize, attendance, webcam, settings.  
> - **Staff** — dashboard, live monitoring, attendance; no people management or settings.  
> - **Student** — dashboard only (and any routes we expose for students).  
>
> Frontend stores token and role; for protected routes it checks role and redirects to Access Denied if not allowed. Backend uses dependencies like `get_current_admin`, `get_current_staff_or_admin`, `get_current_any_user` to enforce this."

**Slide:** Roles vs permissions table.

---

## 10. Live Webcam Monitoring (3 min)

**What to say:**

> "Staff or admin can start **webcam monitoring** from the Live Monitoring page.  
>
> Backend opens the camera with OpenCV, runs a loop in a **background thread**. Every **Nth frame** (stride), it resizes the frame to a configured width, runs **detect_and_encode_faces**, then compares each face to DB embeddings. Recognized persons get **attendance records** (with a cooldown so the same person isn’t recorded repeatedly within 30 seconds).  
> Check-in/check-out and duration are updated in the **attendance** table; optional **attendance_sessions** track continuous presence.  
> Annotated frames (boxes and labels) can be returned as base64 for **preview** in the UI. Optionally we **save images** when someone is recognized.  
> Start/stop/status/capture/preview/export are all exposed as API endpoints so the React app can control and display the flow."

**Slide:** Webcam flow: Camera → Frame loop → Every Nth frame → Recognize → Update DB + optional image save → Preview/Export.

---

## 11. Frontend Structure & Pages (3 min)

**What to say:**

> "The frontend is a **React + TypeScript** SPA.  
>
> **Routes:**  
> - `/` — Welcome.  
> - `/auth` — Login (and register).  
> - `/app` — Protected app layout (sidebar + outlet).  
> - `/app` (index) — **Dashboard** (overview, summary).  
> - `/app/monitoring` — **Live Monitoring** (start/stop webcam, preview, status) — admin/staff.  
> - `/app/people` — **People** (list, add, edit, delete, **train with photos**) — admin only.  
> - `/app/attendance` — **Attendance** (list, filters, date range) — admin/staff.  
> - `/app/settings` — **Settings** (API base URL, recognition threshold, stride, width) — admin only.  
>
> **Auth:** We use an **AuthContext** that holds token and role in state and localStorage. Axios is configured to send the Bearer token on each request. **RequireAuth** redirects to login if not logged in; **RequireRole** shows Access Denied for wrong role.  
>
> API base URL can be set in Settings or via env so the same frontend can talk to different backends."

**Slide:** Sitemap or route tree.

---

## 12. Key Frontend–Backend Flows (2 min)

**What to say:**

> "**Login:** User enters username/email and password → POST `/api/auth/login` → store token and role → redirect to `/app`.  
>
> **Training:** Admin goes to People, selects or creates a person, uploads multiple images → POST `/api/train/` with person_id, name, files → backend returns success and faces_processed.  
>
> **Live monitoring:** User opens Live Monitoring → Start → POST `/api/webcam/start/` → backend starts thread; frontend can poll `/api/webcam/preview/` or `/api/webcam/status/` to show stream and status; Stop → POST `/api/webcam/stop/`.  
>
> **Attendance report:** User picks date range (and optional filters) → GET `/api/attendance` → table shows person, date, check-in, check-out, confidence, duration, image link."

**Slide:** Sequence diagram for one flow (e.g. login or train).

---

## 13. Configuration & Deployment (1–2 min)

**What to say:**

> "Backend uses **pydantic-settings** and a `.env` file: database URL, secret key, JWT expiry, admin default credentials, **recognition threshold**, **detection size**, **live recognition stride and width**, max upload size, output directory.  
>
> Frontend uses **Vite**: build with `npm run build`; API base can be set with `VITE_API_BASE_URL` or in Settings.  
>
> To run: start **MySQL**, run backend with `uvicorn app.main:app --reload` (e.g. port 8000), run frontend with `npm run dev` (e.g. port 5173). First run, DeepFace may download the VGG-Face model (~500MB) once."

**Slide:** Backend .env variables; Frontend env; Run commands.

---

## 14. Challenges & How We Addressed Them (2 min)

**What to say:**

> "**Accuracy:** Single poor photo gives bad embedding — we **average multiple photos** per person and recommend 3–5 varied images.  
>
> **Performance:** Running DeepFace on every frame is heavy — we use **stride** (every Nth frame) and **resize** for live recognition.  
>
> **Duplicate attendance:** Same person detected in consecutive frames — we use a **cooldown** (e.g. 30 seconds) per person before recording again.  
>
> **Security:** Passwords are hashed (Passlib); API is protected with JWT and role checks.  
>
> **Usability:** Admin vs staff vs student roles so each user sees only relevant menus and data."

**Slide:** Challenge → Solution bullets.

---

## 15. Possible Future Enhancements (1 min)

**What to say:**

> "We could add:  
> - **Export** attendance to CSV/Excel.  
> - **Notifications** (e.g. when someone is marked present).  
> - **Liveness detection** to reduce spoofing.  
> - **Multiple cameras** or camera selection in UI.  
> - **Student self-view** of their own attendance.  
> - **Dashboard charts** (attendance rate over time, peak times)."

**Slide:** Future work list.

---

## 16. Conclusion (1 min)

**What to say:**

> "To summarize: we built a **full-stack Multiface Recognition and Attendance System** with FastAPI, React, MySQL, and DeepFace. We covered **problem and motivation**, **technologies**, **architecture**, **database**, **face pipeline**, **API**, **auth**, **webcam monitoring**, **frontend structure**, **configuration**, and **challenges**.  
>
> Thank you. I am happy to take questions."

---

## Quick Reference — Project Structure

**Backend:**  
- `app/main.py` — FastAPI app, CORS, router.  
- `app/api/routes.py` — auth, persons, train, recognize, attendance, settings, health.  
- `app/api/webcam.py` — webcam start/stop/status/capture/preview/export.  
- `app/api/deps.py` — JWT and role dependencies.  
- `app/core/config.py` — settings; `database.py` — engine, session, init DB; `security.py` — hash, JWT.  
- `app/models/attendance.py` — Person, Attendance, AttendanceSession; `user.py` — AdminUser, AppUser.  
- `app/services/face_encoder.py` — DeepFace encode/detect; `webcam_service.py` — camera loop, recognition, DB write.

**Frontend:**  
- `src/App.tsx` — routes, RequireAuth, RequireRole.  
- `src/state/AuthContext.tsx` — token, role, isAuthenticated.  
- `src/pages/` — Login, Welcome, Dashboard, LiveMonitoring, People, Attendance, Settings, AccessDenied.  
- `src/components/AppLayout.tsx` — layout and nav.

Use this script section-by-section in your seminar to cover the project from A to Z.
