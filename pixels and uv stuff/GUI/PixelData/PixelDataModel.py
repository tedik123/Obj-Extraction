from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class LabelData:
    label: str
    starting_points: List[List[int]]
    acceptable_colors_rgb: List[List[int]]
    pixel_deviation: int = 0
    min_X: Union[List[int], None] = None
    max_X: Union[List[int], None] = None
    min_Y: Union[List[int], None] = None
    max_Y: Union[List[int], None] = None
    enable_default_range: bool = False


class PixelDataModel:

    def __init__(self):
        self.starting_points: List[int] = []

    def add_starting_point(self, x: int, y: int):
        self.starting_points.append([x, y])

    def add_rgb_value(self, r: int, g: int, b: int, index=None):
        pass
        # self.acceptable_colors_rgb.append([r, g, b])

    def increment_rgb_value(self, rgb_value: int, color_index: int, item_index: int):
        pass
        # self.acceptable_colors_rgb[item_index][color_index] = rgb_value
