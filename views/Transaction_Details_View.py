from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class TransactionDetailsView(QWidget):
    def __init__(self, parent, transaction_data):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)

        # Display transaction details
        transaction_id_label = QLabel(f"Transaction ID: {transaction_data['id']}")
        transaction_type_label = QLabel(f"Type: {transaction_data['transactionType']}")
        transaction_amount_label = QLabel(f"Amount: ${transaction_data['amount']}")
        transaction_date_label = QLabel(f"Date: {transaction_data['date']}")
        transaction_description_label = QLabel(f"Description: {transaction_data['description']}")
        transaction_category_label = QLabel(f"Category: {transaction_data['category']}")
        transaction_created_at_label = QLabel(f"Created At: {transaction_data['createdAt']}")

        self.layout.addWidget(transaction_id_label)
        self.layout.addWidget(transaction_type_label)
        self.layout.addWidget(transaction_amount_label)
        self.layout.addWidget(transaction_date_label)
        self.layout.addWidget(transaction_description_label)
        self.layout.addWidget(transaction_category_label)
        self.layout.addWidget(transaction_created_at_label)

        # Add a back button to return to the content view
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.show_content_view)
        self.layout.addWidget(back_button, alignment=Qt.AlignRight)


# Modify the display_transaction_details method in the ContentView class
def display_transaction_details(self, item):
    """Display detailed info for a selected transaction."""
    transaction = item.data(Qt.UserRole)  # Retrieve the full transaction data
    self.parent.show_transaction_details_view(transaction)

# Add a new method in the MainWindow class to show the transaction details view
def show_transaction_details_view(self, transaction_data):
    """Show the transaction details view."""
    self.transaction_details_view = TransactionDetailsView(self, transaction_data)
    self.setCentralWidget(self.transaction_details_view)

# Add a new method in the MainWindow class to show the content view
def show_content_view(self):
    """Show the content view."""
    self.setCentralWidget(self.content_view)