# Multiface Recognition & Attendance — Short Seminar Version

Use this when you have **10–15 minutes**. Hit only the key points.

---

## 1. Intro (30 sec)

> "Our project is a **Multiface Recognition and Attendance System**. It uses **AI face recognition** to mark attendance automatically from photos or live webcam, with **admin, staff, and student** roles. I'll cover: what we built, tech stack, how it works, and a quick demo flow."

---

## 2. Problem & Solution (1 min)

> "Manual attendance is slow and easy to fake. We built a system that:
> - **Trains** on multiple photos per person  
> - **Recognizes** multiple faces in one image or from webcam  
> - **Records** check-in/check-out in a database  
> - **Restricts** features by role (admin/staff/student)"

---

## 3. Tech Stack (1 min)

> "**Backend:** FastAPI, MySQL (SQLAlchemy), DeepFace for face embeddings, OpenCV, JWT for auth.  
> **Frontend:** React, TypeScript, Vite, React Router, Axios.  
> **Flow:** Browser → React → FastAPI API → MySQL; face recognition uses DeepFace (VGG-Face) and cosine similarity."

---

## 4. How Face Recognition Works (2 min)

> "**Training:** Admin uploads 3–5 photos per person. Backend extracts a **face embedding** (vector) for each face with DeepFace, averages them, normalizes, and stores in the database.  
> **Recognition:** For any new image or webcam frame we detect faces, get their embeddings, and compare with stored ones using **cosine similarity**. If similarity is above a threshold, we assign the person's name and record attendance. For webcam we only run recognition every few frames to keep it fast."

---

## 5. Main Features (2 min)

> "**Auth:** Login/register; JWT; roles — admin (full access), staff (monitoring + attendance), student (dashboard).  
> **People:** Admin adds persons (name, email, department, type: student/staff) and **trains** them with photos.  
> **Recognition:** Upload an image → get back the same image with faces marked (name or Unknown).  
> **Live monitoring:** Staff/admin start webcam → system recognizes faces and records attendance with a cooldown to avoid duplicates.  
> **Attendance:** View/filter records by date and person; summary (present count, rate)."

---

## 6. Database in One Sentence

> "We store **persons** (with face embedding), **attendance** (check-in/check-out per person per day), **sessions** for continuous monitoring, and **users** (admin + app users with roles)."

---

## 7. Demo Flow (2 min)

> "First **login** as admin. In **People**, add a person and **train** with a few photos. Then either:  
> - Use **Recognize** to upload a photo and show faces marked, or  
> - Go to **Live Monitoring**, start the webcam, and show attendance being recorded.  
> Finally open **Attendance** and show the recorded entries and summary."

---

## 8. Challenges We Solved (1 min)

> "**Accuracy** — we use multiple photos per person and average embeddings. **Performance** — we run recognition every Nth frame and resize for webcam. **Duplicate records** — we use a 30-second cooldown per person. **Security** — hashed passwords and JWT with role checks."

---

## 9. Conclusion (30 sec)

> "We built a full-stack system: React frontend, FastAPI backend, MySQL, and DeepFace for multi-face recognition and attendance. Thank you. Questions?"

---

**Total: ~10 minutes.** For full detail use **SEMINAR_SCRIPT_A_TO_Z.md**.
