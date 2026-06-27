# Full Frontend Explanation + Algorithms Used in the Project

This document has two parts: **Part A** is a full explanation of the frontend (structure, routing, auth, pages, API). **Part B** explains the **algorithms** the project uses (face detection, embedding, similarity, threshold, training, webcam). Use it to explain the frontend and the “how it works” to teachers or judges.

---

# PART A — Full Frontend Explanation

---

## A.1 What Is the Frontend?

The **frontend** is the part of the application that runs **in the user’s browser**. It is what the user sees and clicks. It is built with **React** (JavaScript/TypeScript) and **Vite**. It does **not** run face recognition or store data itself; it only **sends HTTP requests** to the backend API and **displays** the data (or errors) that the backend returns. So the frontend is the **interface** between the user and the backend.

---

## A.2 How the Frontend Is Built (Tech Stack)

- **React 18** — Library for building the UI (components, state, effects).
- **TypeScript** — Typed JavaScript so we have types for API responses and props.
- **Vite** — Build tool: development server, bundling, and production build.
- **React Router** — Handles URLs (routes) so we can have different “pages” (/, /auth, /app, /app/monitoring, etc.) without reloading the whole page.
- **Axios** — Library to send HTTP requests (GET, POST, PATCH, DELETE) to the backend. We use it from small **API modules** (auth, persons, attendance, webcam, settings).

So: **React + TypeScript + Vite + React Router + Axios**.

---

## A.3 Folder Structure (Frontend)

```
frontend/
├── src/
│   ├── main.tsx           ← Entry: renders App inside BrowserRouter + AuthProvider
│   ├── App.tsx            ← Defines all routes and RequireAuth / RequireRole
│   ├── styles.css         ← Global styles
│   ├── state/
│   │   └── AuthContext.tsx   ← Holds token, role, isAuthenticated; used by whole app
│   ├── components/
│   │   └── AppLayout.tsx     ← Sidebar + topbar + outlet for /app pages
│   ├── pages/
│   │   ├── Welcome.tsx       ← Landing: “Enter System” → /auth
│   │   ├── Login.tsx        ← Login / Register form; calls auth API
│   │   ├── Dashboard.tsx    ← Summary stats + latest attendance + quick links
│   │   ├── People.tsx       ← List persons, add/edit/delete, train with photos
│   │   ├── LiveMonitoring.tsx ← Start/stop webcam, show preview + detections
│   │   ├── Attendance.tsx   ← Table of attendance with date/type filters
│   │   ├── Settings.tsx     ← API base URL + recognition settings
│   │   └── AccessDenied.tsx ← Shown when user has wrong role for a page
│   └── api/
│       ├── http.ts         ← Axios instance + base URL + Bearer token
│       ├── auth.ts         ← login, register, me
│       ├── persons.ts      ← fetchPersons, createPerson, updatePerson, delete, trainPerson
│       ├── attendance.ts   ← fetchAttendance, fetchAttendanceSummary
│       ├── webcam.ts       ← startMonitoring, stopMonitoring, fetchStatus, fetchPreview
│       └── settings.ts    ← fetchRecognitionSettings, updateRecognitionSettings
├── index.html
├── package.json
└── vite.config.ts (or similar)
```

