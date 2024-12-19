import logging
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
import logging_config

# Initialize centralized logging
logging_config.setup_logging()
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setFixedSize(480, 600)

        self.jwt_token = load_token()
        self.user_id = None
        self.username = None
        self.subscription_key = TRANSACTION_SERVICE_SUBSCRIPTION_KEY

        # Initialize QStackedWidget for managing multiple views
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Initialize views dictionary with pre-initialized and dynamically created views
        self.views = {
            "main_page": MainPage(self),
            "register_view": RegisterView(self),
            "message_view": None,  # To be created dynamically when needed
            "forgot_password_view": ForgotPasswordView(self),
            "content_view": ContentView(self),
            "add_transaction_view": AddTransactionView(self),
            "transaction_details_view": None,
            "report_view": ReportView(self),
            "user_profile_view": None,
        }
        logger.debug("Initializing and adding pre-initialized views to the stacked widget.")
        # Add pre-initialized views to the stacked widget
        for view_name, view_instance in self.views.items():
            if view_instance:
                self.stacked_widget.addWidget(view_instance)
                logger.debug(f"Added view '{view_name}' to the stacked widget.")

        self.jwt_token = load_token()

        if self.jwt_token:
            logger.info("Clearing any pre-existing tokens...")
            delete_token()
            self.jwt_token = None
            logger.debug("Pre-existing token cleared.")

        if self.jwt_token and is_token_valid(self.jwt_token):
            logger.info("JWT token is valid. Extracting user details and showing content view.")
            self.extract_user_details_from_token()
            self.show_content_view()
        else:
            logger.info("JWT token is invalid or not present. Showing main page.")
            self.show_main_page()

    def save_jwt_token(self, token):
        logger.info("Saving JWT token.")
        save_token(token)
        self.jwt_token = token
        logger.debug(f"JWT token saved: {token[:20]}...")

    def logout_user(self):
        logger.info("Logging out user by deleting token.")
        delete_token()
        self.jwt_token = None
        self.show_main_page()

    def switch_to_view(self, view_name):
        """Switch to a specific view and connect signals dynamically."""
        logger.debug(f"Attempting to switch to view '{view_name}'.")
        if view_name in self.views:
            view = self.views[view_name]
            if view:
                # Dynamically connect signals for specific views
                if view_name == "add_transaction_view" and isinstance(view, AddTransactionView):
                    logger.debug("Connecting 'transaction_added' signal to 'fetch_all_transactions'.")
                    view.transaction_added.connect(self.views["content_view"].fetch_all_transactions)

                self.stacked_widget.setCurrentWidget(view)
                logger.info(f"Switched to view '{view_name}'.")
            else:
                logger.warning(f"View '{view_name}' is not initialized.")
        else:
            logger.error(f"View '{view_name}' does not exist.")

    def show_main_page(self):
        """Display the main page view."""
        logger.debug("Displaying the main page.")
        if not self.views["main_page"]:
            logger.info("Initializing MainPage view.")
            self.views["main_page"] = MainPage(self)
            self.stacked_widget.addWidget(self.views["main_page"])
            logger.debug("MainPage view initialized and added to the stacked widget.")
        self.switch_to_view("main_page")

    def show_register_view(self):
        """Display the registration view."""
        logger.debug("Displaying the register view.")
        self.switch_to_view("register_view")

    def show_message_view(self, message):
        """Display a message to the user."""
        logger.debug("Displaying the message view.")
        if not self.views["message_view"]:
            logger.info("Initializing MessageView.")
            self.views["message_view"] = MessageView(message, self)
            self.stacked_widget.addWidget(self.views["message_view"])
            logger.debug("MessageView initialized and added to the stacked widget.")
        self.views["message_view"].set_message(message)
        logger.debug("Message updated in MessageView.")
        self.switch_to_view("message_view")

    def show_forgot_password_view(self):
        """Display the forgot password view."""
        logger.debug("Displaying the forgot password view.")
        self.switch_to_view("forgot_password_view")

    def show_content_view(self):
        """Display the content view with user-specific information."""
        logger.debug("Displaying the content view.")
        if not self.views["content_view"]:
            logger.info("Initializing ContentView with user details.")
            self.views["content_view"] = ContentView(self, user_id=self.user_id, username=self.username)
            self.stacked_widget.addWidget(self.views["content_view"])
            logger.debug("ContentView initialized and added to the stacked widget.")
        self.stacked_widget.setCurrentWidget(self.views["content_view"])
        logger.info("Switched to content view.")

    def on_login_result(self, user_id, username, jwt_token):
        """Handle the result of a user login."""
        logger.info("Handling login result.")
        self.user_id = user_id
        self.username = username
        self.jwt_token = jwt_token
        logger.debug(f"User ID: {user_id}, Username: {username}, JWT Token: {jwt_token[:10]}...")

        if self.views["content_view"] is None:
            logger.info("Creating ContentView after login.")
            self.views["content_view"] = ContentView(self, user_id=self.user_id, username=self.username)
            self.stacked_widget.addWidget(self.views["content_view"])
            logger.debug("ContentView created and added successfully.")
        else:
            logger.info("Updating existing ContentView with new user info.")
            self.views["content_view"].update_user_info(user_id, jwt_token)
            logger.debug("ContentView user info updated.")

        # Switch to ContentView
        self.show_content_view()

    def show_add_transaction_view(self):
        """Display the add transaction view."""
        logger.debug("Displaying the add transaction view.")
        self.switch_to_view("add_transaction_view")

    def show_transaction_details_view(self, transaction_data):
        """Display details of a specific transaction."""
        logger.debug("Displaying the transaction details view.")
        if not self.views["transaction_details_view"]:
            logger.info("Initializing TransactionDetailsView.")
            self.views["transaction_details_view"] = TransactionDetailsView(self, transaction_data)
            self.views["transaction_details_view"].transaction_deleted.connect(
                self.views["content_view"].fetch_all_transactions
            )
            self.stacked_widget.addWidget(self.views["transaction_details_view"])
            logger.debug("TransactionDetailsView initialized and added to the stacked widget.")
        else:
            logger.info("Updating existing TransactionDetailsView with new data.")
            self.views["transaction_details_view"].update_data(transaction_data)
            logger.debug("TransactionDetailsView data updated.")

        self.switch_to_view("transaction_details_view")

    def show_report_view(self):
        """Display the report view."""
        logger.debug("Displaying the report view.")
        self.switch_to_view("report_view")

    def show_user_profile_view(self):
        """Display the user profile view."""
        logger.debug("Displaying the user profile view.")
        if not self.views["user_profile_view"]:
            logger.info("Initializing UserProfileView.")
            self.views["user_profile_view"] = UserProfileView(self, user_id=self.user_id, username=self.username)
            self.stacked_widget.addWidget(self.views["user_profile_view"])
            logger.debug("UserProfileView initialized and added to the stacked widget.")
        else:
            # Reset fields state each time the view is reopened
            logger.info("Resetting UserProfileView fields.")
            self.views["user_profile_view"].reset_fields_state()
            logger.debug("UserProfileView fields reset.")
        self.switch_to_view("user_profile_view")

def main():
    logger.info("Starting the Expense Tracker application.")
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
    logger.info("Application window displayed.")
    app.exec()
    logger.info("Expense Tracker application has exited.")


if __name__ == "__main__":
    main()
