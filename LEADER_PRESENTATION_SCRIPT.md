# How to Explain This Project as the Group Leader

Use this as your **presentation script** when you are the leader explaining the project to teachers or judges. It is written in **enough detail** so that **common counter-questions are already answered** in the flow. You can speak it section by section; if the teacher asks something, you will often find the answer already in the next point or in the “If they ask…” lines.

---

## 1. Opening (30 seconds)

**What to say:**

> “Good morning/afternoon. I am [name], the leader of this group. We are here to present our project: **Multiface Recognition and Professional Attendance Monitoring System**.  
>  
> In the next [X] minutes I will cover: what problem we solved, what we built, how it works end-to-end, the technologies we used and why we chose them, and a quick demo flow. We have also prepared for questions on security, performance, and limitations.  
>  
> My team members [names] will support with the demo and technical questions if needed.”

**Why this helps:** You set the role (leader), the title, and the structure. Teachers often ask “what exactly does your project do?” — you answer that next.

---

## 2. Problem Statement (1 minute)

**What to say:**

> “In colleges and offices, attendance is usually taken manually: roll call or sheets. That has three main problems.  
>  
> **First**, it is **time-consuming** — every day the teacher or staff has to call names or pass a sheet. **Second**, it is **easy to fake** — someone else can mark for an absent friend, so we cannot fully trust the data. **Third**, it is **hard to use** — finding who was absent on which date or generating reports is difficult when everything is on paper or in simple spreadsheets.  
>  
> We wanted attendance to be **automatic**, **reliable**, and **easy to analyze**. So we decided to build a system that uses **face recognition** to mark who is present, without manual roll call.”

**If they ask:** “Why not RFID or fingerprint?”  
**Answer:** “We chose face recognition because it is **contactless** — no cards or touching devices. We can use the **same camera** that might already be there, and in **one image or one camera frame** we can identify **multiple people** at once. So it fits our goal of automatic, multi-person attendance with minimal extra hardware.”

---

## 3. What We Built — One Clear Sentence (30 seconds)

**What to say:**

> “So, in one sentence: we built a **full-stack web application** where the **backend** uses **AI face recognition** to detect and identify **multiple faces** from uploaded photos or a **live webcam**, **records attendance** in a database with check-in and check-out, and the **frontend** lets **admin**, **staff**, and **students** log in with **different permissions** — admin can manage people and train faces, staff can run the webcam and see attendance, students have limited access.  
>  
> So the **user** only uses the website; the **server** does the face recognition and stores everything.”

**Why this helps:** You give one clear sentence so the teacher knows “what it is.” You already mention: full-stack, multiface, webcam, database, roles. That reduces “what is multiface?” or “who can do what?” later.

---

## 4. High-Level Architecture (1 minute)

**What to say:**

> “The system has **three layers**.  
>  
> **First**, the **frontend** — a React web app that runs in the browser. The user sees the login page, dashboard, list of people, training form, live webcam screen, attendance table, and settings. The frontend **does not** do face recognition or store data; it only **sends requests** to the backend and **displays** what the backend returns.  
>  
> **Second**, the **backend** — a FastAPI server in Python. It receives those requests, checks who is logged in and their role (admin, staff, or student), talks to the database, and runs the **face recognition** using **DeepFace** and **OpenCV**. So all the business logic and AI run here.  
>  
> **Third**, the **database** — MySQL. We store **persons** (with their face data as a vector, not the photo), **attendance** records (who was present on which date and time), and **users** (who can log in and with what role).  
>  
> So the flow is: **User → Frontend → Backend → Database + Face recognition → Backend → Frontend → User.** The frontend never talks to the database directly; only the backend does.”

**If they ask:** “Where is the face recognition done?”  
**Answer:** “Only on the **backend** server. The frontend only sends images (e.g. upload or via API for webcam) and receives results. The heavy work — DeepFace and OpenCV — runs on the server.”

---

## 5. How Face Recognition Works — So Few Questions Later (2 minutes)

**What to say:**

