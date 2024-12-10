import re
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QScrollArea
from PySide6.QtGui import QMovie, QIcon
from PySide6.QtCore import QSize
import os
from services.user_service import register_user

class RegisterThread(QThread):
    """Thread for handling the registration API call."""
    register_result = Signal(bool, str)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        success, message = register_user(self.data)
        self.register_result.emit(success, message)

class RegisterView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Create a scrollable area for the layout
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #b3b3b3;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8e8e8e;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Main layout for the scrollable content
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Add Back button
        self.add_back_button()

        # Add input fields
        self.username_input = self.add_input_field("Username:")
        self.password_input = self.add_input_field("Password:", password=True)
        self.email_input = self.add_input_field("Email:")
        self.first_name_input = self.add_input_field("First Name:")
        self.last_name_input = self.add_input_field("Last Name:")
        self.phone_number_input = self.add_input_field("Phone Number:")
        self.date_of_birth_input = self.add_input_field("Date of Birth (YYYY-MM-DD):")

        # Add Register button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #0288d1;
                color: white;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0277bd;
            }
            QPushButton:pressed {
                background-color: #01579b;
            }
        """)
        self.register_button.clicked.connect(self.register_user)
        self.layout.addWidget(self.register_button)

        # Add feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("color: red; font-size: 14px; text-align: center;")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.feedback_label)

        # Set the scrollable content and apply the layout
        scroll_area.setWidget(scroll_content)

        # Set the main layout to hold the scroll area
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

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

    def add_input_field(self, label_text, password=False, placeholder=None):
        """Add an input field with a modern style."""
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; color: #555; font-weight: bold;")
        self.layout.addWidget(label)

        input_field = QLineEdit()
        if placeholder:  # Only set placeholder if provided
            input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.7);
            }
            QLineEdit:focus {
                border: 2px solid #6a1b9a;
                background: rgba(255, 255, 255, 0.9);
            }
            QLineEdit:hover {
                border: 2px solid #8e24aa;
            }
        """)
        if password:
            input_field.setEchoMode(QLineEdit.Password)

        self.layout.addWidget(input_field)
        return input_field

    def show_loading_animation_on_button(self):
        """Show a spinning icon on the Register button."""
        self.register_button.setText("")
        self.spinner_label = QLabel(self.register_button)
        self.spinner_label.setFixedSize(20, 20)
        self.spinner_label.setAlignment(Qt.AlignCenter)

        # Position the spinner inside the button
        self.spinner_label.move(
            (self.register_button.width() // 2) - 10,
            (self.register_button.height() // 2) - 10
        )

        # Load and start the spinner animation
        spinner_path = os.path.join(os.getcwd(), "assets", "spinner.gif")
        self.spinner_movie = QMovie(spinner_path)
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_movie.start()
        self.spinner_label.show()

        # Disable the button to prevent multiple clicks
        self.register_button.setDisabled(True)

    def hide_loading_animation_on_button(self):
        """Remove the spinning icon from the Register button."""
        if hasattr(self, "spinner_label") and self.spinner_label:
            self.spinner_movie.stop()
            self.spinner_label.deleteLater()
            self.spinner_label = None

        self.register_button.setText("Register")
        self.register_button.setDisabled(False)

    def register_user(self):
        """Handle user registration."""
        """Handle user registration with a loading spinner."""
        data = {
            "username": self.username_input.text().strip(),
            "passwordHash": self.password_input.text().strip(),
            "email": self.email_input.text().strip(),
            "firstName": self.first_name_input.text().strip(),
            "lastName": self.last_name_input.text().strip(),
            "phoneNumber": self.phone_number_input.text().strip(),
            "dateOfBirth": self.date_of_birth_input.text().strip(),
        }

        # Client-side validation
        if not all(data.values()):
            self.feedback_label.setText("All fields are required.")
            return

        # Validate email format
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, data["email"]):
            self.feedback_label.setText("Please enter a valid email address.")
            return

        # Validate phone number format (10 digits)
        if not data["phoneNumber"].isdigit() or len(data["phoneNumber"]) != 10:
            self.feedback_label.setText("Phone number must be exactly 10 digits.")
            return

        # Show spinner on the Register button
        self.show_loading_animation_on_button()
        # Start the register thread
        self.register_thread = RegisterThread(data)
        self.register_thread.register_result.connect(self.on_register_result)  # Connect the result signal
        self.register_thread.start()

    def on_register_result(self, success, message):
        """Handle the result of the register API call."""
        self.hide_loading_animation_on_button()

        if success:
            self.parent.show_message_view("Registration Successful! Please check your email to activate your account")
        else:
            self.feedback_label.setText(message)


