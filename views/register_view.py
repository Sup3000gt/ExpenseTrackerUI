from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QScrollArea
from services.user_service import register_user

class RegisterView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Create a scrollable area for the layout
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)

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
        self.register_button.setStyleSheet(
            "padding: 10px; font-size: 14px; background-color: #0275d8; color: white; border-radius: 8px;"
        )
        self.register_button.clicked.connect(self.register_user)
        self.layout.addWidget(self.register_button)

        # Add feedback label
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet("color: red; font-size: 14px;")
        self.layout.addWidget(self.feedback_label)

        # Set the scrollable content and apply the layout
        scroll_area.setWidget(scroll_content)

        # Set the main layout to hold the scroll area
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

    def add_back_button(self):
        """Add a back button with an arrow to return to the main page."""
        back_button = QPushButton("←")
        back_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                padding: 5px 10px;
                color: white;
                background-color: #d9534f;
                border-radius: 8px;
                min-width: 50px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            """
        )
        back_button.clicked.connect(self.parent.show_main_page)

        # Add to a horizontal layout to align it to the left
        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(back_button)
        back_button_layout.setAlignment(Qt.AlignLeft)  # Align to the left
        self.layout.addLayout(back_button_layout)

    def add_input_field(self, label_text, password=False):
        """Add an input field with a label."""
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setPlaceholderText(f"Enter {label_text.lower()}")
        input_field.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        if password:
            input_field.setEchoMode(QLineEdit.Password)

        self.layout.addWidget(input_field)
        return input_field

    def register_user(self):
        """Handle user registration."""
        data = {
            "username": self.username_input.text().strip(),
            "passwordHash": self.password_input.text().strip(),
            "email": self.email_input.text().strip(),
            "firstName": self.first_name_input.text().strip(),
            "lastName": self.last_name_input.text().strip(),
            "phoneNumber": self.phone_number_input.text().strip(),
            "dateOfBirth": self.date_of_birth_input.text().strip(),
        }

        # Validate fields
        if not all(data.values()):
            self.feedback_label.setText("All fields are required.")
            return

        # Call the API
        success, message = self.parent.register_user(data)
        if success:
            self.parent.show_message_view("Registration Successful!")
        else:
            self.feedback_label.setText(message)
