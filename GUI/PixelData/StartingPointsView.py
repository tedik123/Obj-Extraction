from PyQt6.QtCore import QPoint, pyqtSignal

from .PixelStartingPointItem import PixelStartingPointItem
from SubComponents import CustomDockWidget


class StartingPointsView(CustomDockWidget):
    max_or_min_changed = pyqtSignal(str, int, int)
    start_value_changed = pyqtSignal(str, int, int)

    def __init__(self, parent=None):
        super().__init__(title="Starting Point", parent=parent)
        self.start_point_list = []

    def add_item_to_vertical_layout(self, point: QPoint, label_data=None):
        # warning if you ever insert a new item in here this will break everything!
        # always insert 1 before the addStretch item
        index_to_insert = self.vertical_layout.count() - 1
        start_point = PixelStartingPointItem(index_to_insert, point)
        start_point.changed_max_or_min.connect(self.max_or_min_changed.emit)
        start_point.changed_point_value.connect(self.start_value_changed.emit)

        if label_data:
            start_point.set_max_or_min_value("min_X", label_data.min_X[index_to_insert])
            start_point.set_max_or_min_value("max_X", label_data.max_X[index_to_insert])
            start_point.set_max_or_min_value("min_Y", label_data.min_Y[index_to_insert])
            start_point.set_max_or_min_value("max_Y", label_data.max_Y[index_to_insert])

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

    def set_start_point_value(self, point: QPoint, index):
        self.start_point_list[index].set_x_and_y_starts(point)
        print("set start point value", point)

    def set_max_or_min_value(self, minMaxXY, value, index):
        self.start_point_list[index].set_max_or_min_value(minMaxXY, value)
