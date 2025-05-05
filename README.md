# Face Recognition Attendance System

This is a desktop-based Face Recognition Attendance System built using Python and PyQt5. It includes real-time face recognition, blink-based liveness detection using dlib, and automatic attendance logging to CSV.

---

## ⚙️ Requirements

- **Python Version:** 3.10.13
- All required libraries are listed in `requirements.txt`.

---

## 📁 Project Structure

```
Face-Attendance-System/
│
├── main.py
├── requirements.txt
├── README.md
├── shape_predictor_68_face_landmarks.dat
├── images/
│   └── (student face images stored here)
```

---

## 📥 Setup Instructions

1. **Install Python 3.10.11**

   Ensure Python version 3.10.11 is installed:

   ```bash
   python --version
   ```

2. **Download the Facial Landmark Model**

   Download [`shape_predictor_68_face_landmarks.dat`](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2), extract it, and place the `.dat` file in the project directory.

3. **Create `images/` Folder**

   Create a folder named `images` in the root of the project. This will store student face images used for recognition.

4. **Install Required Libraries**

   It's recommended to use a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   Then install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**

   Start the application by running:

   ```bash
   python main.py
   ```

---

## 📌 Notes

- Keep the `images/` folder and the `.dat` file in the same directory where the project is unpacked.
- for login -  User Name is `admin@123` and the password is `admin` 
- Attendance records are saved in CSV format with student details and timestamps.
- Blink detection ensures liveness before marking attendance.

---

## 🧠 Technologies Used

- PyQt5
- OpenCV
- dlib
- NumPy

---

## 👤 Developed by

- Arnav Pundir
In collaboration with *Atharv Kumar* and *Aman Bhatti*
---
