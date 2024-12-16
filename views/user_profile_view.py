import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
import requests

class UserProfileView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Add back button
        self.add_back_button()

        # Title
        self.title_label = QLabel("User Profile")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.layout.addWidget(self.title_label)

        # Divider
        self.add_divider()

        # Profile Fields
        self.fields = {}
        self.create_profile_fields()

        # Buttons Layout
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("✏️ Edit Profile")
        self.save_button = QPushButton("💾 Save Changes")
        self.save_button.setDisabled(True)  # Initially disabled

        # Button Styling
        self.style_buttons()

        self.edit_button.clicked.connect(self.enable_editing)
        self.save_button.clicked.connect(self.submit_profile_changes)

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        self.layout.addLayout(button_layout)

        # Divider
        self.add_divider()

        # Change Password Section
        self.change_password_button = QPushButton("🔒 Change Password")
        self.change_password_button.setStyleSheet(self.button_style())
        self.change_password_button.clicked.connect(self.show_password_input)
        self.layout.addWidget(self.change_password_button, alignment=Qt.AlignCenter)

        # Password Input and Submit Button (initially hidden)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter new password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setStyleSheet("background-color: #ffffff; border-radius: 5px;")
        self.password_input.hide()

        self.submit_password_button = QPushButton("💾 Submit Password")
        self.submit_password_button.setStyleSheet(self.button_style())
        self.submit_password_button.clicked.connect(self.submit_password_change)
        self.submit_password_button.hide()

        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.submit_password_button, alignment=Qt.AlignCenter)

        # Fetch and populate user profile
        self.fetch_user_profile()

    def add_back_button(self):
        """Add a back button."""
        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/left-arrow.png"))
        back_button.setIconSize(QSize(30, 30))
        back_button.setStyleSheet("background-color: transparent; border: none;")
        back_button.clicked.connect(self.parent.show_content_view)
        self.layout.addWidget(back_button, alignment=Qt.AlignLeft)

    def style_buttons(self):
        """Style the Edit and Save buttons."""
        button_style = self.button_style()
        self.edit_button.setStyleSheet(button_style)
        self.save_button.setStyleSheet(button_style)

    def add_divider(self):
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(divider)

    def button_style(self):
        """Reusable button style."""
        return """
            QPushButton {
                background-color: #5A9CFF;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0073E6;
            }
        """

    def create_profile_fields(self):
        """Create textboxes for displaying user profile information."""
        placeholders = {
            "Email": "Enter your new email",
            "First Name": "Enter your new first name",
            "Last Name": "Enter your new last name",
            "Phone": "Enter your new phone number",
            "Date of Birth": "YYYY-MM-DD"
        }

        labels = ["Username", "Email", "First Name", "Last Name", "Phone", "Date of Birth"]
        for label in labels:
            field_layout = QHBoxLayout()

            lbl = QLabel(f"{label}:")
            lbl.setFont(QFont("Arial", 14, QFont.Bold))
            lbl.setFixedWidth(120)

            field = QLineEdit()
            field.setFont(QFont("Arial", 14))
            field.setDisabled(True)  # Initially disabled
            field.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
            if label in placeholders:
                field.setPlaceholderText(placeholders[label])

            if label == "Username":
                field.setStyleSheet("background-color: #e0e0e0; color: gray;")

            field_layout.addWidget(lbl)
            field_layout.addWidget(field)
            self.fields[label] = field
            self.layout.addLayout(field_layout)

    def fetch_user_profile(self):
        """Fetch user profile and populate fields."""
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/profile"
        headers = {"Authorization": f"Bearer {self.parent.jwt_token}"}
        params = {"username": self.parent.username}

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                profile = response.json()
                self.populate_fields(profile)
            else:
                QMessageBox.critical(self, "Error", f"Failed to fetch profile: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def populate_fields(self, profile):
        """Populate fields with user data."""
        self.fields["Username"].setText(profile["username"])
        self.fields["Email"].setText(profile["email"])
        self.fields["First Name"].setText(profile["firstName"])
        self.fields["Last Name"].setText(profile["lastName"])
        self.fields["Phone"].setText(self.format_phone(profile["phoneNumber"]))
        self.fields["Date of Birth"].setText(profile["dateOfBirth"][:10])

    def show_password_input(self):
        """Show the password input and submit button."""
        self.password_input.show()
        self.submit_password_button.show()

    def submit_password_change(self):
        """Validate and send the new password to the Change Password API."""
        new_password = self.password_input.text().strip()
        if not new_password:
            QMessageBox.warning(self, "Validation Error", "Password cannot be empty.")
            return

        payload = {"username": self.fields["Username"].text(), "newPassword": new_password}
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/change-password"
        headers = {"Authorization": f"Bearer {self.parent.jwt_token}"}

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Password changed successfully!")
                self.password_input.hide()
                self.submit_password_button.hide()
                self.password_input.clear()
            else:
                QMessageBox.critical(self, "Error", f"Failed to change password: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def enable_editing(self):
        """Enable editing for fields except Username."""
        for label, field in self.fields.items():
            if label != "Username":
                field.setDisabled(False)
                field.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
        self.save_button.setDisabled(False)

    def submit_profile_changes(self):
        """Validate fields and submit data."""
        email = self.fields["Email"].text()
        phone = self.fields["Phone"].text()
        dob = self.fields["Date of Birth"].text()

        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Validation Error", "Invalid email format.")
            return

        # Validate phone number
        clean_phone = re.sub(r"\D", "", phone)  # Remove non-digits
        if len(clean_phone) != 10:
            QMessageBox.warning(self, "Validation Error", "Phone number must be 10 digits.")
            return

        # Validate DOB
        if not re.match(r"\d{4}-\d{2}-\d{2}", dob):
            QMessageBox.warning(self, "Validation Error", "DOB must be in YYYY-MM-DD format.")
            return

        updated_data = {
            "username": self.fields["Username"].text(),
            "email": email,
            "firstName": self.fields["First Name"].text(),
            "lastName": self.fields["Last Name"].text(),
            "phoneNumber": clean_phone,
            "dateOfBirth": dob
        }

        # Send to API
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/update-profile"
        headers = {"Authorization": f"Bearer {self.parent.jwt_token}"}
        try:
            response = requests.put(api_url, headers=headers, json=updated_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Profile updated successfully!")
                self.parent.show_content_view()
            else:
                QMessageBox.critical(self, "Error", f"Failed to update profile: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    @staticmethod
    def format_phone(phone):
        """Format phone number as (123) 456-7890."""
        clean_phone = re.sub(r"\D", "", phone)
        return f"({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
