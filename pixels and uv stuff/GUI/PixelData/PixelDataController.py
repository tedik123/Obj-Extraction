from .PixelDataModel import PixelDataModel
from .StartingPointsView import StartingPointsView
from .RgbView import RgbView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint


class PixelDataController:

    def __init__(self, model: PixelDataModel, starting_points_view: StartingPointsView, rgb_view: RgbView):
        self.model = model
        self.starting_points_view = starting_points_view
        self.rgb_view = rgb_view

    def handle_mouse_image_left_click(self, QPoint):
        self.model.add_starting_point(QPoint.x(), QPoint.y())
        self.starting_points_view.add_item_to_vertical_layout(QPoint)

    def handle_mouse_image_right_click(self, QColor: QColor):
        r, g, b, a = QColor.getRgb()
        self.model.add_rgb_value(r, g, b)
        self.rgb_view.add_item_to_vertical_layout(r, g, b)