> “Let me explain how we recognize a face, so it is clear what the system is doing.  
>  
> **Step 1 — Training.** The admin adds a person (name, department, type) and uploads **several photos** of that person — we recommend 3 to 5. For each photo we use **DeepFace** with the **VGG-Face** model to **detect the face** and convert it into a **list of numbers** — we call it an **embedding** or **vector** — 2624 numbers per face. We **average** all these vectors for that person and **normalize** the result, then we **store only this vector** in the database. We **do not** store the training photos; we only keep the numbers. So after training we have **one vector per person** in the database.  
>  
> **Step 2 — Recognition.** When we get a **new** image — either uploaded or one frame from the webcam — we use the same **DeepFace** to **detect all faces** in the image and get one **embedding per face**. We then **compare** each new embedding with **every stored** vector in the database. The comparison is **cosine similarity** — in simple terms, a number between -1 and 1; **higher means more similar**. We take the **best match**. If that best similarity is **above a threshold** — we use 0.4 by default — we say ‘this face is that person’ and we use their name and ID. If it is **below** the threshold we say ‘Unknown’.  
>  
> **Step 3 — Attendance.** When we recognize someone (from an uploaded image or from the webcam), we **record** it: who (person_id), which date, check-in or check-out time, and confidence. We **do not** create a new row every time we see the same person the same day; we have **one row per person per day** and we **update** it (e.g. check-out time, duration). So we avoid duplicate records.  
>  
> So in short: **training** = photos → vectors → average → save one vector per person; **recognition** = new image → vectors for each face → compare with stored vectors → threshold → name or Unknown; **attendance** = one row per person per day, updated on each detection.”

**If they ask:** “What is cosine similarity?”  
**Answer:** “It measures how similar two vectors are. After we normalize our vectors, it is just the **dot product** of the two vectors. Same person gives a high value (close to 1); different person gives a lower value. We set a **threshold** (e.g. 0.4) so that we only say ‘recognized’ when we are confident enough.”

**If they ask:** “Why average multiple photos?”  
**Answer:** “One photo can have bad angle or lighting. **Averaging** several photos gives a more **stable** vector that represents the person across different conditions, so recognition works better later.”

---

## 6. Technologies and Why We Chose Them (1 minute)

**What to say:**

> “On the **backend** we use **FastAPI** because it is async, gives us automatic API docs (Swagger), and has built-in validation. We use **MySQL** because we need relational data — persons, attendance, users — and we need to query by date, person, and type. We use **SQLAlchemy** as the ORM so we work with Python classes instead of raw SQL. For face recognition we use **DeepFace** with the **VGG-Face** model — it is pre-trained, so we don’t train our own model; we only use it to get embeddings. We use **OpenCV** for image decoding, resizing, and drawing boxes on the result image. For security we use **JWT** for the login token and **Passlib** for password hashing — we never store plain passwords.  
>  
> On the **frontend** we use **React** with **TypeScript** for a component-based UI and type safety. We use **Vite** for fast development and build. We use **React Router** for routes (e.g. /app/dashboard, /app/people) and **Axios** to call the backend API. The frontend stores the **token** and **role** in localStorage and sends the token with every request so the backend knows who is calling.  
>  
> So we chose each technology for a reason: FastAPI for the API, MySQL for structured data, DeepFace for ready-made face recognition, React for the UI, and JWT for secure access.”

**If they ask:** “Why not Django or Flask?”  
**Answer:** “We needed a **REST API** that does heavy work (face encoding). FastAPI gives us **async** support and **automatic docs** out of the box. Django is more for full web apps with templates; we only needed an API that the React frontend talks to.”

---

## 7. Security and Access Control (1 minute)

**What to say:**

> “We take **security** seriously.  
>  
> **Passwords** are never stored in plain text. We hash them with **Passlib** (pbkdf2_sha256) and store only the hash. On login we verify by hashing the entered password and comparing with the stored hash.  
>  
> **Authentication** is done with **JWT**. After a successful login the backend returns a **signed token** that contains who the user is (username or email) and their **role** (admin, staff, or student). The frontend stores this token and sends it in the **Authorization: Bearer** header on every request. The backend **decodes** the token and checks the signature, so no one can fake a token without our secret key.  
>  
> **Access control** is **role-based**. **Admin** can do everything: add and edit persons, train faces, run recognition, view attendance, start and stop webcam, change settings. **Staff** can run the webcam and view attendance but **cannot** manage the person list or settings. **Student** can log in and see the dashboard with limited access. So the backend **checks the role** on every protected route and returns 403 if the role is not allowed. The frontend also **hides** menu items the user is not allowed to use, so they don’t see options they can’t access.”

