from typing import Tuple
import numpy as np
from shapely.geometry import Point, Polygon
from Triangles import Triangle

MAX_TRIANGLES_PER_NODE = 700_000
MAX_DEPTH = 8





class QuadTreeNode:
    def __init__(self, boundary, depth=0):
        self.depth = depth
        self.boundary = boundary
        # triangles
        self.triangles = []
        self.children = [None, None, None, None]

    def insert_triangle(self, triangle: Triangle):
        # if it's not within the defined boundary ignore it
        if not self.boundary.intersects_triangle(triangle):
            return False
        # if it's not full then insert or if it's at the max depth
        if len(self.triangles) < MAX_TRIANGLES_PER_NODE or self.depth == MAX_DEPTH:
            self.triangles.append(triangle)
            return True
        else:
            if self.children[0] is None:
                self.split()

            if self.children[0].insert_triangle(triangle):
                return True
            elif self.children[1].insert_triangle(triangle):
                return True
            elif self.children[2].insert_triangle(triangle):
                return True
            elif self.children[3].insert_triangle(triangle):
                return True

            # if it fails all of them override and insert into the parent node, or at least try
            # we know it can't have intersected because of the first if statement, so it's safe to append
            self.triangles.append(triangle)
            print("All children failed to contain triangle inserting in parent")
        return False

    def split(self):
        sub_width = self.boundary.width / 2
        sub_height = self.boundary.height / 2
        x = self.boundary.x
        y = self.boundary.y

        self.children[0] = QuadTreeNode(Boundary(x + sub_width, y, sub_width, sub_height), self.depth + 1)
        self.children[1] = QuadTreeNode(Boundary(x, y, sub_width, sub_height), self.depth + 1)
        self.children[2] = QuadTreeNode(Boundary(x, y + sub_height, sub_width, sub_height), self.depth + 1)
        self.children[3] = QuadTreeNode(Boundary(x + sub_width, y + sub_height, sub_width, sub_height), self.depth + 1)

    def query(self, point):
        triangles_list = []
        if not self.boundary.contains_point(point):
            return triangles_list

        for triangle in self.triangles:
            if point_in_triangle(point, triangle):
                triangles_list.append(triangle)
                return triangles_list

        if self.children[0] is None:
            return triangles_list

        triangles_list += self.children[0].query(point)
        triangles_list += self.children[1].query(point)
        triangles_list += self.children[2].query(point)
        triangles_list += self.children[3].query(point)
        # for child in self.children:
        #     triangle = child.query(point)
        #     if triangle:
        #         triangles_list.append(triangle)
        #         return triangles_list

        return triangles_list


class Boundary:
    def __init__(self, x, y, width, height):
        # top left point
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rectangle = Polygon(
            [self.get_top_left(), self.get_top_right(), self.get_bottom_right(), self.get_bottom_left()])

    # def contains_point(self, point: Tuple):
    #     return self.x <= point[0] < self.x + self.width and self.y <= point[1] < self.y + self.height
    def contains_point(self, point: Tuple):
        if self.rectangle.contains(Point(point)):
            return True
        return False

    def intersects_triangle(self, triangle):
        # this will check if the whole triangle is in the rectangle, no intersection occurs
        for vertex in triangle.vertices:
            if self.contains_point(vertex):
                return True
        if self.rectangle.intersects(triangle.triangle):
            return True
        return False

    def get_top_left(self):
        return (self.x, self.y)

    def get_top_right(self):
        return (self.x + self.width, self.y)

    def get_bottom_left(self):
        return (self.x, self.y + self.height)

    def get_bottom_right(self):
        return (self.x + self.width, self.y + self.height)


# def point_in_triangle(point, triangle):
#     """
#     Check if a point lies within a triangle
#
#     Parameters:
#         triangle (list of tuples): A list of 3 vertices of the triangle [(x1,y1), (x2,y2), (x3,y3)]
#         point (tuple): A point to check (x,y)
#
#     Returns:
#         bool: True if the point lies within the triangle, False otherwise
#     """
#     p1, p2, p3 = triangle.vertices
#     p = point
#
#     # Calculate the vectors between the points
#     v1 = (p3[0] - p1[0], p3[1] - p1[1])
#     v2 = (p2[0] - p1[0], p2[1] - p1[1])
#     vp = (p[0] - p1[0], p[1] - p1[1])
#
#     # Calculate dot products
#     dot11 = v1[0] * v1[0] + v1[1] * v1[1]
#     dot12 = v1[0] * v2[0] + v1[1] * v2[1]
#     dot1p = v1[0] * vp[0] + v1[1] * vp[1]
#     dot22 = v2[0] * v2[0] + v2[1] * v2[1]
#     dot2p = v2[0] * vp[0] + v2[1] * vp[1]
#
#     # Calculate barycentric coordinates
#     invDenom = 1.0 / (dot11 * dot22 - dot12 * dot12)
#     u = (dot22 * dot1p - dot12 * dot2p) * invDenom
#     v = (dot11 * dot2p - dot12 * dot1p) * invDenom
#
#     # Check if point is in triangle
#     # if we do this the border is acceptable too idk idk if you want that
#     # return (u >= 0) and (v >= 0) and (u + v <= 1)
#     return (u >= 0) and (v >= 0) and (u + v < 1)


