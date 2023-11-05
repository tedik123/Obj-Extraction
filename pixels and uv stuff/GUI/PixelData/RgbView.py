from PyQt5.QtCore import pyqtSignal
from SubComponents import CustomDockWidget
from .RgbItem import RgbItem

class RgbView(CustomDockWidget):
    color_chosen = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(title="Rgb Values", parent=parent)

    # TODO
    def add_item_to_vertical_layout(self, r, g, b):
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1

        rgb_item = RgbItem(index_to_insert, (r, g, b))
        rgb_item.color_chosen.connect(self.color_chosen.emit)

        self.vertical_layout.insertWidget(index_to_insert, rgb_item)
        # self.vertical_layout.addWidget(PixelStartingPointItem(point))
        print("children list", self.vertical_layout.count())
