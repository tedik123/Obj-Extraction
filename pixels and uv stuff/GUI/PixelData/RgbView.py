from PyQt5.QtCore import pyqtSignal

# I do this ugliness because pycharm intellisense is just not working :( and i want intellisense
try:
    from SubComponents import CustomDockWidget
except:
    from ..SubComponents import CustomDockWidget

from .RgbItem import RgbItem

class RgbView(CustomDockWidget):
    color_chosen = pyqtSignal(list, int)
    # first int is the r,g, or b value, the second is the positional argument for rgb, last is the index of the item
    rgb_value_incremented = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(title="Rgb Values", parent=parent)
        self.rgb_items_list = []


    def add_item_to_vertical_layout(self, r, g, b):
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1

        rgb_item = RgbItem(index_to_insert, (r, g, b))
        self.rgb_items_list.append(rgb_item)
        # this is for the color dialog
        rgb_item.color_chosen.connect(self.color_chosen)
        rgb_item.rgb_value_incremented.connect(self.rgb_value_incremented)

        self.vertical_layout.insertWidget(index_to_insert, rgb_item)
        # self.vertical_layout.addWidget(PixelStartingPointItem(point))
        print("children list", self.vertical_layout.count())

    def set_rgb_value(self, color: list, index: int):
        print("INDEX ", index)
        # inline function destructure of color
        r, g, b = color
        self.rgb_items_list[index].set_rgb_value(r, g, b)

    def set_single_color_value(self, color_value: int, color_index: int, index: int):
        self.rgb_items_list[index].set_single_color_value(color_value, color_index)

    def populate_new_data(self, label_data):
        for rgb_item in self.rgb_items_list:
            rgb_item.setParent(None)
            rgb_item.deleteLater()
        self.rgb_items_list = []
        for rgb_value in label_data.acceptable_colors_rgb:
            self.add_item_to_vertical_layout(rgb_value[0], rgb_value[1], rgb_value[2])
        self.show()
        print("POPULATED NEW DATA")
