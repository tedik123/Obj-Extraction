from PyQt5.QtCore import QPoint

from .PixelStartingPointItem import PixelStartingPointItem
from SubComponents import CustomDockWidget


class StartingPointsView(CustomDockWidget):
    def __init__(self, parent=None):
        super().__init__(title="Starting Point", parent=parent)
        self.start_point_list = []

    def add_item_to_vertical_layout(self, point: QPoint, label_data=None):
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1
        start_point = PixelStartingPointItem(index_to_insert, point)
        # todo label data where we set the min and max

        self.vertical_layout.insertWidget(index_to_insert, start_point)
        self.start_point_list.append(start_point)
        # self.vertical_layout.addWidget(PixelStartingPointItem(point))
        print("children list", self.vertical_layout.count())

    def populate_new_data(self, label_data):
        for start_point in self.start_point_list:
            # need to do this so it gets cleared properly ig
            start_point.setParent(None)
            start_point.deleteLater()

        self.start_point_list = []
        for point in label_data.starting_points:
            self.add_item_to_vertical_layout(QPoint(point[0], point[1]), label_data)
        print("children list", self.vertical_layout.count())
