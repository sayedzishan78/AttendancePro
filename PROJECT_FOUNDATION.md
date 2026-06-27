# Foundation of Our Project — Multiface Recognition & Attendance System

This document explains the **foundation** of the project: the core idea, the problem we solve, the main building blocks, and how they work together. Use it to introduce the project to teachers, judges, or team members.

---

## 1. The Core Idea (One Sentence)

**We built a system that uses AI-based face recognition to automatically mark who is present, by recognizing multiple faces from photos or a live camera and recording attendance in a database, with different access for admin, staff, and students.**

That is the foundation: **automate attendance using faces**, support **multiple faces at once**, and control **who can do what** through roles.

---

## 2. The Problem We Want to Solve

Manual attendance has real-world problems:

- **Time-consuming** — Calling roll or passing a sheet takes time every day.
- **Easy to fake** — Someone else can mark for an absent friend (proxy).
- **Hard to use** — Finding who was absent on which date or generating reports is difficult when everything is on paper or in simple spreadsheets.
- **No proof** — There is no automatic record of “who was actually there and when.”

So the **foundation of the project** is: **replace manual attendance with something automatic, reliable, and easy to analyze.**

---

## 3. Why Face Recognition?

We could use cards, fingerprints, or RFID. We chose **face recognition** because:

- **Contactless** — No need to touch a device or carry a card.
- **Uses existing cameras** — Laptop webcam or a single camera at the door is enough.
- **Multiple people at once** — One image or one camera frame can contain several faces; we can identify all of them in one go (“multiface”).
- **Familiar and understandable** — Everyone understands “the camera sees who is there.”

So the **foundation** includes: **face recognition as the way we identify people**, and **multiface** as the way we handle groups.

---

## 4. The Three Pillars of the System

Think of the project as standing on **three pillars**:

---

### Pillar 1 — Identity (Who Can We Recognize?)

- We need a **list of people** the system knows (e.g. students and staff).
- For each person we need a **face representation** the computer can compare. We do **not** store photos for recognition; we store a **vector of numbers** (embedding) that represents their face.
- We get this by **training**: the admin uploads several photos of the person; the system extracts a face vector from each photo, **averages** them, and saves that single vector in the database. So the **foundation of identity** is: **one vector per person**, stored in the database.

---

### Pillar 2 — Recognition (Is This Face Someone We Know?)

- When we see a **new** face (from an uploaded image or from the camera), we need to answer: “Is this one of our trained people, and if so, who?”
- We do this by:  
  (1) **Converting** the new face into the same kind of vector (embedding).  
  (2) **Comparing** that vector with all stored vectors using a similarity measure (cosine similarity).  
  (3) If the **best match** is above a **threshold**, we say “this is that person”; otherwise “Unknown.”  
- So the **foundation of recognition** is: **same type of vector for everyone**, and **comparison by similarity** with a threshold.

---

### Pillar 3 — Attendance and Access (Who Was Present and Who Can Do What?)

- **Attendance** — When we recognize someone (from an image or webcam), we **record** it: who (person_id), when (date and time), and how confident we were. We store this in a database so we can later see “who was present on which day” and generate reports. So the **foundation of attendance** is: **one record per person per day** (with check-in/check-out and optional proof image).
- **Access** — Not everyone should do everything. We have **roles**:  
  - **Admin** — Full control: add/edit people, train faces, run recognition, manage attendance, webcam, settings.  
  - **Staff** — Can run webcam and view attendance; cannot manage people or settings.  
  - **Student** — Can log in and see the dashboard (limited access).  
  So the **foundation of access** is: **login with username/email and password**, then a **token (JWT)** that carries “who you are” and “your role,” and the backend **checks this on every request**.

---

## 5. How the System Is Built (Architecture in Simple Words)

The **technical foundation** is a **three-layer** setup:

---

### Layer 1 — Frontend (What the User Sees and Clicks)

- A **web application** that runs in the browser (we use **React**).
- It has screens for: login, dashboard, people list, training (upload photos), live webcam, attendance list, and settings.
- It **does not** do face recognition or store data itself. It only **sends requests** to the backend (e.g. “log me in,” “train this person,” “start webcam,” “show attendance”) and **displays** what the backend sends back.
- So the **foundation** here is: **the user talks to the system through this web interface.**