- **main.tsx** — Renders the app; wraps everything in **BrowserRouter** and **AuthProvider**.
- **App.tsx** — Defines **routes** and **guards** (RequireAuth, RequireRole).
- **state/AuthContext.tsx** — Single place for **login state** (token, role, isAuthenticated).
- **components/AppLayout.tsx** — Layout for **/app**: sidebar navigation + outlet where child routes (Dashboard, People, etc.) render.
- **pages/** — One component per “screen” (Welcome, Login, Dashboard, People, LiveMonitoring, Attendance, Settings, AccessDenied).
- **api/** — Functions that call the backend; all use the shared **http** (Axios) instance so the token is sent on every request.

---

## A.4 Entry Point and Auth Provider (main.tsx)

- **ReactDOM.createRoot** — Renders the app into the HTML element with id `"root"`.
- **BrowserRouter** — Enables routing (URLs like /auth, /app/monitoring).
- **AuthProvider** — Wraps the whole app so any component can use **useAuth()** to get token, role, setToken, setRole, isAuthenticated. So **login state is global**.
- **App** — The root component that contains all routes.

So the **foundation** of the frontend is: one root, router, auth provider, and then the App with routes.

---

## A.5 Routing and Guards (App.tsx)

**Routes:**

- **/** — Renders **Welcome** (landing page).
- **/login** — Redirects to **/auth**.
- **/auth** — Renders **Login** (login and register form).
- **/app** — Wrapped in **RequireAuth**. If the user is **not** logged in (no token), we **redirect** to **/login** (then to /auth). If logged in, we render **AppLayout**.
- **/app** (index) — Inside AppLayout, renders **Dashboard**.
- **/app/monitoring** — Wrapped in **RequireRole allowed={["admin","staff"]}**. Renders **LiveMonitoring**. If role is not admin or staff, we render **AccessDenied**.
- **/app/people** — **RequireRole allowed={["admin"]}**. Renders **People**. Only admin.
- **/app/attendance** — **RequireRole allowed={["admin","staff"]}**. Renders **Attendance**.
- **/app/settings** — **RequireRole allowed={["admin"]}**. Renders **Settings**. Only admin.
- **\*** (any other path) — Redirect to **/**.

**RequireAuth:**  
Uses **useAuth()**. If **!isAuthenticated** (no token), **Navigate to="/login"**. Otherwise renders **children** (here, AppLayout).

**RequireRole:**  
Uses **useAuth()** for **role**. If **role** is not in the **allowed** array, we render **AccessDenied**. Otherwise we render **children**.

So: **first** we check “logged in?” (RequireAuth), **then** we check “right role?” (RequireRole) for each protected page.

---

## A.6 Auth Context (AuthContext.tsx)

- **AuthContext** — A React Context that holds: **token**, **setToken**, **role**, **setRole**, **isAuthenticated** (true when token is not null).
- **Storage** — We keep **token** in **localStorage** under key `"attendance_token"` and **role** under `"attendance_role"`. So after refresh the user is still “logged in” if the token is there.
- **setToken:**  
  - If we set a new token we save it to localStorage.  
  - If we set **null** (logout) we remove token and role from localStorage and reset role to `"staff"` in state.
- **setRole** — Saves role to localStorage and state.
- **useAuth()** — Any component can call **useAuth()** to get token, setToken, role, setRole, isAuthenticated. So the **whole app** shares one login state.

So the **foundation** of auth on the frontend is: **token and role in state + localStorage**, and **AuthProvider** making them available everywhere.

---

## A.7 HTTP Client and API Base (http.ts)

- We create an **Axios instance** with **baseURL** from:  
  **localStorage "attendance_api_base"** → else **VITE_API_BASE_URL** (env) → else **"http://localhost:8000/api"**.
- So the user can change the backend URL from **Settings** (we save it in **attendance_api_base**), or we use the env variable at build time.
- **Request interceptor:**  
  Before every request we read **attendance_token** from localStorage. If it exists we set **Authorization: Bearer &lt;token&gt;** on the request. So **every API call** automatically sends the login token.

So: **one Axios instance**, **one base URL** (from localStorage or env), and **Bearer token** on every request.

---

## A.8 API Modules (What Each One Does)

**auth.ts**  
- **login(username, password)** — POST **/auth/login** with `{ username, password }`. Returns **access_token**, **token_type**, **role**.  
- **register(payload)** — POST **/auth/register** with full_name, email, password, role, department, note. Returns message, id, role.  
- **me()** — GET **/auth/me**. Returns current user info (used with token).

