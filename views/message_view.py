from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

class MessageView(QWidget):
    def __init__(self, message, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)  # Align everything to the center

        # Display the message in the center
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #4CAF50;
                background-color: rgba(255, 255, 255, 0.5); /* 50% transparency */
                padding: 15px;
                border: 1px solid #DDD;
                border-radius: 8px;
            }
        """)
        self.layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        # Add a button at the bottom to return to the main page
        self.return_button = QPushButton("Back to Main Page")
        self.return_button.clicked.connect(self.return_to_main_page)
        self.return_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                color: white;
                background-color: #6C8CD5;  /* Lighter blue */
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5A7BC4;  /* Slightly darker blue */
            }
            QPushButton:pressed {
                background-color: #4C6BA8;  /* Even darker blue */
            }
        """)
        self.layout.addWidget(self.return_button, alignment=Qt.AlignCenter)

    def return_to_main_page(self):
        """Return to the main page."""
        self.parent.show_main_page()
