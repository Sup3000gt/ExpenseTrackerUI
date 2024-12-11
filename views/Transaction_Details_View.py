from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout

class TransactionDetailsView(QWidget):
    def __init__(self, parent, transaction_data):
        super().__init__()
        self.parent = parent

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
