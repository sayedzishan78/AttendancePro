# Viva Questions & Answers — Multiface Recognition & Attendance Project

**Short, easy answers** — 2 to 4 sentences each. Use in your own words.

---

## A. Project & Problem

**Q1. What is your project in one sentence?**  
**Answer:** Our project is a full-stack **multiface recognition and attendance system**. We use AI (DeepFace) to detect and identify multiple faces from images or webcam, save attendance in a database, and give different access to admin, staff, and student. So the camera automatically marks who is present instead of manual roll call.

**Q2. What problem does it solve?**  
**Answer:** Manual attendance is slow, can be faked (proxy), and is hard to analyze. Our system automates it with face recognition, supports multiple faces at once, and stores check-in/check-out with proof. We save time, reduce proxy, and get data that is easy to filter and report.

**Q3. Why face recognition and not RFID or biometric?**  
**Answer:** Face recognition is contactless — no card or touch. We can use the same camera (e.g. laptop webcam) and in one frame we can mark several people present. RFID needs cards for everyone; fingerprint needs extra hardware at each point.

**Q4. What do you mean by "multiface"?**  
**Answer:** Multiface means we can detect and recognize **multiple faces in one image or one webcam frame**. So one group photo or one snapshot can mark attendance for several people at once, not just one person per image.

---

## B. Technologies & Why

**Q5. Why FastAPI and not Django or Flask?**  
**Answer:** FastAPI is async, so the server can handle other requests while doing heavy face encoding. It gives automatic API docs (Swagger/ReDoc) and uses Pydantic for validation. We needed a REST API that does CPU-heavy work — FastAPI fits that well.

**Q6. Why React for frontend?**  
**Answer:** React is component-based so we build login, dashboard, people, monitoring as reusable components. We use TypeScript for type safety and Vite for fast dev and build. It fits our single-page app with dashboard, forms, and live preview.

**Q7. Why MySQL?**  
**Answer:** We need a relational database because we have persons, attendance, and users with clear relationships. We need to query by date, person, and type. MySQL works well with SQLAlchemy (ORM) so we use Python classes instead of raw SQL.

**Q8. Why DeepFace and not building our own CNN?**  
**Answer:** Building our own model would need a huge dataset, GPU, and a lot of time. DeepFace gives pre-trained models (we use VGG-Face) for face detection and embedding. We get good accuracy without training — we only use it to get embeddings and compare.

**Q9. What is OpenCV used for?**  
**Answer:** OpenCV decodes uploaded image bytes, opens the webcam and reads frames (VideoCapture), resizes frames for faster recognition, and draws bounding boxes and labels on the result image.

---

## C. Architecture & Flow

**Q10. Explain the overall architecture.**  
**Answer:** We have three parts. **Frontend (React):** login, dashboard, people, train, live monitoring, attendance, settings. **Backend (FastAPI):** REST API for auth, persons, train, recognize, attendance, webcam, settings. **Database (MySQL):** persons (with face embedding), attendance, sessions, admin_users, app_users. Face pipeline: DeepFace detects faces and gives embeddings; we compare with stored embeddings using cosine similarity.

**Q11. What happens when a user logs in?**  
**Answer:** User sends username/email and password to POST /api/auth/login. Backend checks admin_users or app_users, verifies password with Passlib, creates a JWT with username and role, and returns token and role. Frontend stores them in localStorage and AuthContext and sends Authorization: Bearer &lt;token&gt; on every later request. Backend decodes JWT to know who the user is and their role.

**Q12. How does training (enrollment) work?**  
**Answer:** Admin creates/selects a person and uploads 3–5 photos. Frontend sends them to POST /api/train/. Backend uses DeepFace to get a 2624-dimensional embedding per face, averages them, L2-normalizes, pickles, and stores in persons.embedding (BLOB). So we have one stored vector per person for later matching.

