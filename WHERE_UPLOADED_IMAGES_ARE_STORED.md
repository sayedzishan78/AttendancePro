# When We Upload Images — Where Are They Stored?

This document explains **where** the images go when you upload them in this project. It depends on **which feature** you use.

---

## 1. Training (People Page — 4 to 5 Face Photos)

**When:** You upload 4–5 images on the **People** page and click **Create & Train** or **Save Changes** (with new photos).

**Where are the uploaded images stored?**

- **The uploaded image files are NOT stored anywhere permanently.**

What actually happens:

1. The server **receives** the images in the request (in memory).
2. For each image, the server **writes it to a temporary file** on disk (e.g. in the system temp folder) only because the face library (DeepFace) needs a file path to read the image.
3. The server **reads** that temp file to detect the face and get the face embedding (the list of numbers).
4. As soon as that is done, the server **deletes** the temporary file.
5. Only the **face embedding** (the vector of numbers) is saved — in the **database**, in the **Person** table, in the **embedding** column. The original photo is not kept.

So: **no permanent storage of the uploaded training images.** Only the computed **embedding** is stored in the database.

---

## 2. Single-Image Recognition (Upload One Image to Recognize)

**When:** You use the “recognize” feature where you upload **one image** and the system returns an image with faces marked (name and box).

**Where is the uploaded image stored?**

- The **uploaded image** itself is **not** stored permanently. It is read into memory, processed (face detection + recognition), and a **result image** (with boxes and labels drawn) is created.
- That **result image** is written to the server’s **output folder** (e.g. a folder named **outputs** under the backend project, often `backend/outputs`). The file name looks like `recognized_<random_id>.jpg`.
- The API **returns** that result image to the frontend (e.g. as the response). The file **remains** on the server in the **outputs** folder unless you delete it or clear that folder.

So: **uploaded image** → not stored; **result image** (marked photo) → stored in the **outputs** folder on the server.

---

## 3. Live Webcam Attendance (When “Save Images” Is On)

**When:** You run **live monitoring** with the webcam and the option to **save attendance images** is enabled.

**Where are images stored?**

- The **webcam frames** are not all saved. When the system **records attendance** for a person (and save-images is on), it can save **one snapshot** of that moment (the frame with the face and optional annotations).
- That image is saved in the same **output folder** as above (e.g. `backend/outputs`), with a name like `attendance_<date>_<time>_<id>.jpg`.
- The **path** to that file (e.g. `outputs/attendance_20250223_143052_abc123.jpg`) is stored in the **database** in the **Attendance** table, in the **image_path** column. So the image file sits on the server disk; the database only stores the path.

So: **webcam attendance images** (when saving is on) → stored in the **outputs** folder; the **path** is stored in the **database** (Attendance.image_path).

---

## Summary Table

| Scenario | Uploaded/original image stored? | What is stored, and where? |
|----------|--------------------------------|----------------------------|
| **Training (4–5 photos on People page)** | **No.** Temp file is deleted after use. | Only the **face embedding** (numbers) in the **database** (Person.embedding). |
| **Single-image recognition (upload one image)** | **No.** Only processed in memory. | The **result image** (with boxes/labels) is saved in the **outputs** folder on the server. |
| **Webcam attendance (save images on)** | N/A (camera, not “upload”). | One **attendance snapshot** per record in the **outputs** folder; its **path** in the **database** (Attendance.image_path). |

---

## Short Answer

- **Training uploads (4–5 images):** The images are **not** stored. They are used only in memory and in a temp file that is **deleted**. Only the **embedding** is stored in the **database**.
- **Recognition upload (1 image):** The uploaded image is **not** stored. The **marked result image** is stored in the server’s **outputs** folder.
- **Webcam:** **Attendance snapshots** (when save is on) are stored in the **outputs** folder; their **paths** are stored in the **database**.

So in most cases when we say “we upload the image,” the **image file itself** is not stored for long; only **derived data** (embedding or result image path) is stored in the database or in the outputs folder.