**persons.ts**  
- **fetchPersons(personType?)** — GET **/persons** with optional **person_type**. Returns **count**, **persons** (list).  
- **createPerson(payload)** — POST **/persons**. Returns **id**, **name**.  
- **updatePerson(id, payload)** — PATCH **/persons/{id}**.  
- **deactivatePerson(id)** — DELETE **/persons/{id}**.  
- **trainPerson(payload)** — POST **/train/** with **FormData**: person_id, name, person_type, optional email, department, person_code, and **files** (array of File). Sends multipart/form-data. Used to upload photos and train a person’s face.

**attendance.ts**  
- **fetchAttendance(params?)** — GET **/attendance** with optional **start_date**, **end_date**, **person_id**, **person_type**. Returns **count**, **records**.  
- **fetchAttendanceSummary(date?)** — GET **/attendance/summary** with optional **target_date**. Returns **date**, **total_people**, **present**, **attendance_rate**.

**webcam.ts**  
- **startMonitoring(camera_id?, save_images?)** — POST **/webcam/start/** with params.  
- **stopMonitoring()** — POST **/webcam/stop/**.  
- **fetchStatus()** — GET **/webcam/status/**. Returns monitoring_active, camera_initialized, attendance_summary, etc.  
- **fetchPreview()** — GET **/webcam/preview/**. Returns **frame_base64**, **timestamp**, **recognition_results** (name, person_id, confidence, recognized, bbox).

**settings.ts**  
- **fetchRecognitionSettings()** — GET **/settings/recognition**. Returns **recognition_threshold**, **live_recognition_stride**, **live_recognition_width**.  
- **updateRecognitionSettings(payload)** — PUT **/settings/recognition** with the same three fields.

All of these use the **http** instance from http.ts, so the token is always sent.

---

## A.9 Layout (AppLayout.tsx)

- Used for all routes under **/app** (after RequireAuth).
- **Sidebar** — Brand “AttendancePro”, then **nav items**: Dashboard, Live Monitoring, Students & Staff, Attendance, Settings. Each item is shown only if the user’s **role** is in that item’s **roles** array (e.g. “Students & Staff” and “Settings” only for **admin**). If the role is not allowed we show the label with “Restricted”. We use **NavLink** so the active link is highlighted. At the bottom we have **Logout** which calls **setToken(null)**.
- **Topbar** — Title “Attendance Monitoring System”, date, and a **role pill** (e.g. “Admin Access”).
- **Content** — **Outlet** from React Router: the child route (Dashboard, People, LiveMonitoring, etc.) renders here.

So the **foundation** of the app layout is: **sidebar by role** + **topbar** + **Outlet** for the current page.

---

## A.10 Each Page in Short

**Welcome**  
- Landing page. Shows “Welcome to AttendancePro”, “Enter System” button. On click we navigate to **/auth**. No API calls.

**Login**  
- **Login form:** username, password. On submit we call **login(username, password)** from auth API. On success we **setToken(data.access_token)** and **setRole(data.role)** and **navigate("/app")**. On error we show the backend error message.  
- **Register form:** full name, email, password, confirm password, role (staff/student), and optional fields (department, roll number, etc.). On submit we call **register(...)**. On success we show a message and can switch to login with email pre-filled.  
- So **Login** is the only place we **set token and role** after a successful login or register.

**Dashboard**  
- On load we call **fetchAttendanceSummary()** and **fetchAttendance()**. We show **total_people**, **present**, **attendance_rate** and a table of **latest 5** attendance records. We show **Quick Actions** links (Manage People, Attendance Reports, Settings) depending on **role** (from useAuth()). So Dashboard is the **home** after login and shows today’s summary and recent records.

**People**  
- We **fetchPersons(filter)** (filter = all / student / staff). We show a table of persons. We have a form to **add** or **edit** (name, email, department, person_code, person_type) and **upload files** (photos). On submit we **createPerson** or **updatePerson** and, if there are files, we call **trainPerson({ person_id, name, person_type, ..., files })**. So **People** is where admin **creates/edits persons** and **trains** their face with photos. We can also delete (delete person API).

