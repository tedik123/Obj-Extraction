from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class LabelData:
    label: str
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
        self.starting_points: List[int] = []

    def add_label(self, label: str):
        self.label_data[label] = LabelData(label)

    def add_starting_point(self, label: str, x: int, y: int):
        self.label_data[label].starting_points.append([x, y])

    def add_rgb_value(self, label: str, r: int, g: int, b: int):
        self.label_data[label].acceptable_colors_rgb.append([r, g, b])

    # updates a single field in rgb so either r,g, or b not both
    def update_rgb_value(self, label: str, rgb_value: int, color_index: int, item_index: int):
        r, g, b = self.label_data[label].acceptable_colors_rgb[item_index]
        self.label_data[label].acceptable_colors_rgb[item_index][color_index] = rgb_value
        print("update rgb value", [r, g, b], self.label_data[label].acceptable_colors_rgb[item_index])
