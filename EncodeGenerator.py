import os
import cv2
import face_recognition
import pickle
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

# ================================================================
# Project: Face Recognition Based Attendance System
# Author: Arnav Pundir
# Year: 2025
# License: Custom Proprietary License - All Rights Reserved
# Unauthorized use, copying, or distribution is strictly prohibited.
# ================================================================


# os.environ["QT_QPA_PLATFORM"] = "wayland"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class FaceCropperApp(QMainWindow):
    def __init__(self, home_window=None):
        super().__init__()
        self.home_window = home_window
        self.setWindowTitle("Attendance System")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet("background-color: #f9f9f9;")

        # Default folder path for images
        self.folder_path = os.path.join(BASE_DIR, "images")

        self.preview_image = QLabel()
        self.status_label = QLabel()

        self.init_ui()

        # Automatically start encoding after UI is ready
        QTimer.singleShot(1000, self.auto_process_images)

    def init_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)

        title = QLabel("😎 Automated Face Encoder")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)

        self.preview_image.setFixedSize(300, 300)
        self.preview_image.setStyleSheet("border: 2px solid #aaa; border-radius: 10px;")

        self.status_label.setStyleSheet("font-size: 16px; color: #555;")
        self.status_label.setAlignment(Qt.AlignCenter)

        back_button = QPushButton("⬅ Back to Home")
        back_button.clicked.connect(self.go_back)
        back_button.setStyleSheet("padding: 10px 20px; font-size: 16px;")

        layout = QVBoxLayout()
        layout.addWidget(title)

        img_status_layout = QHBoxLayout()
        img_status_layout.addWidget(self.preview_image, alignment=Qt.AlignCenter)
        img_status_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        layout.addLayout(img_status_layout)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        widget.setLayout(layout)

    def auto_process_images(self):
        if os.path.exists(self.folder_path) and os.path.isdir(self.folder_path):
            self.status_label.setText(f"📁 Auto-selected folder:\n{self.folder_path}")
            self.process_images()
        else:
            QMessageBox.critical(self, "Folder Not Found", f"Default folder '{self.folder_path}' does not exist.")

    def process_images(self):
        encodings = []
        names = []

        for filename in os.listdir(self.folder_path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(self.folder_path, filename)
                name = os.path.splitext(filename)[0]

                image = cv2.imread(img_path)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb_image)
                face_encs = face_recognition.face_encodings(rgb_image, boxes)

                if face_encs:
                    encodings.append(face_encs[0])
                    names.append(name)

                    # Update preview and status
                    self.display_image(rgb_image)
                    self.status_label.setText(f"✅ Processed: {filename}")
                    QApplication.processEvents()
                else:
                    self.status_label.setText(f"⚠ No face found in: {filename}")
                    QApplication.processEvents()

        if encodings and names:
            with open('EncodeFile.p', 'wb') as f:
                pickle.dump((encodings, names), f)
            self.status_label.setText("🎉 All faces encoded Successfully`")
        else:
            self.status_label.setText("⚠ No valid face encodings found.")

    def display_image(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        height, width, channel = rgb_image.shape
        step = channel * width
        q_image = QImage(rgb_image.data, width, height, step, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image).scaled(300, 300, Qt.KeepAspectRatio)
        self.preview_image.setPixmap(pixmap)

    def go_back(self):
        try:
            # Import inside the method to avoid circular imports
            from adminPanel import AdminPanel
            self.admin_panel_window = AdminPanel()
            self.admin_panel_window.show()
            self.hide()
        except Exception as e:
            print(f"[Error] Failed to open Admin Panel: {e}")


# Run the app
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = FaceCropperApp()
    window.show()
    sys.exit(app.exec_())
