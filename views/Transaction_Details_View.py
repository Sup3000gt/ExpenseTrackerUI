import os
import logging
import requests
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QDialog,
    QDialogButtonBox, QHBoxLayout, QSizePolicy,
    QScrollArea, QGridLayout, QWidget
)

logger = logging.getLogger(__name__)


class TransactionDetailsView(QWidget):
    """View to display detailed information about a single transaction."""

    transaction_deleted = Signal(int)  # Signal emitted when a transaction is deleted

    def __init__(self, parent, transaction_data):
        super().__init__()
        self.parent = parent
        self.transaction_data = transaction_data
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface components."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(40)

        self.add_back_button()

        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(20)
        self.grid_layout.setVerticalSpacing(20)
        self.main_layout.addLayout(self.grid_layout)

        self.label_font = QFont("Arial", 14, QFont.Bold)
        self.value_font = QFont("Arial", 14)

        self.create_ui_elements()
        self.add_delete_button()

    def create_ui_elements(self):
        """Create and arrange the transaction detail labels and values."""
        raw_date = self.transaction_data.get('date', '')
        formatted_date = self.format_date(raw_date)

        formatted_amount = self.format_amount(self.transaction_data.get('amount', 0))

        details = [
            ("Transaction ID", str(self.transaction_data.get('id', 'N/A'))),
            ("Type", self.transaction_data.get('transactionType', 'N/A')),
            ("Amount", formatted_amount),
            ("Date", formatted_date),
            ("Category", self.transaction_data.get('category', 'N/A')),
            ("Description", self.transaction_data.get('description', 'N/A')),
        ]

        self.widgets = {}
        for row, (label_text, value_text) in enumerate(details):
            label = QLabel(label_text)
            label.setFont(self.label_font)
            label.setStyleSheet("color: #333; background: transparent;")
            label.setAlignment(Qt.AlignCenter)

            if label_text == "Description":
                description_label = QLabel(value_text)
                description_label.setFont(self.value_font)
                description_label.setStyleSheet("color: #000; background: transparent; padding: 10px;")
                description_label.setWordWrap(True)

                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setWidget(description_label)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                scroll_area.setFrameShape(QScrollArea.NoFrame)
                scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
                scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                scroll_area.setFixedHeight(100)

                value_widget = scroll_area
            else:
                value = QLabel(value_text)
                value.setFont(self.value_font)
                value.setStyleSheet("color: #000; background: transparent;")
                value.setAlignment(Qt.AlignCenter)
                value_widget = value

            self.widgets[label_text] = value_widget
            self.grid_layout.addWidget(label, row, 0)
            self.grid_layout.addWidget(value_widget, row, 1)

        for i in range(len(details)):
            self.grid_layout.setRowStretch(i, 0)

    def add_back_button(self):
        """Add a back button to navigate to the content view."""
        back_button = QPushButton()
        back_button.setIcon(QIcon(os.path.join("assets", "left-arrow.png")))
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
        self.main_layout.addLayout(back_button_layout)

    def add_delete_button(self):
        """Add a button to delete the current transaction."""
        delete_button = QPushButton("Delete Transaction")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e60000;
            }
        """)
        delete_button.clicked.connect(self.confirm_delete_transaction)
        self.main_layout.addWidget(delete_button, alignment=Qt.AlignCenter)

    def confirm_delete_transaction(self):
        """Display a confirmation dialog before deleting the transaction."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Confirmation")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fefefe;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                font-size: 14px;
                color: white;
                background-color: #007bff;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        layout = QVBoxLayout(dialog)
        label = QLabel("Are you sure you want to delete this transaction?")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Yes).setText("Yes")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancel")
        buttons.button(QDialogButtonBox.Yes).setStyleSheet("background-color: #007bff; color: white;")
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet("background-color: #f44336; color: white;")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            self.delete_transaction(self.transaction_data.get('id'))

    def delete_transaction(self, transaction_id):
        """Send a DELETE request to remove the transaction."""
        url = f"https://expensetransactionserviceapi.azure-api.net/api/Transactions/{transaction_id}"
        headers = {
            "Authorization": f"Bearer {self.parent.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                self.show_success_dialog("Transaction deleted successfully.")
                self.transaction_deleted.emit(transaction_id)
                self.parent.show_content_view()
            else:
                self.show_error_dialog(f"Failed to delete transaction: {response.text}")
        except requests.RequestException as e:
            self.show_error_dialog(f"An error occurred: {str(e)}")

    def show_success_dialog(self, message):
        """Display a success message to the user."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Success")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fefefe;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #4caf50;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        layout = QVBoxLayout(dialog)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        dialog.exec()

    def show_error_dialog(self, message):
        """Display an error message to the user."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Error")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fefefe;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
                color: #d9534f;
            }
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)

        layout = QVBoxLayout(dialog)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        dialog.exec()

    def update_data(self, new_transaction_data):
        """
        Update the transaction data and refresh the UI elements.

        Args:
            new_transaction_data (dict): The updated transaction information.
        """
        logger.debug("Updating transaction data.")
        self.transaction_data = new_transaction_data

        formatted_date = self.format_date(self.transaction_data.get('date', ''))
        formatted_amount = self.format_amount(self.transaction_data.get('amount', 0))

        updated_values = {
            "Transaction ID": str(self.transaction_data.get('id', 'N/A')),
            "Type": self.transaction_data.get('transactionType', 'N/A'),
            "Amount": formatted_amount,
            "Date": formatted_date,
            "Category": self.transaction_data.get('category', 'N/A'),
            "Description": self.transaction_data.get('description', 'N/A'),
        }

        for label_text, new_value in updated_values.items():
            widget = self.widgets.get(label_text)
            if isinstance(widget, QScrollArea):
                inner_label = widget.widget()
                inner_label.setText(new_value)
                logger.debug(f"Updated Description: {new_value}")
            elif isinstance(widget, QLabel):
                widget.setText(new_value)
                logger.debug(f"Updated {label_text}: {new_value}")

    def format_date(self, raw_date):
        """Format the raw date string to YYYY/MM/DD."""
        if 'T' in raw_date:
            raw_date = raw_date.split('T')[0]
        date_parts = raw_date.split('-')
        if len(date_parts) == 3:
            return f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}"
        return raw_date

    def format_amount(self, amount):
        """Format the amount with commas and a dollar sign."""
        try:
            amount = float(amount)
            return f"${amount:,.0f}"
        except (ValueError, TypeError):
            logger.warning("Invalid amount format encountered.")
            return 'N/A'
