from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                               QDialog, QDialogButtonBox, QFormLayout, QComboBox, QTextEdit)
from PySide6.QtCore import Qt, QDate
import requests
import locale
import calendar
import json


class ReportView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Generate Reports")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 600;
            }
        """)
        self.layout.addWidget(self.title_label)

        # Buttons for monthly report and custom report with updated names and style
        buttons_layout = QHBoxLayout()

        self.monthly_report_button = QPushButton("Monthly Summary")
        self.monthly_report_button.clicked.connect(self.generate_monthly_report)
        self.monthly_report_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(self.monthly_report_button)

        self.custom_report_button = QPushButton("Custom Summary")
        self.custom_report_button.clicked.connect(self.generate_custom_report)
        self.custom_report_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        buttons_layout.addWidget(self.custom_report_button)

        self.layout.addLayout(buttons_layout)

        # A text area to display the report results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.layout.addWidget(self.results_text)

    def generate_monthly_report(self):
        # Show a dialog to pick year and month
        dialog = MonthlyReportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            year, month = dialog.get_year_month()
            self.fetch_monthly_report(year, month)

    def generate_custom_report(self):
        # Show a dialog to pick start and end dates from combo boxes
        dialog = CustomReportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            start_date, end_date = dialog.get_date_range()
            self.fetch_custom_report(start_date, end_date)

    def fetch_monthly_report(self, year, month):
        """Fetch monthly summary report from the API."""
        api_url = "https://personalexpensetrackerreportserviceapi.azure-api.net/api/Report/monthly-summary"

        headers = {
            "Authorization": f"Bearer {self.parent.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        params = {
            "userId": self.parent.user_id,
            "year": year,
            "month": month
        }

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                report_data = response.json()
                self.display_report_data(report_data)
            else:
                self.results_text.setText(f"Error fetching monthly report: {response.status_code}\n{response.text}")
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")

    def fetch_custom_report(self, start_date, end_date):
        """Fetch custom date range report from the API."""
        api_url = "https://personalexpensetrackerreportserviceapi.azure-api.net/api/Report/custom-date-range"

        headers = {
            "Authorization": f"Bearer {self.parent.jwt_token}",
            "Ocp-Apim-Subscription-Key": self.parent.subscription_key
        }
        params = {
            "userId": self.parent.user_id,
            "startDate": start_date.toString("yyyy-MM-dd"),
            "endDate": end_date.toString("yyyy-MM-dd")
        }

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                report_data = response.json()
                self.display_report_data(report_data)
            else:
                self.results_text.setText(f"Error fetching custom report: {response.status_code}\n{response.text}")
        except Exception as e:
            self.results_text.setText(f"Error: {str(e)}")

    def display_report_data(self, data):
        """Display the returned JSON data in the text area."""
        formatted_data = json.dumps(data, indent=4)
        self.results_text.setText(formatted_data)


class MonthlyReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Month and Year")

        self.year_combo = QComboBox()
        self.month_combo = QComboBox()

        current_year = QDate.currentDate().year()
        for y in range(current_year - 5, current_year + 6):
            self.year_combo.addItem(str(y), y)

        # English month names
        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        for i, m in enumerate(month_names, start=1):
            self.month_combo.addItem(m, i)

        # Set current month and year as default
        self.year_combo.setCurrentIndex(5)  # This will roughly point to current year in the combo (since we added ±5)
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)

        form_layout = QFormLayout()
        form_layout.addRow("Year:", self.year_combo)
        form_layout.addRow("Month:", self.month_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_year_month(self):
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        return year, month


class CustomReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Start and End Dates")

        self.start_year_combo = QComboBox()
        self.start_month_combo = QComboBox()
        self.start_day_combo = QComboBox()

        self.end_year_combo = QComboBox()
        self.end_month_combo = QComboBox()
        self.end_day_combo = QComboBox()

        # Populate year and month combos
        current_year = QDate.currentDate().year()
        for y in range(current_year - 5, current_year + 6):
            self.start_year_combo.addItem(str(y), y)
            self.end_year_combo.addItem(str(y), y)

        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        for i, m in enumerate(month_names, start=1):
            self.start_month_combo.addItem(m, i)
            self.end_month_combo.addItem(m, i)

        # Connect signals to update day combos when year or month changes
        self.start_year_combo.currentIndexChanged.connect(self.update_start_days)
        self.start_month_combo.currentIndexChanged.connect(self.update_start_days)
        self.end_year_combo.currentIndexChanged.connect(self.update_end_days)
        self.end_month_combo.currentIndexChanged.connect(self.update_end_days)

        # Set default values to current date for end and one month before for start
        # For simplicity, start date: previous month, same day if possible
        today = QDate.currentDate()
        start_date = today.addMonths(-1)

        # Set defaults
        self.set_combo_to_value(self.start_year_combo, start_date.year())
        self.set_combo_to_value(self.start_month_combo, start_date.month())
        self.set_combo_to_value(self.end_year_combo, today.year())
        self.set_combo_to_value(self.end_month_combo, today.month())

        self.update_start_days()
        self.set_combo_to_value(self.start_day_combo, start_date.day())

        self.update_end_days()
        self.set_combo_to_value(self.end_day_combo, today.day())

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Start Year:", self.start_year_combo)
        form_layout.addRow("Start Month:", self.start_month_combo)
        form_layout.addRow("Start Day:", self.start_day_combo)

        form_layout.addRow("End Year:", self.end_year_combo)
        form_layout.addRow("End Month:", self.end_month_combo)
        form_layout.addRow("End Day:", self.end_day_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def set_combo_to_value(self, combo, value):
        # Finds the combo box index for given data and sets it
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break

    def update_start_days(self):
        year = self.start_year_combo.currentData()
        month = self.start_month_combo.currentData()
        self.populate_days(self.start_day_combo, year, month)

    def update_end_days(self):
        year = self.end_year_combo.currentData()
        month = self.end_month_combo.currentData()
        self.populate_days(self.end_day_combo, year, month)

    def populate_days(self, day_combo, year, month):
        day_combo.clear()
        # Get number of days in the given month and year
        num_days = calendar.monthrange(year, month)[1]
        for d in range(1, num_days + 1):
            day_combo.addItem(str(d), d)

    def get_date_range(self):
        # Construct QDates from combo values
        start_year = self.start_year_combo.currentData()
        start_month = self.start_month_combo.currentData()
        start_day = self.start_day_combo.currentData()

        end_year = self.end_year_combo.currentData()
        end_month = self.end_month_combo.currentData()
        end_day = self.end_day_combo.currentData()

        start_date = QDate(start_year, start_month, start_day)
        end_date = QDate(end_year, end_month, end_day)

        return start_date, end_date
