import logging
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                               QDialog, QDialogButtonBox, QFormLayout, QComboBox, QTextEdit)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtCharts import QChart, QChartView, QLegend, QBarCategoryAxis, QBarSeries, QBarSet, QValueAxis
from PySide6.QtGui import QPainter, QColor, QFont, QIcon
import calendar

logger = logging.getLogger(__name__)


class ReportView(QWidget):
    """View for generating and displaying reports."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.add_back_button(self.layout)
        self.layout.addStretch()

        self.title_label = QLabel("Generate Reports")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-family: 'Comic Sans MS', sans-serif;
                font-weight: 600;
                color: #222;
                margin-bottom: 10px;
            }
        """)
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        buttons_layout = QVBoxLayout()

        self.monthly_report_button = QPushButton("Monthly")
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
        buttons_layout.addWidget(self.monthly_report_button, alignment=Qt.AlignCenter)

        self.custom_report_button = QPushButton("Custom Range")
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
        buttons_layout.addWidget(self.custom_report_button, alignment=Qt.AlignCenter)

        self.layout.addLayout(buttons_layout)
        self.layout.addStretch()

        self.chart_selector = QComboBox()
        self.chart_selector.setVisible(False)
        self.layout.addWidget(self.chart_selector)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setVisible(False)
        self.layout.addWidget(self.chart_view)

        self.text_report = QTextEdit()
        self.text_report.setVisible(False)
        self.text_report.setReadOnly(True)
        self.text_report.setMinimumHeight(400)
        self.text_report.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.text_report)

        self.monthly_diff_label = QLabel()
        self.monthly_diff_label.setAlignment(Qt.AlignCenter)
        self.monthly_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #000;")
        self.monthly_diff_label.setVisible(False)
        self.layout.addWidget(self.monthly_diff_label)

        self.category_chart = None
        self.type_chart = None
        self.monthly_chart = None
        self.income_chart = None
        self.expense_chart = None
        self.all_categories_text = None

    def add_back_button(self, main_layout):
        """Add a back button to return to the content view."""
        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/left-arrow.png"))
        back_button.setIconSize(QSize(30, 30))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 12px;
            }
        """)
        back_button.clicked.connect(self.parent.show_content_view)

        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(back_button)
        back_button_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(back_button_layout)

    def generate_monthly_report(self):
        """Open dialog to select month and year for the monthly report."""
        dialog = MonthlyReportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            year, month = dialog.get_year_month()
            self.fetch_monthly_report(year, month)

    def generate_custom_report(self):
        """Open dialog to select date range for the custom report."""
        dialog = CustomReportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            start_date, end_date = dialog.get_date_range()
            self.fetch_custom_report(start_date, end_date)

    def fetch_monthly_report(self, year, month):
        """Fetch and display the monthly report data."""
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

        logger.debug(f"Fetching monthly report for user_id={self.parent.user_id}, year={year}, month={month}")
        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                report_data = response.json()
                self.display_report_data(report_data, report_type="monthly")
            else:
                self.show_error(f"Error fetching monthly report: {response.status_code}\n{response.text}")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def fetch_custom_report(self, start_date, end_date):
        """Fetch and display the custom date range report data."""
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

        logger.debug(f"Fetching custom report from {start_date.toString('yyyy-MM-dd')} to {end_date.toString('yyyy-MM-dd')}")
        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                report_data = response.json()
                self.display_report_data(report_data, report_type="custom")
            else:
                self.show_error(f"Error fetching custom report: {response.status_code}\n{response.text}")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        """Display an error message to the user."""
        self.chart_view.setVisible(False)
        self.chart_selector.setVisible(False)
        self.text_report.setVisible(False)
        self.monthly_diff_label.setVisible(False)

        error_label = QLabel(message)
        error_label.setStyleSheet("color: red; font-weight: bold;")
        error_label.setAlignment(Qt.AlignCenter)

        # Clear previous non-essential widgets
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if w and w not in [self.title_label, self.monthly_report_button, self.custom_report_button,
                                   self.chart_selector, self.chart_view, self.text_report, self.monthly_diff_label]:
                    w.setParent(None)

        self.layout.addWidget(error_label)

    def display_report_data(self, data, report_type="custom"):
        """Process and display the fetched report data."""
        self.clear_charts()

        if report_type == "monthly":
            income_total = 0.0
            expense_total = 0.0

            for item in data:
                ttype = item.get("transactionType", "Unknown")
                amt = item.get("totalAmount", 0.0)
                if ttype.lower() == "income":
                    income_total = amt
                else:
                    expense_total = amt

            difference = income_total - expense_total

            bar_set = QBarSet("Amounts")
            bar_set.append([income_total, expense_total])
            bar_set.setColor(QColor("#2196F3"))

            series_bar = QBarSeries()
            series_bar.append(bar_set)

            self.monthly_chart = QChart()
            self.monthly_chart.addSeries(series_bar)
            self.monthly_chart.setTitle("Monthly Summary")
            self.monthly_chart.setAnimationOptions(QChart.SeriesAnimations)
            self.monthly_chart.setTheme(QChart.ChartThemeBlueCerulean)

            categories = ["Income", "Expense"]
            axisX = QBarCategoryAxis()
            axisX.append(categories)
            self.monthly_chart.addAxis(axisX, Qt.AlignBottom)
            series_bar.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText("Amount")
            axisY.setLabelFormat("$%.0f")
            self.monthly_chart.addAxis(axisY, Qt.AlignLeft)
            series_bar.attachAxis(axisY)

            bar_legend = self.monthly_chart.legend()
            bar_legend.setVisible(True)
            bar_legend.setAlignment(Qt.AlignBottom)
            bar_legend.setFont(QFont("Arial", 10, QFont.Bold))
            bar_legend.setLabelColor("white")
            bar_legend.setMarkerShape(QLegend.MarkerShapeRectangle)

            self.chart_view.setChart(self.monthly_chart)
            self.chart_view.setVisible(True)

            self.monthly_diff_label.setText(
                f"<span style='font-size:16px; font-weight:bold;'>Difference (Income - Expense): </span>"
                f"<span style='font-size:16px; color:#FF5722;'>${difference:,.2f}</span>")
            self.monthly_diff_label.setVisible(True)

            self.chart_selector.setVisible(False)
            self.text_report.setVisible(False)

        elif report_type == "custom":
            self.monthly_diff_label.setVisible(False)

            income_categories = {}
            expense_categories = {}

            for txn in data:
                cat = txn.get("category", "Other")
                ttype = txn.get("transactionType", "Expense")
                amt = txn.get("amount", 0.0)
                if ttype.lower() == "income":
                    income_categories[cat] = income_categories.get(cat, 0.0) + amt
                else:
                    expense_categories[cat] = expense_categories.get(cat, 0.0) + amt

            income_categories = dict(sorted(income_categories.items(), key=lambda item: item[1], reverse=True))
            expense_categories = dict(sorted(expense_categories.items(), key=lambda item: item[1], reverse=True))

            top_income = self.top_n_dict(income_categories, 3)
            top_expense = self.top_n_dict(expense_categories, 3)

            full_text = f"""
            <div style='font-family:Helvetica, Arial, sans-serif; padding:10px;'>
                {self.dict_to_html(income_categories, "All Income Categories")}
                {self.dict_to_html(expense_categories, "All Expense Categories")}
            </div>
            """

            self.text_report.setHtml(full_text)

            self.income_chart = self.create_bar_chart("Distribution by Income Category", top_income)
            self.expense_chart = self.create_bar_chart("Distribution by Expense Category", top_expense)

            self.chart_view.setChart(self.income_chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)
            self.chart_view.setVisible(True)

            self.chart_selector.clear()
            self.chart_selector.addItem("Income")
            self.chart_selector.addItem("Expense")
            self.chart_selector.addItem("All Categories")
            self.chart_selector.setVisible(True)
            self.chart_selector.currentIndexChanged.connect(self.switch_chart)
            self.chart_selector.setCurrentIndex(0)

            self.text_report.setVisible(False)

    def top_n_dict(self, orig_dict, n):
        """Return the top n items from a dictionary based on values."""
        return dict(list(orig_dict.items())[:n])

    def dict_to_html(self, d, title):
        """Convert a dictionary to an HTML formatted string."""
        lines = [f"<h2 style='color:#3F51B5; font-size:18px; margin-bottom:4px;'>{title}:</h2>"]
        lines.append("<ul style='font-size:16px; line-height:1.6; margin-top:2px;'>")
        for k, v in d.items():
            lines.append(f"<li><strong>{k}:</strong> <span style='color:#4CAF50;'>${v:,.0f}</span></li>")
        lines.append("</ul>")
        return "\n".join(lines)

    def create_bar_chart(self, title, cat_dict):
        """Create a bar chart for the given category dictionary."""
        categories = list(cat_dict.keys())
        values = list(cat_dict.values())

        bar_set = QBarSet("Distribution")
        bar_set.append(values)
        bar_set.setColor(QColor("#FFD700"))

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeBlueCerulean)

        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setTitleText("Amount")
        axisY.setLabelFormat("$%.0f")
        axisY.setTickCount(10)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setFont(QFont("Arial", 10, QFont.Bold))
        legend.setLabelColor("white")
        legend.setMarkerShape(QLegend.MarkerShapeRectangle)

        return chart

    def switch_chart(self, index):
        """Switch between different charts based on user selection."""
        if index == 0 and self.income_chart:
            self.chart_view.setChart(self.income_chart)
            self.chart_view.setVisible(True)
            self.text_report.setVisible(False)
            logger.debug("Switched to Income chart.")
        elif index == 1 and self.expense_chart:
            self.chart_view.setChart(self.expense_chart)
            self.chart_view.setVisible(True)
            self.text_report.setVisible(False)
            logger.debug("Switched to Expense chart.")
        elif index == 2:
            self.chart_view.setVisible(False)
            self.text_report.setVisible(True)
            logger.debug("Switched to All Categories text report.")

    def clear_charts(self):
        """Clear all existing charts and reset visibility."""
        self.category_chart = None
        self.type_chart = None
        self.monthly_chart = None
        self.income_chart = None
        self.expense_chart = None
        self.all_categories_text = None
        self.text_report.setVisible(False)
        self.chart_view.setVisible(False)
        self.chart_selector.setVisible(False)
        logger.debug("Cleared all charts and reset view.")


class MonthlyReportDialog(QDialog):
    """Dialog for selecting month and year for the monthly report."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Month and Year")

        self.year_combo = QComboBox()
        self.month_combo = QComboBox()

        current_year = QDate.currentDate().year()
        for y in range(current_year - 5, current_year + 6):
            self.year_combo.addItem(str(y), y)

        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        for i, m in enumerate(month_names, start=1):
            self.month_combo.addItem(m, i)

        self.set_default_date(current_year)

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

    def set_default_date(self, current_year):
        """Set the combo boxes to the current year and month."""
        for i in range(self.year_combo.count()):
            if self.year_combo.itemData(i) == current_year:
                self.year_combo.setCurrentIndex(i)
                break
        current_month = QDate.currentDate().month()
        self.month_combo.setCurrentIndex(current_month - 1)

    def get_year_month(self):
        """Retrieve the selected year and month."""
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        return year, month