---

### Layer 2 — Backend (The Brain and the Worker)

- A **server application** (we use **FastAPI** in Python) that:
  - **Receives** requests from the frontend (e.g. login, upload image, start webcam).
  - **Checks** who is logged in and their role (using the token).
  - **Does the work**: talks to the database, runs face recognition (using **DeepFace** and **OpenCV**), and runs the webcam loop when live monitoring is on.
  - **Sends back** responses: JSON (e.g. list of persons, attendance) or files (e.g. image with names drawn).
- So the **foundation** here is: **all business logic and face processing happen on the backend**; the frontend only sends and receives.

---

### Layer 3 — Database (What We Remember)

- A **database** (we use **MySQL**) that stores:
  - **Persons** — Who we know (name, email, department, type) and their **face vector** (embedding).
  - **Attendance** — Who was present on which date, at what time, with optional proof image path.
  - **Users** — Who can log in (admin, staff, student) and their hashed passwords.
- So the **foundation** here is: **persistent storage** for identity, attendance, and access — the backend reads and writes this, the frontend never talks to the database directly.

---

## 6. The Flow in One Picture (Foundation Level)

```
User (Browser)
    ↓
[ Frontend: React ]
    ↓  HTTP (e.g. POST /api/train/, GET /api/attendance)
[ Backend: FastAPI ]
    ↓                    ↓
[ Database: MySQL ]   [ Face recognition: DeepFace + OpenCV ]
    ↑                    ↑
    └────────────────────┘
         (backend uses both)
```

- **User** uses the **frontend**.
- **Frontend** sends **requests** to the **backend**.
- **Backend** uses the **database** (to store/load persons, attendance, users) and **face recognition** (to get vectors and compare faces). It never stores raw images for recognition; it stores **vectors** and **attendance rows** (with optional image **paths** for proof).
- **Backend** sends **responses** back to the **frontend**, which shows them to the user.

So the **foundation** is: **User → Frontend → Backend → Database + Face recognition → Backend → Frontend → User.**

---

## 7. Key Concepts That Underpin Everything

These are the **foundational concepts** that the whole project rests on:

| Concept | Meaning in Our Project |
|--------|--------------------------|
| **Embedding / vector** | A fixed list of numbers that represents a face. Same person → similar vectors; different person → different vectors. We store one (averaged) vector per person and compare new faces to these. |
| **Training / enrollment** | Giving the system photos of a person so it can compute and save their face vector. We do **not** save the photos; we only save the vector. |
| **Recognition** | Taking a new image (or frame), getting a vector for each face, and comparing to stored vectors to get a name (or “Unknown”). |
| **Threshold** | Minimum similarity (e.g. 0.4) to say “recognized.” Below that we say “Unknown.” |
| **One row per person per day** | We don’t create a new attendance row every time we see someone; we have one row per person per day and update it (e.g. check-out time, duration). This is the foundation of how we record attendance. |
| **Token (JWT)** | After login, the backend gives the frontend a signed token. The frontend sends it with every request. The backend decodes it to know “who” and “which role” — that is the foundation of access control. |

---

## 8. Summary: What Is the Foundation?

- **Idea:** Automate attendance using **face recognition**, support **multiple faces** (multiface), and control **who can do what** (roles).
- **Problem:** Manual attendance is slow, easy to fake, and hard to analyze; we want it **automatic, reliable, and useful**.
- **Choice:** **Face recognition** (contactless, one camera, many faces at once).
- **Three pillars:** (1) **Identity** — one vector per person in the DB. (2) **Recognition** — compare new face vector to stored vectors with a threshold. (3) **Attendance and access** — record who was present when, and enforce admin/staff/student via login and JWT.
- **Architecture:** **Frontend** (React) → **Backend** (FastAPI) → **Database** (MySQL) + **Face recognition** (DeepFace + OpenCV). User only talks to the frontend; the backend does all work and uses DB and face logic.
- **Concepts:** Embedding, training (no photo storage, only vector), recognition (similarity + threshold), one attendance row per person per day, JWT for access.

That is the **foundation** of your project: the core idea, the problem, the three pillars, the three layers, and the key concepts that everything else is built on.
