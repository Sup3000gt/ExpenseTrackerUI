from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from services.auth_service import login_user
from utils.storage_utils import save_token


class LoginView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)

        self.username_input = self.add_input_field("Username:")
        self.password_input = self.add_input_field("Password:", password=True)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user)
        self.layout.addWidget(self.login_button)

        self.feedback_label = QLabel("")
        self.layout.addWidget(self.feedback_label)

    def add_input_field(self, label_text, password=False):
        label = QLabel(label_text)
        self.layout.addWidget(label)
        input_field = QLineEdit()
        if password:
            input_field.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(input_field)
        return input_field

    def login_user(self):
        """Handle user login."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        success, message, token = login_user(username, password)
        if success:
            save_token(token)  # Save token securely using keyring
            self.parent.jwt_token = token
            self.parent.show_message_view("Login Successful!")
        else:
            self.feedback_label.setText(message)