**LiveMonitoring**  
- We show **Start** and **Stop** buttons. Start calls **startMonitoring()**, Stop calls **stopMonitoring()**. We call **fetchStatus()** on load and after start/stop. When **status.monitoring_active** is true we **poll** **fetchPreview()** every 1.5 seconds and show **frame_base64** as an image and **recognition_results** in a table. So **LiveMonitoring** is the **webcam UI**: start/stop and live preview + detections.

**Attendance**  
- We have **filters**: start_date, end_date, person_type. We call **fetchAttendance(filters)** and show the result in a table (name, type, date, check-in, check-out, etc.). So **Attendance** is the **attendance report** page with filters.

**Settings**  
- We show **API Base URL** (from localStorage); on save we **localStorage.setItem("attendance_api_base", apiBase)**. We **fetchRecognitionSettings()** and show **recognition_threshold**, **live_recognition_stride**, **live_recognition_width**. We can edit and call **updateRecognitionSettings(...)** to save. So **Settings** is where admin **changes backend URL** and **recognition parameters**.

**AccessDenied**  
- Shown when the user’s role is not in the **allowed** list for a route (e.g. staff tries to open /app/people). We just show a message that they don’t have access.

---

## A.11 Flow: User Opens Login and Logs In

1. User opens the app → **main.tsx** renders App inside **BrowserRouter** and **AuthProvider**.  
2. User is on **/** → **Welcome** is shown. User clicks “Enter System” → **navigate("/auth")**.  
3. **Login** page is shown. User enters username and password, clicks Login.  
4. **onSubmit** calls **login(username, password)** → **http.post("/auth/login", { username, password })**. The **http** instance uses the base URL (e.g. http://localhost:8000/api) and, at this point, there is no token yet.  
5. Backend returns **access_token** and **role**. We **setToken(data.access_token)** and **setRole(data.role)**. AuthContext saves them in state and in localStorage.  
6. We **navigate("/app")**. App.tsx sees **RequireAuth**: we have a token so **isAuthenticated** is true → we render **AppLayout**. The **index** route under **/app** renders **Dashboard**.  
7. Dashboard calls **fetchAttendanceSummary()** and **fetchAttendance()**. The **http** interceptor adds **Authorization: Bearer &lt;token&gt;** from localStorage. Backend validates the token and returns data. We show summary and table.

So the **foundation** of the flow is: **Welcome → Login → set token/role → redirect to /app → Dashboard (and other pages) use the same token for every API call.**

---

**End of PART A — Frontend.**

---

# PART B — Algorithms the Project Uses

---

## B.1 Overview: What “Algorithm” Means Here

The project uses **algorithms** in two places:  
(1) **Face recognition pipeline** — how we get a “face vector” from an image and how we compare two vectors to say “same person” or “different.”  
(2) **Attendance and webcam logic** — how we avoid duplicate records (one row per person per day, cooldown), and how we decide when to run recognition (every Nth frame).

Below we explain each **algorithm** or **rule** in simple terms.

---

## B.2 Face Detection (Finding a Face in an Image)

**What we use:**  
We use **DeepFace** with **detector_backend='opencv'**. So the **algorithm** for “where is the face?” is the **OpenCV-based face detector** built into DeepFace. It scans the image and returns **rectangles** (bounding boxes) where faces are found. We do **not** implement the detector ourselves; we use this built-in option.

**In simple words:**  
Given an image, the detector **finds regions** that look like a face (e.g. eyes, nose, mouth pattern) and returns their positions (x, y, width, height). So the **algorithm** here is “classic face detection” (e.g. Haar-like or similar) via OpenCV inside DeepFace.

---

## B.3 Face Embedding (Turning a Face into a Vector of Numbers)

**What we use:**  
We use the **VGG-Face** model through **DeepFace**. So the **algorithm** for “what does this face look like in number form?” is the **VGG-Face neural network**. It is a **deep convolutional neural network (CNN)** that was trained on a large dataset of faces. It takes a **cropped face image** and outputs a **fixed-length vector** (in our case **2624 numbers**). This vector is called an **embedding**. The property we use: **the same person** in different photos gives **similar** vectors (close in space); **different people** give **different** vectors (far apart).

