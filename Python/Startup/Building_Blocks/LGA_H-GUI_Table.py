from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide2.QtGui import QScreen
from PySide2.QtCore import Qt
import nuke
import os
import re
import sys

class ReadNodeInfo(QWidget):
    def __init__(self, parent=None):
        super(ReadNodeInfo, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Read Nodes EXR Info")
        layout = QVBoxLayout(self)

        # Create the table
        self.table = QTableWidget(0, 4, self)  # Start with 0 rows and 5 columns now
        self.table.setHorizontalHeaderLabels(['Shot', 'Task', 'Status', 'Status'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Load data into the table
        self.load_data()

        layout.addWidget(self.table)
        self.setLayout(layout)
        
        # Adjust window size and position to be centered
        self.adjust_window_size()

    def load_data(self):
        # For simplicity, let's invent some fictitious data for a single row
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        
        # Add fictitious data to the table
        self.table.setItem(row_count, 0, QTableWidgetItem("EHQALPV_001_010_SombraOvni_Aparece_comp_v05"))
        self.table.setItem(row_count, 1, QTableWidgetItem("Comp"))
        self.table.setItem(row_count, 2, QTableWidgetItem("In Progress"))
        self.table.setItem(row_count, 3, QTableWidgetItem("Corrections"))

        # Adjust column sizes
        self.table.resizeColumnsToContents()

    def adjust_window_size(self):
        # Temporarily disable stretching of the last column
        self.table.horizontalHeader().setStretchLastSection(False)

        # Adjust columns to content
        self.table.resizeColumnsToContents()

        # Calculate window width based on column widths
        width = self.table.verticalHeader().width() - 30  # Some padding for aesthetics
        for i in range(self.table.columnCount()):
            width += self.table.columnWidth(i) + 20  # Some padding between columns

        # Ensure width does not exceed 80% of screen width
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        max_width = screen_rect.width() * 0.8
        final_width = min(width, max_width)

        # Calculate height based on header height and row heights
        height = self.table.horizontalHeader().height() + 20
        for i in range(self.table.rowCount()):
            height += self.table.rowHeight(i) + 4  # Some padding per row

        # Ensure height does not exceed 80% of screen height
        max_height = screen_rect.height() * 0.8
        final_height = min(height, max_height)

        # Re-enable stretching of the last column
        self.table.horizontalHeader().setStretchLastSection(True)

        # Adjust window size and center it
        self.resize(final_width, final_height)
        self.move((screen_rect.width() - final_width) // 2, (screen_rect.height() - final_height) // 2)

app = None
window = None

def main():
    global app, window
    app = QApplication.instance() or QApplication(sys.argv)
    if not app:
        app = QApplication([])
    window = ReadNodeInfo()
    window.show()

# Call main() to start the application
main()
