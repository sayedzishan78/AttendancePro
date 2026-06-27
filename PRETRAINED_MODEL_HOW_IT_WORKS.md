# How the Pretrained Model Works in Our Project

This document explains **what “pretrained model” means** in our project and **how it is used** — in simple language, with code references.

---

## 1. What Is a Pretrained Model?

- **Pretrained** = the model was **already trained by someone else** (e.g. researchers) on a **large dataset of faces** (e.g. millions of face images).
- **We do NOT train this model.** We only **use** it to convert a face image into a **list of numbers** (embedding). That list is like a “fingerprint” for that face.
- So: **pretrained** = ready-to-use model; we load it and call it; we never update its weights.

---

## 2. Which Pretrained Model We Use

- **Name:** **VGG-Face**
- **Library:** **DeepFace** (Python). DeepFace gives us easy access to VGG-Face and other models.
- **Where it’s set in code:**  
  `backend/app/services/face_encoder.py`:

```python
self.model_name = "VGG-Face"  # Can also use "Facenet", "OpenFace", etc.
```

- **What it does:**  
  Given an image (or a cropped face), it outputs a **vector of 2624 numbers**. That vector is the **face embedding**. Same person in different photos gives **similar** vectors; different persons give **different** vectors.

---

## 3. How We Load the Pretrained Model (Preload)

- We want the model **loaded once** when the backend starts, so the **first** user request doesn’t wait for a big download.
- When the backend starts, it creates one **FaceEncoder** and calls **`preload_model()`** on it.

**Where:**  
`backend/app/api/routes.py`:

```python
encoder = FaceEncoder()
# Preload model on startup
encoder.preload_model()
```

**What `preload_model()` does** (in `backend/app/services/face_encoder.py`):

1. Creates a **small dummy image** (random pixels, 100×100).
2. Saves it as a **temporary file** (DeepFace needs a file path).
3. Calls **`DeepFace.represent(img_path=..., model_name="VGG-Face", ...)`** once.
4. That **first call** makes DeepFace **download** the VGG-Face weights from the internet (if not already cached) and **load** them into memory.
5. Deletes the temp file.
6. Sets **`_model_preloaded = True`** so we know the model is ready.

**Code:**

```python
def preload_model(self):
    if self._model_preloaded:
        return True
    try:
        dummy_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            cv2.imwrite(tmp_file.name, dummy_img)
            tmp_path = tmp_file.name
        try:
            DeepFace.represent(
                img_path=tmp_path,
                model_name=self.model_name,
                enforce_detection=False,  # Don't fail on dummy image
                detector_backend='opencv'
            )
            self._model_preloaded = True
            return True
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        ...
```

So: **pretrained model “works” at load time** by being **downloaded (if needed) and loaded once** at startup; after that, every face encoding reuses the same in-memory model.

---

## 4. How We Use the Pretrained Model (Encoding a Face)

Whenever we need to get a **face embedding** (e.g. when you upload 4–5 training images, or when the webcam captures a frame):

1. We have an **image** (bytes or numpy array).
2. We call **`encoder.encode_image(image_bytes)`** or use **`detect_and_encode_faces`** for a full image with multiple faces.
3. Inside **`encode_image`**:
   - The image is written to a **temporary file** (DeepFace expects a path).
   - We call **`DeepFace.represent(img_path=..., model_name="VGG-Face", enforce_detection=True, detector_backend='opencv')`**.
   - **OpenCV** (detector) finds the **face region** in the image.
   - **VGG-Face** (pretrained model) takes that face region and outputs a **2624-dimensional vector**.
   - We **L2-normalize** that vector (make it unit length) and return it.
4. We **do not** change the model’s weights; we only **read** its output.

**Code (concept):**

```python
embedding_obj = DeepFace.represent(
    img_path=tmp_path,
    model_name=self.model_name,
    enforce_detection=True,
    detector_backend='opencv'
)
embedding = np.array(embedding_obj[0]['embedding'])
return self.l2_normalize(embedding)
```

So: **the pretrained model “works” at runtime** by turning each face image into **one fixed-size vector** that we then use for comparison (e.g. cosine similarity) with stored embeddings in our database.

---

## 5. Short Summary

| Question | Answer |
|----------|--------|
| What is the pretrained model? | **VGG-Face**, used via the **DeepFace** library. |
| Do we train it? | **No.** We only use it to get face embeddings. |
| When is it loaded? | At backend startup, in **`encoder.preload_model()`** (triggered from `routes.py`). |
| How is it loaded? | First call to **`DeepFace.represent(...)`** downloads (if needed) and loads the model into memory. |
| How do we use it? | We pass an image (via temp file) to **`DeepFace.represent`**; we get back a 2624-d vector; we L2-normalize and use it for training (average with other photos) or recognition (compare with DB). |
| Where is the code? | **`backend/app/services/face_encoder.py`** (FaceEncoder, preload_model, encode_image, detect_and_encode_faces); **`backend/app/api/routes.py`** (encoder creation and preload_model call). |

---

## 6. One-Line Answer for “How Does the Pretrained Model Work?”

**We use the pretrained VGG-Face model (via DeepFace): we load it once at startup, and then we only use it to convert each face image into a 2624-dimensional vector (embedding); we never train or update the model, only use its output for our own training (averaging) and recognition (comparing with the database).**

You can use this document to explain in a seminar or viva how the pretrained model works in your project.