class CustomReportDialog(QDialog):
    """Dialog for selecting custom date range for the report."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Start and End Dates")

        self.start_year_combo = QComboBox()
        self.start_month_combo = QComboBox()
        self.start_day_combo = QComboBox()

        self.end_year_combo = QComboBox()
        self.end_month_combo = QComboBox()
        self.end_day_combo = QComboBox()

        current_year = QDate.currentDate().year()
        for y in range(current_year - 5, current_year + 6):
            self.start_year_combo.addItem(str(y), y)
            self.end_year_combo.addItem(str(y), y)

        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        for i, m in enumerate(month_names, start=1):
            self.start_month_combo.addItem(m, i)
            self.end_month_combo.addItem(m, i)

        self.start_year_combo.currentIndexChanged.connect(self.update_start_days)
        self.start_month_combo.currentIndexChanged.connect(self.update_start_days)
        self.end_year_combo.currentIndexChanged.connect(self.update_end_days)
        self.end_month_combo.currentIndexChanged.connect(self.update_end_days)

        today = QDate.currentDate()
        start_date = today.addMonths(-1)

        self.set_combo_to_value(self.start_year_combo, start_date.year())
        self.set_combo_to_value(self.start_month_combo, start_date.month())
        self.update_start_days()
        self.set_combo_to_value(self.start_day_combo, start_date.day())

        self.set_combo_to_value(self.end_year_combo, today.year())
        self.set_combo_to_value(self.end_month_combo, today.month())
        self.update_end_days()
        self.set_combo_to_value(self.end_day_combo, today.day())

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
        """Set the combo box to the specified value."""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break

    def update_start_days(self):
        """Update the day combo box based on selected start year and month."""
        year = self.start_year_combo.currentData()
        month = self.start_month_combo.currentData()
        self.populate_days(self.start_day_combo, year, month)

    def update_end_days(self):
        """Update the day combo box based on selected end year and month."""
        year = self.end_year_combo.currentData()
        month = self.end_month_combo.currentData()
        self.populate_days(self.end_day_combo, year, month)

    def populate_days(self, day_combo, year, month):
        """Populate the day combo box based on year and month."""
        num_days = calendar.monthrange(year, month)[1]
        day_combo.clear()
        for d in range(1, num_days + 1):
            day_combo.addItem(str(d), d)

    def get_date_range(self):
        """Retrieve the selected start and end dates."""
        start_year = self.start_year_combo.currentData()
        start_month = self.start_month_combo.currentData()
        start_day = self.start_day_combo.currentData()

        end_year = self.end_year_combo.currentData()
        end_month = self.end_month_combo.currentData()
        end_day = self.end_day_combo.currentData()

        start_date = QDate(start_year, start_month, start_day)
        end_date = QDate(end_year, end_month, end_day)

        return start_date, end_date
