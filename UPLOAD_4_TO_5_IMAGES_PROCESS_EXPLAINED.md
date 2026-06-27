# What Happens When You Upload 4 to 5 Images for Training — Full Process (Step by Step)

This document explains **exactly** what happens when you upload 4 to 5 face images and click **Create & Train** or **Save Changes** (with photos). Each step is explained in simple language so you can explain it clearly (e.g. in a seminar or viva).

---

## Overview in One Sentence

You select 4–5 photos → the browser sends them to the backend → the backend **finds the face** in each photo, **converts each face into a list of numbers** (embedding), **averages** those lists into one, **saves** that average in the database for that person → later, when the camera sees a face, it compares that face’s numbers to this saved average to recognize the person.

---

## Part 1: On the Screen (Frontend — What You Do)

### Step 1 — You fill the form and choose images

- You open the **People** page (Admin only).
- You fill: **Full Name**, **Person Type** (student/staff), **Email**, **Department**, **Student/Employee ID** (optional).
- In **“Face Images (2–5)”** you click **Choose File** and select **4 or 5 images** (e.g. from your computer).
- The app tells you: *“Use clear photos with different angles/lighting for best accuracy.”*

**Why 4–5?**  
Using several photos (different angles/lighting) gives a **more stable** representation of the person’s face. The system will **average** the face data from all photos into one “signature,” so more good photos usually mean better recognition.

**Code that does this:**  
`frontend/src/pages/People.tsx` — the file input:

```tsx
<input
  type="file"
  multiple
  accept="image/*"
  onChange={(e) => setFiles(Array.from(e.files || []))}
/>
```

- `multiple` = you can select more than one file.
- `accept="image/*"` = only image types (jpg, png, etc.).
- When you select files, they are stored in React state as `files` (array of `File` objects).

---

### Step 2 — You click “Create & Train” or “Save Changes”

- If it’s a **new person**: you click **“Create & Train”**.
- If you are **editing** an existing person and added new photos: you click **“Save Changes”**.

**What the frontend does first (before sending images):**

1. **Create person in database (if new)**  
   It calls the **Create Person** API with name, type, email, department, code. The backend creates a new row in the `persons` table **without** any face data yet, and returns the new **person_id**.

2. **If you had selected images**, it then calls the **Train** API with that **person_id** and your **files**.

**Code that does this:**  
`frontend/src/pages/People.tsx` — inside `handleSubmit`:

```tsx
// For NEW person:
const created = await createPerson({ name, email, department, person_code, person_type });
if (files.length) {
  await trainPerson({
    person_id: created.id,  // use the new ID
    name, person_type, email, department, person_code,
    files,  // your 4–5 images
  });
}
```

So: **first** the person is created (or updated), **then** the 4–5 images are sent to the **train** endpoint.

---

### Step 3 — How the 4–5 images are sent to the server

The frontend does **not** send JSON. It sends **multipart form data** (like a form with file uploads).

- It builds a `FormData` object.
- It appends: `person_id`, `name`, `person_type`, and optionally `email`, `department`, `person_code`.
- It appends **each of your 4–5 files** under the same field name `"files"`.

**Code that does this:**  
`frontend/src/api/persons.ts` — inside `trainPerson`:

```ts
const form = new FormData();
form.append("person_id", String(payload.person_id));
form.append("name", payload.name);
form.append("person_type", payload.person_type);
if (payload.email) form.append("email", payload.email);
// ... same for department, person_code
payload.files.forEach((file) => form.append("files", file));

const response = await http.post("/train/", form, {
  headers: { "Content-Type": "multipart/form-data" },
});
```

So the **request** that hits the backend looks like:

- **person_id** = number  
- **name** = string  
- **person_type** = "student" or "staff"  
- **files** = 4 or 5 image files (binary)

---

## Part 2: On the Server (Backend — What Happens to Your 4–5 Images)

The **Train** API runs on the backend. Below is the same process, step by step.

---

### Step 4 — Backend receives the request

