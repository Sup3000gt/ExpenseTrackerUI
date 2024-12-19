import re
import logging
import requests
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QFrame, QDialog, QDialogButtonBox,
    QSpacerItem, QSizePolicy
)

logger = logging.getLogger(__name__)


class UserProfileView(QWidget):
    """View for displaying and editing the user's profile."""

    def __init__(self, parent, user_id=None, username=None):
        super().__init__()
        self.parent = parent
        self.user_id = user_id
        self.username = username

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 50, 20, 20)

        self.add_back_button()
        self.setup_title()
        self.add_divider()
        self.fields = {}
        self.create_profile_fields()
        self.setup_buttons()
        self.add_divider()
        self.setup_password_section()
        self.fetch_user_profile()

    def reset_fields_state(self):
        """Disable all editable fields except Username and reset their styles."""
        for label, field in self.fields.items():
            field.setDisabled(True)
            if label != "Username":
                field.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        self.save_button.setDisabled(True)
        self.edit_button.setDisabled(False)
        self.password_input.setDisabled(True)
        self.password_input.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")

    def add_back_button(self):
        """Add a back button to navigate to the content view."""
        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/left-arrow.png"))
        back_button.setIconSize(QSize(30, 30))
        back_button.setStyleSheet("background-color: transparent; border: none;")
        back_button.clicked.connect(self.parent.show_content_view)
        self.layout.addWidget(back_button, alignment=Qt.AlignLeft)

    def setup_title(self):
        """Configure and add the title label."""
        self.title_label = QLabel("User Profile")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-family: 'Comic Sans MS', sans-serif;
                font-weight: 600;
                color: #222;
                margin-bottom: 10px;
            }
        """)
        self.layout.addWidget(self.title_label)

    def add_divider(self):
        """Insert a horizontal line divider."""
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(divider)

    def button_style(self):
        """Return the common style for buttons."""
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
        """Initialize and add profile input fields."""
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
            field.setDisabled(True)
            field.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
            if label in placeholders:
                field.setPlaceholderText(placeholders[label])

            if label == "Username":
                field.setStyleSheet("background-color: #e0e0e0; color: gray;")

            field_layout.addWidget(lbl)
            field_layout.addWidget(field)
            self.fields[label] = field
            self.layout.addLayout(field_layout)

    def setup_buttons(self):
        """Set up Edit and Save buttons with styling and connections."""
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("✏️ Edit Profile")
        self.save_button = QPushButton("💾 Save Changes")
        self.save_button.setDisabled(True)

        self.edit_button.setStyleSheet(self.button_style())
        self.save_button.setStyleSheet(self.button_style())

        self.edit_button.clicked.connect(self.enable_editing)
        self.save_button.clicked.connect(self.submit_profile_changes)

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        self.layout.addLayout(button_layout)

    def setup_password_section(self):
        """Configure the password change section with input and buttons."""
        password_layout = QHBoxLayout()

        pwd_label = QLabel("Password:")
        pwd_label.setFont(QFont("Arial", 14, QFont.Bold))
        pwd_label.setFixedWidth(120)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter new password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setDisabled(True)
        self.password_input.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")

        password_layout.addWidget(pwd_label)
        password_layout.addWidget(self.password_input)
        self.layout.addLayout(password_layout)

        # Password action buttons
        self.password_button_layout = QHBoxLayout()
        self.password_button_layout.setAlignment(Qt.AlignCenter)

        self.change_password_button = QPushButton("🔒 Change Password")
        self.change_password_button.setStyleSheet(self.button_style())
        self.change_password_button.clicked.connect(self.enable_password_editing)

        self.submit_password_button = QPushButton("💾 Submit Password")
        self.submit_password_button.setStyleSheet(self.button_style())
        self.submit_password_button.clicked.connect(self.submit_password_change)
        self.submit_password_button.hide()

        self.password_button_layout.addWidget(self.change_password_button)
        self.password_button_layout.addWidget(self.submit_password_button)
        self.layout.addLayout(self.password_button_layout)

    def fetch_user_profile(self):
        """Retrieve and display the user's profile information."""
        self.reset_fields_state()
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/profile"
        headers = {"Authorization": f"Bearer {self.parent.jwt_token}"}
        params = {"username": self.parent.username}

        logger.debug(f"Fetching profile for username={self.parent.username}")
        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                profile = response.json()
                self.populate_fields(profile)
                logger.info("User profile fetched successfully.")
            else:
                logger.error(f"Failed to fetch profile: {response.status_code} - {response.text}")
                self.show_message("Error", f"Failed to fetch profile: {response.text}", is_error=True)
        except requests.RequestException as e:
            logger.exception("Exception occurred while fetching profile.")
            self.show_message("Error", str(e), is_error=True)

    def populate_fields(self, profile):
        """Fill input fields with fetched profile data."""
        self.fields["Username"].setText(profile.get("username", ""))
        self.fields["Email"].setText(profile.get("email", ""))
        self.fields["First Name"].setText(profile.get("firstName", ""))
        self.fields["Last Name"].setText(profile.get("lastName", ""))
        self.fields["Phone"].setText(self.format_phone(profile.get("phoneNumber", "")))
        self.fields["Date of Birth"].setText(profile.get("dateOfBirth", "")[:10])

    def enable_password_editing(self):
        """Allow the user to edit the password and display the submit button."""
        self.password_input.setDisabled(False)
        self.password_input.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
        self.change_password_button.hide()
        self.submit_password_button.show()

    def submit_password_change(self):
        """Validate and send the new password to the API."""
        new_password = self.password_input.text().strip()
        if not new_password:
            self.show_message("Validation Error", "Password cannot be empty.", is_error=True)
            return

        payload = {"username": self.fields["Username"].text(), "newPassword": new_password}
        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/change-password"
        headers = {"Authorization": f"Bearer {self.parent.jwt_token}"}

        logger.debug("Submitting password change.")
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                logger.info("Password changed successfully.")
                self.show_message("Success", "Password changed successfully!")
                self.password_input.setDisabled(True)
                self.password_input.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
                self.password_input.clear()
                self.submit_password_button.hide()
                self.change_password_button.show()
                self.parent.show_content_view()
            else:
                logger.error(f"Failed to change password: {response.status_code} - {response.text}")
                self.show_message("Error", f"Failed to change password: {response.text}", is_error=True)
        except requests.RequestException as e:
            logger.exception("Exception occurred while changing password.")
            self.show_message("Error", str(e), is_error=True)

    def enable_editing(self):
        """Enable editing for all fields except Username."""
        for label, field in self.fields.items():
            if label != "Username":
                field.setDisabled(False)
                field.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
        self.save_button.setDisabled(False)
        self.edit_button.setDisabled(True)

    def submit_profile_changes(self):
        """Validate input fields and send updated profile data to the API."""
        email = self.fields["Email"].text()
        phone = self.fields["Phone"].text()
        dob = self.fields["Date of Birth"].text()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.show_message("Validation Error", "Invalid email format.", is_error=True)
            logger.warning("Invalid email format entered.")
            return

        clean_phone = re.sub(r"\D", "", phone)
        if len(clean_phone) != 10:
            self.show_message("Validation Error", "Phone number must be 10 digits.", is_error=True)
            logger.warning("Invalid phone number entered.")
            return

        if not re.match(r"\d{4}-\d{2}-\d{2}", dob):
            self.show_message("Validation Error", "DOB must be in YYYY-MM-DD format.", is_error=True)
            logger.warning("Invalid date of birth format entered.")
            return

        updated_data = {
            "username": self.fields["Username"].text(),
            "email": email,
            "firstName": self.fields["First Name"].text(),
            "lastName": self.fields["Last Name"].text(),
            "phoneNumber": clean_phone,
            "dateOfBirth": dob
        }

        api_url = "https://expenseuserserviceapi.azure-api.net/api/Users/update-profile"
        headers = {"Authorization": f"Bearer {self.parent.jwt_token}"}

        logger.debug("Submitting profile changes.")
        try:
            response = requests.put(api_url, headers=headers, json=updated_data)
            if response.status_code == 200:
                logger.info("Profile updated successfully.")
                self.show_message("Success", "Profile updated successfully!")
                self.edit_button.setDisabled(False)
                self.parent.show_content_view()
            else:
                logger.error(f"Failed to update profile: {response.status_code} - {response.text}")
                self.show_message("Error", f"Failed to update profile: {response.text}", is_error=True)
        except requests.RequestException as e:
            logger.exception("Exception occurred while updating profile.")
            self.show_message("Error", str(e), is_error=True)

    @staticmethod
    def format_phone(phone):
        """Format phone number as (123) 456-7890."""
        clean_phone = re.sub(r"\D", "", phone)
        if len(clean_phone) == 10:
            return f"({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
        return phone

    def show_message(self, title, text, is_error=False):
        """Display a styled dialog with the provided message."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(20, 20, 20, 20)
        dlg_layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #333;")
        dlg_layout.addWidget(title_label)

        message_label = QLabel(text)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(QFont("Arial", 12))
        message_label.setWordWrap(True)

        if is_error:
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #ffe6e6;
                    border-radius: 10px;
                }
                QLabel {
                    color: #333;
                }
            """)
        else:
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #e6ffec;
                    border-radius: 10px;
                }
                QLabel {
                    color: #333;
                }
            """)

        dlg_layout.addWidget(message_label)
        dlg_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.setCenterButtons(True)
        button_box.button(QDialogButtonBox.Ok).setText("OK")
        button_box.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #5A9CFF;
                color: white;
                font-size: 14px;
                padding: 8px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0073E6;
            }
        """)
        button_box.accepted.connect(dialog.accept)

        dlg_layout.addWidget(button_box)
        dialog.exec()
