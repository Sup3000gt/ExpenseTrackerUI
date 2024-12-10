from PySide6.QtWidgets import QApplication, QMainWindow
from views.main_page import MainPage
from views.login_view import LoginView
from views.register_view import RegisterView
from views.message_view import MessageView
from utils.storage_utils import save_token, load_token, delete_token
from utils.jwt_utils import is_token_valid

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.jwt_token = load_token()  # Load token from keyring
        self.setFixedSize(480, 600)

        if self.jwt_token and is_token_valid(self.jwt_token):
            self.show_message_view("Welcome back!")
        else:
            self.show_main_page()

    def save_jwt_token(self, token):
        """Save the JWT token securely."""
        save_token(token)
        self.jwt_token = token

    def logout_user(self):
        """Handle user logout."""
        delete_token()  # Delete the JWT token from keyring
        self.jwt_token = None
        self.show_main_page()


    def show_main_page(self):
        self.main_page = MainPage(self)
        self.setCentralWidget(self.main_page)

    def show_login_view(self):
        self.login_view = LoginView(self)
        self.setCentralWidget(self.login_view)

    def show_register_view(self):
        self.register_view = RegisterView(self)
        self.setCentralWidget(self.register_view)

    def show_message_view(self, message):
        """Display a message view."""
        self.message_view = MessageView(message, self)
        self.setCentralWidget(self.message_view)


def main():
    app = QApplication([])
    # Set global styles
    app.setStyleSheet("""
        /* Gradient Background */
        QMainWindow {
            background: qlineargradient(
                spread: pad,
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #ff9a9e,
                stop: 0.5 #fad0c4,
                stop: 1 #fbc2eb
            );
        }

        /* Modern Title Styling */
        QLabel#TitleLabel {
            font-size: 36px;
            font-weight: 700;
            color: #2e2e2e;
            text-align: center;
            letter-spacing: 1.5px;
            font-family: "Poppins", sans-serif;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }
        QLabel#TitleLabel:hover {
            color: #555;
        }

        /* Input Fields Styling */
        QLineEdit {
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
            background-color: #fff;
        }
        QLineEdit:focus {
            border: 2px solid #6c63ff;
        }

        /* Buttons Styling */
        QPushButton {
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
            color: white;
        }
        QPushButton#LoginButton {
            background-color: #5cb85c;
        }
        QPushButton#LoginButton:hover {
            background-color: #4cae4c;
        }
        QPushButton#RegisterButton {
            background-color: #0275d8;
        }
        QPushButton#RegisterButton:hover {
            background-color: #025aa5;
        }
        QPushButton#ForgotPasswordButton {
            background-color: #f0ad4e;
        }
        QPushButton#ForgotPasswordButton:hover {
            background-color: #ec971f;
        }
    """)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
