from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QListWidget, \
    QListWidgetItem, QComboBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import requests
import os
import locale
from datetime import datetime

class ContentView(QWidget):
    def __init__(self, parent,user_id=None, username=None):
        print("\n=== Initializing ContentView ===")
        print(f"Creating ContentView with user_id={user_id}, username={username}")
        super().__init__()
        print(f"ContentView initialized with parent: {parent}, type: {type(parent)}")

        self.parent = parent
        self.user_id = user_id
        self.username = username

        # 检查 subscription_key 是否可用
        if not hasattr(self.parent, 'subscription_key'):
            raise AttributeError("Parent does not have attribute 'subscription_key'")
        print(f"Subscription key: {self.parent.subscription_key}")

        self.current_page = 1
        self.current_month = "All"
        self.all_transactions = []  # Will hold all transactions once fetched
        self.grouped_transactions = {}  # Dictionary to hold transactions by month
        self.transactions_per_page = 8

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

        # Add buttons layout to the main layout
        self.layout.addLayout(self.buttons_layout)

        # Month filter combo box
        self.month_filter = QComboBox()
        self.month_filter.addItems(
            ["All", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December"])
        self.month_filter.setStyleSheet("padding: 5px; font-size: 14px;")
        self.month_filter.currentTextChanged.connect(self.update_month_filter)
        self.layout.addWidget(self.month_filter)

        # Container for headers and transaction list
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

        # Pagination buttons
        pagination_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #2d89ef;
                color: white;
                border-radius: 5px;
                padding: 2px 5px; /* Very small horizontal padding */
                font-weight: bold;
                border: none;
                font-size: 12px; /* Slightly smaller font */
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        self.prev_button.setFixedHeight(35)
        self.prev_button.setFixedWidth(100)  # Force a narrower width
        pagination_layout.addWidget(self.prev_button)

        self.page_label = QLabel(str(self.current_page))
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                background-color: rgba(240, 240, 240, 0.7); /* Semi-transparent background */
                padding: 2px 2px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
        """)
        self.page_label.setFixedWidth(30)  # Narrow fixed width for the label
        pagination_layout.addWidget(self.page_label)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #2d89ef;
                color: white;
                border-radius: 5px;
                padding: 2px 5px; /* Very small horizontal padding */
                font-weight: bold;
                border: none;
                font-size: 12px; /* Slightly smaller font */
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        self.next_button.setFixedHeight(35)
        self.next_button.setFixedWidth(100)  # Force a narrower width
        pagination_layout.addWidget(self.next_button)

        self.layout.addLayout(pagination_layout)

        # Fetch transactions placeholder
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
        print("\n=== update_user_info called ===")
        self.user_id = user_id
        self.jwt_token = jwt_token
        print(f"Updated user info: user_id={self.user_id}, jwt_token={self.jwt_token[:10]}...")  # Debugging user info

        # Fetch transactions after updating user info
        self.fetch_all_transactions()

    def fetch_all_transactions(self):
        """Fetch all transaction records for the logged-in user."""
        print("fetch_all_transactions called")
        print(f"Fetching transactions for user_id={self.user_id}")
        print(f"JWT token available: {'yes' if self.jwt_token else 'no'}")
        print(f"Subscription key: {self.parent.subscription_key}")
        if not self.user_id or not self.jwt_token:
            self.transaction_list.clear()
            self.transaction_list.addItem("Error: User information is missing.")
            return

        api_url = f"https://expensetransactionserviceapi.azure-api.net/api/Transactions/user/{self.user_id}"

        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        params = {
            "page": 1,
            "pageSize": 10000,  # Large number to fetch all transactions
            "sortBy": "date",
            "sortOrder": "desc"
        }

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"API URL: {api_url}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                self.all_transactions = data.get('transactions', [])
                print(f"API Response: {response.status_code}")
                print(f"Response Content: {response.text}")
                self.group_by_month()
                self.current_month = "All"
                index = self.month_filter.findText("All")
                if index != -1:
                    self.month_filter.setCurrentIndex(index)

                self.display_transactions_for_current_month()
                self.fetch_transactions_placeholder.hide()  # Hide placeholder
            else:
                self.transaction_list.clear()
                self.transaction_list.addItem(f"Error fetching transactions: {response.status_code}")
                self.fetch_transactions_placeholder.show()  # Show placeholder
        except Exception as e:
            self.transaction_list.clear()
            self.transaction_list.addItem(f"Error: {str(e)}")
            self.fetch_transactions_placeholder.show()  # Show placeholder

    def group_by_month(self):
        """Group all transactions by month name."""
        self.grouped_transactions.clear()
        # Also create an "All" entry containing all transactions
        self.grouped_transactions["All"] = self.all_transactions

        for txn in self.all_transactions:
            # Parse month from date
            date_str = txn['date'][:10]  # YYYY-MM-DD
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_name = date_obj.strftime("%B")

            if month_name not in self.grouped_transactions:
                self.grouped_transactions[month_name] = []
            self.grouped_transactions[month_name].append(txn)

    def display_transactions_for_current_month(self):
        """Display transactions for the currently selected month with pagination."""
        self.transaction_list.clear()

        # Get the transactions for the current month
        transactions = self.grouped_transactions.get(self.current_month, [])

        # Pagination logic
        start_idx = (self.current_page - 1) * self.transactions_per_page
        end_idx = start_idx + self.transactions_per_page
        page_transactions = transactions[start_idx:end_idx]

        self.populate_transaction_list(page_transactions)

        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(len(page_transactions) == self.transactions_per_page)
        self.page_label.setText(f"{self.current_page}")

    def populate_transaction_list(self, transactions):
        """Populate the transaction list widget with styled data."""
        self.transaction_list.clear()  # Clear any existing items

        for transaction in transactions:
            # Create a widget for the transaction item
            item_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(10, 5, 10, 5)  # Left, Top, Right, Bottom margins
            layout.setSpacing(10)  # Space between widgets
            item_widget.setLayout(layout)

            # Icon for transaction type
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

            # Create a QListWidgetItem and set the custom widget
            list_item = QListWidgetItem()
            item_widget.setFixedHeight(50)  # Set a fixed height for the row
            list_item.setSizeHint(item_widget.sizeHint())

            list_item.setData(Qt.UserRole, transaction)  # Store transaction data
            self.transaction_list.addItem(list_item)
            self.transaction_list.setItemWidget(list_item, item_widget)

        # Connect item click signal
        self.transaction_list.itemClicked.connect(self.display_transaction_details)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_transactions_for_current_month()

    def next_page(self):
        # Check if there might be more transactions for the current month
        self.current_page += 1
        self.display_transactions_for_current_month()

    def update_month_filter(self, month):
        self.current_month = month
        self.current_page = 1
        self.display_transactions_for_current_month()

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
        self.parent.show_report_view()

    def add_transaction(self):
        """Navigate to the AddTransactionView."""
        self.parent.show_add_transaction_view()
