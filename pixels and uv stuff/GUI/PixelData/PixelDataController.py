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
        self.main_controller = None
        # this should be like a list of the labels they've made,
        # and current_label should change depending on which is selected
        # self.labels = []
        self.current_label = None
        # self.add_new_label(self.current_label)
        self.set_events()

    def set_main_controller(self, main_controller):
        self.main_controller = main_controller

    def change_current_label(self, label_name: str):
        # we need to get the model entry and then pass that down to rgbview
        label_data = self.model.label_data[label_name]
        self.rgb_view.populate_new_data(label_data)
        self.starting_points_view.populate_new_data(label_data)
        self.current_label = label_name

    # TODO make it more dynamic
    def add_new_label(self, label: str, is_initial=False):
        self.model.add_new_label(label)
        if is_initial:
            self.current_label = label

    def edit_label(self, label: str):
        self.current_label = label

    def get_label(self):
        return self.current_label

    def handle_mouse_image_left_click(self, q_point):
        self.model.add_starting_point(self.current_label, q_point.x(), q_point.y())
        self.starting_points_view.add_item_to_vertical_layout(q_point)

    def handle_mouse_image_right_click(self, q_color: QColor):
        r, g, b, a = q_color.getRgb()
        self.model.add_rgb_value(self.current_label, r, g, b)
        self.rgb_view.add_item_to_vertical_layout(r, g, b)

    # this is like if they adjust in the color dialog window
    def handle_color_chosen(self, color: list, index: int):
        r, g, b = color
        # FIXME this is terrible you MUST delete the old value before adding the new one
        # the rgb values should be parallel to the rgb_items_list
        self.model.add_rgb_value(self.current_label, r, g, b)
        self.rgb_view.set_rgb_value(color, index=index)
        print("COLOR CHOSEN!!!")

    def set_events(self):
        self.rgb_view.color_chosen.connect(self.handle_color_chosen)
        self.rgb_view.rgb_value_incremented.connect(self.increment_rgb_value)
        self.starting_points_view.max_or_min_changed.connect(self.handle_max_or_min_change)
        self.starting_points_view.start_value_changed.connect(self.handle_start_value_changed)

    def increment_rgb_value(self, rgb_value: int, color_index: int, item_index: int):
        print("INCREMENTING IN CONTROLLER")
        self.model.update_rgb_value(self.current_label, rgb_value, color_index, item_index)
        self.rgb_view.set_single_color_value(rgb_value, color_index, item_index)

    def handle_start_value_changed(self, x_or_y: str, value: int, index: int):
        # switch statement to see if x or y
        match x_or_y:
            case "x":
                point = self.model.update_starting_point(self.current_label, 0, value, index)
            case "y":
                point = self.model.update_starting_point(self.current_label, 1, value, index)
            case _:
                print("ERROR")
                return
        self.starting_points_view.set_start_point_value(QPoint(point[0], point[1]), index)

    def handle_max_or_min_change(self, minMaxXY: str, value: int, index: int):
        try:
            new_value = self.model.update_xy_max_or_min(self.current_label, minMaxXY, value, index)
            self.starting_points_view.set_max_or_min_value(minMaxXY, new_value, index)
        except ValueError:
            print("NO can do with that max or min")
