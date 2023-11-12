from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class LabelData:
    name: str
    abr: str = ""
    starting_points: List[List[int]] = field(default_factory=list)
    acceptable_colors_rgb: List[List[int]] = field(default_factory=list)
    pixel_deviation: int = 0
    min_X: Union[List[int], None] = None
    max_X: Union[List[int], None] = None
    min_Y: Union[List[int], None] = None
    max_Y: Union[List[int], None] = None
    enable_default_range: bool = False


class PixelDataModel:

    def __init__(self):
        # dict of labeldata
        self.label_data: dict[str, LabelData] = {}

    def add_new_label(self, name: str):
        if self.label_data.get(name):
            raise ValueError("Label already exists")
        self.label_data[name] = LabelData(name)

    def edit_label(self, old_name: str, new_name: str):
        if new_name in self.label_data:
            raise ValueError("Label already exists")
        self.label_data[new_name] = self.label_data.pop(old_name)

    def add_starting_point(self, name: str, x: int, y: int):
        self.label_data[name].starting_points.append([x, y])

    def add_rgb_value(self, name: str, r: int, g: int, b: int):
        self.label_data[name].acceptable_colors_rgb.append([r, g, b])

    # updates a single field in rgb so either r,g, or b not both
    def update_rgb_value(self, name: str, rgb_value: int, color_index: int, item_index: int):
        r, g, b = self.label_data[name].acceptable_colors_rgb[item_index]
        self.label_data[name].acceptable_colors_rgb[item_index][color_index] = rgb_value
        print("update rgb value", [r, g, b], self.label_data[name].acceptable_colors_rgb[item_index])
