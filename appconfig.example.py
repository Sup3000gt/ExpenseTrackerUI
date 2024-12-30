# Base URL for APIs
USER_BASE_API_URL = "https://your-user-service-api.example.com/api"
TRANSACTION_SERVICE_BASE_URL = "https://your-transaction-service-api.example.com/api"
REPORT_SERVICE_BASE_URL = "https://your-report-service-api.example.com/api"

# Subscription Key
USER_SERVICE_SUBSCRIPTION_KEY = "your_user_service_key_here"
TRANSACTION_SERVICE_SUBSCRIPTION_KEY = "your_transaction_service_key_here"

# For Transaction Details
TRANSACTION_DELETE_URL = f"{TRANSACTION_SERVICE_BASE_URL}/Transactions"
TRANSACTION_ADD_URL = f"{TRANSACTION_SERVICE_BASE_URL}/Transactions/add"
TRANSACTION_USER_URL = f"{TRANSACTION_SERVICE_BASE_URL}/Transactions/user/{{user_id}}"

# For Report Service
REPORT_MONTHLY_SUMMARY_URL = f"{REPORT_SERVICE_BASE_URL}/Report/monthly-summary"
REPORT_CUSTOM_RANGE_URL = f"{REPORT_SERVICE_BASE_URL}/Report/custom-date-range"

# For User Profile
USER_PROFILE_URL = f"{USER_BASE_API_URL}/Users/profile"
USER_PASSWORD_CHANGE_URL = f"{USER_BASE_API_URL}/Users/change-password"