- The request goes to: **POST /api/train/** (mounted under `/api` in `main.py`).
- The handler is the function **`train_person`** in `backend/app/api/routes.py`.
- FastAPI reads:
  - `person_id`, `name`, `person_type`, `email`, `department`, `person_code` from the form.
  - `files` = list of uploaded files (your 4–5 images).

**Code:**

```python
@router.post("/train/", dependencies=[Depends(get_current_admin)])
async def train_person(
    person_id: int = Form(...),
    name: str = Form(...),
    person_type: str = Form("student"),
    email: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    person_code: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
```

So at this point the server has: **one person identity** (id, name, type, etc.) and **4–5 image files**.

---

### Step 5 — Check that the face recognition service is ready

- The app uses a **FaceEncoder** (DeepFace + VGG-Face) to convert faces into vectors.
- Before using it, the backend checks: **encoder.initialized**.
- If the model is not loaded (e.g. first request after restart), it returns an error like “Face recognition service is not initialized.”

**Code:**

```python
if not encoder.initialized:
    raise HTTPException(status_code=503, detail="Face recognition service is not initialized...")
```

This ensures we don’t try to process images when the AI part is not ready.

---

### Step 6 — Process **each** of the 4–5 images, one by one

The backend loops over **every file** you uploaded:

```python
embeddings = []
for file in files:
```

For **each** file it does the following.

---

### Step 6.1 — Read the file and check size

- **Read** the full file from the request into memory: `contents = await file.read()`.
- **Check size**: if the file is larger than the allowed maximum (e.g. 10 MB or whatever is set in config), it returns an error and **stops** (so no one can upload huge files and overload the server).

**Code:**

```python
contents = await file.read()
file_size_mb = len(contents) / (1024 * 1024)
if file_size_mb > settings.MAX_FILE_SIZE_MB:
    raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds maximum size...")
```

So: **each of your 4–5 images** is first read as bytes and checked for size.

---

### Step 6.2 — Get a “face embedding” from this one image

- The backend calls **`encoder.encode_image(contents)`**.
- **Input:** raw image bytes (one of your 4–5 photos).
- **Output:** either **one vector of numbers** (embedding) or **None** (if no face was found or something went wrong).

**What happens inside `encode_image`** (in `backend/app/services/face_encoder.py`):

1. **Temporary file**  
   DeepFace in this project works with a **file path**, not raw bytes. So the backend writes the image bytes to a **temporary file** on disk (e.g. a temp JPG), then passes that path to DeepFace. After use, it deletes the temp file.

2. **Face detection**  
   DeepFace uses a **detector** (here: OpenCV) to find a **face** in the image.  
   - If **no face** is found → the function returns **None** for this image (and this image is **not** added to the list).  
   - If **more than one face** is found → DeepFace still returns data; in this code we use the **first** face only for training (to keep one face per photo).

3. **VGG-Face model**  
   DeepFace uses the **VGG-Face** model to convert the **cropped face** into a **vector of numbers** (embedding). This vector is long (e.g. 2624 numbers). It’s like a “fingerprint” of that face.

4. **L2 normalize**  
   That vector is then **L2-normalized** (made unit length). So we don’t store the raw embedding; we store a **normalized** version. This makes later comparison (e.g. cosine similarity) simple and consistent.

**Code (concept):**

```python
emb = encoder.encode_image(contents)
if emb is not None:
    embeddings.append(emb)
```

So after the loop:

- **embeddings** = list of vectors: one vector per image where a face was found.
- If you uploaded 5 images but only 4 had a clear face, **embeddings** has 4 elements.

---

### Step 7 — At least one face must be found

- If **no** image had a detectable face, **embeddings** is empty.
- The backend then returns an error, for example: *“No valid faces found in uploaded images for [name]”* and **does not** save anything.

**Code:**

```python
if not embeddings:
    raise HTTPException(status_code=400, detail=f"No valid faces found in uploaded images for {name}")
```

So: **at least one** of your 4–5 images must contain a detectable face.

---

### Step 8 — Average the embeddings and normalize again

- We now have **several** vectors (e.g. 4 or 5), one per photo.
- The backend **averages** them: one number per position.  
  Example: if each vector has 2624 numbers, we do (v1 + v2 + v3 + v4) / 4 (or 5) and get **one** vector of 2624 numbers.
- That average vector is again **L2-normalized** so it has length 1. This single vector is the **representative face** for this person.

**Why average?**  
Different photos have different lighting and angles. Averaging smooths out small differences and gives a **single, stable** “signature” for the person. Later, when the camera sees a new face, we compare that face’s vector to **this one** average vector.

**Code:**

```python
avg_embedding = np.mean(embeddings, axis=0)
avg_embedding = encoder.l2_normalize(avg_embedding)
serialized = pickle.dumps(avg_embedding)
```

- **serialized** = the average embedding converted to bytes (using Python’s `pickle`) so it can be stored in the database.

---

### Step 9 — Save in the database

- The backend loads the **Person** row (by `person_id`).  
  - If it’s a **new** person (e.g. just created by the first API call), it might still create the row here with id, name, email, department, person_code, person_type, and **embedding**.
  - If the person **already exists**, it **updates** that row: same fields + **replaces** the **embedding** with the new serialized average.
- The **embedding** column is **LargeBinary**: it stores the pickled bytes of the 2624-dimensional vector.
- Then it runs **commit** so the change is saved to MySQL.

**Code:**

```python
person = db.query(Person).filter(Person.id == person_id).first()
if person is None:
    person = Person(id=person_id, name=name, email=email, department=department,
                    person_code=person_code, person_type=person_type, embedding=serialized)
    db.add(person)
else:
    person.name = name
    person.email = email
    person.department = department
    person.person_code = person_code
    person.person_type = person_type
    person.embedding = serialized
db.commit()
```

So: **one row per person**, and that row now has the **averaged, normalized face embedding** from your 4–5 images.

---

### Step 10 — Send success response back to the frontend

- The backend returns a JSON message, for example:  
  *“✅ [Name] (ID=…) trained successfully with 4 face(s)!”*  
  (or 5, depending on how many images had a valid face.)
- It also returns **person_id**, **name**, and **faces_processed** (how many images contributed to the average).

**Code:**

```python
return {
    "message": f"✅ {name} (ID={person_id}) trained successfully with {len(embeddings)} face(s)!",
    "person_id": person_id,
    "name": name,
    "faces_processed": len(embeddings)
}
```

---

## Part 3: Back on the Frontend (After the Request)

### Step 11 — Show success and refresh the list

- The frontend receives this response.
- It shows the **message** (e.g. “Person created and trained successfully.”).
- It clears the form and the selected files, and **reloads** the list of people so the new (or updated) person appears in the table.

**Code:**

```tsx
setMessage("Person created and trained successfully.");
setForm(emptyForm);
setFiles([]);
await load();  // refetch list of people
```

---

## Summary Table (Quick Reference)

| Step | Where | What happens |
|------|--------|----------------|
| 1 | Frontend (People page) | You select 4–5 images; they are stored in React state as `files`. |
| 2 | Frontend | You click Create & Train / Save; frontend may create/update person, then calls Train API with `person_id` + `files`. |
| 3 | Frontend (API layer) | Builds `FormData`, appends person fields + all files; sends POST to `/api/train/`. |
| 4 | Backend (routes) | `train_person` receives form data and list of files. |
| 5 | Backend | Checks that face recognition service (encoder) is initialized. |
| 6 | Backend | For each file: read bytes → check size → call `encoder.encode_image(contents)` → if a face is found, append normalized embedding to list. |
| 6.1–6.2 | Backend (face_encoder) | For each image: temp file → DeepFace detects face → VGG-Face gives embedding → L2 normalize → return vector or None. |
| 7 | Backend | If no valid face in any image → return error. |
| 8 | Backend | Average all embeddings; L2-normalize the average; pickle to bytes. |
| 9 | Backend (database) | Save or update `Person` row with this serialized embedding. |
| 10 | Backend | Return success message + person_id, name, faces_processed. |
| 11 | Frontend | Show message, clear form, reload people list. |

---

## How This Is Used Later (Recognition)

- When **live monitoring** or **single-image recognition** runs, the system:
  1. Gets a face from the camera or uploaded image.
  2. Runs the **same** pipeline: detect face → VGG-Face → L2-normalized embedding.
  3. Loads **all** persons’ embeddings from the database.
  4. Compares the **new** face’s vector to **each** stored vector (e.g. cosine similarity = dot product of normalized vectors).
  5. If the best similarity is **above** the recognition threshold → “Recognized” as that person; otherwise “Unknown”.

So: **uploading 4–5 images** creates the **single averaged embedding** that is later used for this comparison. No images are stored in the DB for training—only that one vector per person.

---

## File Reference (Where to find each part)

| What | File |
|------|------|
| Form + file input + submit logic | `frontend/src/pages/People.tsx` |
| Train API call (FormData, POST /train/) | `frontend/src/api/persons.ts` → `trainPerson` |
| Train endpoint, loop over files, average, save | `backend/app/api/routes.py` → `train_person` |
| Encode one image → embedding (temp file, DeepFace, L2) | `backend/app/services/face_encoder.py` → `encode_image` |
| Person table (id, name, embedding, etc.) | `backend/app/models/attendance.py` → `Person` |

You can use this document to explain, point by point, what happens from the moment you upload 4–5 images until the system has one stored “face signature” for that person.
