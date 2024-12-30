# Base URL for APIs
USER_BASE_API_URL = "https://expenseuserserviceapi.azure-api.net/api"
TRANSACTION_SERVICE_BASE_URL = "https://expensetransactionserviceapi.azure-api.net/api"
REPORT_SERVICE_BASE_URL = "https://personalexpensetrackerreportserviceapi.azure-api.net/api"

# Subscription Key
USER_SERVICE_SUBSCRIPTION_KEY = "49630d64dd954e64b06992eade60a44e"
TRANSACTION_SERVICE_SUBSCRIPTION_KEY = "dcd9d662530e43f788e434b6678274a7"

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