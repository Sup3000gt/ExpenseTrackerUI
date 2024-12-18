from PySide6.QtWidgets import QApplication, QMainWindow
from views.Transaction_Details_View import TransactionDetailsView
from views.add_transaction_view import AddTransactionView
from views.forget_password_view import ForgotPasswordView
from views.main_page import MainPage
from views.login_view import LoginView
from views.register_view import RegisterView
from views.message_view import MessageView
from utils.storage_utils import save_token, load_token, delete_token
from utils.jwt_utils import is_token_valid
from views.content_View import ContentView
from appconfig import TRANSACTION_SERVICE_SUBSCRIPTION_KEY
from views.report_view import ReportView
from views.user_profile_view import UserProfileView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.jwt_token = load_token()  # Load token from keyring
        self.user_id = None
        self.username = None
        self.subscription_key = TRANSACTION_SERVICE_SUBSCRIPTION_KEY
        self.setFixedSize(480, 600)

        self.main_page = MainPage(self)

        if self.jwt_token and is_token_valid(self.jwt_token):
            self.show_main_page()

    def save_jwt_token(self, token):
        save_token(token)
        self.jwt_token = token

    def logout_user(self):
        """Handle user logout."""
        delete_token()  # Delete the JWT token from keyring
        self.jwt_token = None
        self.show_main_page()

    def show_add_transaction_view(self):
        """Show the AddTransactionView."""
        self.add_transaction_view = AddTransactionView(self)
        self.setCentralWidget(self.add_transaction_view)

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

    def show_forgot_password_view(self):
        self.setCentralWidget(ForgotPasswordView(self))

    def show_content_view(self):
        self.setCentralWidget(ContentView(self))

    def show_transaction_details_view(self, transaction_data):
        """Show the transaction details view."""
        self.transaction_details_view = TransactionDetailsView(self, transaction_data)
        self.setCentralWidget(self.transaction_details_view)

    def show_user_profile_view(self):
        self.setCentralWidget(UserProfileView(self))

    def show_report_view(self):
        self.report_view = ReportView(self)
        self.setCentralWidget(self.report_view)

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