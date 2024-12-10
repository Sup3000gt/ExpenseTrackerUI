from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from services.auth_service import login_user
from PySide6.QtCore import Qt

class MainPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # Title with word wrapping
        self.title_label = QLabel("Welcome to Expense Tracker")
        self.title_label.setAlignment(Qt.AlignCenter)  # Center-align horizontally
        self.title_label.setWordWrap(True)  # Enable word wrapping
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        self.layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: #5cb85c; color: white; border-radius: 8px;")
        self.login_button.clicked.connect(self.login_user)
        self.layout.addWidget(self.login_button)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: #0275d8; color: white; border-radius: 8px;")
        self.register_button.clicked.connect(self.parent.show_register_view)
        self.layout.addWidget(self.register_button)

        # Forgot Password button
        self.forgot_password_button = QPushButton("Forgot Password")
        self.forgot_password_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: #f0ad4e; color: white; border-radius: 8px;")
        self.layout.addWidget(self.forgot_password_button)

        # Feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("color: red; font-size: 14px;")
        self.layout.addWidget(self.feedback_label)

    def login_user(self):
        """Handle user login."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.feedback_label.setText("Username and password cannot be empty.")
            return

        # Call the login API
        success, message, token = login_user(username, password)
        if success:
            self.parent.jwt_token = token
            self.feedback_label.setStyleSheet("color: green; font-size: 14px;")
            self.feedback_label.setText("Login Successful!")
        else:
            self.feedback_label.setStyleSheet("color: red; font-size: 14px;")
            self.feedback_label.setText(message)
