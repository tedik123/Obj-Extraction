
from SubComponents import CustomDockWidget
from .RgbItem import RgbItem

class RgbView(CustomDockWidget):
    def __init__(self, parent=None):
        super().__init__(title="Rgb Values", parent=parent)

    # TODO
    def add_item_to_vertical_layout(self, r, g, b):
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1
        self.vertical_layout.insertWidget(index_to_insert, RgbItem(index_to_insert))
        # self.vertical_layout.addWidget(PixelStartingPointItem(point))
        print("children list", self.vertical_layout.count())