**If they ask:** “Can someone cheat with a photo?”  
**Answer:** “Right now we **don’t** have **liveness detection** — we don’t check if the face is from a live person or a photo. So in theory someone could hold a photo of another person. To reduce that we could add **liveness detection** in the future — for example asking the user to blink or move. We mention this as a **limitation** and **future work**.”

---

## 8. Images: When We Save and When We Don’t (1 minute)

**What to say:**

> “Teachers often ask: **when do we save images and where?**  
>  
> **Training:** When the admin uploads photos to train a person, we **do not save** those photos on the server. We only use them in memory (and a temporary file for DeepFace) to **extract the face vector**; then we **delete** the temp file. We store **only the vector** in the database. So we don’t keep the training photos.  
>  
> **Recognition (upload):** When the user uploads one image to recognize faces, we **detect** faces, **match** them to the database, and **draw** boxes and names on the image. We **save this result image** (with drawings) in a folder called **outputs** on the server and **return** that same file to the user. So we save only the **annotated result**, not the original upload as a separate file.  
>  
> **Webcam:** We **don’t** save every frame. We save an image **only when** we **recognize** at least one person in that frame and record attendance. That image (with boxes and names) is saved in the **outputs** folder and we store the **file path** in the **attendance** table (image_path) so we have proof of who was present. So the image is on disk; the database only stores the path.”  

**Why this helps:** You answer “where are the images?” and “do you save training photos?” in one go, so the teacher doesn’t have to ask.

---

## 9. Performance and Duplicate Prevention (1 minute)

**What to say:**

> “We had to handle **performance** and **duplicate records**.  
>  
> **Performance:** Running face recognition on **every** webcam frame would be too heavy. So we run recognition only **every Nth frame** — we call it **stride**; for example every 2nd frame. We also **resize** the frame to a smaller width before sending it to DeepFace. So we reduce CPU load while still capturing attendance, because the same person appears in many frames.  
>  
> **Duplicate prevention:** We have two rules. **First**, in the database we have **one attendance row per person per day**. The first time we see that person that day we **create** the row; when we see them again we **update** the same row (check-out time, total detections, duration). So we never create multiple rows for the same person the same day. **Second**, in the webcam we use a **cooldown** — after we record a person we don’t record them again for **30 seconds**. So even if the camera sees them in every frame we don’t write to the database every second; we only update when they are seen again after the cooldown.  
>  
> So: **stride** for performance, **one row per person per day** and **cooldown** for duplicate prevention.”

**If they ask:** “What if two people look similar?”  
**Answer:** “The model still produces **different** vectors for different people. Usually the **correct** person has the **highest** similarity if we have good training photos. If the scores are very close we could **raise the threshold** or add **more training images** so the stored vectors are more distinct.”

---

## 10. Demo Flow — What You Will Show (1 minute)

**What to say:**

> “For the **demo** we will show the following.  
>  
> **First**, we open the app and go to the **login** page. We log in as **admin** (username and password). After login we are on the **dashboard**, which shows today’s **attendance summary** — total people, how many are present, and the attendance rate — and the **latest attendance** records.  
>  
> **Second**, we go to **People** (Students & Staff). We **add a person** (name, department, type) and **upload 3–5 photos** of that person and click **Train**. The backend will extract the face vectors, average them, and save. We show the success message.  
>  
> **Third**, we either **upload one image** in the recognition flow (if we have that screen) and show the **returned image** with boxes and names, or we go to **Live Monitoring**. We click **Start** so the backend starts the webcam. We show the **preview** (the current frame with boxes and names) and the **latest detections** table. When someone is recognized we show that attendance is being recorded. Then we click **Stop**.  
>  
> **Fourth**, we go to **Attendance** and show the **table** with filters (date range, person type). We show the records we just created.  
>  
> So the demo covers: **login → dashboard → add and train a person → run recognition or webcam → view attendance**. That is the full flow.”

