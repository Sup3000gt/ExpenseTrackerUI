from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

class MessageView(QWidget):
    def __init__(self, message, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Optional margins for better spacing
        self.layout.setAlignment(Qt.AlignCenter)  # Center the content overall

        # Spacer above the label to push it down when needed
        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Centered label
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

        # Spacer below the label to push the button down
        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Button stuck to the bottom
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

    def set_message(self, message):
        """Update the displayed message."""
        self.message_label.setText(message)

    def return_to_main_page(self):
        """Return to the main page."""
        self.parent.show_main_page()
