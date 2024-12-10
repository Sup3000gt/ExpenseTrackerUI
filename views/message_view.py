from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MessageView(QWidget):
    def __init__(self, message, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)

        # Display the message
        self.message_label = QLabel(message)
        self.layout.addWidget(self.message_label)
        self.message_label.setStyleSheet("font-size: 18px; color: #333; text-align: center;")

        # Add a Logout button (if applicable)
        self.logout_button = QPushButton("Back to Main Page")
        self.logout_button.clicked.connect(self.logout_user)
        self.layout.addWidget(self.logout_button)

    def logout_user(self):
        """Handle user logout."""
        self.parent.jwt_token = None  # Clear the token
        self.parent.show_main_page()  # Redirect to the main page
