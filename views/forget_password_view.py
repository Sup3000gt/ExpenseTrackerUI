from PySide6.QtCore import Qt
import requests
from appconfig import USER_BASE_API_URL, USER_SERVICE_SUBSCRIPTION_KEY
from PySide6.QtCore import QThread, Signal
import os
from PySide6.QtGui import QMovie, QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QScrollArea

class PasswordResetThread(QThread):
    """Thread for handling the password reset API call."""
    reset_result = Signal(bool, str)

    def __init__(self, username, email):
        super().__init__()
        self.username = username
        self.email = email

    def run(self):
        """Send username and email to the password reset API."""
        api_url = f"{USER_BASE_API_URL}/Users/request-password-reset"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": USER_SERVICE_SUBSCRIPTION_KEY
        }
        payload = {
            "username": self.username,
            "email": self.email
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                self.reset_result.emit(True, "Password reset request successful. Please check your email.")
            else:
                self.reset_result.emit(False, f"Error: {response.text}")
        except requests.exceptions.RequestException as e:
            self.reset_result.emit(False, f"Error: {e}")

class ForgotPasswordView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(40, 40, 40, 40)

        self.add_back_button()  # Add back button

        # Title label
        self.title_label = QLabel("Reset Your Password")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #555; text-align: center;")
        self.layout.addWidget(self.title_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        self.layout.addWidget(self.username_input)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        self.email_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        self.layout.addWidget(self.email_input)

        # Submit button
        self.submit_button = QPushButton("Request Password Reset")
        self.submit_button.setStyleSheet("padding: 10px; font-size: 18px; background-color: #0275d8; color: white; border-radius: 8px;")
        self.submit_button.clicked.connect(self.request_password_reset)
        self.layout.addWidget(self.submit_button)

        # Feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red; text-align: center;")
        self.layout.addWidget(self.feedback_label)

    def add_back_button(self):
        """Add a modern back button with an arrow to return to the main page."""
        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/left-arrow.png"))
        back_button.setIconSize(QSize(30, 30))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* Transparent background */
                border: none;  /* No border for flat design */
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);  /* Light hover effect */
                border-radius: 12px;  /* Rounded corners for hover */
            }
        """)
        back_button.clicked.connect(self.parent.show_main_page)

        # Add to a horizontal layout to align it to the left
        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(back_button)
        back_button_layout.setAlignment(Qt.AlignLeft)  # Align to the left
        self.layout.addLayout(back_button_layout)

    def request_password_reset(self):
        """Handle password reset with a loading spinner."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()

        if not username or not email:
            self.feedback_label.setText("Username and email cannot be empty.")
            return

        # Show spinner on the button
        self.show_loading_animation_on_button()

        # Start the password reset thread
        self.reset_thread = PasswordResetThread(username, email)
        self.reset_thread.reset_result.connect(self.on_reset_result)  # Connect the result signal
        self.reset_thread.start()

    def on_reset_result(self, success, message):
        """Handle the result of the password reset API call."""
        self.hide_loading_animation_on_button()

        if success:
            self.parent.show_message_view(message)
        else:
            self.feedback_label.setText(message)

    def show_loading_animation_on_button(self):
        """Show a spinning icon on the Request Password Reset button."""
        self.submit_button.setText("")
        self.spinner_label = QLabel(self.submit_button)
        self.spinner_label.setFixedSize(20, 20)  # Set spinner size
        self.spinner_label.setAlignment(Qt.AlignCenter)

        # Position the spinner inside the button
        self.spinner_label.move(
            (self.submit_button.width() // 2) - 10,  # Center horizontally
            (self.submit_button.height() // 2) - 10  # Center vertically
        )

        # Load and start the spinner animation
        spinner_path = os.path.join(os.getcwd(), "assets", "spinner.gif")
        self.spinner_movie = QMovie(spinner_path)
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_movie.start()
        self.spinner_label.show()

        # Disable the button to prevent multiple clicks
        self.submit_button.setDisabled(True)

    def hide_loading_animation_on_button(self):
        """Remove the spinning icon from the Request Password Reset button."""
        if hasattr(self, "spinner_label") and self.spinner_label:
            self.spinner_movie.stop()
            self.spinner_label.deleteLater()
            self.spinner_label = None

        self.submit_button.setText("Request Password Reset")
        self.submit_button.setDisabled(False)