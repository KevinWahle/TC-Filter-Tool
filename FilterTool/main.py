import sys
from PyQt5.QtWidgets import QApplication
from src.FilterToolApp import FilterToolApp

app = QApplication(sys.argv)
win = FilterToolApp()
win.show()
sys.exit(app.exec())