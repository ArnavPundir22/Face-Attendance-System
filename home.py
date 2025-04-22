import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from main import AttendanceSystem

# os.environ["QT_QPA_PLATFORM"] = "wayland"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Welcome")

        # Optional gradient background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 1, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor("#f0f4ff"))
        gradient.setColorAt(1.0, QColor("#e0e4fa"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        self.init_ui()
        self.start_animation()
        QTimer.singleShot(3000, self.goto_home)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("👋 Welcome to the Attendance System")
        self.title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.title.setStyleSheet("color: #7A5FFF;")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("Smart. Secure. Seamless.")
        self.subtitle.setFont(QFont("Segoe UI", 20))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet("color: #555;")

        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addWidget(self.subtitle)
        self.setLayout(layout)

    def start_animation(self):
        for widget in [self.title, self.subtitle]:
            animation = QPropertyAnimation(widget, b"windowOpacity")
            animation.setDuration(1200)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.start()
            widget._fade = animation  # Prevent garbage collection

    def goto_home(self):
        self.home = HomePage()
        self.home.show()
        self.close()


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendance System - Home")
        self.showFullScreen()
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 50, 60, 50)
        main_layout.setSpacing(40)

        header = QLabel("📘 ATTENDANCE SYSTEM")
        header.setFont(QFont("Segoe UI", 40, QFont.Bold))
        header.setStyleSheet("color: #7A5FFF;")
        header.setAlignment(Qt.AlignCenter)

        sub_label = QLabel("What would you like to do?")
        sub_label.setFont(QFont("Segoe UI", 20))
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setStyleSheet("color: #555;")

        main_layout.addWidget(header)
        main_layout.addWidget(sub_label)

        main_layout.addSpacerItem(QSpacerItem(20, 30))

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(60)
        button_layout.setAlignment(Qt.AlignCenter)

        self.attendance_btn = self.create_button("📷  Mark Attendance", self.open_attendance_system)
        self.admin_btn = self.create_button("🔐  Admin Panel", self.open_admin_panel)

        button_layout.addWidget(self.attendance_btn)
        button_layout.addWidget(self.admin_btn)

        main_layout.addLayout(button_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 30))

        # Exit Button
        exit_layout = QHBoxLayout()
        exit_layout.setAlignment(Qt.AlignCenter)
        exit_btn = self.create_button("❌  Exit", self.close_app, small=True)
        exit_btn.setFixedWidth(180)
        exit_layout.addWidget(exit_btn)

        main_layout.addLayout(exit_layout)
        self.setLayout(main_layout)

    def create_button(self, text, callback, small=False):
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setFont(QFont("Segoe UI", 16 if not small else 13, QFont.Bold))
        button.setMinimumHeight(80 if not small else 50)
        button.setStyleSheet("""

            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7A5FFF, stop:1 #5E4FD4
                );
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #634DDB;
            }
            QPushButton:pressed {
                background-color: #4E3FB3;
            }
        """)
        button.clicked.connect(callback)
        return button

    def open_attendance_system(self):
        self.attendance_window = AttendanceSystem()
        self.attendance_window.show()
        self.hide()


    def open_admin_panel(self):
        try:
            # Import inside the method to avoid circular imports
            from adminPanel import AdminPanel
            self.admin_panel_window = AdminPanel()
            self.admin_panel_window.show()
            self.hide()
        except Exception as e:
            print(f"[Error] Failed to open Admin Panel: {e}")

    def close_app(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomePage()
    welcome.show()
    sys.exit(app.exec_())
