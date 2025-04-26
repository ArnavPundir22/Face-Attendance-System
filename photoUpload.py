import sys
import os
import shutil
import csv
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# os.environ["QT_QPA_PLATFORM"] = "wayland"
class UploadWindow(QWidget):
    def __init__(self, image_dir=os.path.join(BASE_DIR, "images"),csv_file=os.path.join(BASE_DIR, "students.csv")):
        super().__init__()
        self.setWindowTitle("Upload Student Photo")
        # Optional icon if available

        self.uploaded_path = None
        self.target_dir = os.path.abspath(image_dir)
        self.csv_path = os.path.abspath(csv_file)

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5ff;
                font-family: Arial;
            }
            QLabel, QLineEdit, QPushButton {
                font-size: 14px;
            }
        """)

        self.init_ui()
        self.showFullScreen()
 # Set full screen on launch

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QLabel("  📄 Upload Student Photo")
        header.setFixedHeight(60)
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("background-color: #7A5FFF; color: white; padding-left: 20px;")
        header.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        main_layout.addWidget(header)

        # Body
        body_frame = QFrame()
        body_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                margin: 20px;
                padding: 30px;
            }
        """)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(40)

        # Left: Image preview
        self.preview_label = QLabel("No photo selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                background-color: #fafafa;
                border-radius: 15px;
                color: #888;
            }
        """)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_layout.addWidget(self.preview_label, 1)  # Stretch factor

        # Right: Form fields and buttons
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        self.name_input = self.create_input("Full Name")
        self.university_id_input = self.create_input("University ID")
        self.program_input = self.create_input("Program (e.g., B.Tech)")
        self.branch_input = self.create_input("Branch (e.g., CSE)")
        self.mobile_input = self.create_input("Mobile Number")
        self.gmail_input = self.create_input("Gmail")

        for widget in [
            self.name_input, self.university_id_input,
            self.program_input, self.branch_input,
            self.mobile_input, self.gmail_input
        ]:
            form_layout.addWidget(widget)
# ================================================================
# Project: Face Recognition Based Attendance System
# Author: Arnav Pundir
# Year: 2025
# License: Custom Proprietary License - All Rights Reserved
# Unauthorized use, copying, or distribution is strictly prohibited.
# ================================================================
        self.choose_btn = self.create_button("📁  Choose Photo", "#7A5FFF")
        self.choose_btn.clicked.connect(self.choose_photo)
        form_layout.addWidget(self.choose_btn)

        self.save_btn = self.create_button("💾  Save Details & Photo", "#7A5FFF")
        self.save_btn.clicked.connect(self.save_photo)
        form_layout.addWidget(self.save_btn)

        self.back_btn = self.create_button("⬅️ Back to Home", "#cccccc", text_color="#333")
        self.back_btn.clicked.connect(self.go_home)
        form_layout.addWidget(self.back_btn)

        form_layout.addStretch()
        body_layout.addLayout(form_layout, 1)  # Stretch factor

        body_frame.setLayout(body_layout)
        main_layout.addWidget(body_frame)
        self.setLayout(main_layout)

    def create_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(40)
        input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #7A5FFF;
                border-radius: 10px;
                padding: 0 10px;
                background-color: #fff;
            }
        """)
        return input_field

    def create_button(self, text, color, text_color="white"):
        button = QPushButton(text)
        button.setFixedHeight(40)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #5E4FD4;
            }}
        """)
        return button

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.uploaded_path = file_path
            pixmap = QPixmap(file_path).scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(pixmap)

    def save_photo(self):
        name = self.name_input.text().strip()
        uid = self.university_id_input.text().strip()
        program = self.program_input.text().strip()
        branch = self.branch_input.text().strip()
        mobile = self.mobile_input.text().strip()
        gmail = self.gmail_input.text().strip()

        if not all([name, uid, program, branch, mobile, gmail]):
            QMessageBox.warning(self, "Missing Info", "Please fill all student details.")
            return
        if not self.uploaded_path:
            QMessageBox.warning(self, "No Photo", "Please choose a photo to upload.")
            return

        os.makedirs(self.target_dir, exist_ok=True)
        ext = os.path.splitext(self.uploaded_path)[1]
        new_image_path = os.path.join(self.target_dir, f"{uid}{ext}")
        shutil.copyfile(self.uploaded_path, new_image_path)

        new_entry = [name, uid, program, branch, mobile, gmail, new_image_path]
        write_header = not os.path.exists(self.csv_path)
        with open(self.csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["Name", "University ID", "Program", "Branch", "Mobile", "Gmail", "Image Path"])
            writer.writerow(new_entry)

        QMessageBox.information(self, "Success", f"Details saved and photo stored at:\n{new_image_path}")
        self.go_home()

    def go_home(self):
        self.close()
        subprocess.Popen([sys.executable, "adminPanel.py"])  # Launch home screen


if __name__ == "__main__":
    image_dir = (os.path.join(BASE_DIR, "images"))
    csv_file = os.path.join(BASE_DIR, "students.csv")

    app = QApplication(sys.argv)
    window = UploadWindow(image_dir=image_dir, csv_file=csv_file)
    window.show()
    sys.exit(app.exec_())