**Q13. How does recognition work step by step?**  
**Answer:** (1) We have an image (upload or webcam frame). (2) DeepFace detects all faces and returns an embedding per face. (3) We load stored person embeddings from DB and L2-normalize. (4) For each face we compute cosine similarity with every stored embedding and take the max. (5) If max &gt; threshold we assign that person’s name; else “Unknown”. (6) We save attendance (person_id, date, time, confidence) and optionally draw boxes on the image.

**Q14. What is cosine similarity and why use it?**  
**Answer:** Cosine similarity measures how similar two vectors are (value between -1 and 1; higher = more similar). After L2 normalization it is just the dot product. We use it to compare a new face’s embedding with every stored one — the highest score above threshold gives the match.

**Q15. What is an embedding?**  
**Answer:** An embedding is a fixed-size vector (here 2624 numbers) that represents a face. Same person gives similar vectors; different people give different vectors. DeepFace’s VGG-Face produces it from a face image. We store this vector, not the photo, and use it for matching.

---

## D. Database

**Q16. Name the main tables and their purpose.**  
**Answer:** **persons** — id, name, email, department, person_code, person_type, embedding (BLOB); our face gallery. **attendance** — person_id, date, check_in_time, check_out_time, confidence, image_path, total_detections, duration_minutes; one row per person per day. **attendance_sessions** — for webcam monitoring (session start/end, status). **admin_users** — admin login (username, password_hash). **app_users** — staff/student (email, password_hash, role, department).

**Q17. Why store embedding as BLOB?**  
**Answer:** The embedding is a numpy array of 2624 floats. MySQL has no array type, so we serialize it with pickle to bytes and store as BLOB. When we need it we read and unpickle to get the array back. Binary is compact and fast.

**Q18. How do you avoid duplicate attendance for the same person on the same day?**  
**Answer:** We have one attendance row per person per day. First detection creates the row; later detections update check_out_time, total_detections, and duration_minutes. For webcam we also use a 30-second cooldown per person so we don’t record the same person again in every frame.

**Q19. What is the relationship between Person and Attendance?**  
**Answer:** One-to-many. One Person has many Attendance records (one per day). Attendance has person_id as foreign key to persons.id. So we join or filter by person_id when we query “all attendance for this person.”

---

## E. API & Backend

**Q20. List the main API endpoints.**  
**Answer:** Auth: POST /auth/login, POST /auth/register, GET /auth/me. Persons (admin): GET/POST /persons, PATCH/DELETE /persons/{id}. POST /train/ (person_id, name, files). POST /recognize/ (one image). GET /attendance, GET /attendance/summary. Webcam: POST /webcam/start/, /stop/, GET /webcam/status/, /capture/, /preview/, /attendance/, POST /webcam/export/. GET/PUT /settings/recognition. GET /health/.

**Q21. What does POST /train/ accept?**  
**Answer:** Form data: person_id, name, person_type (student/staff), optional email, department, person_code, and **files** (multiple image files). Backend encodes each face, averages embeddings, and saves to that person’s record. Response: success message and how many faces were processed.

**Q22. What does POST /recognize/ return?**  
**Answer:** It accepts one image file. Backend detects faces, compares with stored embeddings, and returns **the same image as JPEG** with bounding boxes and labels (name + confidence or “Unknown”) drawn on it.

**Q23. How is the webcam monitoring implemented?**  
**Answer:** Backend opens the camera with OpenCV and runs a loop in a **background thread**. Every Nth frame (stride) we run face detection and recognition, update attendance in DB (with cooldown), and optionally save an image. Frontend calls /webcam/start/, /stop/, /preview/ etc. to control and display. So camera and recognition run on the server; frontend talks via API.

**Q24. Why run recognition every Nth frame (stride)?**  
**Answer:** Running DeepFace on every frame is too heavy for the CPU. We run recognition only every 2nd or 3rd frame to reduce load. We still capture attendance because the same person appears in many frames. Stride is configurable in settings.

---

## F. Security & Auth

**Q25. How are passwords stored?**  
**Answer:** We never store the plain password. We use Passlib (pbkdf2_sha256) to hash the password and store only the hash. On login we hash the entered password and compare with the stored hash. So even if someone gets the DB they can’t get the real passwords.

