# How Images Work — From Upload/Save to Process (For Teachers)

This document explains **step by step** when we receive an image, what we do with it, when we save it, and which process runs. Use this to explain to your teachers.

---

## Overview in One Line

- **Training:** We **do not save** the uploaded photos. We only **extract a face vector** from them and save that vector in the database.
- **Recognition (upload):** We **save** the result image (with names/boxes drawn) on the server and **return** that same image to the user.
- **Webcam:** We **save** a photo only when we **recognize** someone; that photo path is stored in the **attendance** record.

---

# Part A — Training (Adding a Person’s Face)

**What the teacher sees:** Admin uploads 3–5 photos of a person and clicks “Train.”

---

## Step 1: Images Arrive at the Backend

- The frontend sends a **POST** request to **/api/train/** with **form data**: person_id, name, person_type, and **multiple image files** (the photos).
- These files are **in memory** on the server when the request is being processed. We do **not** save them to a folder on the disk at this step.

---

## Step 2: Each Image Is Processed One by One

For **each** uploaded image we do this:

1. **Read the file** — We read the raw bytes (content) of the image into memory.
2. **Check size** — If the file is larger than the allowed limit (e.g. 10 MB), we reject the request and stop.
3. **Save to a temporary file** — DeepFace (the library we use for face recognition) needs a **file path**, not raw bytes. So we write the bytes to a **temporary file** on the server (e.g. in the system temp folder). This is only for DeepFace to read; we **delete this temp file** as soon as we finish with that image.
4. **Call DeepFace** — We pass the temp file path to DeepFace. DeepFace **detects the face** in the image and **converts the face** into a list of numbers (called an **embedding** or **vector**). That list has a fixed length (e.g. 2624 numbers). This vector “represents” the face; we do not store the photo.
5. **Collect the vector** — We take that list of numbers, **normalize** it (so that later we can compare faces using simple math), and add it to a list. So after processing all photos we have **one vector per photo** (e.g. 3 photos → 3 vectors).
6. **Delete the temp file** — We remove the temporary image file from the server. So the **original uploaded photos are not kept** anywhere on the server.

---

## Step 3: Combine Vectors and Save in the Database

- We **average** all the vectors we got (e.g. 3 vectors → 1 average vector). This single vector represents that person’s face in a stable way.
- We **normalize** this average vector again.
- We **convert** this vector (a list of numbers) into **bytes** using a standard method (pickle) so we can store it in the database.
- We **save** these bytes in the **database** in the **persons** table, in the **embedding** column, for that person’s row. We **do not** save the original images in the database or in any folder.

---

## Summary for Training (What to Tell Teachers)

- **Input:** 3–5 photos of one person (uploaded by admin).  
- **Where they go:** Only in **memory** and in a **temporary file** that we **delete** after use.  
- **What we keep:** Only the **face vector** (embedding) stored in the **database** for that person.  
- **What we do not do:** We do **not** save the uploaded training photos on the server or in the database.  
- **Process:** Upload → read bytes → temp file → DeepFace extracts face → get vector → delete temp file → average all vectors → save one vector in DB.

---

# Part B — Recognition (Upload One Image and Get It Back with Names)

**What the teacher sees:** User uploads one image; the system returns the **same image** with **boxes and names** drawn on the faces.

---

## Step 1: Image Arrives at the Backend

- The frontend sends a **POST** request to **/api/recognize/** with **one image file** (e.g. JPEG/PNG).
- We **read the bytes** of the file and **decode** them into an image (a matrix of pixels) in memory using OpenCV. We do **not** save this original file to a folder yet.

---

## Step 2: Load Known Faces from the Database

- We load **all persons** from the **persons** table. For each person we have their **embedding** (the vector we saved during training). We **unpack** those bytes back into vectors and **normalize** them. So we have: list of vectors, list of names, list of person IDs.

---

## Step 3: Detect Faces in the Uploaded Image

- We give the **image** (in memory) to DeepFace. DeepFace **detects all faces** in the image and returns, for each face:
  - its **embedding** (vector), and  
  - the **position** of the face (a rectangle: x, y, width, height).  
- So we get a list of “face vector + rectangle” for that one image. We still have not saved any image to disk.

---

## Step 4: Match Each Face to a Person

- For **each** detected face we **compare** its vector with **all** stored vectors (from the database). The comparison is a math operation (dot product / cosine similarity).  
- We find the **best match**: the stored person whose vector is **most similar** to this face.  
- If that similarity is **above a threshold** (e.g. 0.4), we say “this face is **that person**” and we take their name and ID. If it is **below** the threshold, we say “**Unknown**.”  
- So we now have, for each face: **name** (or “Unknown”), **similarity score**, and **rectangle**.

---

## Step 5: Draw on the Image and Save It

- We **draw** on the **same image** we have in memory:
  - a **rectangle** around each face (e.g. green if recognized, red if unknown), and  
  - a **text label** (name and similarity, or “Unknown”).  
- We **save** this **annotated image** to the **server’s disk** in a folder called **outputs** (or whatever is set in config). The file name is unique (e.g. `recognized_abc123.jpg`). So **this is the first time we save an image** in this flow.  
- We **return** that **saved file** to the user (the browser gets the same image they uploaded but with boxes and names drawn on it). The response is the image file (e.g. JPEG).

---

## Summary for Recognition / Upload (What to Tell Teachers)

- **Input:** One image file (uploaded).  
- **Where it is first:** Only in **memory** (decoded as pixels).  
- **Process:** Decode image → load known vectors from DB → DeepFace detects all faces and gives vectors + rectangles → we match each face to a person (or Unknown) → we **draw** boxes and names on the image → we **save** this **result image** to the **outputs** folder → we **send** that saved image back to the user.  
- **What we save:** Only the **final image with drawings** (in the **outputs** folder). We do **not** save the original uploaded image in a folder; we only use it in memory and then return the annotated version.  
- **Which process:** The **same request** that receives the upload does all the steps (decode → load DB → DeepFace → match → draw → save → return). So “the API process” or “the backend process” that handles **POST /api/recognize/** does this entire flow.

---

# Part C — Webcam (Live Camera and Attendance)

**What the teacher sees:** Staff turns on the webcam; when someone is recognized, attendance is marked and optionally a photo is saved.

---

## Step 1: Camera Starts

- When the user clicks “Start” (webcam), the frontend calls **POST /api/webcam/start/**.
- The backend **opens the camera** (e.g. laptop webcam) and starts a **background loop** (a separate thread). That loop keeps reading **frames** (images) from the camera one after another. Each frame is **in memory**; we do **not** save every frame to disk.

---

## Step 2: Every Nth Frame We Run Recognition

- To avoid overloading the server we **do not** run face recognition on **every** frame. We run it only every **Nth** frame (e.g. every 2nd frame). So we might process frame 2, 4, 6, … and skip 1, 3, 5, …
- For the frame we **do** process:
  1. We **resize** it (e.g. to 480 px width) in memory to make recognition faster.  
  2. We **detect all faces** in that frame (using DeepFace) and get their **embeddings** and **rectangles**.  
  3. We **load** known persons’ embeddings from the **database** (same as in recognition).  
  4. We **compare** each detected face with known persons (dot product / similarity).  
  5. If similarity **above threshold** we say “recognized” and we have a name and person_id. We also apply a **cooldown**: we do **not** record the same person again within e.g. 30 seconds, so we don’t write many rows for the same person in one minute.  
  6. If we **did** recognize someone and the cooldown allows it, we **write an attendance record** in the database (person_id, date, time, confidence). We may also **save an image** (see next step).  
- The **latest frame** (with or without drawings) is kept **in memory** so that when the frontend asks for “preview,” we can send that frame (e.g. as base64). We do **not** save every frame to disk.

---

## Step 3: When We Save an Image in Webcam

- We **save an image** only when **at least one face** in the frame was **recognized** (and we wrote an attendance record).  
- What we save is the **current frame** with **boxes and names drawn** on it (same style as in recognition).  
- **Where we save:** In the same **outputs** folder on the server, with a unique name (e.g. `attendance_20250223_143052_abc12.jpg`).  
- **What we do with the path:** We store this **file path** (e.g. `C:\...\backend\outputs\attendance_20250223_143052_abc12.jpg`) in the **attendance** table, in the **image_path** column, for the **attendance row(s)** we just created or updated for that moment. So later we can show “proof” of who was present by linking to this image.

---

## Step 4: What Runs in the Background

- The **webcam loop** runs in a **background thread** (not in the main request). So:
  - The **main process** (or main thread) keeps handling other API requests (e.g. “give me preview,” “stop webcam”).  
  - The **background thread** only does: read frame → every Nth frame run recognition → if someone recognized and cooldown OK → write attendance (+ optionally save image and update image_path) → store latest frame for preview.  
- So the **process** that “does the work” for the image is: **the same backend server process**, but the **webcam loop** runs in a **separate thread** inside that process.

---

## Summary for Webcam (What to Tell Teachers)

- **Input:** Continuous **frames** from the camera (in memory).  
- **When we save an image:** Only when we **recognize** at least one person in a frame **and** we record attendance. We save the **annotated frame** (with boxes and names) to the **outputs** folder.  
- **What we save in the database:** We save an **attendance row** (person_id, date, check-in/check-out time, confidence, etc.) and we save the **path** to the saved image in the **image_path** column. We do **not** store the image itself in the database, only the path.  
- **Which process:** The **backend server process**; inside it a **background thread** runs the camera loop. So “the server” reads the camera, runs recognition every Nth frame, and when it recognizes someone it (1) writes to the database and (2) saves the image file to disk and (3) stores that file path in the attendance record.  
- **Flow in short:** Camera → frame in memory → every Nth frame: resize → DeepFace (detect + vector) → compare with DB → if recognized + cooldown OK → write attendance row → save annotated image to **outputs** → put path in **attendance.image_path** → keep latest frame in memory for preview.

---

# Quick Reference Table for Teachers

| Scenario        | Image source     | Where image is first        | Do we save the image to disk?        | Where?        | What we save in DB                    |
|----------------|------------------|-----------------------------|--------------------------------------|---------------|---------------------------------------|
| **Training**   | Upload (3–5)     | Memory + temp file (deleted)| **No** (we only keep the face vector)| —             | **Person.embedding** (vector bytes)   |
| **Recognize**  | Upload (1)       | Memory                      | **Yes** (annotated result)           | **outputs/**  | Nothing (we only return the file)     |
| **Webcam**     | Camera frames    | Memory                      | **Yes**, only when someone recognized | **outputs/**  | **Attendance.image_path** (file path)|

---

# One-Paragraph Version for Teachers

**Training:** When the admin uploads photos of a person, we do not save those photos. We only use them in memory (and a temporary file that we delete) to extract a “face vector” with DeepFace, then we average those vectors and save **only that vector** in the database for that person.  
**Recognition (upload):** When the user uploads one image, we detect faces, match them to our stored vectors, draw boxes and names on the image, **save that result image** in the **outputs** folder on the server, and send that same image back to the user.  
**Webcam:** The server reads frames from the camera in a background loop. It runs face recognition every few frames. When it recognizes someone, it writes an **attendance** row and **saves the current frame** (with names/boxes drawn) in the **outputs** folder, and stores that file’s **path** in the attendance table so we have proof of who was present. So: **images are saved only for “result” or “proof”** (recognize result, webcam attendance), and **training images are never saved**, only the numbers (embedding) derived from them.

---

You can use this document to explain to your teachers: **how an image is received**, **which process runs** (API request for upload, background thread for webcam), and **when and where we save** (outputs folder + DB path only for webcam).
