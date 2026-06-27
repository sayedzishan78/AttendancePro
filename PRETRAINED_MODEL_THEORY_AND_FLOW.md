# Pretrained Model — Theory: What We Download, What’s Inside, and How It Works With Our Uploaded Images

This is a **theoretical** explanation only (no code). It answers: what we download, what “data” is already inside the model, and how everything works when you upload images from the frontend.

---

## 1. What We Download (the “500 something” MB)

When the backend runs for the first time, it downloads a **pretrained model** (e.g. VGG-Face). The size is often around **500 MB or more** depending on the model and framework.

- That download is **not** a database of faces or a list of people.
- It is the **trained neural network**: millions of **numbers (weights and parameters)** that were learned by training on a **huge dataset of face images** (often millions of images, from public research datasets).
- So the “data” already available in the model is **learned knowledge**: the network has already learned how to turn **any** face image into a **meaningful list of numbers** (an embedding). Same person tends to get similar numbers; different people get different numbers. We do not add our users’ faces “into” this file; we only **use** the model to convert our images into such lists of numbers.

---

## 2. What Is “Already There” in the Model (No Upload Yet)

- **Already there:** The **architecture** of the network (how many layers, how they are connected) and the **weights** (all the learned numbers). Together they form a **function**: input = face image, output = a long vector of numbers (e.g. 2624 numbers for VGG-Face).
- **Not there:** Your app’s persons, your users’ photos, or any list of “who is who.” Those live in **your database** (e.g. one averaged embedding per person that you computed using this model). So: the **model** = general “face → numbers” machine; the **database** = your specific people and their face signatures.

So when we say “there is already data in the model,” we mean **learned parameters (weights)** that allow it to produce good face embeddings. We do **not** mean a ready-made list of our students or staff.

---

## 3. Flow When You Upload Images From the Frontend (Theory, Step by Step)

### From the user’s side

- The user opens the **People** page, fills name and other details, selects **4 to 5 face images**, and clicks **Create & Train** (or **Save Changes** with new photos).
- The browser sends those images to the server (e.g. as multipart form data). So the **frontend** only **upload**s the images; it does not run any face algorithm. All face processing happens on the **backend**.

### On the server (backend) — in order

**Step 1 — Receiving the images**  
The server receives the request and the 4–5 image files. It now has raw image data (pixels) for each file. No face “data” from the pretrained model is mixed in here; the model is only used in the next steps as a **tool** to process these pixels.

**Step 2 — Face detection (before the pretrained “embedding” model)**  
Before we can use the big pretrained model, we need to **find where the face is** in each image. So we use a **face detection** algorithm (e.g. OpenCV-based detector). That algorithm looks at the image and returns a **rectangle** (region) where the face is. It does **not** identify “who” the person is; it only says “there is a face in this box.” So the flow is: **full image → detector → face region (crop)**.  
If no face is found in an image, that image is skipped. Only images with at least one detected face are used for the next step.

**Step 3 — Using the pretrained model to get an embedding**  
For each **face region** (crop) we got from Step 2, we pass it through the **pretrained model** (e.g. VGG-Face). That model was trained on millions of faces so that its output — a long vector of numbers — is **good for comparing faces**: same person → similar vector; different person → different vector. So the **algorithm** here is: **face crop → pretrained neural network → one vector of numbers (embedding)**.  
We do **not** train or change this model. We only **run** it (forward pass) and take the output vector. The “data” already in the model (its weights) is what makes this vector meaningful.

**Step 4 — Normalization**  
The raw vector from the model is then **L2-normalized**: we scale it so that its length is 1. That way, when we later compare two faces, we can use a simple **dot product** (or cosine similarity) between two vectors. So the algorithm here is: **embedding → divide by its length → unit-length embedding**.

**Step 5 — Averaging (for training with 4–5 images)**  
We have 4–5 images, so we get 4–5 vectors (one per image). We **average** them: we add the vectors and divide by the number of vectors. Then we **normalize again** so the average is also unit length. That single averaged vector is the **representative face** for that person. So the algorithm is: **sum of embeddings ÷ count → normalize → one “signature” vector**.  
This averaged vector is what we **store** in **our database** for that person. The pretrained model is not “updated” with this person; we only **use** its output and then save that output in our own tables.

**Step 6 — Saving in our database**  
That one averaged vector (and the person’s id, name, type, etc.) is saved in **our** database. So: the **pretrained model** stays as it was downloaded (no new “data” added to it); the **new data** is only in **our** system: one vector per person, computed using the model.

---

## 4. Which Algorithms Are Involved (Theory Only)

- **Face detection:** A classical or simple neural detector that finds “where is a face” in the image (e.g. OpenCV-based). It does **not** use the big 500 MB model; it’s a separate, lighter step.
- **Face embedding (the pretrained model):** A **deep convolutional neural network** (e.g. VGG-Face) that was trained so that its last layers output a **vector** that is good for comparing faces. The “algorithm” is: many layers of convolutions and pooling, then fully connected layers, then the embedding vector. The **weights** of this network are what we downloaded (the “500 something” MB); they are fixed when we use them.
- **Normalization:** L2 normalization (make vector length 1) so that **cosine similarity** between two faces is just the **dot product** of their normalized vectors.
- **Averaging:** For training, we take the **mean** of the 4–5 embeddings and normalize again. So the “algorithm” for “one face per person” is: **arithmetic mean + L2 normalize**.
- **Recognition (later, when camera or single image is used):** We get a new face embedding from the pretrained model (same steps: detect → crop → model → normalize). We compare this new vector to **each** stored vector in our database (e.g. dot product). The **highest score** above a **threshold** gives “recognized as that person”; otherwise “unknown.” So the algorithm is: **similarity = dot product (or cosine)** and **decision = threshold**.

---

## 5. Summary in Plain Words

- **What we download:** A **pretrained neural network** (e.g. ~500 MB). The “data” in it is **learned weights** from training on millions of faces. There is **no** list of our users or their photos inside it.
- **What happens when you upload 4–5 images:** The server **detects** the face in each image, runs each face crop through the **pretrained model** to get a vector, **normalizes** each vector, **averages** the vectors into one, and **saves that one vector** in our database for that person. The pretrained model is **never** updated; we only **use** it to produce these vectors.
- **Algorithms involved:** Face **detection** (find face region); **pretrained CNN** (face → embedding); **L2 normalization**; **averaging** for training; **dot product / cosine similarity** and **threshold** for recognition.

This is the full theoretical picture: what the downloaded model is, what “data” is already in it, and how it works step by step when images are uploaded from the frontend — without writing any code.
