from PyQt5.QtCore import QPoint

from .PixelStartingPointItem import PixelStartingPointItem
from SubComponents import CustomDockWidget


class StartingPointsView(CustomDockWidget):
    def __init__(self, parent=None):
        super().__init__(title="Starting Point", parent=parent)

    def add_item_to_vertical_layout(self, point: QPoint):
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1
        self.vertical_layout.insertWidget(index_to_insert, PixelStartingPointItem(index_to_insert, point))
        # self.vertical_layout.addWidget(PixelStartingPointItem(point))
        print("children list", self.vertical_layout.count())
