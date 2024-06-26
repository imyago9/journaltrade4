from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import *
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import mplcursors
import matplotlib.dates as mdates
from custom_calendar import CustomCalendar
from SettingsApexDataWidget import SettingsWidget


class ApexDataWidget(QDialog):
    def __init__(self, parent=None):
        super(ApexDataWidget, self).__init__(parent)
        self.setGeometry(100, 100, 1600, 600)
        self.setWindowTitle("Apex Account(s) Data")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setupUi()
        self._is_moving = False
        self._start_pos = None
        self.current_date = QDate.currentDate()
        self.targets = {
            25: 1500, 50: 3000, 75: 4250, 100: 6000, 150: 9000, 250: 15000, 300: 20000 }
        self.stop_losses = {
            25: 1500, 50: 2500, 75: 2750, 100: 3000, 150: 5000, 250: 6500, 300: 7500 }
    
    def setupUi(self):
        self.main_layout_vertical = QVBoxLayout(self)
        
        self.setupTopFrame()
        self.setupBottomFrame()

        self.main_layout_vertical.addWidget(self.top_frame)
        self.main_layout_vertical.addWidget(self.bottom_frame)

        self.accountselection_comboBox.currentIndexChanged.connect(self.display_selected_account)

    def setupTopFrame(self):
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet("border: 2px solid black;")
        self.top_frame.setMaximumHeight(50)

        self.top_frame_layout_horizontal = QHBoxLayout(self.top_frame)
        self.top_frame_layout_horizontal.setContentsMargins(0, 0, 0, 0)
        self.top_frame_layout_horizontal.setSpacing(0)

        self.setupDataManagementFrame()
        self.setupTopFrameTitle()
        self.seutpWindowButtonsFrame()
        self.top_frame_layout_horizontal.addWidget(self.data_management_frame)
        self.top_frame_layout_horizontal.addWidget(self.top_frame_title)
        self.top_frame_layout_horizontal.addWidget(self.window_buttons_frame)
        
    def setupDataManagementFrame(self):
        self.data_management_frame = QFrame(self.top_frame)
        self.data_management_frame_layout_horizontal = QHBoxLayout(self.data_management_frame)
        
        self.first_dateEdit = QDateEdit(self.data_management_frame)
        self.second_dateEdit = QDateEdit(self.data_management_frame)
        self.accountselection_comboBox = QComboBox(self.data_management_frame)
        self.account_settings_button = QPushButton(self.data_management_frame, clicked=self.open_settings_widget)
        account_settings_icon = QtGui.QIcon()
        account_settings_icon.addPixmap(QtGui.QPixmap("resources/settings-v-svgrepo-com.svg"), QtGui.QIcon.Normal,
                                QtGui.QIcon.Off)
        self.account_settings_button.setIcon(account_settings_icon)

        self.load_apex_accounts()
        
        self.data_management_frame_layout_horizontal.addWidget(self.first_dateEdit)
        self.data_management_frame_layout_horizontal.addWidget(self.second_dateEdit)
        self.data_management_frame_layout_horizontal.addWidget(self.accountselection_comboBox)
        self.data_management_frame_layout_horizontal.addWidget(self.account_settings_button)
        
    def setupTopFrameTitle(self):
        self.top_frame_title = QLabel("Apex Account(s) Data")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.top_frame_title.setFont(font)
        self.top_frame_title.setAlignment(QtCore.Qt.AlignCenter)
        
    def seutpWindowButtonsFrame(self):
        self.window_buttons_frame = QFrame(self.top_frame)
        self.window_buttons_frame_layout_horizontal = QHBoxLayout(self.window_buttons_frame)

        self.minimize_button = QPushButton(self.window_buttons_frame, clicked=self.showMinimized)
        minimize_icon = QtGui.QIcon()
        minimize_icon.addPixmap(QtGui.QPixmap("resources/minimize.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimize_button.setIcon(minimize_icon)
        self.close_button = QPushButton(self.window_buttons_frame, clicked=self.close)
        close_icon = QtGui.QIcon()
        close_icon.addPixmap(QtGui.QPixmap("resources/close.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.close_button.setIcon(close_icon)

        self.window_buttons_frame_layout_horizontal.addWidget(self.minimize_button)
        self.window_buttons_frame_layout_horizontal.addWidget(self.close_button)

    def setupBottomFrame(self):
        self.bottom_frame = QFrame()
        self.bottom_frame_layout_vertical = QVBoxLayout(self.bottom_frame)

        self.stats_frame = self.createStatsFrame()
        self.graphs_frame = self.createGraphsFrame()
        self.bottom_frame_layout_vertical.addWidget(self.stats_frame)
        self.bottom_frame_layout_vertical.addWidget(self.graphs_frame)
        
    def createStatsFrame(self):
        stats_frame = QFrame(self.bottom_frame)
        stats_frame_layout_horizontal = QHBoxLayout(stats_frame)

        self.first_stats_label = self.createStatsBox()
        self.second_stats_label = self.createStatsBox()
        self.third_stats_label = self.createStatsBox()
        self.fourth_stats_label = self.createStatsBox()

        stats_frame_layout_horizontal.addWidget(self.first_stats_label)
        stats_frame_layout_horizontal.addWidget(self.second_stats_label)
        stats_frame_layout_horizontal.addWidget(self.third_stats_label)
        stats_frame_layout_horizontal.addWidget(self.fourth_stats_label)
        return stats_frame

    def createStatsBox(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        label = QLabel(frame)
        layout.addWidget(label)
        frame.setStyleSheet("border: 2px solid black;")
        return label
    
    def createGraphsFrame(self):
        graphs_frame = QFrame(self.bottom_frame)
        graphs_frame.setStyleSheet("border: 2px solid black;")
        horizontal_layout = QHBoxLayout(graphs_frame)
        self.first_graph_frame = QFrame(graphs_frame)
        self.second_graph_frame = QFrame(graphs_frame)
        self.third_graph_frame = QFrame(graphs_frame)

        self.first_graph_frame.setLayout(QVBoxLayout())
        self.second_graph_frame.setLayout(QVBoxLayout())
        self.third_graph_frame.setLayout(QVBoxLayout())

        horizontal_layout.addWidget(self.first_graph_frame)
        horizontal_layout.addWidget(self.second_graph_frame)
        horizontal_layout.addWidget(self.third_graph_frame)

        return graphs_frame

    def load_apex_accounts(self):
        data_file_path = 'resources/to_use_data.csv'
        visibility_file_path = 'resources/account_settings.csv'
        self.data = pd.read_csv(data_file_path)
        self.data_settings = pd.read_csv(visibility_file_path)
        accounts = self.data['Account'].unique()
        apex_accounts = sorted([account for account in accounts if 'Apex' in account])
        visible_accounts = self.data_settings[self.data_settings['Visibility'] == 'visible']['Account']
        visible_apex_accounts = [account for account in apex_accounts if account in visible_accounts.values]
        self.accountselection_comboBox.clear()
        self.accountselection_comboBox.addItems(visible_apex_accounts)
        self.accountselection_comboBox.setCurrentIndex(-1)

    def display_selected_account(self):
        self.selected_account = self.accountselection_comboBox.currentText()
        self.account_data = self.data[self.data['Account'] == self.selected_account]
        self.account_row = self.data_settings.loc[self.data_settings['Account'] == self.selected_account]
        grouped_data = self.account_data.groupby('EntryT').agg({'Profit': 'sum', 'LorS': 'first'}).reset_index()

        net_pnl = grouped_data['Profit'].sum()
        total_trades = len(grouped_data)
        winning_trades = len(grouped_data[grouped_data['Profit'] >= 50])
        losing_trades = len(grouped_data[grouped_data['Profit'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        loss_rate = (losing_trades / total_trades) * 100 if total_trades > 0 else 0
        break_even_rate = 100 - (win_rate + loss_rate)
        avg_win = grouped_data[grouped_data['Profit'] > 0]['Profit'].mean()
        avg_loss = grouped_data[grouped_data['Profit'] < 0]['Profit'].mean()

        self.updateStatsLabels(net_pnl, win_rate, loss_rate, break_even_rate, avg_win, avg_loss, total_trades)
        self.plot_line_graph()
        self.plot_calendar()
        self.plot_trade_performance(self.account_data)

    def updateStatsLabels(self, net_pnl, win_rate, loss_rate, break_even_rate, avg_win, avg_loss, total_trades):
        self.first_stats_label.setText(f"Net Profit: ${net_pnl:.2f}")
        self.second_stats_label.setText(f"Win Rate: {win_rate:.2f}%\nLoss Rate: {loss_rate:.2f}%\nB/e Rate: {break_even_rate:.2f}%\nAvg Win: ${avg_win:.2f} | Avg Loss: ${avg_loss:.2f}")
        self.third_stats_label.setText("")
        self.fourth_stats_label.setText(f"Number of Trades: {total_trades}")

    def plot_line_graph(self):
        for i in reversed(range(self.first_graph_frame.layout().count())):
            widget_to_remove = self.first_graph_frame.layout().itemAt(i).widget()
            self.first_graph_frame.layout().removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        a_size = self.account_row['ASize'].values[0]
        initial_amount = (a_size * 1000)

        self.account_data.loc[:, 'EntryT'] = pd.to_datetime(self.account_data['EntryT'])
        cumulative_progress = self.account_data.groupby('EntryT')['Profit'].sum().cumsum() + initial_amount

        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#F0F0F0')
        ax.set_facecolor('#F0F0F0')
        line, = ax.plot(cumulative_progress.index, cumulative_progress, color='black', label='Cumulative Profit')
        ax.scatter(cumulative_progress.index, cumulative_progress, color='black', s=10, zorder=5)
        ax.grid(False)
        ax.axhline(initial_amount, color='black', linestyle='--', linewidth=1)
        self.addLines(ax)

        cursor = mplcursors.cursor(line, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"Date: {cumulative_progress.index[int(sel.index)].strftime('%m/%d - %H:%M')}\n"
            f"Profit: {cumulative_progress.iloc[int(sel.index)]:.2f}"
        ))
        cursor.connect("add", lambda sel: self.annotation_color(sel))

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator())

        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        fig.tight_layout(pad=0, h_pad=0, w_pad=0)

        ax.set_title("Profit Across Trades")

        canvas = FigureCanvas(fig)
        self.first_graph_frame.layout().addWidget(canvas)

    def calculate_target_and_stop_lines(self):
        cumulative_progress = self.account_data.groupby('ExitT')['Profit'].sum().cumsum()

        highest_profit = cumulative_progress.max()
        lowest_profit = cumulative_progress.min()

        account_row = self.data_settings.loc[self.data_settings['Account'] == self.selected_account]

        if not account_row.empty:
            a_size = account_row['ASize'].values[0]
            initial_value = a_size * 1000

            highest_acc_size = initial_value + highest_profit
            lowest_acc_size = initial_value + lowest_profit

            stop_value = self.stop_losses.get(a_size, 0)
            target_line = self.targets.get(a_size, None) + initial_value
            stop_line = highest_acc_size - stop_value if highest_acc_size > initial_value else initial_value - stop_value
            print(f"ASize: {a_size}, Target Line: {target_line}, Stop Line: {stop_line}, Initial value: {initial_value},"
                  f" Highest value: {highest_acc_size}, Lowest value: {lowest_acc_size}")  # Debug statement
            return target_line, stop_line, highest_acc_size, lowest_acc_size
        else:
            print("Account row not found or empty")  # Debug statement
            return None, None

    def addLines(self, ax):
        if not self.account_row.empty:
            target_condition = self.account_row['TargetLines'].values[0]
            if target_condition == 'On':
                self.target_line, self.stop_line, self.highest_acc_size, self.lowest_acc_size = self.calculate_target_and_stop_lines()
                if self.target_line is not None:
                    ax.axhline(self.target_line, color='green', linestyle='--', linewidth=1, label='Target')
                if self.stop_line is not None:
                    ax.axhline(self.stop_line, color='red', linestyle='--', linewidth=1, label='Stop Loss')

    def plot_trade_performance(self, data, aggregation='single'):
        for i in reversed(range(self.second_graph_frame.layout().count())):
            widget_to_remove = self.second_graph_frame.layout().itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        self.second_graph_frame.setLayout(QtWidgets.QVBoxLayout())

        filtered_data = data.copy()
        filtered_data.loc[:, 'EntryT'] = pd.to_datetime(filtered_data['EntryT'], errors='coerce')

        if filtered_data.empty:
            label = QLabel("No trades were made in this date range.")
            self.second_graph_frame.layout().addWidget(label)
            return

        if aggregation == 'daily':
            grouped_data = filtered_data.groupby(filtered_data['EntryT'].dt.date).agg(
                Profit=('Profit', 'sum'),
                Qty=('Qty', 'sum')).reset_index()
        elif aggregation == 'weekly':
            grouped_data = filtered_data.groupby(pd.Grouper(key='EntryT', freq='W-MON')).agg(
                Profit=('Profit', 'sum'),
                Qty=('Qty', 'sum')).reset_index()
        else:
            grouped_data = filtered_data.groupby('EntryT').agg(
                Profit=('Profit', 'sum'),
                Qty=('Qty', 'sum'),
                LorS=('LorS', 'first'),
                Account=('Account', 'first')).reset_index()

        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#F0F0F0')
        ax.set_facecolor('#F0F0F0')
        bars = ax.bar(grouped_data.index, grouped_data['Profit'],
                      color=np.where(grouped_data['Profit'] > 0, 'green', 'red'))

        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"Date: {pd.to_datetime(grouped_data.iloc[sel.index]['EntryT']).strftime('%m/%d - %H:%M')}\n" +
            f"RR: {grouped_data.iloc[sel.index]['Profit']:.2f}\n" +
            f"Qty: {grouped_data.iloc[sel.index]['Qty']}\n" +
            f"LorS: {grouped_data.iloc[sel.index]['LorS']}\n" +
            f"Account: {grouped_data.iloc[sel.index]['Account']}"
        ))
        cursor.connect("add", lambda sel: self.annotation_color(sel))

        ax.set_title('Trade Performance')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.axhline(0, color='grey', linewidth=0.8)

        plt.tight_layout()

        canvas = FigureCanvas(fig)
        self.second_graph_frame.layout().addWidget(canvas)

    def plot_calendar(self):
        for i in reversed(range(self.third_graph_frame.layout().count())):
            widget_to_remove = self.third_graph_frame.layout().itemAt(i).widget()
            if widget_to_remove:
                self.third_graph_frame.layout().removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)

        self.calendar = CustomCalendar(parent=None)
        self.calendar.setGeometry(0, 0, 600, 400)
        self.calendar.account_data = self.account_data

        self.update_calendar()

        self.third_graph_frame.layout().addWidget(self.calendar)
        self.show()

    def update_calendar(self):
        data = self.account_data
        data = data.groupby('EntryT').agg({'Profit': 'sum', 'LorS': 'first'}).reset_index()

        data['EntryT'] = pd.to_datetime(data['EntryT'])
        data['Date'] = data['EntryT'].dt.date
        grouped_data = data.groupby('Date').agg({
            'Profit': 'sum',
            'EntryT': 'count'
        }).rename(columns={'EntryT': 'Trades'}).reset_index()

        for index, row in grouped_data.iterrows():
            date = row['Date']
            if date.month == self.current_date.month() and date.year == self.current_date.year():
                day = date.day
                text = f"Profit: {row['Profit']}\nTrades: {row['Trades']}"
                self.calendar.setText(day, text)

    def open_settings_widget(self):
        if not self.accountselection_comboBox.currentIndex() == -1:
            self.settings_widget = SettingsWidget()
            self.settings_widget.selected_account = self.selected_account
            self.settings_widget.data_settings = self.data_settings
            self.settings_widget.update_values()
            self.settings_widget.closed.connect(self.enable_apex_data_widget)
            self.settings_widget.reloadPressed.connect(self.update_graph)
            self.settings_widget.show()
            self.setEnabled(False)

    def enable_apex_data_widget(self):
        self.setEnabled(True)

    def update_graph(self):
        self.display_selected_account()

    def annotation_color(self, sel):
        sel.annotation.get_bbox_patch().set(fc='black', alpha=0.6)
        sel.annotation.get_bbox_patch().set_edgecolor('none')
        sel.annotation.set_color('white')

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._is_moving = True
            self._start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self._is_moving:
            self.move(self.pos() + event.pos() - self._start_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._is_moving = False