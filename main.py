import sys
import os
import cv2
import pickle
import numpy as np
import subprocess
import face_recognition
import dlib
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import QTimer, Qt
from imutils import face_utils
from scipy.spatial import distance
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
# if session_type == "wayland":
#     os.environ["QT_QPA_PLATFORM"] = "wayland"
# else:
#     os.environ["QT_QPA_PLATFORM"] = "xcb"

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

class AttendanceSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition Attendance System")
        self.showFullScreen()
        self.initUI()  # <- move all UI setup here
        self.setupCamera()
        self.loadEncodings()

    def initUI(self):
        # Window background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        # Constants
        self.EAR_THRESHOLD = 0.22
        self.CONSEC_FRAMES = 3
        self.REQUIRED_BLINKS = 3

        # Header
        header = QLabel("\U0001F4D8 ATTENDANCE SYSTEM")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #7A5FFF;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)

        # Camera feed
        self.image_label = QLabel()
        self.image_label.setFixedSize(960, 720)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 4px solid #7A5FFF;
                border-radius: 12px;
                background-color: white;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Status and details
        self.status_label = QLabel("\U0001F4F8 Waiting for Face...")
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #6a11cb, stop:1 #2575fc);
                padding: 12px;
                border-radius: 12px;
                margin: 10px;
            }
        """)

        self.blink_label = QLabel("")
        self.blink_label.setFont(QFont("Arial", 14))
        self.blink_label.setAlignment(Qt.AlignCenter)
        self.blink_label.setStyleSheet("""
            QLabel {
                background-color: #FFE082;
                color: #4E342E;
                padding: 8px 18px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 5px;
            }
        """)

        self.attendance_status_label = QLabel("")
        self.attendance_status_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.attendance_status_label.setAlignment(Qt.AlignCenter)
        self.attendance_status_label.setStyleSheet("""
            QLabel {
                color: #d84315;
                background-color: #FFF3E0;
                border: 1px solid #FFCCBC;
                padding: 8px;
                border-radius: 10px;
                margin-top: 8px;
            }
        """)

        self.back_button = QPushButton("Back to Home")
        self.back_button.setFixedSize(150, 40)
        self.back_button.clicked.connect(self.go_home)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2979FF;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)

        self.photo_label = QLabel()
        self.photo_label.setFixedSize(510, 500)
        self.photo_label.setScaledContents(True)
        self.photo_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        self.photo_label.setGraphicsEffect(shadow)

        self.photo_msg_label = QLabel("")
        self.photo_msg_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.photo_msg_label.setAlignment(Qt.AlignCenter)
        self.photo_msg_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                margin-top: 8px;
                padding: 6px;
                background-color: #E0F7FA;
                border: 1px solid #81D4FA;
                border-radius: 8px;
            }
        """)

        self.details_label = QLabel("")
        self.details_label.setFont(QFont("Arial", 11))
        self.details_label.setStyleSheet("""
            QLabel {
                background-color: #FAFAFA;
                border: 1px solid #D1D1D1;
                border-radius: 12px;
                padding: 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #333;
            }
        """)
        self.details_label.setAlignment(Qt.AlignTop)
        self.details_label.setWordWrap(True)

        # Layout
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addWidget(self.back_button, alignment=Qt.AlignRight)

        right_panel = QVBoxLayout()
        right_panel.addLayout(top_row)
        right_panel.addWidget(self.status_label)
        right_panel.addWidget(self.blink_label)
        right_panel.addWidget(self.photo_label, alignment=Qt.AlignCenter)
        right_panel.addWidget(self.photo_msg_label)
        right_panel.addWidget(self.attendance_status_label)
        right_panel.addWidget(self.details_label)
        right_panel.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label, stretch=2)
        main_layout.addLayout(right_panel, stretch=1)

        final_layout = QVBoxLayout()
        final_layout.setContentsMargins(20, 20, 20, 20)
        final_layout.addWidget(header)
        final_layout.addSpacing(10)
        final_layout.addLayout(main_layout)
        self.setLayout(final_layout)

    def setupCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def loadEncodings(self):
        with open("EncodeFile.p", "rb") as f:
            self.encodeListKnown, self.studentIds = pickle.load(f)

        self.recognized_students = {}
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        self.csv_file_path = os.path.join(BASE_DIR, "students.csv")

        self.attendance_file_path = os.path.join(BASE_DIR, "attendance_log.csv")


        self.attendance_time_window = timedelta(minutes=10)

        self.last_matched_img = None
        self.last_matched_id = None

    def get_attendance_summary(self, student_id):
        count = 0
        last_time = "N/A"
        if os.path.exists(self.attendance_file_path):
            with open(self.attendance_file_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["University ID"] == student_id:
                        count += 1
                        last_time = f"{row['Date']} {row['Time']}"
        return count, last_time

    def go_home(self):
        try:
            self.timer.stop()
            if self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            self.close()

            # Import here to avoid circular import at module level
            from home import HomePage
            self.home_window = HomePage()
            self.home_window.show()
        except Exception as e:
            print(f"[Error] Failed to go home: {e}")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

    def get_student_info(self, student_id):
        try:
            with open(self.csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                reader.fieldnames = [field.strip() for field in reader.fieldnames]
                for row in reader:
                    clean_row = {str(k).strip(): str(v).strip() if v is not None else "" for k, v in row.items()}
                    if clean_row.get("University ID", "").strip() == student_id.strip():
                        return clean_row
        except Exception as e:
            print(f"Error reading CSV: {e}")
        return None

    def mark_attendance(self, student_info):
        if not student_info:
            self.attendance_status_label.setText("❌ Student info missing.")
            return

        now = datetime.now()
        student_id = student_info.get("University ID", "N/A")

        attendance_marked = False

        if os.path.exists(self.attendance_file_path):
            with open(self.attendance_file_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reversed(list(reader)):
                    if row["University ID"] == student_id:
                        try:
                            last_time = datetime.strptime(f"{row['Date']} {row['Time']}", "%Y-%m-%d %H:%M:%S")
                            if now - last_time < self.attendance_time_window:
                                self.attendance_status_label.setText(
                                    f"⚠️ Attendance already marked for {student_id} at {last_time.strftime('%H:%M:%S')}."
                                )
                                return
                        except Exception as e:
                            print(f"[WARN] Failed to parse previous attendance time: {e}")
                        break

        with open(self.attendance_file_path, "a", newline="") as f:
            writer = csv.writer(f)
            if os.stat(self.attendance_file_path).st_size == 0:
                writer.writerow(["Name", "University ID","Program","Branch","Mobile", "Date", "Time"])

            writer.writerow([
                student_info.get("Name", "N/A"),
                student_info.get("University ID", "N/A"),
                student_info.get("Program", "N/A"),
                student_info.get("Branch", "N/A"),
                student_info.get("Mobile", "N/A"),
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S")
            ])
            self.attendance_status_label.setText(f"✅ Attendance marked at {now.strftime('%H:%M:%S')}")
            attendance_marked = True

        if attendance_marked:
            count, last_time = self.get_attendance_summary(student_id)
            self.details_label.setText(
                f"<b>Name:</b> {student_info.get('Name', 'N/A')}<br>"
                f"<b>University ID:</b> {student_id}<br>"
                f"<b>Program:</b> {student_info.get('Program', 'N/A')}<br>"
                f"<b>Branch:</b> {student_info.get('Branch', 'N/A')}<br>"
                f"<b>Mobile:</b> {student_info.get('Mobile', 'N/A')}<br>"
                f"<b>Total Attendance:</b> {count}<br>"
                f"<b>Last Marked:</b> {last_time}"
            )

    def update_frame(self):
        ret, img = self.cap.read()
        if not ret:
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        small_img = cv2.resize(img_rgb, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small_img)
        encodings = face_recognition.face_encodings(small_img, face_locations)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dlib_faces = self.detector(gray)

        for encodeFace, faceLoc in zip(encodings, face_locations):
            # Compute matches and distances
            faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            # Set a strict threshold (recommended: 0.45 or lower for better accuracy)
            threshold = 0.45

            if faceDis[matchIndex] < threshold:
                student_id = self.studentIds[matchIndex]

                if student_id not in self.recognized_students:
                    self.recognized_students[student_id] = {
                        "blinks": 0,
                        "eye_closed": False,
                        "verified": False,
                        "logged": False
                    }

                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Blink Detection
                matching_face = min(
                    dlib_faces,
                    key=lambda f: abs(f.left() + f.width() // 2 - (x1 + x2) // 2) +
                                  abs(f.top() + f.height() // 2 - (y1 + y2) // 2),
                    default=None
                )
                if matching_face is not None:
                    shape = self.predictor(gray, matching_face)
                    shape_np = face_utils.shape_to_np(shape)
                    left_eye = shape_np[42:48]
                    right_eye = shape_np[36:42]
                    avg_ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

                    student_blink = self.recognized_students[student_id]
                    if not student_blink["verified"]:
                        if avg_ear < self.EAR_THRESHOLD:
                            student_blink["eye_closed"] = True
                        else:
                            if student_blink["eye_closed"]:
                                student_blink["blinks"] += 1
                                student_blink["eye_closed"] = False

                        cv2.putText(img_rgb, f"Blinks: {student_blink['blinks']}/{self.REQUIRED_BLINKS}",
                                    (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        cv2.putText(img_rgb, f"ID: {student_id}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
# ================================================================
# Project: Face Recognition Based Attendance System
# Author: Arnav Pundir
# Year: 2025
# License: Custom Proprietary License - All Rights Reserved
# Unauthorized use, copying, or distribution is strictly prohibited.
# ================================================================
                        self.status_label.setText("👁️ Please blink to verify your identity")
                        self.blink_label.setText(f"🔁 Blinks: {student_blink['blinks']}/{self.REQUIRED_BLINKS}")

                        if student_blink["blinks"] >= self.REQUIRED_BLINKS:
                            student_blink["verified"] = True

                    if student_blink["verified"]:
                        self.status_label.setText(f"✅ Welcome, {student_id}")
                        self.blink_label.setText("")

                        if not student_blink["logged"]:
                            student_blink["logged"] = True
                            student_info = self.get_student_info(student_id)
                            self.mark_attendance(student_info)

                            possible_exts = [".jpg", ".jpeg", ".png"]
                            for ext in possible_exts:
                                photo_path = os.path.join(BASE_DIR, "images", f"{student_id}{ext}")
                                if os.path.exists(photo_path):
                                    self.last_matched_img = QPixmap(photo_path)
                                    self.last_matched_id = student_id
                                    break
                                else:
                                    # Unknown face detected
                                    print(f"Face not recognized. Closest distance: {faceDis[matchIndex]:.2f} — treated as Unknown")

                                    y1, x2, y2, x1 = [v * 4 for v in faceLoc]

                                    # Draw red box for unknown
                                    cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 0, 255), 2)

                                    # Add 🚫 and warning message
                                    cv2.putText(img_rgb, "🚫 Unknown Face Detected", (x1, y1 - 10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                                    # Set PyQt status label
                                    self.status_label.setText("🚫 Unknown Face Detected — Please try again")

                                    # Optionally clear previous info for clarity
                                    self.blink_label.setText("")
                                    self.photo_label.clear()
                                    self.photo_msg_label.setText("")
                                    self.details_label.setText("")

            # Convert frame to Qt and display
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            convert_to_qt = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_qt = convert_to_qt.scaled(
                self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(scaled_qt))

            # Display matched photo and student info
            if self.last_matched_id:
                self.photo_label.setPixmap(self.last_matched_img)
                self.photo_msg_label.setText(f"🖼️ Matched face with <b>{self.last_matched_id}</b>")

                student_info = self.get_student_info(self.last_matched_id)
                if student_info:
                    attendance_count, last_time = self.get_attendance_summary(self.last_matched_id)

                    # Emoji mapping
                    emoji_map = {
                        'Name': '👤',
                        'University ID': '🎓',
                        'Program': '📘',
                        'Branch': '🏢',
                        'Mobile': '📞',
                        'gmail': '📧',
                        'Total Attendance': '📅',
                        'Last Marked': '🕒'
                    }

                    # Add attendance summary
                    student_info['Total Attendance'] = str(attendance_count)
                    student_info['Last Marked'] = last_time

                    # Remove any image-related keys
                    student_info = {
                        k: v for k, v in student_info.items()
                        if 'image' not in k.lower()
                    }

                    # Prepare split rows for table
                    items = list(student_info.items())
                    half = (len(items) + 1) // 2
                    row1, row2 = items[:half], items[half:]

                    # Build table HTML
                    details_text = "<div align='center'><table style='font-size:13px;'>"
                    for row in [row1, row2]:
                        details_text += "<tr>"
                        for key, value in row:
                            emoji = emoji_map.get(key, 'ℹ️')
                            details_text += f"<td style='padding-bottom: 12px;'><b>{emoji} {key}:</b></td><td style='padding-bottom: 12px;'>{value}</td>"
                        details_text += "</tr>"
                    details_text += "</table></div>"

                    self.details_label.setText(details_text)
                else:
                    self.details_label.setText("Student info not found.")
            else:
                self.photo_label.clear()
                self.photo_msg_label.setText("")
                self.details_label.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceSystem()
    window.show()
    sys.exit(app.exec_())

else:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

class AttendanceSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition Attendance System")
        self.showFullScreen()
        self.initUI()  # <- move all UI setup here
        self.setupCamera()
        self.loadEncodings()

    def initUI(self):
        # Window background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        # Constants
        self.EAR_THRESHOLD = 0.22
        self.CONSEC_FRAMES = 3
        self.REQUIRED_BLINKS = 3

        # Header
        header = QLabel("\U0001F4D8 ATTENDANCE SYSTEM")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #7A5FFF;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)

        # Camera feed
        self.image_label = QLabel()
        self.image_label.setFixedSize(960, 720)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 4px solid #7A5FFF;
                border-radius: 12px;
                background-color: white;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Status and details
        self.status_label = QLabel("\U0001F4F8 Waiting for Face...")
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #6a11cb, stop:1 #2575fc);
                padding: 12px;
                border-radius: 12px;
                margin: 10px;
            }
        """)

        self.blink_label = QLabel("")
        self.blink_label.setFont(QFont("Arial", 14))
        self.blink_label.setAlignment(Qt.AlignCenter)
        self.blink_label.setStyleSheet("""
            QLabel {
                background-color: #FFE082;
                color: #4E342E;
                padding: 8px 18px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 5px;
            }
        """)

        self.attendance_status_label = QLabel("")
        self.attendance_status_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.attendance_status_label.setAlignment(Qt.AlignCenter)
        self.attendance_status_label.setStyleSheet("""
            QLabel {
                color: #d84315;
                background-color: #FFF3E0;
                border: 1px solid #FFCCBC;
                padding: 8px;
                border-radius: 10px;
                margin-top: 8px;
            }
        """)

        self.back_button = QPushButton("Back to Home")
        self.back_button.setFixedSize(150, 40)
        self.back_button.clicked.connect(self.go_home)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2979FF;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)

        self.photo_label = QLabel()
        self.photo_label.setFixedSize(510, 500)
        self.photo_label.setScaledContents(True)
        self.photo_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        self.photo_label.setGraphicsEffect(shadow)

        self.photo_msg_label = QLabel("")
        self.photo_msg_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.photo_msg_label.setAlignment(Qt.AlignCenter)
        self.photo_msg_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                margin-top: 8px;
                padding: 6px;
                background-color: #E0F7FA;
                border: 1px solid #81D4FA;
                border-radius: 8px;
            }
        """)

        self.details_label = QLabel("")
        self.details_label.setFont(QFont("Arial", 11))
        self.details_label.setStyleSheet("""
            QLabel {
                background-color: #FAFAFA;
                border: 1px solid #D1D1D1;
                border-radius: 12px;
                padding: 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #333;
            }
        """)
        self.details_label.setAlignment(Qt.AlignTop)
        self.details_label.setWordWrap(True)

        # Layout
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addWidget(self.back_button, alignment=Qt.AlignRight)

        right_panel = QVBoxLayout()
        right_panel.addLayout(top_row)
        right_panel.addWidget(self.status_label)
        right_panel.addWidget(self.blink_label)
        right_panel.addWidget(self.photo_label, alignment=Qt.AlignCenter)
        right_panel.addWidget(self.photo_msg_label)
        right_panel.addWidget(self.attendance_status_label)
        right_panel.addWidget(self.details_label)
        right_panel.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label, stretch=2)
        main_layout.addLayout(right_panel, stretch=1)

        final_layout = QVBoxLayout()
        final_layout.setContentsMargins(20, 20, 20, 20)
        final_layout.addWidget(header)
        final_layout.addSpacing(10)
        final_layout.addLayout(main_layout)
        self.setLayout(final_layout)

    def setupCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def loadEncodings(self):
        with open("EncodeFile.p", "rb") as f:
            self.encodeListKnown, self.studentIds = pickle.load(f)

        self.recognized_students = {}
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        self.csv_file_path = os.path.join(BASE_DIR, "students.csv")
        self.attendance_file_path =  os.path.join(BASE_DIR, "attendance_log.csv")
        self.attendance_time_window = timedelta(minutes=10)

        self.last_matched_img = None
        self.last_matched_id = None

    def get_attendance_summary(self, student_id):
        count = 0
        last_time = "N/A"
        if os.path.exists(self.attendance_file_path):
            with open(self.attendance_file_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["University ID"] == student_id:
                        count += 1
                        last_time = f"{row['Date']} {row['Time']}"
        return count, last_time

    def go_home(self):
        try:
            self.timer.stop()
            if self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            self.close()

            # Import here to avoid circular import at module level
            from home import HomePage
            self.home_window = HomePage()
            self.home_window.show()
        except Exception as e:
            print(f"[Error] Failed to go home: {e}")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

    def get_student_info(self, student_id):
        try:
            with open(self.csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                reader.fieldnames = [field.strip() for field in reader.fieldnames]
                for row in reader:
                    clean_row = {str(k).strip(): str(v).strip() if v is not None else "" for k, v in row.items()}
                    if clean_row.get("University ID", "").strip() == student_id.strip():
                        return clean_row
        except Exception as e:
            print(f"Error reading CSV: {e}")
        return None

    def mark_attendance(self, student_info):
        if not student_info:
            self.attendance_status_label.setText("❌ Student info missing.")
            return

        now = datetime.now()
        student_id = student_info.get("University ID", "N/A")

        attendance_marked = False

        if os.path.exists(self.attendance_file_path):
            with open(self.attendance_file_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reversed(list(reader)):
                    if row["University ID"] == student_id:
                        try:
                            last_time = datetime.strptime(f"{row['Date']} {row['Time']}", "%Y-%m-%d %H:%M:%S")
                            if now - last_time < self.attendance_time_window:
                                self.attendance_status_label.setText(
                                    f"⚠️ Attendance already marked for {student_id} at {last_time.strftime('%H:%M:%S')}."
                                )
                                return
                        except Exception as e:
                            print(f"[WARN] Failed to parse previous attendance time: {e}")
                        break

        with open(self.attendance_file_path, "a", newline="") as f:
            writer = csv.writer(f)
            if os.stat(self.attendance_file_path).st_size == 0:
                writer.writerow(["Name", "University ID", "Program", "Branch", "Mobile", "Date", "Time"])
            writer.writerow([
                student_info.get("Name", "N/A"),
                student_info.get("University ID", "N/A"),
                student_info.get("Program", "N/A"),
                student_info.get("Branch", "N/A"),
                student_info.get("Mobile", "N/A"),
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S")
            ])
            attendance_marked = True

        if attendance_marked:
            self.attendance_status_label.setText(
                f"✅ Attendance marked for {student_id} at {now.strftime('%H:%M:%S')}."
            )

    def update_frame(self):
        ret, img = self.cap.read()
        if not ret:
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        small_img = cv2.resize(img_rgb, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small_img)
        encodings = face_recognition.face_encodings(small_img, face_locations)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dlib_faces = self.detector(gray)

        for encodeFace, faceLoc in zip(encodings, face_locations):
            # Compute matches and distances
            faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            # Set a strict threshold (recommended: 0.45 or lower for better accuracy)
            threshold = 0.45

            if faceDis[matchIndex] < threshold:
                student_id = self.studentIds[matchIndex]

                if student_id not in self.recognized_students:
                    self.recognized_students[student_id] = {
                        "blinks": 0,
                        "eye_closed": False,
                        "verified": False,
                        "logged": False
                    }

                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Blink Detection
                matching_face = min(
                    dlib_faces,
                    key=lambda f: abs(f.left() + f.width() // 2 - (x1 + x2) // 2) +
                                  abs(f.top() + f.height() // 2 - (y1 + y2) // 2),
                    default=None
                )
                if matching_face is not None:
                    shape = self.predictor(gray, matching_face)
                    shape_np = face_utils.shape_to_np(shape)
                    left_eye = shape_np[42:48]
                    right_eye = shape_np[36:42]
                    avg_ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

                    student_blink = self.recognized_students[student_id]
                    if not student_blink["verified"]:
                        if avg_ear < self.EAR_THRESHOLD:
                            student_blink["eye_closed"] = True
                        else:
                            if student_blink["eye_closed"]:
                                student_blink["blinks"] += 1
                                student_blink["eye_closed"] = False

                        cv2.putText(img_rgb, f"Blinks: {student_blink['blinks']}/{self.REQUIRED_BLINKS}",
                                    (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        cv2.putText(img_rgb, f"ID: {student_id}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                        self.status_label.setText("👁️ Please blink to verify your identity")
                        self.blink_label.setText(f"🔁 Blinks: {student_blink['blinks']}/{self.REQUIRED_BLINKS}")
                        if student_blink["blinks"] >= self.REQUIRED_BLINKS:
                            student_blink["verified"] = True
                    if student_blink["verified"]:
                        self.status_label.setText(f"✅ Welcome, {student_id}")
                        self.blink_label.setText("")
                        if not student_blink["logged"]:
                            student_blink["logged"] = True
                            student_info = self.get_student_info(student_id)
                            self.mark_attendance(student_info)
                            possible_exts = [".jpg", ".jpeg", ".png"]
                            for ext in possible_exts:
                                photo_path = os.path.join(BASE_DIR, "images", f"{student_id}{ext}")
                                if os.path.exists(photo_path):
                                    self.last_matched_img = QPixmap(photo_path)
                                    self.last_matched_id = student_id
                                    break
                                else:
                                    # Unknown face detected
                                    print(f"Face not recognized. Closest distance: {faceDis[matchIndex]:.2f} — treated as Unknown")
                                    y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                                    # Draw red box for unknown
                                    cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                    # Add 🚫 and warning message
                                    cv2.putText(img_rgb, "🚫 Unknown Face Detected", (x1, y1 - 10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                                    # Set PyQt status label
                                    self.status_label.setText("🚫 Unknown Face Detected — Please try again")
                                    # Optionally clear previous info for clarity
                                    self.blink_label.setText("")
                                    self.photo_label.clear()
                                    self.photo_msg_label.setText("")
                                    self.details_label.setText("")
            # Convert frame to Qt and display
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            convert_to_qt = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_qt = convert_to_qt.scaled(
                self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(scaled_qt))
            # Display matched photo and student info
            if self.last_matched_id:
                self.photo_label.setPixmap(self.last_matched_img)
                self.photo_msg_label.setText(f"🖼️ Matched face with <b>{self.last_matched_id}</b>")

                student_info = self.get_student_info(self.last_matched_id)
                if student_info:
                    attendance_count, last_time = self.get_attendance_summary(self.last_matched_id)
                    # Emoji mapping
                    emoji_map = {
                        'Name': '👤',
                        'University ID': '🎓',
                        'Program': '📘',
                        'Branch': '🏢',
                        'Mobile': '📞',
                        'gmail': '📧',
                        'Total Attendance': '📅',
                        'Last Marked': '🕒'
                    }
                    # Add attendance summary
                    student_info['Total Attendance'] = str(attendance_count)
                    student_info['Last Marked'] = last_time
                    # Remove any image-related keys
                    student_info = {
                        k: v for k, v in student_info.items()
                        if 'image' not in k.lower()
                    }
                    # Prepare split rows for table
                    items = list(student_info.items())
                    half = (len(items) + 1) // 2
                    row1, row2 = items[:half], items[half:]
                    # Build table HTML
                    details_text = "<div align='center'><table style='font-size:13px;'>"
                    for row in [row1, row2]:
                        details_text += "<tr>"
                        for key, value in row:
                            emoji = emoji_map.get(key, 'ℹ️')
                            details_text += f"<td style='padding-bottom: 12px;'><b>{emoji} {key}:</b></td><td style='padding-bottom: 12px;'>{value}</td>"
                        details_text += "</tr>"
                    details_text += "</table></div>"
                    self.details_label.setText(details_text)
                else:
                    self.details_label.setText("Student info not found.")
            else:
                self.photo_label.clear()
                self.photo_msg_label.setText("")
                self.details_label.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceSystem()
    window.show()
    sys.exit(app.exec_())
