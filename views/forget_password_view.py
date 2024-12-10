from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
import requests
from appconfig import USER_BASE_API_URL, USER_SERVICE_SUBSCRIPTION_KEY

class ForgotPasswordView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # Title label
        self.title_label = QLabel("Forgot Password")
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

    def request_password_reset(self):
        """Send username and email to the password reset API."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()

        if not username or not email:
            self.feedback_label.setText("Username and email cannot be empty.")
            return

        # Ensure payload is properly constructed
        payload = {
            "username": username,
            "email": email
        }

        print(payload)  # Debugging step

        # API endpoint
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/request-password-reset"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": USER_SERVICE_SUBSCRIPTION_KEY
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                self.parent.show_message_view("Password reset request successful. Please check your email.")
            else:
                self.feedback_label.setText(f"Failed to request password reset. Error: {response.text}")
        except Exception as e:
            self.feedback_label.setText(f"An error occurred: {e}")
