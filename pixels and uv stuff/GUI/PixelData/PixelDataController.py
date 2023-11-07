from .PixelDataModel import PixelDataModel
from .StartingPointsView import StartingPointsView
from .RgbView import RgbView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint


class PixelDataController:

    def __init__(self, model: PixelDataModel, starting_points_view: StartingPointsView, rgb_view: RgbView):
        self.model: PixelDataModel = model
        self.starting_points_view: StartingPointsView = starting_points_view
        self.rgb_view: RgbView = rgb_view
        self.set_events()

    def handle_mouse_image_left_click(self, QPoint):
        self.model.add_starting_point(QPoint.x(), QPoint.y())
        self.starting_points_view.add_item_to_vertical_layout(QPoint)

    def handle_mouse_image_right_click(self, QColor: QColor):
        r, g, b, a = QColor.getRgb()
        self.model.add_rgb_value(r, g, b)
        self.rgb_view.add_item_to_vertical_layout(r, g, b)

    # TODO pass to model
    # this is like if they adjust in the color dialog window
    def handle_color_chosen(self, color: list, index: int):
        r, g, b = color
        self.model.add_rgb_value(r, g, b)
        # todo index
        self.rgb_view.set_rgb_value(color, index=index)
        print("COLOR CHOSEN!!!")

    def set_events(self):
        self.rgb_view.color_chosen.connect(self.handle_color_chosen)
        self.rgb_view.rgb_value_incremented.connect(self.increment_rgb_value)

    def increment_rgb_value(self, rgb_value: int, color_index: int, item_index: int):
        print("INCREMENTING IN CONTROLLER")
        self.model.increment_rgb_value(rgb_value, color_index, item_index)
        self.rgb_view.set_single_color_value(rgb_value, color_index, item_index)