**Q26. What is JWT and how do you use it?**  
**Answer:** JWT is a signed token that contains who the user is (subject) and their role. After login we create a JWT with expiry (e.g. 12 hours), sign it with our secret, and send it to the frontend. Frontend sends it in Authorization: Bearer &lt;token&gt; on every request. Backend decodes and verifies to know the user and role. So the token carries identity without storing sessions in DB for every request.

**Q27. How do you implement role-based access?**  
**Answer:** Backend: we have dependencies (get_current_admin, get_current_staff_or_admin, get_current_any_user). Each route uses one of them; if the user’s role doesn’t match we return 403. Frontend: we show/hide menus by role and use RequireRole so wrong role sees Access Denied. So both backend and frontend enforce who can do what.

**Q28. Who can do what?**  
**Answer:** **Admin:** full access — people, train, recognize, attendance, webcam, settings. **Staff:** dashboard, live monitoring, view attendance; cannot manage people or settings. **Student:** dashboard only. So admin has full control, staff does daily monitoring, student has minimal access.

---

## G. Frontend

**Q29. How does the frontend know the user is logged in?**  
**Answer:** We store token and role in localStorage and in AuthContext. If we have a token we consider the user logged in. We send the token with every Axios request. If the API returns 401 we clear token and redirect to login. So “logged in” = we have a token and send it; 401 means we log out and redirect.

**Q30. What is AuthContext?**  
**Answer:** AuthContext is a React Context that holds token, role, setToken, setRole, and isAuthenticated. Any component can call useAuth() to get these. Login page sets token and role after success; logout clears them. So it’s the single place for “who is logged in and with what role.”

**Q31. How do you protect routes?**  
**Answer:** RequireAuth: if not authenticated we redirect to login. RequireRole: if the user’s role is not in the allowed list (e.g. admin for People page) we show Access Denied. We wrap route components with these in App.tsx.

**Q32. How does the frontend talk to the backend?**  
**Answer:** We use Axios with a configurable base URL (env or Settings). We add Authorization: Bearer &lt;token&gt; from AuthContext to every request. We call endpoints like GET /persons, POST /train/, POST /webcam/start/, GET /attendance. Backend responds with JSON or image. So frontend only talks to the API, not to the database.

---

## H. Face Recognition Deep Dive

**Q33. What is VGG-Face?**  
**Answer:** VGG-Face is a deep CNN model for face recognition. DeepFace uses it to turn a face image into a 2624-dimensional embedding. We call DeepFace.represent() with model_name="VGG-Face" to get the embedding. So VGG-Face is the model; DeepFace is the library that gives us access.

**Q34. What is L2 normalization and why do you use it?**  
**Answer:** L2 normalization divides the vector by its length so the result has length 1. After that, dot product = cosine similarity, so we can compare two faces with a simple dot product. We normalize both stored and new embeddings so comparison is consistent.

**Q35. What is the recognition threshold?**  
**Answer:** A number between 0 and 1 (e.g. 0.4). If the max cosine similarity between the detected face and stored faces is above this value we say “recognized”; else “Unknown”. Lower threshold = looser (more matches, more false positives); higher = stricter. We can change it in Settings (admin).

**Q36. Why average multiple embeddings per person during training?**  
**Answer:** One photo can have bad angle or lighting. Averaging 3–5 photos gives a more stable vector that represents the person across conditions. So when we see the same person later in different light or angle, the new embedding is still close to this average. That improves accuracy.

**Q37. What if no face is detected in an uploaded image?**  
**Answer:** DeepFace returns an empty list. For training we return an error like “No valid faces found” and ask for clearer photos. For recognition we return “No faces detected”. So we don’t process that image and we give a clear error.

---

## I. Challenges & Solutions

**Q38. How do you improve recognition accuracy?**  
**Answer:** Use 3–5 training images per person from different angles and lighting, and average their embeddings. Use good quality, front-facing photos. Tune the threshold (higher if too many false positives, lower if we miss correct matches). We use a well-trained model (VGG-Face) from DeepFace.