**In simple words:**  
VGG-Face is a **pre-trained model** (we don’t train it). We only **use** it: input = face image, output = 2624 numbers. That list of numbers is the “fingerprint” of the face. So the **algorithm** here is **deep learning (CNN)** for **representation learning**: the network was trained so that the embedding captures the identity of the face.

---

## B.4 L2 Normalization (Making Vectors the Same Length)

**What we use:**  
We **normalize** every embedding so that its **length (L2 norm)** is 1. The formula:  
**v_normalized = v / ||v||**  
where **||v||** is the square root of the sum of squares of all elements of **v**.

**Why:**  
After normalization, the **dot product** of two vectors equals their **cosine similarity** (the cosine of the angle between them). So we can **compare** two faces by just taking the dot product of their normalized vectors; we don’t need to compute angles explicitly. We **always** normalize both the **stored** embeddings (in the database) and the **new** face’s embedding before comparing.

**In simple words:**  
The **algorithm** is: **divide the vector by its length**. Result: length = 1. Then **dot product = similarity** between two faces (same person → high dot product; different person → low).

---

## B.5 Cosine Similarity (Comparing Two Faces)

**What we use:**  
**Cosine similarity** between two vectors is the **cosine of the angle** between them. For two vectors **a** and **b** of length 1 it is:  
**cosine_similarity(a, b) = a · b** (dot product).  
Value is between **-1** and **1**. **1** = same direction (same person); **0** = unrelated; **-1** = opposite.

**In our project:**  
Because we **L2-normalize** all embeddings, we **compute** cosine similarity by **dot product**:  
**similarity = np.dot(embedding_stored, embedding_new)**.  
We do this for the new face against **every** stored person; we take the **maximum** similarity and the **person** that gave it. So the **algorithm** for “who is this face?” is: **compare the new embedding with all stored embeddings using dot product (cosine similarity) and pick the best match.**

**In simple words:**  
We use **dot product** as the **similarity score** between two face vectors. Higher score = more similar = more likely the same person.

---

## B.6 Recognition Threshold (When to Say “Recognized” vs “Unknown”)

**What we use:**  
We have a **threshold** (e.g. **0.4**) stored in settings. After we compute the **maximum** cosine similarity between the new face and all stored persons:

- If **max_similarity ≥ threshold** → we say **“Recognized”** and assign that person’s name and ID.  
- If **max_similarity &lt; threshold** → we say **“Unknown”**.

**In simple words:**  
The **algorithm** is a **single rule**: **if the best similarity is above the threshold, recognize as that person; otherwise label as Unknown.** So the project uses a **threshold-based decision** on top of cosine similarity.

---

## B.7 Training: Averaging Multiple Embeddings per Person

**What we use:**  
For each person we **do not** store one photo’s embedding. We store the **average** of several embeddings (one per training photo). Steps:

1. For each training image we get one embedding (via DeepFace/VGG-Face).  
2. We **average** them: **avg = mean(embedding_1, embedding_2, ..., embedding_k)**.  
3. We **L2-normalize** this average.  
4. We store this **single vector** in the database for that person.

**Why:**  
One photo can be bad (angle, light). So the **algorithm** we use for “one vector per person” is **averaging**: the **mean** of multiple embeddings is more stable and usually gives better recognition across different conditions.

**In simple words:**  
We use the **average** of several face vectors per person as the “representative” vector. So the project uses an **averaging algorithm** for training.

---

## B.8 One Row per Person per Day (Attendance Deduplication)

**What we use:**  
We **do not** create a new attendance row every time we see a person. We use **one row per person per day**. So the **algorithm** is:

- **First time** we see person P on date D: **create** a row (person_id=P, date=D, check_in_time=now, check_out_time=now, total_detections=1).  
- **Next times** we see P on date D: **update** that same row: set **check_out_time=now**, **total_detections += 1**, and **duration_minutes** from check_in to check_out.

**In simple words:**  
The **algorithm** for “when to create vs update” is: **one row per (person, date)**; first detection = create, later detections = update. So we use a **deduplication rule** in the database.

