from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout, QDialog, QDialogButtonBox, QVBoxLayout
import requests

class TransactionDetailsView(QWidget):
    def __init__(self, parent, transaction_data):
        super().__init__()
        self.parent = parent
        self.transaction_data = transaction_data

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(20)

        # Add the back button at the top-left
        self.add_back_button(main_layout)

        # Create a grid layout for the table-like display
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(40)
        grid_layout.setVerticalSpacing(20)
        main_layout.addLayout(grid_layout)

        # Fonts
        label_font = QFont("Arial", 14, QFont.Bold)
        value_font = QFont("Arial", 14)

        # Format date as YYYY/MM/DD
        raw_date = transaction_data['date']
        if 'T' in raw_date:
            raw_date = raw_date.split('T')[0]
        date_parts = raw_date.split('-')
        if len(date_parts) == 3:
            formatted_date = f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}"
        else:
            formatted_date = raw_date

        # Format the amount with commas (e.g. $8,000)
        amount = float(transaction_data['amount'])
        formatted_amount = f"${amount:,.0f}"  # no decimals if .00

        # Transaction data mapping
        details = [
            ("Transaction ID", str(transaction_data['id'])),
            ("Type", transaction_data['transactionType']),
            ("Amount", formatted_amount),
            ("Date", formatted_date),
            ("Description", transaction_data['description']),
            ("Category", transaction_data['category']),
        ]

        # Add data to the grid (center-aligned)
        row = 0
        for label_text, value_text in details:
            label = QLabel(label_text)
            label.setFont(label_font)
            label.setStyleSheet("color: #333;")
            label.setAlignment(Qt.AlignCenter)

            value = QLabel(value_text)
            value.setFont(value_font)
            value.setStyleSheet("color: #000;")
            value.setAlignment(Qt.AlignCenter)

            if label_text == "Description":
                value.setWordWrap(True)

            grid_layout.addWidget(label, row, 0, alignment=Qt.AlignCenter)
            grid_layout.addWidget(value, row, 1, alignment=Qt.AlignCenter)
            row += 1

        # Add the delete button
        self.add_delete_button(main_layout)

    def add_back_button(self, main_layout):
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
        main_layout.addLayout(back_button_layout)

    def add_delete_button(self, main_layout):
        """Add a delete button with confirmation dialog."""
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
        main_layout.addWidget(delete_button, alignment=Qt.AlignCenter)

    def confirm_delete_transaction(self):
        """Show a modern confirmation dialog before deleting the transaction."""
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
            self.delete_transaction(self.transaction_data['id'])

    def delete_transaction(self, transaction_id):
        """Send a DELETE request to the API to delete the transaction."""
        url = f"https://expensetransactionserviceapi.azure-api.net/api/Transactions/{transaction_id}"
        try:
            response = requests.delete(url)
            if response.status_code == 200:
                self.show_success_dialog("Transaction deleted successfully.")
                self.parent.show_content_view()  # Go back to the previous view
            else:
                self.show_error_dialog(f"Failed to delete transaction: {response.text}")
        except requests.RequestException as e:
            self.show_error_dialog(f"An error occurred: {str(e)}")

    def show_success_dialog(self, message):
        """Show a modern success dialog."""
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
        """Show a modern error dialog."""
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
                color: #333;
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
