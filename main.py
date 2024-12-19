from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from views.Transaction_Details_View import TransactionDetailsView
from views.add_transaction_view import AddTransactionView
from views.forget_password_view import ForgotPasswordView
from views.main_page import MainPage
from views.register_view import RegisterView
from views.message_view import MessageView
from views.content_View import ContentView
from views.report_view import ReportView
from views.user_profile_view import UserProfileView
from utils.storage_utils import save_token, load_token, delete_token
from utils.jwt_utils import is_token_valid
from appconfig import TRANSACTION_SERVICE_SUBSCRIPTION_KEY


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setFixedSize(480, 600)

        self.jwt_token = load_token()
        self.user_id = None
        self.username = None
        self.subscription_key = TRANSACTION_SERVICE_SUBSCRIPTION_KEY

        # Initialize QStackedWidget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Initialize views
        self.views = {
            "main_page": MainPage(self),
            "register_view": RegisterView(self),
            "message_view": None,  # Dynamically created
            "forgot_password_view": ForgotPasswordView(self),
            "content_view": ContentView(self),
            "add_transaction_view": AddTransactionView(self),
            "transaction_details_view": None,  # Dynamically created
            "report_view": ReportView(self),
            "user_profile_view": None,  # Dynamically created
        }
        # Add views to QStackedWidget
        for view_name, view_instance in self.views.items():
            if view_instance:
                self.stacked_widget.addWidget(view_instance)

        self.jwt_token = load_token()

        if self.jwt_token:
            print("Clearing any pre-existing tokens...")
            delete_token()
            self.jwt_token = None

        if self.jwt_token and is_token_valid(self.jwt_token):
            self.extract_user_details_from_token()
            self.show_content_view()
        else:
            self.show_main_page()

    def save_jwt_token(self, token):
        print(f"Saving JWT token: {token[:20]}...")
        save_token(token)
        self.jwt_token = token

    def logout_user(self):
        delete_token()
        self.jwt_token = None
        self.show_main_page()

    def switch_to_view(self, view_name):
        """Switch to a specific view."""
        if view_name in self.views:
            view = self.views[view_name]
            if view:
                self.stacked_widget.setCurrentWidget(view)
            else:
                print(f"View '{view_name}' is not initialized.")

    def show_main_page(self):
        if not self.views["main_page"]:
            print("Initializing MainPage...")
            self.views["main_page"] = MainPage(self)
            self.stacked_widget.addWidget(self.views["main_page"])
        self.switch_to_view("main_page")

    def show_register_view(self):
        self.switch_to_view("register_view")

    def show_message_view(self, message):
        if not self.views["message_view"]:
            self.views["message_view"] = MessageView(message, self)
            self.stacked_widget.addWidget(self.views["message_view"])
        self.views["message_view"].set_message(message)  # Assuming set_message updates the displayed message
        self.switch_to_view("message_view")

    def show_forgot_password_view(self):
        self.switch_to_view("forgot_password_view")

    def show_content_view(self):
        if not self.views["content_view"]:
            self.views["content_view"] = ContentView(self, user_id=self.user_id, username=self.username)
            self.stacked_widget.addWidget(self.views["content_view"])
        self.stacked_widget.setCurrentWidget(self.views["content_view"])

    def on_login_result(self, user_id, username, jwt_token):
        print("on_login_result: Initializing ContentView")
        self.user_id = user_id
        self.username = username
        self.jwt_token = jwt_token
        print("=== on_login_result called ===")
        print(f"user_id: {user_id}, username: {username}, jwt_token: {jwt_token[:10]}...")

        if self.views["content_view"] is None:
            print("Creating ContentView...")
            self.views["content_view"] = ContentView(self, user_id=self.user_id, username=self.username)
            self.stacked_widget.addWidget(self.views["content_view"])
            print("ContentView created and added successfully")
        else:
            print("Updating ContentView user info")
            self.views["content_view"].update_user_info(user_id, jwt_token)

        # 切换到 ContentView
        self.show_content_view()

    def show_add_transaction_view(self):
        self.switch_to_view("add_transaction_view")

    def show_transaction_details_view(self, transaction_data):
        if not self.views["transaction_details_view"]:
            self.views["transaction_details_view"] = TransactionDetailsView(self, transaction_data)
            self.stacked_widget.addWidget(self.views["transaction_details_view"])
        else:
            self.views["transaction_details_view"].update_data(transaction_data)  # Assuming update_data refreshes data
        self.switch_to_view("transaction_details_view")

    def show_report_view(self):
        self.switch_to_view("report_view")

    def show_user_profile_view(self):
        if not self.views["user_profile_view"]:
            self.views["user_profile_view"] = UserProfileView(self, user_id=self.user_id, username=self.username)
            self.stacked_widget.addWidget(self.views["user_profile_view"])
        else:
            # 每次重新打开时重置状态
            self.views["user_profile_view"].reset_fields_state()
        self.switch_to_view("user_profile_view")

    # def extract_user_details_from_token(self):
    #     """Extract and store user details from the JWT token."""
    #     # Assuming decode_jwt is a utility function that decodes JWT tokens.
    #     payload = decode_jwt(self.jwt_token)
    #     self.user_id = payload.get("userId")
    #     self.username = payload.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name")


def main():
    app = QApplication([])
    app.setStyleSheet("""
        /* Global styles */
        QMainWindow {
            background: qlineargradient(
                spread: pad,
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #ff9a9e,
                stop: 0.5 #fad0c4,
                stop: 1 #fbc2eb
            );
        }
        QLabel#TitleLabel {
            font-size: 36px;
            font-weight: 700;
            color: #2e2e2e;
            text-align: center;
            letter-spacing: 1.5px;
            font-family: "Poppins", sans-serif;
        }
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
    """)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