def point_in_triangle(p: tuple, triangle):
    p0, p1, p2 = triangle.vertices
    x0 = p[0]
    y0 = p[1]
    x1 = p0[0]
    y1 = p0[1]
    x2 = p1[0]
    y2 = p1[1]
    x3 = p2[0]
    y3 = p2[1]
    # print(x0, y0, x1, y1, x2, y2, x3, y3)
    b0 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    # There's a lot of uvs that are 0 in the model that we absolutely don't care about
    # because it means (I think) that they're untextured points
    if b0 != 0:
        b1 = ((x2 - x0) * (y3 - y0) - (x3 - x0) * (y2 - y0)) / b0
        b2 = ((x3 - x0) * (y1 - y0) - (x1 - x0) * (y3 - y0)) / b0
        b3 = ((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / b0
        if b1 > 0 and b2 > 0 and b3 > 0:
            # return [b1, b2, b3];
            return True
        else:
            # return [];
            return False
    return False


def print_num_triangles(node):
    """
    Recursively prints the number of triangles in each QuadNode of a given quadtree.
    """
    if node.children[0] is None:
        print(f"QuadNode at depth {node.depth} has {len(node.triangles)} triangle(s)")
    else:
        print(f"QuadNode at depth {node.depth} has {len(node.triangles)} triangle(s)")
        for child in node.children:
            print_num_triangles(child)


def print_tree(node, level=0):
    if node:
        print("    " * level + f"- {len(node.triangles)} triangles")
        for child in node.children:
            print_tree(child, level + 1)


def print_tree_counts_branched(node):
    if node:
        print("|--", len(node.triangles))
        for i in range(4):
            print("|", "   " * (node.depth + 1), end="")
            print_tree_counts_branched(node.children[i])


def print_quadtree(node, prefix=''):
    if node is None:
        return
    # elif not node.has_children():
    #     print(f"{prefix}└── {node.num_triangles}")
    #     return
    elif not node.children[0]:
        print(f"{prefix}└── {len(node.triangles)}")
        return
    children_str = ""
    for i, child in enumerate(node.children):
        if child is not None:
            if i == 0:
                children_str += "┌── "
            elif i == 3:
                children_str += "└── "
            else:
                children_str += "├── "
            children_str += f"{len(child.triangles)}\n"
    print(f"{prefix}{len(node.triangles)}")
    print_quadtree(node.children[0], prefix + "│   ")
    print(children_str, end="")
    print_quadtree(node.children[1], prefix + "│   ")
    print_quadtree(node.children[2], prefix + "│   ")
    print_quadtree(node.children[3], prefix + "    ")


if __name__ == "__main__":

    # create a list of triangles
    # triangles = [
    #     Triangle((.0, .0), (.0, .10), (.10, .0)),
    #     Triangle((.10,.10), (.0, .10), (.10, .0)),
    #     Triangle((.5, .5), (.15, .15), (.5, .15)),
    #     Triangle((.20,.20), (.10, .20), (.20, .10))
    # ]
    #
    # # create a boundary object with a range of (0,0) to (50,50)
    # boundary = Boundary(.0, .0, 1.0, 1.0)
    # # create a list of points to test
    # points = [(.2, .2), (.5, .5), (.7, .7), (.10, .10), (.15, .15), (.20, .20), (.25, .25)]

    # create a list of int triangles
    triangles = [
        Triangle((0, 0), (0, 10), (10, 0)),
        Triangle((10, 10), (0, 10), (10, 0)),
        Triangle((5, 5), (15, 15), (5, 15)),
        Triangle((20, 20), (10, 20), (20, 10))
    ]

    # create a boundary object with a range of (0,0) to (50,50)
    boundary = Boundary(0, 0, 50, 50)
    # create a list of points to test
    points = [(2, 2), (5, 5), (7, 7), (10, 10), (15, 15), (20, 20), (25, 25)]

    # create a quad tree with a max depth of 10
    quad_tree = QuadTreeNode(boundary)

    # insert each triangle into the quad tree
    for current_triangle in triangles:
        quad_tree.insert_triangle(current_triangle)

    # loop through each point and find the triangle(s) it is contained within
    for point in points:
        triangles_containing_point = quad_tree.query(point)
        if triangles_containing_point is not None:
            print(f"Point {point} is contained in the following triangles:\n {triangles_containing_point}")
        else:
            print(f"Point {point} not found ")

    print("#### Tree Print ###")
    print_num_triangles(quad_tree)
    print("Tree print 2")
    print_tree(quad_tree, 0)
    # print("Tree 3")
    # print_tree_counts_branched(quad_tree)
    # print("tree 4")
    # print_quadtree(quad_tree)
