from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton
from services.auth_service import login_user
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMovie
from PySide6.QtCore import QThread, Signal
import os
from PySide6.QtGui import QPixmap


class LoginThread(QThread):
    login_result = Signal(bool, str, str)  # Signal to send (success, message, token)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        """Run the API call in a separate thread."""
        success, message, token = login_user(self.username, self.password)
        self.login_result.emit(success, message, token)

class MainPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # Title with word wrapping
        self.title_label = QLabel("Personal Expense Tracker")
        self.title_label.setAlignment(Qt.AlignCenter)  # Center-align horizontally
        self.title_label.setWordWrap(True)  # Enable word wrapping
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #555; text-align: center;")
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
        self.login_button.setStyleSheet("padding: 10px; font-size: 18px; background-color: #5cb85c; color: white; border-radius: 8px;")
        self.login_button.clicked.connect(self.login_user)
        self.layout.addWidget(self.login_button)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("padding: 10px; font-size: 18px; background-color: #0275d8; color: white; border-radius: 8px;")
        self.register_button.clicked.connect(self.parent.show_register_view)
        self.layout.addWidget(self.register_button)

        # Forgot Password button
        self.forgot_password_button = QPushButton("Forgot Password")
        self.forgot_password_button.setStyleSheet("padding: 10px; font-size: 18px; background-color: #f0ad4e; color: white; border-radius: 8px;")
        self.forgot_password_button.clicked.connect(self.parent.show_forgot_password_view)
        self.layout.addWidget(self.forgot_password_button)

        # Feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red; text-align: center;")
        self.layout.addWidget(self.feedback_label)

        # Add Microsoft Icon
        self.icon_label = QLabel(self)
        pixmap = QPixmap("assets/microsoft3.png")
        self.icon_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))  # Scale to fit
        self.layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        # Add Text Below the Icon
        self.text_label = QLabel("Microsoft Software and Systems Academy", self)
        self.text_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #555; text-align: center;")
        self.layout.addWidget(self.text_label, alignment=Qt.AlignCenter)

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

    def on_login_result(self, success, message, token):
        """Handle the result of the login API call."""
        self.hide_loading_animation_on_button()

        if success:
            self.parent.jwt_token = token
            self.parent.show_message_view("Login Successful!")
        else:
            self.feedback_label.setText("· Invalid Username or password")

    def show_loading_animation_on_button(self):
        self.login_button.setText("")
        """Show a spinning icon on the Login button."""
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
        print(f"Spinner GIF Path: {spinner_path}")

        self.spinner_movie = QMovie(spinner_path)
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_movie.start()
        self.spinner_label.show()

        # Disable the button to prevent multiple clicks
        self.login_button.setDisabled(True)

    def hide_loading_animation_on_button(self):
        """Remove the spinning icon from the Login button."""
        if hasattr(self, "spinner_label") and self.spinner_label:
            self.spinner_movie.stop()
            self.spinner_label.deleteLater()
            self.spinner_label = None

        # Re-enable the button
        self.login_button.setText("Login")
        self.login_button.setDisabled(False)
