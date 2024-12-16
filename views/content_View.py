from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import requests
import os
import locale

class ContentView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Title at the top center
        self.title_label = QLabel("Expense Tracker Dashboard")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;  /* Slightly larger font size for emphasis */
                font-family: 'Comic Sans MS', sans-serif;  /* Playful and casual font */
                font-weight: 600;  /* Semi-bold for a subtle emphasis */
                color: #222;  /* Darker gray for better readability */
                margin-bottom: 10px;  /* Add some space below the title */
            }
        """)
        self.layout.addWidget(self.title_label)

        # Buttons container
        self.buttons_layout = QHBoxLayout()  # Define the buttons layout here
        self.buttons_layout.setSpacing(15)

        # User profile button
        self.profile_button = QPushButton()
        self.profile_button.setIcon(QIcon(QPixmap("assets/user_profile_icon.png")))
        self.profile_button.setIconSize(QSize(32, 32))
        self.profile_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1); /* Optional hover effect */
            }
        """)
        self.profile_button.clicked.connect(self.show_user_profile)
        self.buttons_layout.addWidget(self.profile_button)

        # Add transaction button
        self.add_transaction_button = QPushButton()
        self.add_transaction_button.setIcon(QIcon(QPixmap("assets/add_transaction_icon.png")))
        self.add_transaction_button.setIconSize(QSize(32, 32))
        self.add_transaction_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1); /* Optional hover effect */
            }
        """)
        self.add_transaction_button.clicked.connect(self.add_transaction)
        self.buttons_layout.addWidget(self.add_transaction_button)

        # Generate report button
        self.generate_report_button = QPushButton()
        self.generate_report_button.setIcon(QIcon(QPixmap("assets/report.png")))
        self.generate_report_button.setIconSize(QSize(32, 32))
        self.generate_report_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1); /* Optional hover effect */
            }
        """)
        self.generate_report_button.clicked.connect(self.generate_report)
        self.buttons_layout.addWidget(self.generate_report_button)

        # Logout button
        self.logout_button = QPushButton()
        self.logout_button.setIcon(QIcon(QPixmap("assets/logout.png")))
        self.logout_button.setIconSize(QSize(32, 32))
        self.logout_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1); /* Optional hover effect */
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        self.buttons_layout.addWidget(self.logout_button)

        # Add buttons layout to the main layout
        self.layout.addLayout(self.buttons_layout)

        # Container for headers and transaction list
        transaction_container = QWidget()
        transaction_layout = QVBoxLayout()
        transaction_layout.setContentsMargins(0, 0, 0, 0)
        transaction_layout.setSpacing(0)
        transaction_container.setLayout(transaction_layout)

        # Header layout (no white frame, just labels and lines)
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Titles for columns
        title_transaction_type = QLabel("Transaction Type")
        title_transaction_type.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_transaction_type.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_transaction_type)

        # Vertical line separator after Transaction Type
        vline1 = QFrame()
        vline1.setFrameShape(QFrame.VLine)
        vline1.setFrameShadow(QFrame.Sunken)
        header_layout.addWidget(vline1)

        title_amount = QLabel("Amount")
        title_amount.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_amount.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_amount)

        # Vertical line separator after Amount
        vline2 = QFrame()
        vline2.setFrameShape(QFrame.VLine)
        vline2.setFrameShadow(QFrame.Sunken)
        header_layout.addWidget(vline2)

        title_date = QLabel("Date")
        title_date.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_date.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_date)

        header_widget.setLayout(header_layout)

        # Add horizontal line under header
        hline_header = QFrame()
        hline_header.setFrameShape(QFrame.HLine)
        hline_header.setFrameShadow(QFrame.Sunken)

        transaction_layout.addWidget(header_widget)
        transaction_layout.addWidget(hline_header)

        # Transaction List Widget
        self.transaction_list = QListWidget()
        self.transaction_list.setStyleSheet("""
            font-size: 14px; 
            border: none;
            background-color: transparent;
        """)
        transaction_layout.addWidget(self.transaction_list)  # Add the list to the container

        # Add the container to the main layout
        self.layout.addWidget(transaction_container)

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
        """Populate the transaction list widget with styled data."""
        self.transaction_list.clear()  # Clear any existing items

        for transaction in transactions.get('transactions', []):
            # Create a widget for the transaction item
            item_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(10, 5, 10, 5)  # Left, Top, Right, Bottom margins
            layout.setSpacing(10)  # Space between widgets
            item_widget.setLayout(layout)

            # Icon for transaction type (no wrapping, just place the icon)
            icon_label = QLabel()
            transaction_type = transaction['transactionType']
            if transaction_type == "Income":
                icon_path = os.path.join(os.getcwd(), "assets/income.png")
            else:
                icon_path = os.path.join(os.getcwd(), "assets/expense.png")

            icon_pixmap = QPixmap(icon_path)
            if not icon_pixmap.isNull():
                icon_label.setPixmap(icon_pixmap.scaled(32, 32, Qt.KeepAspectRatio))
            else:
                icon_label.setText("No Icon")
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

            # Vertical line separator after icon
            vline1 = QFrame()
            vline1.setFrameShape(QFrame.VLine)
            vline1.setFrameShadow(QFrame.Sunken)
            vline1.setStyleSheet("margin: 0 10px;")
            layout.addWidget(vline1)

            # Amount
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            amount = locale.format_string("%0.2f", transaction['amount'], grouping=True)
            amount_label = QLabel(f"${amount}" if transaction_type == "Income" else f"-${amount}")
            amount_label.setAlignment(Qt.AlignCenter)
            if transaction_type == "Income":
                amount_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
            else:
                amount_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            layout.addWidget(amount_label)

            # Vertical line separator after Amount
            vline2 = QFrame()
            vline2.setFrameShape(QFrame.VLine)
            vline2.setFrameShadow(QFrame.Sunken)
            vline2.setStyleSheet("margin: 0 10px;")
            layout.addWidget(vline2)

            # Date
            date = transaction['date'][:10]  # Extract YYYY-MM-DD
            date_label = QLabel(date)
            date_label.setAlignment(Qt.AlignCenter)
            date_label.setStyleSheet("font-size: 14px; color: #555;")
            layout.addWidget(date_label)

            # Horizontal line at the bottom of each item (optional)
            # If you'd like a horizontal line below each item, you can add another frame after adding the item.
            # For now, we skip it as it's not requested.

            # Create a QListWidgetItem and set the custom widget
            list_item = QListWidgetItem()
            # Increase row height for better appearance
            item_widget.setFixedHeight(50)  # Set a fixed height for the row
            list_item.setSizeHint(item_widget.sizeHint())

            list_item.setData(Qt.UserRole, transaction)  # Store transaction data
            self.transaction_list.addItem(list_item)
            self.transaction_list.setItemWidget(list_item, item_widget)

        # Connect item click signal
        self.transaction_list.itemClicked.connect(self.display_transaction_details)

    def display_transaction_details(self, item):
        """Display detailed info for a selected transaction."""
        transaction = item.data(Qt.UserRole)  # Retrieve the full transaction data
        self.parent.show_transaction_details_view(transaction)

    def logout(self):
        """Handle logout functionality."""
        self.parent.jwt_token = None
        self.parent.user_id = None
        self.parent.show_main_page()

    def show_user_profile(self):
        """Navigate to the user profile view."""
        self.parent.show_user_profile_view()

    def generate_report(self):
        self.parent.show_generate_report_view()

    def add_transaction(self):
        """Navigate to the AddTransactionView."""
        self.parent.show_add_transaction_view()

    def generate_report(self):
        """Placeholder for Generate Report functionality."""
        pass