**Why this helps:** You set expectations for what the teacher will see, so they don’t ask “what are you going to show?” in the middle.

---

## 11. Limitations and Future Work (1 minute)

**What to say:**

> “We are clear about **limitations** and **future work**.  
>  
> **Limitations:**  
> - We don’t have **liveness detection** yet, so someone could try to use a photo.  
> - Recognition accuracy depends on **lighting and photo quality**; we recommend good, front-facing training photos.  
> - The webcam runs on the **same machine** as the backend; for multiple cameras or different locations we would need to extend the design.  
>  
> **Future work:**  
> - Add **liveness detection** to reduce photo spoofing.  
> - **Export** attendance to CSV or Excel.  
> - More **dashboard charts** (e.g. attendance rate over time).  
> - **Student view** of their own attendance.  
> - **Notifications** when someone is marked present.  
>  
> So we are honest about what the system can and cannot do today, and what we would add next.”

**Why this helps:** You answer “what are the drawbacks?” and “what would you improve?” before they ask.

---

## 12. Closing and Handover to Questions (30 seconds)

**What to say:**

> “To summarize: we built a **full-stack Multiface Recognition and Attendance System**. We use **face recognition** (DeepFace, VGG-Face) to **train** on photos and **recognize** multiple faces from uploads or webcam, **record attendance** in a database with one row per person per day, and control **access** with roles and JWT. The **frontend** is React; the **backend** is FastAPI; the **database** is MySQL. We have explained **how** recognition works, **when** we save images, **how** we handle security and performance, and our **limitations** and **future work**.  
>  
> We are happy to take your questions — technical, on the design, or on the demo. [Team member names] can answer on [specific areas] if needed.”

**Why this helps:** You give a short recap and invite questions in a structured way, so the teacher knows the presentation is complete and can ask anything they still want to clarify.

---

## Quick Reference: If They Ask This, Say This

| If they ask… | You can say… |
|---------------|--------------|
| What is multiface? | We can detect and recognize **multiple faces in one image or one webcam frame**; we don’t need one photo per person. |
| Why face and not RFID? | Face is **contactless**, uses **one camera**, and we can identify **many people at once** in one frame. |
| Where are the training photos stored? | We **don’t store** them. We only extract the **face vector** and save that in the database; we delete the temp file after use. |
| Where is the result image saved? | The **annotated** image (with boxes and names) is saved in the **outputs** folder on the server; for webcam we also save the **path** in the attendance table. |
| How do you avoid duplicate attendance? | **One row per person per day** in the database (we update, not insert again) and a **30-second cooldown** per person in the webcam. |
| How do you handle performance? | **Stride** — we run recognition only every **Nth** frame — and **resize** the frame before recognition. |
| What is the threshold? | A number (e.g. 0.4). If **cosine similarity** between the new face and the best-matching stored face is **above** this, we say “recognized”; else “Unknown”. |
| Can someone cheat with a photo? | We don’t have **liveness** yet; we mention it as a **limitation** and **future work** (e.g. blink or motion check). |
| Who can do what? | **Admin**: full access. **Staff**: webcam and attendance; no people or settings. **Student**: limited (e.g. dashboard). |

---

## How to Use This as the Leader

1. **Rehearse** sections 1–12 once so you don’t read word-for-word but speak naturally.  
2. **Keep** the “If they ask…” and the **Quick Reference** table handy; if a teacher asks something, you can use that line.  
3. **Assign** one team member to handle “algorithms and math” (embedding, cosine similarity, threshold) and one for “frontend and API” if the teacher goes deep.  
4. **Time yourself**: the script is about **10–12 minutes**; adjust by shortening or expanding sections.  
5. After the **demo**, come back to **section 11 (Limitations)** and **section 12 (Closing)** so you end clearly.

If you explain in this order and level of detail, **counter-questions** from the teacher should be fewer, because you will have already covered problem, solution, architecture, how recognition works, technologies, security, images, performance, demo, and limitations.
