from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class LabelData:
    name: str
    abr: str = ""
    starting_points: List[List[int]] = field(default_factory=list)
    acceptable_colors_rgb: List[List[int]] = field(default_factory=list)
    pixel_deviation: int = 0
    min_X: List[int] = field(default_factory=list)
    max_X: List[int] = field(default_factory=list)
    min_Y: List[int] = field(default_factory=list)
    max_Y: List[int] = field(default_factory=list)
    enable_default_range: bool = False


class PixelDataModel:

    def __init__(self):
        # dict of labeldata
        self.label_data: dict[str, LabelData] = {}

    def get_abr(self, name):
        return self.label_data[name].abr

    def add_new_label(self, name: str):
        if self.label_data.get(name):
            raise ValueError("Label already exists")
        self.label_data[name] = LabelData(name)

    def edit_label(self, old_name: str, new_name: str):
        if new_name in self.label_data:
            raise ValueError("Label already exists")
        self.label_data[new_name] = self.label_data.pop(old_name)

    def edit_abr(self, name: str, new_abr: str):
        print(f"current label {name} setting new abr to {new_abr}")
        self.label_data[name].abr = new_abr
        return self.label_data[name].abr

    def add_starting_point(self, name: str, x: int, y: int):
        data = self.label_data[name]
        data.starting_points.append([x, y])
        data.min_X.append(0)
        data.max_X.append(0)
        data.min_Y.append(0)
        data.max_Y.append(0)

    def add_rgb_value(self, name: str, r: int, g: int, b: int):
        self.label_data[name].acceptable_colors_rgb.append([r, g, b])

    # updates a single field in rgb so either r,g, or b not both
    def update_rgb_value(self, name: str, rgb_value: int, color_index: int, item_index: int):
        r, g, b = self.label_data[name].acceptable_colors_rgb[item_index]
        self.label_data[name].acceptable_colors_rgb[item_index][color_index] = rgb_value
        print("update rgb value", [r, g, b], self.label_data[name].acceptable_colors_rgb[item_index])

    # updates a single field in starting point so either x or y not both
    # where x_or_y_index is either 0 or 1
    def update_starting_point(self, name: str, x_or_y_index: int, value: int, index: int):
        self.label_data[name].starting_points[index][x_or_y_index] = value
        print("update starting point", self.label_data[name].starting_points[index])
        return self.label_data[name].starting_points[index]

    def update_xy_max_or_min(self, name: str, minMaxXY: str, value, index):
        match minMaxXY:
            case "min_X":
                self.label_data[name].min_X[index] = value
                return self.label_data[name].min_X[index]
            case "max_X":
                self.label_data[name].max_X[index] = value
                return self.label_data[name].max_X[index]
            case "min_Y":
                self.label_data[name].min_Y[index] = value
                return self.label_data[name].min_Y[index]
            case "max_Y":
                self.label_data[name].max_Y[index] = value
                return self.label_data[name].max_Y[index]
            case _:
                raise ValueError("Invalid min or max value")
