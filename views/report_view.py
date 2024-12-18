from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                               QDialog, QDialogButtonBox, QFormLayout, QComboBox, QTextEdit, QToolButton)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QLegend, QBarCategoryAxis, QBarSeries, QBarSet, QValueAxis
from PySide6.QtGui import QPainter, QColor, QFont, QIcon
import requests
import json
import calendar

class ReportView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Main layout for the ReportView
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add the back button at the top
        self.add_back_button(self.layout)

        # Add a stretch to center content vertically
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

        # Vertical layout for buttons (Top and bottom arrangement)
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

        # Another stretch to center vertically
        self.layout.addStretch()

        # A combo box to switch charts (hidden by default)
        self.chart_selector = QComboBox()
        self.chart_selector.setVisible(False)
        self.layout.addWidget(self.chart_selector)

        # Create a chart view to display the selected chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setVisible(False)
        self.layout.addWidget(self.chart_view)

        # Make the text report larger to match chart view height and improve readability
        self.text_report = QTextEdit()
        self.text_report.setVisible(False)
        self.text_report.setReadOnly(True)
        self.text_report.setMinimumHeight(400)  # increased height
        self.text_report.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.text_report)

        # Initialize the monthly_diff_label once
        self.monthly_diff_label = QLabel()
        self.monthly_diff_label.setAlignment(Qt.AlignCenter)
        self.monthly_diff_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #000;")
        self.monthly_diff_label.setVisible(False)
        self.layout.addWidget(self.monthly_diff_label)

        # Variables to hold charts
        self.category_chart = None
        self.type_chart = None
        self.monthly_chart = None
        self.income_chart = None
        self.expense_chart = None
        self.all_categories_text = None

    def add_back_button(self, main_layout):
        """Add a modern back button with an arrow to return to the content view."""
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
        dialog = MonthlyReportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            year, month = dialog.get_year_month()
            self.fetch_monthly_report(year, month)

    def generate_custom_report(self):
        dialog = CustomReportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            start_date, end_date = dialog.get_date_range()
            self.fetch_custom_report(start_date, end_date)

    def fetch_monthly_report(self, year, month):
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
                self.display_report_data(report_data, report_type="monthly")
            else:
                self.show_error(f"Error fetching monthly report: {response.status_code}\n{response.text}")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def fetch_custom_report(self, start_date, end_date):
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
                self.display_report_data(report_data, report_type="custom")
            else:
                self.show_error(f"Error fetching custom report: {response.status_code}\n{response.text}")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        self.chart_view.setVisible(False)
        self.chart_selector.setVisible(False)
        self.text_report.setVisible(False)
        self.monthly_diff_label.setVisible(False)  # Hide the difference label on error

        error_label = QLabel(message)
        error_label.setStyleSheet("color: red; font-weight: bold;")
        error_label.setAlignment(Qt.AlignCenter)

        # Clear previous layout items except crucial ones
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if w and w not in [self.title_label, self.monthly_report_button, self.custom_report_button,
                                   self.chart_selector, self.chart_view, self.text_report, self.monthly_diff_label]:
                    w.setParent(None)

        self.layout.addWidget(error_label)

    def display_report_data(self, data, report_type="custom"):
        self.clear_charts()

        if report_type == "monthly":
            # 月度报告的处理
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

            # 创建条形图
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
            axisY.setLabelFormat("$%.0f")  # 显示美元符号，无小数
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

            # 更新现有的 monthly_diff_label，而不是创建新的标签
            self.monthly_diff_label.setText(
                f"<span style='font-size:16px; font-weight:bold;'>Difference (Income - Expense): </span>"
                f"<span style='font-size:16px; color:#FF5722;'>${difference:,.2f}</span>")
            self.monthly_diff_label.setVisible(True)

            self.chart_selector.setVisible(False)
            self.text_report.setVisible(False)


        elif report_type == "custom":

            # 隐藏 monthly_diff_label

            self.monthly_diff_label.setVisible(False)

            # 分类处理

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

            # 排序

            income_categories = dict(sorted(income_categories.items(), key=lambda item: item[1], reverse=True))

            expense_categories = dict(sorted(expense_categories.items(), key=lambda item: item[1], reverse=True))

            # 只显示前3个分类

            def top_3_dict(orig_dict):

                return dict(list(orig_dict.items())[:3])

            top_income = top_3_dict(income_categories)

            top_expense = top_3_dict(expense_categories)

            # 使用HTML设置字体大小和样式

            def dict_to_html(d, title):
                lines = [f"<h2 style='color:#3F51B5; font-size:18px; margin-bottom:4px;'>{title}:</h2>"]  # 调整标题的下边距
                lines.append("<ul style='font-size:16px; line-height:1.6; margin-top:2px;'>")  # 调整列表的上边距
                for k, v in d.items():
                    lines.append(f"<li><strong>{k}:</strong> <span style='color:#4CAF50;'>${v:,.0f}</span></li>")
                lines.append("</ul>")
                return "\n".join(lines)

            # 构建完整的HTML文本

            full_text = f"""

            <div style='font-family:Helvetica, Arial, sans-serif; padding:10px;'>

                {dict_to_html(income_categories, "All Income Categories")}

                {dict_to_html(expense_categories, "All Expense Categories")}

            </div>

            """

            self.text_report.setHtml(full_text)  # 仅使用 setHtml 设置内容

            # 创建收入和支出的条形图
            def create_bar_chart(title, cat_dict):
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
                axisY.setLabelFormat("$%.0f")  # 显示美元符号
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

            self.income_chart = create_bar_chart("Distribution by Income Category", top_income)
            self.expense_chart = create_bar_chart("Distribution by Expense Category", top_expense)

            # 默认显示收入图表
            self.chart_view.setChart(self.income_chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)
            self.chart_view.setVisible(True)

            # 设置组合框用于切换图表
            self.chart_selector.clear()
            self.chart_selector.addItem("Income")
            self.chart_selector.addItem("Expense")
            self.chart_selector.addItem("All Categories")
            self.chart_selector.setVisible(True)
            self.chart_selector.currentIndexChanged.connect(self.switch_chart)
            self.chart_selector.setCurrentIndex(0)

            self.text_report.setVisible(False)
    def switch_chart(self, index):
        # 0 = Income, 1 = Expense, 2 = All Categories (Text)
        if index == 0 and self.income_chart:
            self.chart_view.setChart(self.income_chart)
            self.chart_view.setVisible(True)
            self.text_report.setVisible(False)
        elif index == 1 and self.expense_chart:
            self.chart_view.setChart(self.expense_chart)
            self.chart_view.setVisible(True)
            self.text_report.setVisible(False)
        elif index == 2:
            # Show text report
            self.chart_view.setVisible(False)
            self.text_report.setVisible(True)

    def clear_charts(self):
        self.category_chart = None
        self.type_chart = None
        self.monthly_chart = None
        # Do not reset monthly_diff_label here
        self.income_chart = None
        self.expense_chart = None
        self.all_categories_text = None
        self.text_report.setVisible(False)
        # Optionally hide chart view and selector if needed
        self.chart_view.setVisible(False)
        self.chart_selector.setVisible(False)

class MonthlyReportDialog(QDialog):
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

        # Set current month and year as default
        for i in range(self.year_combo.count()):
            if self.year_combo.itemData(i) == current_year:
                self.year_combo.setCurrentIndex(i)
                break
        current_month = QDate.currentDate().month()
        self.month_combo.setCurrentIndex(current_month - 1)

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
        num_days = calendar.monthrange(year, month)[1]
        day_combo.clear()
        for d in range(1, num_days + 1):
            day_combo.addItem(str(d), d)

    def get_date_range(self):
        start_year = self.start_year_combo.currentData()
        start_month = self.start_month_combo.currentData()
        start_day = self.start_day_combo.currentData()

        end_year = self.end_year_combo.currentData()
        end_month = self.end_month_combo.currentData()
        end_day = self.end_day_combo.currentData()

        start_date = QDate(start_year, start_month, start_day)
        end_date = QDate(end_year, end_month, end_day)

        return start_date, end_date
