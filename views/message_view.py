import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


class MessageView(QWidget):
    """View to display messages to the user."""

    def __init__(self, message, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setAlignment(Qt.AlignCenter)

        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #4CAF50;
                background-color: rgba(255, 255, 255, 0.5);
                padding: 15px;
                border: 1px solid #DDD;
                border-radius: 8px;
            }
        """)
        self.layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.return_button = QPushButton("Back to Main Page")
        self.return_button.clicked.connect(self.return_to_main_page)
        self.return_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                color: white;
                background-color: #6C8CD5;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5A7BC4;
            }
            QPushButton:pressed {
                background-color: #4C6BA8;
            }
        """)
        self.layout.addWidget(self.return_button, alignment=Qt.AlignCenter)

    def set_message(self, message):
        """Update the displayed message."""
        logger.debug("Updating message to the user.")
        self.message_label.setText(message)

    def return_to_main_page(self):
        """Return to the main page."""
        logger.info("User requested to return to the main page.")
        self.parent.show_main_page()
