from typing import Tuple

import numpy as np
from shapely import Polygon


class Triangle:
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], index: int):
        self.vertices = np.array([p1, p2, p3])
        # self.xmin = np.min(self.vertices[:, 0])
        # self.ymin = np.min(self.vertices[:, 1])
        # self.xmax = np.max(self.vertices[:, 0])
        # self.ymax = np.max(self.vertices[:, 1])
        self.triangle = Polygon([p1, p2, p3])
        self.index_value = index

    def __str__(self):
        return self.vertices.__str__()
        # return self.vertices.__repr__()

    def __repr__(self):
        return self.vertices.__str__()
        # return self.vertices.__repr__()