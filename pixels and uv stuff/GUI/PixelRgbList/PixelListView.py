from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QSizePolicy, QDockWidget

from .PixelListStartingPointItem import PixelStartingPointItem

class PixelListView(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.setWindowTitle("Starting Points")
        self.setStyleSheet("QDockWidget { font-family: 'Roboto Lt'; font-size: 12pt; }")

        self.scrollArea = QScrollArea()
        # I Don't know if I even need this
        self.main_widget = QWidget()
        self.scrollArea.setWidget(self.main_widget)

        # set the scroll area so it vertically allows for scrolling
        self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.vertical_layout = QVBoxLayout()
        self.main_widget.setLayout(self.vertical_layout)
        self.vertical_layout.insertWidget(0, PixelStartingPointItem())

        self.vertical_layout.addStretch()
        self.setWidget(self.scrollArea)
        self.show()

