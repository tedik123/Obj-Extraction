from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class LabelData:
    label: str
    starting_points: List[List[Union[int, int]]]
    acceptable_colors_rgb: List[List[int]]
    pixel_deviation: int = 0
    min_X: Union[List[int], None] = None
    max_X: Union[List[int], None] = None
    min_Y: Union[List[int], None] = None
    max_Y: Union[List[int], None] = None
    enable_default_range: bool = False


class PixelListModel:

    def __init__(self):
        pass