**Q39. How do you handle performance with webcam?**  
**Answer:** We use stride (recognize every Nth frame), resize the frame to a smaller width before DeepFace, and run the loop in a background thread. So we reduce CPU load and keep the API responsive while still capturing attendance.

**Q40. How do you prevent the same person being marked present many times in a minute?**  
**Answer:** We use a cooldown: after recording a person we don’t record them again for 30 seconds (configurable). We track last recognition time per person in memory. We also have one attendance row per person per day and update it instead of inserting again. So we avoid duplicate records.

**Q41. What if two people look similar?**  
**Answer:** The model still gives different embeddings. Usually the correct person has the highest similarity if training is good. If two people have very close scores we can raise the threshold or add more training images so their embeddings are more distinct.

**Q42. Can someone cheat with a photo?**  
**Answer:** We don’t have liveness detection yet, so in theory someone could show a photo of another person. To reduce that we could add liveness detection (e.g. blink or motion) in the future. So we acknowledge this limitation as future work.

---

## J. Deployment & Config

**Q43. How do you run the project?**  
**Answer:** Start MySQL. Backend: pip install -r requirements.txt, set .env (DATABASE_URL, SECRET_KEY, etc.), run uvicorn app.main:app --reload --port 8000. First run may download DeepFace model (~500MB). Frontend: npm install, npm run dev (e.g. port 5173). Set API base URL in .env or Settings. Open frontend URL in browser.

**Q44. What environment variables does the backend need?**  
**Answer:** DATABASE_URL (MySQL connection), SECRET_KEY (for JWT), ADMIN_USERNAME, ADMIN_PASSWORD, RECOGNITION_THRESHOLD, LIVE_RECOGNITION_STRIDE, LIVE_RECOGNITION_WIDTH, MAX_FILE_SIZE_MB. Full list is in .env.example.

**Q45. Where is the face model stored?**  
**Answer:** DeepFace downloads the model on first use and stores it in ~/.deepface/weights/ (user home folder). VGG-Face is about 500MB. We don’t ship it with our code — DeepFace manages it automatically.

---

## K. Testing & Validation

**Q46. How do you test the API?**  
**Answer:** We use Swagger UI at http://localhost:8000/docs to try endpoints (add Bearer token after login). We can also use Postman or curl. For automation we could add pytest with FastAPI’s TestClient.

**Q47. How do you validate uploaded images?**  
**Answer:** We check file size (max e.g. 10MB). We decode with OpenCV; if it fails we return an error. For training we use enforce_detection=True so DeepFace only returns embeddings when a face is found; if no face we return “No valid faces found.”

---

## L. Future Work & Conclusion

**Q48. What can be improved?**  
**Answer:** Liveness detection to prevent photo spoofing; export attendance to CSV/Excel; more dashboard charts; multiple camera support; student view of own attendance; notifications. So both security (liveness) and features (export, charts) can be added.

**Q49. Why did you choose this project?**  
**Answer:** It combines web development (React, FastAPI), applied AI (face recognition), and a real use case (attendance). It shows we can build a full-stack app, integrate an ML model, and balance accuracy, performance, and usability.

**Q50. What did you learn?**  
**Answer:** Full-stack flow (frontend, API, DB), JWT auth and role-based access, face recognition pipeline (embedding, cosine similarity, threshold), and how to reduce load (stride, resize) and avoid duplicates (cooldown, one row per person per day). We learned both technical (APIs, DB, ML) and practical (security, performance) aspects.

---

## Quick revision checklist

- [ ] Project in one sentence
- [ ] Problem and solution
- [ ] Tech stack (FastAPI, React, MySQL, DeepFace, OpenCV)
- [ ] Training vs recognition flow
- [ ] Cosine similarity and threshold
- [ ] Main tables (persons, attendance, users)
- [ ] Auth: JWT, roles, who can do what
- [ ] Webcam: stride, cooldown, background thread
- [ ] Challenges: accuracy, performance, duplicates
- [ ] One improvement you would add

Practice these in your own words. Keep answers to 2–4 sentences when you speak.
