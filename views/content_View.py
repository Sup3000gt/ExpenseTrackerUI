import logging
import requests
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame,
    QListWidget, QListWidgetItem, QComboBox
)
import os
import locale
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentView(QWidget):
    """Dashboard view displaying user transactions and navigation options."""

    def __init__(self, parent, user_id=None, username=None):
        super().__init__()
        self.parent = parent
        self.user_id = user_id
        self.username = username

        # Ensure subscription_key is available
        if not hasattr(self.parent, 'subscription_key'):
            logger.error("Parent does not have attribute 'subscription_key'")
            raise AttributeError("Parent does not have attribute 'subscription_key'")
        logger.debug(f"Subscription key: {self.parent.subscription_key}")

        self.current_page = 1
        self.current_month = "All"
        self.all_transactions = []
        self.grouped_transactions = {}
        self.transactions_per_page = 8

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.setup_title()
        self.setup_buttons()
        self.setup_filters()
        self.setup_transaction_list()
        self.setup_pagination()
        self.setup_placeholder()

    def setup_title(self):
        """Add the dashboard title to the layout."""
        self.title_label = QLabel("Expense Tracker Dashboard")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-family: 'Comic Sans MS', sans-serif;
                font-weight: 600;
                color: #222;
                margin-bottom: 10px;
            }
        """)
        self.layout.addWidget(self.title_label)

    def setup_buttons(self):
        """Initialize and add navigation buttons to the layout."""
        self.buttons_layout = QHBoxLayout()
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
                background-color: rgba(0, 0, 0, 0.1);
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
                background-color: rgba(0, 0, 0, 0.1);
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
                background-color: rgba(0, 0, 0, 0.1);
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
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        self.buttons_layout.addWidget(self.logout_button)

        self.layout.addLayout(self.buttons_layout)

    def setup_filters(self):
        """Initialize and add the month filter combo box."""
        self.month_filter = QComboBox()
        self.month_filter.addItem("All")
        self.month_filter.setStyleSheet("padding: 5px; font-size: 14px;")
        self.month_filter.currentTextChanged.connect(self.update_month_filter)
        self.layout.addWidget(self.month_filter)

    def setup_transaction_list(self):
        """Set up the transaction list and header."""
        transaction_container = QWidget()
        transaction_layout = QVBoxLayout()
        transaction_layout.setContentsMargins(0, 0, 0, 0)
        transaction_layout.setSpacing(0)
        transaction_container.setLayout(transaction_layout)

        # Header layout
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Column titles
        titles = ["Transaction Type", "Amount", "Date"]
        for title in titles:
            lbl = QLabel(title)
            lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
            lbl.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(lbl)

            # Add vertical separator except after the last title
            if title != titles[-1]:
                vline = QFrame()
                vline.setFrameShape(QFrame.VLine)
                vline.setFrameShadow(QFrame.Sunken)
                header_layout.addWidget(vline)

        header_widget.setLayout(header_layout)

        # Horizontal line under header
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
        transaction_layout.addWidget(self.transaction_list)

        self.layout.addWidget(transaction_container)

    def setup_pagination(self):
        """Initialize and add pagination controls."""
        pagination_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #2d89ef;
                color: white;
                border-radius: 5px;
                padding: 2px 5px;
                font-weight: bold;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        self.prev_button.setFixedHeight(35)
        self.prev_button.setFixedWidth(100)
        pagination_layout.addWidget(self.prev_button)

        self.page_label = QLabel(str(self.current_page))
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                background-color: rgba(240, 240, 240, 0.7);
                padding: 2px 2px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
        """)
        self.page_label.setFixedWidth(30)
        pagination_layout.addWidget(self.page_label)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #2d89ef;
                color: white;
                border-radius: 5px;
                padding: 2px 5px;
                font-weight: bold;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        self.next_button.setFixedHeight(35)
        self.next_button.setFixedWidth(100)
        pagination_layout.addWidget(self.next_button)

        self.layout.addLayout(pagination_layout)

    def setup_placeholder(self):
        """Add a placeholder label when transactions are not loaded."""
        self.fetch_transactions_placeholder = QLabel("Please log in to view transactions.")
        self.fetch_transactions_placeholder.setAlignment(Qt.AlignCenter)
        self.fetch_transactions_placeholder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #888;
            }
        """)
        self.layout.addWidget(self.fetch_transactions_placeholder)

    def update_user_info(self, user_id, jwt_token):
        """Update user-related information and refresh the view."""
        self.user_id = user_id
        self.jwt_token = jwt_token
        logger.debug(f"Updated user info: user_id={self.user_id}, jwt_token={self.jwt_token[:10]}...")
        self.fetch_all_transactions()

    def fetch_all_transactions(self):
        """Fetch all transaction records for the logged-in user."""
        logger.debug("Fetching all transactions.")
        logger.debug(f"Fetching transactions for user_id={self.user_id}")
        logger.debug(f"JWT token available: {'yes' if self.jwt_token else 'no'}")
        logger.debug(f"Subscription key: {self.parent.subscription_key}")
        if not self.user_id or not self.jwt_token:
            self.transaction_list.clear()
            self.transaction_list.addItem("Error: User information is missing.")
            logger.error("User information is missing.")
            return

        api_url = f"https://expensetransactionserviceapi.azure-api.net/api/Transactions/user/{self.user_id}"

        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        params = {
            "page": 1,
            "pageSize": 10000,
            "sortBy": "date",
            "sortOrder": "desc"
        }

        logger.debug(f"Sending GET request to {api_url} with headers {headers} and params {params}")
        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                self.all_transactions = data.get('transactions', [])
                logger.debug(f"Fetched {len(self.all_transactions)} transactions.")
                self.group_by_month()
                self.current_month = "All"
                index = self.month_filter.findText("All")
                if index != -1:
                    self.month_filter.setCurrentIndex(index)

                self.display_transactions_for_current_month()
                self.fetch_transactions_placeholder.hide()
                logger.info("Transactions fetched and displayed successfully.")
            else:
                self.transaction_list.clear()
                self.transaction_list.addItem(f"Error fetching transactions: {response.status_code}")
                self.fetch_transactions_placeholder.show()
                logger.warning(f"Failed to fetch transactions: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.transaction_list.clear()
            self.transaction_list.addItem(f"Error: {str(e)}")
            self.fetch_transactions_placeholder.show()
            logger.error(f"An error occurred while fetching transactions: {e}")

    def group_by_month(self):
        """Group all transactions by month and year."""
        self.grouped_transactions.clear()
        self.grouped_transactions["All"] = self.all_transactions

        for txn in self.all_transactions:
            date_str = txn['date'][:10]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_year = date_obj.strftime("%B %Y")

            if month_year not in self.grouped_transactions:
                self.grouped_transactions[month_year] = []
            self.grouped_transactions[month_year].append(txn)

        # Update the month_filter ComboBox
        self.month_filter.blockSignals(True)
        self.month_filter.clear()
        self.month_filter.addItem("All")

        sorted_month_year = sorted(
            [k for k in self.grouped_transactions.keys() if k != "All"],
            key=lambda x: datetime.strptime(x, "%B %Y"),
            reverse=True
        )
        self.month_filter.addItems(sorted_month_year)
        self.month_filter.blockSignals(False)
        logger.debug("Grouped transactions by month and updated month filter.")

    def display_transactions_for_current_month(self):
        """Display transactions for the currently selected month with pagination."""
        self.transaction_list.clear()

        transactions = self.grouped_transactions.get(self.current_month, [])

        start_idx = (self.current_page - 1) * self.transactions_per_page
        end_idx = start_idx + self.transactions_per_page
        page_transactions = transactions[start_idx:end_idx]

        self.populate_transaction_list(page_transactions)

        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(len(page_transactions) == self.transactions_per_page)
        self.page_label.setText(f"{self.current_page}")

        logger.debug(f"Displaying page {self.current_page} with {len(page_transactions)} transactions.")

    def populate_transaction_list(self, transactions):
        """Populate the transaction list widget with styled data."""
        self.transaction_list.clear()

        for transaction in transactions:
            item_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(10)
            item_widget.setLayout(layout)

            # Icon for transaction type
            icon_label = QLabel()
            transaction_type = transaction['transactionType']
            icon_path = os.path.join(os.getcwd(), "assets/income.png") if transaction_type == "Income" else os.path.join(os.getcwd(), "assets/expense.png")

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
            try:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            except locale.Error:
                locale.setlocale(locale.LC_ALL, '')  # Fallback to default locale
                logger.warning("Locale 'en_US.UTF-8' not available. Using default locale.")
            amount = locale.format_string("%0.2f", transaction['amount'], grouping=True)
            amount_label = QLabel(f"${amount}" if transaction_type == "Income" else f"-${amount}")
            amount_label.setAlignment(Qt.AlignCenter)
            color = "green" if transaction_type == "Income" else "red"
            amount_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            layout.addWidget(amount_label)

            # Vertical line separator after Amount
            vline2 = QFrame()
            vline2.setFrameShape(QFrame.VLine)
            vline2.setFrameShadow(QFrame.Sunken)
            vline2.setStyleSheet("margin: 0 10px;")
            layout.addWidget(vline2)

            # Date
            date = transaction['date'][:10]
            date_label = QLabel(date)
            date_label.setAlignment(Qt.AlignCenter)
            date_label.setStyleSheet("font-size: 14px; color: #555;")
            layout.addWidget(date_label)

            # Create a QListWidgetItem and set the custom widget
            list_item = QListWidgetItem()
            item_widget.setFixedHeight(50)
            list_item.setSizeHint(item_widget.sizeHint())

            list_item.setData(Qt.UserRole, transaction)
            self.transaction_list.addItem(list_item)
            self.transaction_list.setItemWidget(list_item, item_widget)

        logger.debug(f"Populated transaction list with {len(transactions)} transactions.")
        self.transaction_list.itemClicked.connect(self.display_transaction_details)

    def prev_page(self):
        """Navigate to the previous page of transactions."""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_transactions_for_current_month()
            logger.debug(f"Navigated to previous page: {self.current_page}")

    def next_page(self):
        """Navigate to the next page of transactions."""
        self.current_page += 1
        self.display_transactions_for_current_month()
        logger.debug(f"Navigated to next page: {self.current_page}")

    def update_month_filter(self, month):
        """Update the displayed transactions based on the selected month and year."""
        self.current_month = month
        self.current_page = 1
        self.display_transactions_for_current_month()
        logger.debug(f"Month filter updated to: {self.current_month}")

    def display_transaction_details(self, item):
        """Display detailed info for a selected transaction."""
        transaction = item.data(Qt.UserRole)
        logger.debug(f"Displaying details for transaction ID: {transaction.get('id')}")
        self.parent.show_transaction_details_view(transaction)

    def logout(self):
        """Handle logout functionality."""
        logger.info("User is logging out.")
        self.parent.jwt_token = None
        self.parent.user_id = None
        self.parent.show_main_page()

    def show_user_profile(self):
        """Navigate to the user profile view."""
        logger.debug("Navigating to user profile view.")
        self.parent.show_user_profile_view()

    def generate_report(self):
        """Navigate to the report generation view."""
        logger.debug("Navigating to generate report view.")
        self.parent.show_report_view()

    def add_transaction(self):
        """Navigate to the AddTransactionView."""
        logger.debug("Navigating to AddTransactionView.")
        self.parent.show_add_transaction_view()