---

## B.9 Cooldown (Avoiding Too Many Records in Webcam)

**What we use:**  
In webcam mode we **do not** record the same person again until a **cooldown time** (e.g. **30 seconds**) has passed. So the **algorithm** is:

- When we **recognize** person P and write an attendance record (or update), we store **last_recognition_time[P] = now**.  
- For the next **30 seconds**, if we see P again we **do not** create another record; we skip.  
- After 30 seconds we **allow** recording P again (and update the same day’s row as in B.8).

**In simple words:**  
We use a **time-based cooldown**: same person can be “recorded” at most once per 30 seconds during live monitoring. So the project uses a **cooldown algorithm** to reduce duplicate records in the webcam loop.

---

## B.10 Stride (Running Recognition Every Nth Frame)

**What we use:**  
We **do not** run face recognition on **every** camera frame. We run it only every **Nth** frame (e.g. **N = 2**). So the **algorithm** is:

- **frame_index** increments every frame.  
- We run recognition only when **frame_index % N == 0**.  
- For other frames we **reuse** the last recognition result (for drawing) or do nothing for DB.

**Why:**  
Recognition (DeepFace) is **expensive**. So we use a **downsampling** rule: **process every Nth frame**. This is a **performance** algorithm: we trade a bit of “freshness” for lower CPU load.

**In simple words:**  
We use a **stride**: run the heavy face recognition only every 2nd (or 3rd, etc.) frame. So the project uses a **frame-sampling algorithm** in the webcam loop.

---

## B.11 Summary Table: Algorithms in the Project

| What | Algorithm / Rule | Where used |
|------|-------------------|------------|
| Face detection | OpenCV-based detector (via DeepFace) | Finding face regions in image |
| Face embedding | VGG-Face CNN (via DeepFace) | Converting face → 2624-dim vector |
| Normalization | L2 normalization (divide by L2 norm) | Before comparing vectors |
| Similarity | Cosine similarity = dot product (for unit vectors) | Comparing new face to stored faces |
| Recognition decision | Threshold: if max_similarity ≥ threshold → recognized | Assigning name or “Unknown” |
| Training | Average of multiple embeddings per person | One stored vector per person |
| Attendance dedup | One row per (person, date); update on later detections | Database attendance table |
| Webcam dedup | Cooldown: same person at most once per 30 s | Webcam monitoring loop |
| Performance | Stride: run recognition every Nth frame | Webcam frame loop |

---

## B.12 One-Paragraph Version for Teachers (Algorithms)

**The project uses these algorithms:**  
(1) **Face detection** — OpenCV (via DeepFace) to find face regions in an image.  
(2) **Face embedding** — VGG-Face (a pre-trained CNN via DeepFace) to turn each face into a 2624-dimensional vector.  
(3) **L2 normalization** — We divide each vector by its length so that length = 1; then **dot product = cosine similarity**.  
(4) **Similarity** — We compare the new face’s vector to all stored vectors using **dot product** (cosine similarity) and take the **maximum**.  
(5) **Threshold** — If that maximum is **above a threshold** (e.g. 0.4) we say “recognized” and assign that person’s name; otherwise “Unknown.”  
(6) **Training** — We **average** the embeddings from several photos per person and store one vector per person.  
(7) **Attendance** — We use **one row per person per day** and update it on each new detection (no duplicate rows per day).  
(8) **Webcam** — We use a **cooldown** (e.g. 30 seconds) so the same person is not recorded again too soon, and we run recognition only every **Nth frame** (stride) to save CPU. So the project is based on **deep learning (VGG-Face) for embeddings** and **cosine similarity + threshold** for recognition, plus **averaging**, **deduplication**, **cooldown**, and **stride** for robustness and performance.

---

**End of PART B — Algorithms.**

---

You can use **Part A** to explain the frontend (structure, routing, auth, pages, API) and **Part B** to explain which algorithms the project uses (detection, embedding, normalization, similarity, threshold, averaging, one row per day, cooldown, stride).
