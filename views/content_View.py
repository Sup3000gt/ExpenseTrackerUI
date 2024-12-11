from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidget, QScrollArea, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import requests
import os
from appconfig import USER_BASE_API_URL, USER_SERVICE_SUBSCRIPTION_KEY

class ContentView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: red; color: white; border-radius: 8px;")
        self.logout_button.clicked.connect(self.logout)
        self.logout_layout = QHBoxLayout()
        self.logout_layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        self.layout.addLayout(self.logout_layout)

        # User profile button
        self.profile_button = QPushButton("User Profile")
        self.profile_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: #0275d8; color: white; border-radius: 8px;")
        self.profile_button.clicked.connect(self.show_user_profile)
        self.layout.addWidget(self.profile_button, alignment=Qt.AlignLeft)

        # Add transaction button
        self.add_transaction_button = QPushButton("Add Transaction")
        self.add_transaction_button.setStyleSheet("padding: 10px; font-size: 14px; background-color: green; color: white; border-radius: 8px;")
        self.add_transaction_button.clicked.connect(self.add_transaction)
        self.layout.addWidget(self.add_transaction_button, alignment=Qt.AlignLeft)

        # Transaction list container
        self.transaction_list = QListWidget()
        self.transaction_list.setStyleSheet("font-size: 14px; border: 1px solid gray; border-radius: 8px;")
        self.layout.addWidget(self.transaction_list)

        # Fetch and display transactions
        self.fetch_transactions()

    def fetch_transactions(self):
        """Fetch transaction records for the logged-in user."""

        api_url = f"https://expensetransactionserviceapi.azure-api.net/api/Transactions/user/{self.parent.user_id}"

        headers = {
            "Authorization": f"Bearer {self.parent.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        params = {
            "page": 1,
            "pageSize": 10,
            "sortBy": "date",
            "sortOrder": "desc"
        }

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                transactions = response.json()
                self.populate_transaction_list(transactions)
            else:
                self.transaction_list.addItem(f"Error fetching transactions: {response.status_code}")
        except Exception as e:
            self.transaction_list.addItem(f"Error: {str(e)}")

    def populate_transaction_list(self, transactions):
        """Populate the transaction list widget with data."""
        self.transaction_list.clear()
        for transaction in transactions.get('data', []):
            self.transaction_list.addItem(f"{transaction['date']} - {transaction['category']}: ${transaction['amount']}")

    def logout(self):
        """Handle logout functionality."""
        self.parent.jwt_token = None
        self.parent.user_id = None
        self.parent.show_login_view()

    def show_user_profile(self):
        """Navigate to the user profile view."""
        self.parent.show_user_profile_view()

    def add_transaction(self):
        """Navigate to the add transaction view."""
        self.parent.show_add_transaction_view()
