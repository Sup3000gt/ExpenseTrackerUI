from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
import requests

class UserProfileView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Add back button
        self.add_back_button(self.layout)

        # Title
        self.title_label = QLabel("User Profile")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #333;")
        self.layout.addWidget(self.title_label)

        # Info labels
        self.username_label = QLabel()
        self.email_label = QLabel()
        self.first_name_label = QLabel()
        self.last_name_label = QLabel()
        self.phone_label = QLabel()
        self.dob_label = QLabel()

        # Add info labels to layout
        for label in [
            self.username_label, self.email_label, self.first_name_label,
            self.last_name_label, self.phone_label, self.dob_label
        ]:
            label.setStyleSheet("font-size: 16px; color: #555; margin-top: 5px;")
            self.layout.addWidget(label)

        # Fetch user profile
        self.fetch_user_profile()

    def add_back_button(self, layout):
        """Add a modern back button with an arrow to return to the content view."""
        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/left-arrow.png"))
        back_button.setIconSize(QSize(30, 30))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 12px;
            }
        """)
        back_button.clicked.connect(self.parent.show_content_view)

        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(back_button)
        back_button_layout.setAlignment(Qt.AlignLeft)
        layout.addLayout(back_button_layout)

    def fetch_user_profile(self):
        """Fetch user profile data using the username."""
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/profile"
        headers = {
            "Authorization": f"Bearer {self.parent.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        params = {"username": self.parent.username}

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                profile = response.json()
                self.populate_profile(profile)
            else:
                self.username_label.setText(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.username_label.setText(f"Error: {str(e)}")

    def populate_profile(self, profile):
        """Populate the profile view with user data."""
        self.username_label.setText(f"Username: {profile['username']}")
        self.email_label.setText(f"Email: {profile['email']}")
        self.first_name_label.setText(f"First Name: {profile['firstName']}")
        self.last_name_label.setText(f"Last Name: {profile['lastName']}")
        self.phone_label.setText(f"Phone: {profile['phoneNumber']}")
        self.dob_label.setText(f"Date of Birth: {profile['dateOfBirth'][:10]}")
