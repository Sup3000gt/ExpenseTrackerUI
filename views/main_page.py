from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QFormLayout
)
from services.auth_service import login_user
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMovie, QPixmap
import os
import jwt
import logging


logger = logging.getLogger(__name__)


class LoginThread(QThread):
    login_result = Signal(bool, dict, str)  # Signal to send (success, message, token)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        """Run the API call in a separate thread."""
        logger.debug("LoginThread: Starting API call...")
        success, response_data, token = login_user(self.username, self.password)
        logger.debug(
            f"LoginThread: API call result - success: {success}, response_data: {response_data}, token: {token}"
        )
        # Ensure response_data is parsed as a dictionary
        if isinstance(response_data, str):
            try:
                import json

                response_data = json.loads(response_data)
            except json.JSONDecodeError:
                response_data = {"message": response_data}  # Fallback for non-JSON responses

        self.login_result.emit(success, response_data, token)


class MainPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        logger.debug(f"MainPage initialized with parent: {self.parent}")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # Title with word wrapping
        self.title_label = QLabel("Personal Expense Tracker")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #555; text-align: center;"
        )
        self.layout.addWidget(self.title_label)

        # Form layout for aligned inputs
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setSpacing(15)

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFixedSize(260, 40)  # Fixed size for the username input box
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        username_label = QLabel("Username:")
        username_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #555; text-align: center;"
        )
        form_layout.addRow(username_label, self.username_input)

        # Connect the returnPressed signal to move focus to password_input
        self.username_input.returnPressed.connect(self.focus_password_input)

        # Password field with checkbox
        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(260, 40)  # Fixed size for the password input box
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        password_input_layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox()
        self.show_password_checkbox.setToolTip("Show Password")  # Tooltip for the checkbox
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.show_password_checkbox)

        password_label = QLabel("Password:")
        password_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #555; text-align: center;"
        )
        form_layout.addRow(password_label, password_input_layout)

        # Connect the returnPressed signal to trigger login
        self.password_input.returnPressed.connect(self.login_user)

        # Add the form layout to the main layout
        self.layout.addLayout(form_layout)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet(
            "padding: 10px; font-size: 18px; background-color: #5cb85c; color: white; border-radius: 8px;"
        )
        self.login_button.setFixedWidth(400)
        self.login_button.clicked.connect(self.login_user)
        self.layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet(
            "padding: 10px; font-size: 18px; background-color: #0275d8; color: white; border-radius: 8px;"
        )
        self.register_button.setFixedWidth(400)
        self.register_button.clicked.connect(self.parent.show_register_view)
        self.layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        # Forgot Password button
        self.forgot_password_button = QPushButton("Forgot Password")
        self.forgot_password_button.setStyleSheet(
            "padding: 10px; font-size: 18px; background-color: #f0ad4e; color: white; border-radius: 8px;"
        )
        self.forgot_password_button.setFixedWidth(400)
        self.forgot_password_button.clicked.connect(self.parent.show_forgot_password_view)
        self.layout.addWidget(self.forgot_password_button, alignment=Qt.AlignCenter)

        # Feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: red; text-align: center;"
        )
        self.layout.addWidget(self.feedback_label)

        # Add Microsoft Icon
        self.icon_label = QLabel(self)
        pixmap = QPixmap("assets/microsoft3.png")
        self.icon_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))  # Scale to fit
        self.layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        # Add Text Below the Icon
        self.text_label = QLabel("Microsoft Software and Systems Academy", self)
        self.text_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #555; text-align: center;"
        )
        self.layout.addWidget(self.text_label, alignment=Qt.AlignCenter)

    def focus_password_input(self):
        """Set focus to the password input field."""
        self.password_input.setFocus()

    def toggle_password_visibility(self, checked):
        """Toggle the visibility of the password."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def login_user(self):
        """Handle user login with a loading spinner on the button."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.feedback_label.setText("Username or password cannot be empty.")
            return

        # Show spinner on the Login button
        self.show_loading_animation_on_button()

        # Start the login thread
        self.login_thread = LoginThread(username, password)
        self.login_thread.login_result.connect(self.on_login_result)  # Connect the result signal
        self.login_thread.start()

    def on_login_result(self, success, response_data, token):
        """Handle the result of the login API call."""
        logger.debug(
            f"on_login_result called - success: {success}, response_data: {response_data}, token: {token[:10]}..."
        )
        self.hide_loading_animation_on_button()

        if success:
            user_id, username = self.get_user_details_from_token(token)
            if user_id and username:
                self.parent.on_login_result(user_id, username, token)
            else:
                self.feedback_label.setText("Failed to decode user details from token.")
        else:
            error_message = response_data.get("message", "Invalid Username or password")
            self.feedback_label.setText(error_message)

    def get_user_details_from_token(self, token):
        """Decode JWT token to extract user details."""
        try:
            # Decode the token to extract the payload
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.debug(f"Decoded JWT payload: {payload}")
            user_id = payload.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier")
            username = payload.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name")
            logger.debug(f"Extracted user_id: {user_id}, username: {username}")
            return user_id, username
        except jwt.PyJWTError as e:
            logger.error(f"Failed to decode JWT token: {e}")
            return None, None

    def show_loading_animation_on_button(self):
        """Show a spinning icon on the Login button."""
        self.login_button.setText("")
        # Create a QLabel to hold the spinner
        self.spinner_label = QLabel(self.login_button)
        self.spinner_label.setFixedSize(20, 20)  # Set the size of the spinner
        self.spinner_label.setAlignment(Qt.AlignCenter)

        # Position the spinner inside the button
        self.spinner_label.move(
            (self.login_button.width() // 2) - 10,  # Center horizontally
            (self.login_button.height() // 2) - 10  # Center vertically
        )

        # Load and start the spinner animation
        spinner_path = os.path.join(os.getcwd(), "assets", "spinner.gif")
        logger.debug(f"Spinner GIF Path: {spinner_path}")

        if not os.path.exists(spinner_path):
            logger.error("Spinner GIF not found. Please ensure the path is correct.")
        else:
            self.spinner_movie = QMovie(spinner_path)
            self.spinner_label.setMovie(self.spinner_movie)
            self.spinner_movie.start()
            self.spinner_label.show()

        # Disable the button to prevent multiple clicks
        self.login_button.setDisabled(True)

    def hide_loading_animation_on_button(self):
        """Remove the spinning icon from the Login button."""
        if hasattr(self, "spinner_label") and self.spinner_label:
            if hasattr(self, "spinner_movie") and self.spinner_movie:
                self.spinner_movie.stop()
            self.spinner_label.deleteLater()
            self.spinner_label = None

        # Re-enable the button
        self.login_button.setText("Login")
        self.login_button.setDisabled(False)
