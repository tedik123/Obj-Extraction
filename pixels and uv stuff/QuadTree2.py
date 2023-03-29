from typing import List, Tuple
import numpy as np


class Triangle:
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]):
        self.vertices = np.array([p1, p2, p3])
        self.xmin = np.min(self.vertices[:, 0])
        self.ymin = np.min(self.vertices[:, 1])
        self.xmax = np.max(self.vertices[:, 0])
        self.ymax = np.max(self.vertices[:, 1])

    def contains_point(self, point: Tuple[float, float]) -> bool:
        # Implement point-in-triangle test
        # ...
        return True  # Replace with actual implementation


class Quadtree:
    def __init__(self, boundary: Tuple[float, float, float, float], capacity: int = 4):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.children = [None, None, None, None]

    def insert(self, triangle: Triangle) -> bool:
        if not self.contains(triangle):
            return False

        if len(self.points) < self.capacity and all(self.children[i] is None for i in range(4)):
            self.points.append(triangle)
            return True

        if all(self.children[i] is None for i in range(4)):
            self.subdivide()

        for child in self.children:
            if child.insert(triangle):
                return True

        return False

    def subdivide(self):
        xmid = (self.boundary[0] + self.boundary[2]) / 2
        ymid = (self.boundary[1] + self.boundary[3]) / 2

        self.children[0] = Quadtree((self.boundary[0], self.boundary[1], xmid, ymid), self.capacity)
        self.children[1] = Quadtree((xmid, self.boundary[1], self.boundary[2], ymid), self.capacity)
        self.children[2] = Quadtree((self.boundary[0], ymid, xmid, self.boundary[3]), self.capacity)
        self.children[3] = Quadtree((xmid, ymid, self.boundary[2], self.boundary[3]), self.capacity)

    def contains(self, triangle: Triangle) -> bool:
        if triangle.xmin > self.boundary[2] or triangle.xmax < self.boundary[0] \
                or triangle.ymin > self.boundary[3] or triangle.ymax < self.boundary[1]:
            return False
        return True

    def find_triangles_containing_point(self, point: Tuple[float, float]) -> List[Triangle]:
        triangles = []
        if not self.contains((point, point)):
            return triangles

        for triangle in self.points:
            if triangle.contains_point(point):
                triangles.append(triangle)

        if any(child is not None for child in self.children):
            for child in self.children:
                triangles += child.find_triangles_containing_point(point)

        return triangles


# Construct the quadtree
boundary = (0.0, 0.0, 1.0, 1.0)
quadtree = Quadtree(boundary)

# Insert triangles into the quadtree
triangles = [Triangle((0.1, 0.1), (0.5, 0.9), (0.9, 0.1)),
             Triangle((0.2, 0.2), (.3, .4), (.4, .4))]

for triangle in triangles:
    quadtree.insert(triangle)

quadtree.find_triangles_containing_point((.1, .2))
