from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QSizePolicy, QDockWidget
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor

from .PixelListStartingPointItem import PixelStartingPointItem
from .SubComponents.CustomDockWidget import CustomDockWidget


class PixelListView(CustomDockWidget):
    def __init__(self, parent=None):
        super().__init__(title="Starting Point", parent=parent)

    def add_item_to_vertical_layout(self, point: QPoint):
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1
        self.vertical_layout.insertWidget(index_to_insert, PixelStartingPointItem(index_to_insert, point))
        # self.vertical_layout.addWidget(PixelStartingPointItem(point))
        print("children list", self.vertical_layout.count())
