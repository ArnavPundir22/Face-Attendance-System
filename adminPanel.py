import sys
import os
import csv
import datetime
import hashlib
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QTableWidget, QAbstractItemView, QTableWidgetItem, QMessageBox, QHeaderView,
    QStackedLayout, QFrame, QGroupBox, QLineEdit, QFormLayout,  QMainWindow, QPushButton, QVBoxLayout,
    QHBoxLayout, QScrollArea,  QSizePolicy, QDialog
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from fpdf import FPDF
import shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox
# os.environ["QT_QPA_PLATFORM"] = "wayland"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STUDENTS_CSV = os.path.join(BASE_DIR, "students.csv")
ATTENDANCE_CSV = os.path.join(BASE_DIR, "attendance_log.csv")
ADMINS_CSV = os.path.join(BASE_DIR, "admins.csv")

class RegisterAdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Admin")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("🆕 Register New Admin")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(20)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Name")
        self.name_input.setFixedHeight(36)

        self.gmail_input = QLineEdit()
        self.gmail_input.setPlaceholderText("Enter Gmail ID")
        self.gmail_input.setFixedHeight(36)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(36)

        layout.addWidget(self.name_input)
        layout.addWidget(self.gmail_input)
        layout.addWidget(self.password_input)

        register_btn = QPushButton("Register")
        register_btn.setFixedHeight(36)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #7a5fff;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #634dff;
            }
        """)
        register_btn.clicked.connect(self.register_admin)

        layout.addSpacing(15)
        layout.addWidget(register_btn)

        self.setLayout(layout)
# ================================================================
# Project: Face Recognition Based Attendance System
# Author: Arnav Pundir
# Year: 2025
# License: Custom Proprietary License - All Rights Reserved
# Unauthorized use, copying, or distribution is strictly prohibited.
# ================================================================
    def register_admin(self):
        name = self.name_input.text().strip()
        gmail = self.gmail_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not gmail or not password:
            QMessageBox.warning(self, "Missing Fields", "All fields are required.")
            return

        if not gmail.endswith("@gmail.com"):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid Gmail ID.")
            return

        headers = ["Name", "Gmail", "Password"]
        file_exists = os.path.exists(ADMINS_CSV)

        # Write to CSV
        with open(ADMINS_CSV, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow({"Name": name, "Gmail": gmail, "Password": password})

        self.accept()

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel - Face Recognition Attendance System")
        self.showFullScreen()
        self.setStyleSheet("background-color: #f6f9fc;")

        self.stacked_layout = QStackedLayout()
        self.setLayout(self.stacked_layout)
        self.login_name = ''
        self.init_login_ui()
        self.init_admin_ui()  # Load both but show only login first

    def init_login_ui(self):
        login_widget = QWidget()
        login_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                background-repeat: no-repeat;
                background-position: center;
            }
        """)
        layout = QVBoxLayout(login_widget)
        layout.setAlignment(Qt.AlignCenter)
        # Back Button
        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(100)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7a5fff;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: #4a39cc;
                text-decoration: underline;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_home)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        # Login Card Frame
        card = QFrame()
        card.setFixedSize(420, 350)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ddd;
                padding: 30px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignTop)

        # Title
        title = QLabel("🔐 Admin Login")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 6px;
                line-height: 1.4em;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        card_layout.addSpacing(10)

        # Name Field (was Email)
        self.login_name = QLineEdit()
        self.login_name.setPlaceholderText("Name")
        self.login_name.setFixedHeight(40)
        self.login_name.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1.5px solid #7a5fff;
            }
        """)

        # Password Field
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setFixedHeight(40)
        self.login_password.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1.5px solid #7a5fff;
            }
        """)

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(40)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #7a5fff;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #634dff;
            }
            QPushButton:pressed {
                background-color: #4a39cc;
            }
        """)
        login_btn.clicked.connect(self.handle_login)

        card_layout.addWidget(self.login_name)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.login_password)
        card_layout.addSpacing(20)
        card_layout.addWidget(login_btn)

        # Register Button
        register_btn = QPushButton("Register New Admin")
        register_btn.setFixedHeight(36)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7a5fff;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                color: #4a39cc;
                text-decoration: underline;
            }
        """)
        register_btn.clicked.connect(self.open_register_dialog)
        card_layout.addSpacing(10)
        card_layout.addWidget(register_btn, alignment=Qt.AlignCenter)

        layout.addWidget(card)
        self.stacked_layout.addWidget(login_widget)


    def open_register_dialog(self):
        dialog = RegisterAdminDialog(self)
        dialog.exec_()

    def handle_login(self):
        name = self.login_name.text().strip()
        password = self.login_password.text().strip()

        if not os.path.exists(ADMINS_CSV):
            QMessageBox.warning(self, "Error", "Admin file not found!")
            return

        with open(ADMINS_CSV, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Name"] == name and row["Password"] == password:
                    self.log_login_logout(name, "Login")
                    self.stacked_layout.setCurrentIndex(1)  # Switch to admin panel
                    return


        QMessageBox.warning(self, "Login Failed", "Invalid credentials!")





    def init_admin_ui(self):
        admin_ui = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(30, 30, 20, 30)
        sidebar.setSpacing(25)

        # Sidebar Scrollable Container
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(30, 30, 20, 30)
        sidebar_layout.setSpacing(25)

        # Title
        title = QLabel("🛠️ Admin Panel")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #4a4a7a;")
        sidebar_layout.addWidget(title)

        # Student Group
        student_group = QGroupBox("📚 Student Options")
        student_layout = QVBoxLayout()
        student_layout.addWidget(self.create_button("📋 View Students", lambda: self.load_table(STUDENTS_CSV)))
        student_layout.addWidget(self.create_button("🧑‍💻 Upload New Student", self.open_upload))
        student_layout.addWidget(self.create_button("📈 View Attendance Logs", lambda: self.load_table(ATTENDANCE_CSV)))
        student_layout.addWidget(self.create_button("✏️ Edit / Remove / Search Students", self.edit_students))
        student_layout.addWidget(self.create_button("📤 Export Attendance Reports", self.export_attendance_reports))
        student_layout.addWidget(self.create_button("📝 Manually Edit Attendance", self.manual_edit_attendance))
        student_layout.addWidget(self.create_button("📁 Import Student Photos", self.choose_and_copy_folder))
        student_group.setLayout(student_layout)
        sidebar_layout.addWidget(student_group)

        # Admin Group
        admin_group = QGroupBox("🔐 Admin & Security Controls")
        admin_layout = QVBoxLayout()
        admin_layout.addWidget(self.create_button("🆕 Add New Admin", self.show_add_admin))
        admin_layout.addWidget(self.create_button("👀 View Admins", lambda: self.load_table(ADMINS_CSV)))
        admin_layout.addWidget(self.create_button("🗑️ Remove Admin", self.show_remove_admin))
        admin_layout.addWidget(self.create_button("🔑 Change Admin Password", self.change_admin_password))
        admin_layout.addWidget(self.create_button("🕓 Login History", self.view_login_logout_history))
        admin_group.setLayout(admin_layout)
        sidebar_layout.addWidget(admin_group)

        # System Group
        sys_group = QGroupBox("⚙️ System Utilities")
        sys_layout = QVBoxLayout()
        sys_layout.addWidget(self.create_button("🧠 Encode Photos", self.launch_encoder))
        sys_layout.addWidget(self.create_button("🧹 Clear All Data", self.clear_all_data))
        sys_layout.addWidget(self.create_button("🚪 Logout / Exit", self.logout))
        sys_group.setLayout(sys_layout)
        sidebar_layout.addWidget(sys_group)

        sidebar_layout.addStretch()

        # Wrap sidebar in QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidget(sidebar_container)

        # Main Layout
        self.content_area = QStackedLayout()
        placeholder = QLabel("Select an option from the left menu.")
        placeholder.setFont(QFont("Segoe UI", 16))
        placeholder.setAlignment(Qt.AlignCenter)
        self.content_area.addWidget(placeholder)

        content_frame = QFrame()
        content_frame.setLayout(self.content_area)

        main_layout = QHBoxLayout()
        main_layout.addWidget(scroll, 1)  # Sidebar with scrollbar
        main_layout.addWidget(content_frame, 4)

        admin_ui = QWidget()
        admin_ui.setLayout(main_layout)
        self.stacked_layout.addWidget(admin_ui)

    def logout(self):
        self.login_name.clear()
        self.login_password.clear()
        self.stacked_layout.setCurrentIndex(0)

    def go_back_to_home(self):
        try:
            from home import HomePage  # Import here to avoid circular imports
            self.home_window = HomePage()
            self.home_window.show()
            self.close()
        except Exception as e:
            print(f"[Error] Failed to return to home: {e}")

    # All your existing helper methods (unchanged)
    def create_button(self, text, action):
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setFont(QFont("Segoe UI", 11))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #7a5fff;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #634dff;
            }
            QPushButton:pressed {
                background-color: #4a39cc;
            }
        """)
        btn.clicked.connect(action)
        return btn

    def load_table(self, csv_path):
        table_widget = QTableWidget()
        table_widget.setAlternatingRowColors(True)
        table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #e5e5f7;
                font-weight: bold;
                border: 1px solid #ddd;
                padding: 6px;
            }
        """)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        if not os.path.exists(csv_path):
            QMessageBox.warning(self, "File Not Found", f"No file found at:\n{csv_path}")
            return

        with open(csv_path, newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        if rows:
            headers = rows[0]
            table_widget.setRowCount(len(rows) - 1)
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            for i, row in enumerate(rows[1:]):
                for j, value in enumerate(row):
                    table_widget.setItem(i, j, QTableWidgetItem(value))
        else:
            table_widget.setRowCount(0)

        self.content_area.addWidget(table_widget)
        self.content_area.setCurrentWidget(table_widget)

    def open_upload(self):
        subprocess.Popen([sys.executable, "photoUpload.py"])
        self.close()

    def launch_attendance(self):
        subprocess.Popen([sys.executable, "main.py"])
        self.close()


    def show_add_admin(self):
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        title = QLabel("➕ Add New Admin")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4a4a7a;")
        title.setAlignment(Qt.AlignCenter)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Full Name")
        email_input = QLineEdit()
        email_input.setPlaceholderText("Email Address")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Password")
        password_input.setEchoMode(QLineEdit.Password)

        for widget in [name_input, email_input, password_input]:
            widget.setFixedHeight(40)
            widget.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding-left: 10px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1.5px solid #7a5fff;
                }
            """)

        add_btn = QPushButton("Add Admin")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #7a5fff;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #634dff;
            }
            QPushButton:pressed {
                background-color: #4a39cc;
            }
        """)
        add_btn.clicked.connect(lambda: self.save_admin(
            name_input.text(), email_input.text(), password_input.text()))

        form_layout.addWidget(title)
        form_layout.addSpacing(10)
        form_layout.addWidget(name_input)
        form_layout.addWidget(email_input)
        form_layout.addWidget(password_input)
        form_layout.addWidget(add_btn)
        form_layout.addStretch()

        form_widget.setLayout(form_layout)
        self.set_content_widget(form_widget)

    def show_remove_admin(self):
        if not os.path.exists(ADMINS_CSV):
            QMessageBox.warning(self, "Error", "Admins file not found.")
            return

        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                font-weight: bold;
                border: 1px solid #ddd;
                padding: 6px;
            }
        """)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Name", "Email", "Password", "Action"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        with open(ADMINS_CSV, newline='') as file:
            reader = list(csv.reader(file))
            if len(reader) <= 1:
                table.setRowCount(0)
            else:
                valid_rows = [row for row in reader[1:] if len(row) >= 3]
                table.setRowCount(len(valid_rows))
                for i, row in enumerate(valid_rows):
                    for j in range(3):
                        table.setItem(i, j, QTableWidgetItem(row[j]))
                    delete_btn = QPushButton("Delete")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #ff4d4d;
                            color: white;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #e60000;
                        }
                    """)
                    delete_btn.clicked.connect(lambda _, index=i: self.delete_admin(index))

                    table.setCellWidget(i, 3, delete_btn)

        self.set_content_widget(table)

    def delete_admin(self, index):
        # Example logic: remove admin from CSV and refresh the table
        try:
            import pandas as pd

            csv_path = os.path.join(BASE_DIR, "admins.csv")  # Or the actual path you use
            df = pd.read_csv(csv_path)

            if index < 0 or index >= len(df):
                print("Invalid index")
                return

            # Optional: confirmation dialog
            from PyQt5.QtWidgets import QMessageBox
            confirm = QMessageBox.question(self, "Confirm Delete",
                                           f"Are you sure you want to delete admin '{df.iloc[index]['Name']}'?",
                                           QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                df.drop(index=index, inplace=True)
                df.to_csv(csv_path, index=False)

                QMessageBox.information(self, "Deleted", "Admin removed successfully.")
                self.load_admins()  # Refresh the table after deletion

        except Exception as e:
            print(f"Error deleting admin: {e}")

    def save_admin(self, name, email, password):
        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if not os.path.exists(ADMINS_CSV):
            with open(ADMINS_CSV, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Email", "Password"])

        with open(ADMINS_CSV, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, email, password])

        QMessageBox.information(self, "Success", f"Admin '{name}' added successfully.")

    def launch_encoder(self):
        subprocess.Popen([sys.executable, "EncodeGenerator.py"])
        self.close()

    def set_content_widget(self, widget):
        self.content_area.addWidget(widget)
        self.content_area.setCurrentWidget(widget)

    def change_admin_password(self):
        change_widget = QWidget()
        layout = QVBoxLayout(change_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # 🔙 Back Button
        back_btn = QPushButton("🔙 Back")
        back_btn.setFixedSize(80, 32)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(1))  # Assuming index 1 is admin panel
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        # Title
        title = QLabel("🔐 Change Admin Password")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4a4a7a;")
        layout.addWidget(title)

        # Input Fields
        old_password_input = QLineEdit()
        old_password_input.setEchoMode(QLineEdit.Password)
        old_password_input.setPlaceholderText("Enter Old Password")

        new_password_input = QLineEdit()
        new_password_input.setEchoMode(QLineEdit.Password)
        new_password_input.setPlaceholderText("Enter New Password")

        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input.setPlaceholderText("Confirm New Password")

        for field in [old_password_input, new_password_input, confirm_password_input]:
            field.setFixedHeight(40)
            field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding-left: 10px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1.5px solid #7a5fff;
                }
            """)
            layout.addWidget(field)

        # Submit Button
        change_btn = QPushButton("🔁 Change Password")
        change_btn.setFixedHeight(42)
        change_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout.addWidget(change_btn)

        def handle_change():
            old_pass = old_password_input.text().strip()
            new_pass = new_password_input.text().strip()
            confirm_pass = confirm_password_input.text().strip()
            admin_name = self.login_name.text().strip()

            if not old_pass or not new_pass or not confirm_pass:
                QMessageBox.warning(change_widget, "Input Error", "Please fill all fields.")
                return

            if new_pass != confirm_pass:
                QMessageBox.warning(change_widget, "Mismatch", "New password and confirmation do not match.")
                return

            rows = []
            found = False
            updated = False

            if os.path.exists(ADMINS_CSV):
                with open(ADMINS_CSV, newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row["Name"] == admin_name and row["Password"] == old_pass:
                            row["Password"] = new_pass
                            found = True
                            updated = True
                        rows.append(row)

                if found and updated:
                    with open(ADMINS_CSV, 'w', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=["Name", "Email", "Password"])
                        writer.writeheader()
                        writer.writerows(rows)
                    QMessageBox.information(change_widget, "Success", "Password updated successfully.")
                    old_password_input.clear()
                    new_password_input.clear()
                    confirm_password_input.clear()
                elif not found:
                    QMessageBox.critical(change_widget, "Authentication Failed", "Old password is incorrect.")
            else:
                QMessageBox.critical(change_widget, "Error", f"Admin database not found: {ADMINS_CSV}")

        change_btn.clicked.connect(handle_change)

        # Show the widget in your stacked layout or replace current view
        self.stacked_layout.addWidget(change_widget)
        self.stacked_layout.setCurrentWidget(change_widget)

    def edit_students(self):
        edit_widget = QWidget()
        layout = QVBoxLayout(edit_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("✏️ Edit / Remove / Search Students")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4a4a7a;")
        layout.addWidget(title)

        # Search field
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search by name, ID, program, or branch...")
        search_input.setFixedHeight(40)
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1.5px solid #7a5fff;
            }
        """)
        layout.addWidget(search_input)

        # Table
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #e5e5f7;
                font-weight: bold;
                border: 1px solid #ddd;
                padding: 6px;
            }
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(table)

        # Load student data
        def load_data():
            if not os.path.exists(STUDENTS_CSV):
                QMessageBox.warning(self, "Error", "Students file not found!")
                return

            with open(STUDENTS_CSV, newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)

            if not rows:
                return

            headers = rows[0]
            table.setRowCount(len(rows) - 1)
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)

            for i, row in enumerate(rows[1:]):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(value)
                    table.setItem(i, j, item)
        load_data()

        # Search functionality
        def search():
            term = search_input.text().lower()
            for i in range(table.rowCount()):
                match = False
                for j in range(table.columnCount()):
                    item = table.item(i, j)
                    if item and term in item.text().lower():
                        match = True
                        break
                table.setRowHidden(i, not match)

        search_input.textChanged.connect(search)

        # Save button
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(save_btn)

        def save_changes():
            headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            rows = [headers]
            for i in range(table.rowCount()):
                row_data = []
                for j in range(table.columnCount()):
                    item = table.item(i, j)
                    row_data.append(item.text() if item else "")
                rows.append(row_data)

            with open(STUDENTS_CSV, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            QMessageBox.information(self, "Success", "Changes saved successfully.")

        save_btn.clicked.connect(save_changes)

        # Delete button
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setFixedHeight(40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        layout.addWidget(delete_btn)

        def delete_selected():
            selected = table.selectedItems()
            if not selected:
                QMessageBox.warning(self, "No Selection", "Please select a student to delete.")
                return
            row = selected[0].row()
            table.removeRow(row)

        delete_btn.clicked.connect(delete_selected)

        layout.addStretch()
        self.content_area.addWidget(edit_widget)
        self.content_area.setCurrentWidget(edit_widget)

    def export_attendance_reports(self):
        attendance_file = os.path.join(BASE_DIR, "attendance_log.csv") # Path to your attendance log
        if not os.path.exists(attendance_file):
            QMessageBox.warning(self, "No Data", "Attendance log file not found!")
            return

        # Choose export format
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Attendance Report", "",
            "Excel Files (*.xlsx);;PDF Files (*.pdf);;CSV Files (*.csv)",
            options=options
        )

        if not save_path:
            return  # Cancelled

        try:
            df = pd.read_csv(attendance_file)

            if save_path.endswith(".xlsx"):
                df.to_excel(save_path, index=False)
                QMessageBox.information(self, "Success", "Attendance report exported as Excel.")
            elif save_path.endswith(".pdf"):
                self._export_pdf(df, save_path)
                QMessageBox.information(self, "Success", "Attendance report exported as PDF.")
            elif save_path.endswith(".csv"):
                df.to_csv(save_path, index=False)
                QMessageBox.information(self, "Success", "Attendance report exported as CSV.")
            else:
                QMessageBox.warning(self, "Unsupported Format", "Please choose a valid format.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export report:\n{str(e)}")

    from datetime import datetime
    from fpdf import FPDF

    def _export_pdf(self, df, path):
        pdf = FPDF(orientation='L', unit='mm', format='A4')  # Landscape for more space
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title & timestamp
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Attendance Report", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.ln(10)

        # Column calculations
        headers = df.columns.tolist()
        page_width = pdf.w - 2 * pdf.l_margin
        col_width = page_width / len(headers)

        # Table Header
        pdf.set_fill_color(50, 130, 184)
        pdf.set_text_color(255)
        pdf.set_font("Arial", 'B', 10)
        for header in headers:
            pdf.cell(col_width, 10, str(header), border=1, align='C', fill=True)
        pdf.ln()

        # Table Rows
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(0)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
            for item in row:
                pdf.cell(col_width, 10, str(item), border=1, align='C', fill=fill)
            pdf.ln()
            fill = not fill

        pdf.output(path)

    def manual_edit_attendance(self):
        edit_widget = QWidget()
        layout = QVBoxLayout(edit_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Back button
        back_btn = QPushButton("🔙 Back")
        back_btn.setFixedSize(80, 32)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        # Title
        title = QLabel("📝 Manually Edit Attendance")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4a4a7a;")
        layout.addWidget(title)

        # Attendance Table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels(["Date", "Time", "Student ID", "Name", "Program"])
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.attendance_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attendance_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.attendance_table)

        self.attendance_file = os.path.join(BASE_DIR, "attendance_log.csv")
        self.load_attendance_table()

        # Editable fields
        edit_layout = QHBoxLayout()
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Edit Date (YYYY-MM-DD)")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Edit Time (HH:MM:SS)")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Edit Name")

        for field in [self.date_input, self.time_input, self.name_input]:
            field.setFixedHeight(35)
            field.setStyleSheet("QLineEdit { padding: 6px; border-radius: 8px; border: 1px solid #ccc; }")
            edit_layout.addWidget(field)

        layout.addLayout(edit_layout)

        # Save button
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_attendance_edit)
        layout.addWidget(save_btn)

        self.attendance_table.cellClicked.connect(self.load_selected_attendance_row)

        self.stacked_layout.addWidget(edit_widget)
        self.stacked_layout.setCurrentWidget(edit_widget)

    def load_attendance_table(self):
        if os.path.exists(self.attendance_file):
            with open(self.attendance_file, newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                if len(rows) > 0:
                    headers = rows[0]
                    data = rows[1:]
                    self.attendance_table.setRowCount(len(data))
                    self.attendance_table.setColumnCount(len(headers))
                    self.attendance_table.setHorizontalHeaderLabels(headers)
                    for row_idx, row in enumerate(data):
                        for col_idx, value in enumerate(row):
                            self.attendance_table.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def choose_and_copy_folder(self):
            # Get the selected folder
            folder = QFileDialog.getExistingDirectory(self, "Select Folder with Images")
            if folder:
                self.copy_photos_to_images_folder(folder)
                QMessageBox.information(self, "Success", "Images copied to the app's image folder.")

    def copy_photos_to_images_folder(self, source_folder, dest_folder=os.path.join(BASE_DIR, "images")):
            if not isinstance(source_folder, (str, bytes, os.PathLike)):
                print(f"[Error] Invalid source_folder: {source_folder}")
                return

            if not os.path.exists(source_folder):
                print(f"[Error] Source folder does not exist: {source_folder}")
                return

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            supported_exts = (".jpg", ".jpeg", ".png")
            count = 0

            for filename in os.listdir(source_folder):
                if filename.lower().endswith(supported_exts):
                    src_path = os.path.join(source_folder, filename)
                    dst_path = os.path.join(dest_folder, filename)

                    try:
                        with open(src_path, 'rb') as src_file:
                            data = src_file.read()
                        with open(dst_path, 'wb') as dst_file:
                            dst_file.write(data)
                        count += 1
                    except Exception as e:
                        print(f"[Error] Failed to copy {filename}: {e}")

            print(f"✅ Copied {count} image(s) to {dest_folder}")

    def load_selected_attendance_row(self, row, _):
        self.selected_row_index = row
        self.date_input.setText(self.attendance_table.item(row, 5).text())
        self.time_input.setText(self.attendance_table.item(row, 6).text())
        self.name_input.setText(self.attendance_table.item(row, 0).text())  # Assuming name is at column index 3

    def save_attendance_edit(self):
        if self.selected_row_index is None:
            QMessageBox.warning(self, "No Selection", "Please select a row to edit.")
            return

        new_date = self.date_input.text().strip()
        new_time = self.time_input.text().strip()
        new_name = self.name_input.text().strip()

        if not (new_date and new_time and new_name):
            QMessageBox.warning(self, "Invalid Input", "All fields must be filled.")
            return

        with open(self.attendance_file, newline='') as file:
            reader = list(csv.reader(file))

        # Edit the specific row (index + 1 to skip header)
        reader[self.selected_row_index + 1][0] = new_date
        reader[self.selected_row_index + 1][1] = new_time
        reader[self.selected_row_index + 1][3] = new_name  # Assuming name is 4th column

        with open(self.attendance_file, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(reader)

        QMessageBox.information(self, "Success", "Attendance record updated successfully.")
        self.load_attendance_table()

    def log_login_logout(self, admin_name, status):  # status = "Login" or "Logout"
        with open(os.path.join(BASE_DIR, "login_logout_history.csv"), "a", newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, admin_name, status])

    def view_login_logout_history(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 🔙 Back Button
        back_btn = QPushButton("🔙 Back")
        back_btn.setFixedSize(80, 32)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(1))
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        # Title
        title = QLabel("🕓 Login/Logout History")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4a4a7a;")
        layout.addWidget(title)

        # Table
        history_table = QTableWidget()
        history_table.setColumnCount(3)
        history_table.setHorizontalHeaderLabels(["Timestamp", "Admin Name", "Status"])
        history_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: #f0f0f0; font-weight: bold; }")
        history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 10px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        history_table.horizontalHeader().setStretchLastSection(True)
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        history_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Load from CSV
        file_path = os.path.join(BASE_DIR, "login_logout_history.csv")
        if os.path.exists(file_path):
            with open(file_path, newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                history_table.setRowCount(len(rows))
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        history_table.setItem(row_idx, col_idx, QTableWidgetItem(value))
        else:
            history_table.setRowCount(1)
            history_table.setItem(0, 0, QTableWidgetItem("No history available"))
            history_table.setSpan(0, 0, 1, 3)

        layout.addWidget(history_table)

        self.stacked_layout.addWidget(main_widget)
        self.stacked_layout.setCurrentWidget(main_widget)

    def clear_all_data(self):
        confirm = QMessageBox.question(self, "Clear All Data",
                                       "⚠️ This will erase all data including student info, attendance logs, and admin credentials. Proceed?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
                open(STUDENTS_CSV, 'w').close()
                open(ATTENDANCE_CSV, 'w').close()
                open(ADMINS_CSV, 'w').close()
                QMessageBox.information(self, "Success", "All data cleared.")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())
