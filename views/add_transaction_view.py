import logging
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QDateEdit, \
    QMessageBox, QTextEdit, QDialog
from PySide6.QtCore import Qt, QDate, QLocale, Signal


logger = logging.getLogger(__name__)


class AddTransactionView(QWidget):
    transaction_added = Signal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel("Add New Transaction")
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

        # Transaction Type
        self.type_label = QLabel("Transaction Type:")
        self.type_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.type_label)

        self.type_combobox = QComboBox()
        self.type_combobox.addItems(["Income", "Expense"])
        self.type_combobox.setStyleSheet("padding: 5px; font-size: 14px;")
        self.type_combobox.currentTextChanged.connect(self.update_category_options)
        self.layout.addWidget(self.type_combobox)

        # Category
        self.category_label = QLabel("Category:")
        self.category_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.category_label)

        self.category_combobox = QComboBox()
        self.category_combobox.setStyleSheet("padding: 5px; font-size: 14px;")
        self.layout.addWidget(self.category_combobox)

        self.update_category_options(self.type_combobox.currentText())

        # Amount
        self.amount_label = QLabel("Amount:")
        self.amount_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.amount_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.amount_input.setStyleSheet("padding: 5px; font-size: 14px;")
        self.layout.addWidget(self.amount_input)

        # Date
        self.date_label = QLabel("Date:")
        self.date_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.date_label)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #ccc;
            }
        """)
        self.date_input.setLocale(QLocale(QLocale.English))
        self.layout.addWidget(self.date_input)

        # Description
        self.description_label = QLabel("Description:")
        self.description_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.description_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter description")
        self.description_input.setStyleSheet("padding: 5px; font-size: 14px;")
        self.description_input.setFixedHeight(100)
        self.layout.addWidget(self.description_input)

        # Buttons
        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Transaction")
        self.add_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: green;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #28a745;
            }
        """)
        self.add_button.clicked.connect(self.add_transaction)
        self.buttons_layout.addWidget(self.add_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: red;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #dc3545;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel)
        self.buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.buttons_layout)

    def update_category_options(self, transaction_type):
        """Update category options based on the selected transaction type."""
        self.category_combobox.clear()
        if transaction_type == "Income":
            categories = ["Salary", "Interest", "Capital Gains", "Refunds", "Other Income"]
        else:  # Expense
            categories = [
                "Housing", "Transportation", "Food", "Health", "Fitness", "Entertainment",
                "Education", "Personal Care", "Debt Payment", "Saving", "Insurance", "Travel", "Miscellaneous"
            ]
        self.category_combobox.addItems(categories)

    def add_transaction(self):
        """Send the transaction data to the API and handle the response."""
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            logger.warning("Invalid amount entered.")
            return

        transaction_data = {
            "userId": self.parent.user_id,
            "transactionType": self.type_combobox.currentText(),
            "amount": amount,
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "description": self.description_input.toPlainText(),
            "category": self.category_combobox.currentText()
        }

        api_url = "https://expensetransactionserviceapi.azure-api.net/api/Transactions/add"
        headers = {
            "Authorization": f"Bearer {self.parent.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }

        logger.debug(f"Sending transaction data to {api_url}: {transaction_data}")

        try:
            response = requests.post(api_url, json=transaction_data, headers=headers)
            if response.status_code == 200:
                logger.info("Transaction added successfully.")
                self.show_success_message()
                self.transaction_added.emit()
                self.parent.show_content_view()
            else:
                logger.warning(f"Failed to add transaction: {response.status_code} - {response.text}")
                QMessageBox.warning(self, "Error", f"Failed to add transaction: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while adding transaction: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def show_success_message(self):
        """Display a success message dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Success")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f4f4f4;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 14px;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        message_label = QLabel("Transaction added successfully!")
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)

        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 40)
        ok_button.clicked.connect(dialog.accept)
        ok_button.setStyleSheet("""
             QPushButton {
                 background-color: #28a745;
                 color: white;
                 font-size: 14px;
                 padding: 6px 12px;
                 border-radius: 4px;
             }
             QPushButton:hover {
                 background-color: #218838;
             }
         """)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        logger.debug("Displaying success message dialog.")
        dialog.setLayout(layout)
        dialog.exec()

    def cancel(self):
        """Handle the cancel action and redirect to the content view."""
        logger.info("Cancel action triggered. Redirecting to content view.")
        self.parent.show_content_view()
