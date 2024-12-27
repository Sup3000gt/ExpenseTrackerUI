
# Expense Tracker Application (Frontend)

## Overview
The **Expense Tracker Application** frontend is a Python-based desktop application built using the PySide6 framework. It provides a user-friendly interface to manage personal finances, including transaction management, reports, and user profile management.

---

## Features

1. **Authentication:**
   - User login and registration.
   - Secure password reset functionality.
   - Token-based session management.

2. **Transaction Management:**
   - Add, edit, and view detailed information about transactions.
   - Categorize transactions as income or expense.
   - Filter transactions by month or category.

3. **Dashboard:**
   - Display an overview of recent transactions.
   - Quick navigation to key application sections (e.g., Profile, Reports).

4. **Reports:**
   - Generate monthly or custom date-range financial reports.
   - Visualize income and expenses with interactive charts.

5. **User Profile:**
   - View and update profile information.
   - Change passwords securely.

6. **User Experience Enhancements:**
   - Responsive and intuitive UI with clear feedback messages.
   - Loading indicators for asynchronous operations.

---

## File Structure

### Main Components
- **`main.py`**: Application entry point. Initializes and manages view transitions.
- **`views` folder**:
  - `add_transaction_view.py`: UI for adding new transactions.
  - `content_view.py`: Dashboard to display transactions and navigation options.
  - `forget_password_view.py`: Password reset functionality.
  - `main_page.py`: Login page.
  - `message_view.py`: Displays messages to the user.
  - `register_view.py`: User registration page.
  - `report_view.py`: Report generation and visualization.
  - `transaction_details_view.py`: Detailed view for a single transaction.
  - `user_profile_view.py`: User profile management.

### Utility Modules
- **`jwt_utils.py`**: Handles JWT validation and decoding.
- **`storage_utils.py`**: Securely manages JWT tokens using the `keyring` library.

### Service Modules
- **`auth_service.py`**: Manages login API calls.
- **`user_service.py`**: Handles user registration API calls.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker/frontend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

---

## Dependencies

- **Python >= 3.8**
- **PySide6**: For GUI components.
- **Requests**: For API communication.
- **Keyring**: For secure storage of sensitive data.
- **PyJWT**: For handling JSON Web Tokens.

---

## Configuration

1. **Environment Variables:**
   Add the following variables to a `.env` file:
   ```env
   USER_BASE_API_URL=<your_api_base_url>
   USER_SERVICE_SUBSCRIPTION_KEY=<your_subscription_key>
   TRANSACTION_SERVICE_SUBSCRIPTION_KEY=<your_transaction_subscription_key>
   ```

2. **Assets:**
   Place your icons and assets (e.g., `user_profile_icon.png`, `left-arrow.png`) in the `assets/` directory.

---

## Usage

1. **Login or Register:**
   Launch the application and log in with your credentials or register as a new user.

2. **Dashboard:**
   Navigate through the dashboard to manage transactions, view reports, and update your profile.

3. **Add Transactions:**
   Use the "Add Transaction" button to record new income or expenses.

4. **Reports:**
   Generate monthly or custom reports to analyze your financial data.

5. **Profile Management:**
   Update personal details or change passwords securely from the profile section.

---

## API Endpoints
The application communicates with backend APIs for authentication, user profile management, transaction operations, and report generation. Ensure the backend service is configured and accessible.

---

## Contribution

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
