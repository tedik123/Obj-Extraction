class Quadtree:
    def __init__(self, depth, bounds):
        self.depth = depth
        self.bounds = bounds
        self.triangles = []
        self.children = None

    def insert(self, triangle):
        if not intersects(triangle, self.bounds):
            return False

        if len(self.triangles) < 4 and self.children is None:
            self.triangles.append(triangle)
            return True

        if self.children is None:
            self.subdivide()

        for child in self.children:
            if child.insert(triangle):
                return True

        self.triangles.append(triangle)
        return True

    def subdivide(self):
        x, y, w, h = self.bounds
        self.children = [
            Quadtree(self.depth + 1, (x, y, w / 2, h / 2)),
            Quadtree(self.depth + 1, (x + w / 2, y, w / 2, h / 2)),
            Quadtree(self.depth + 1, (x, y + h / 2, w / 2, h / 2)),
            Quadtree(self.depth + 1, (x + w / 2, y + h / 2, w / 2, h / 2))
        ]
        for triangle in self.triangles:
            for child in self.children:
                child.insert(triangle)
        self.triangles = []

    def query_point(self, point):
        if not contains(self.bounds, point):
            return []
        triangles = self.triangles[:]
        if self.children is not None:
            for child in self.children:
                triangles += child.query_point(point)
        return triangles

    def query_rectangle(self, rect):
        if not intersects(self.bounds, rect):
            return []
        triangles = self.triangles[:]
        if self.children is not None:
            for child in self.children:
                triangles += child.query_rectangle(rect)
        return triangles


def intersects(triangle, rect):
    x, y, w, h = rect
    x1, y1 = triangle[0]
    x2, y2 = triangle[1]
    x3, y3 = triangle[2]
    return (contains(rect, (x1, y1)) or contains(rect, (x2, y2)) or contains(rect, (x3, y3))) or \
        (line_rect_intersect(x1, y1, x2, y2, rect) or
         line_rect_intersect(x2, y2, x3, y3, rect) or
         line_rect_intersect(x3, y3, x1, y1, rect))


def contains(rect, point):
    x, y, w, h = rect
    px, py = point
    return x <= px < x + w and y <= py < y + h


def line_rect_intersect(x1, y1, x2, y2, rect):
    x, y, w, h = rect
    return (line_intersect(x1, y1, x2, y2, x, y, x, y + h) or
            line_intersect(x1, y1, x2, y2, x, y + h, x + w, y + h) or
            line_intersect(x1, y1, x2, y2, x + w, y + h, x + w, y) or
            line_intersect(x1, y1, x2, y2, x + w, y, x, y))


def line_intersect(p1, p2, q1, q2):
    """Find the intersection point of two lines defined by (p1, p2) and (q1, q2).

    Returns None if the lines are parallel or collinear.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:  # lines are parallel
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ua < 0 or ua > 1 or ub < 0 or ub > 1:  # intersection point is outside the line segments
        return None
    # calculate and return the intersection point
    x = x1 + ua * (x2 - x1)
    y = y1 + ua * (y2 - y1)
    return (x, y)

def point_in_triangle(triangle, point):
    """
    Check if a point lies within a triangle

    Parameters:
        triangle (list of tuples): A list of 3 vertices of the triangle [(x1,y1), (x2,y2), (x3,y3)]
        point (tuple): A point to check (x,y)

    Returns:
        bool: True if the point lies within the triangle, False otherwise
    """
    p1, p2, p3 = triangle
    p = point

    # Calculate the vectors between the points
    v1 = (p3[0]-p1[0], p3[1]-p1[1])
    v2 = (p2[0]-p1[0], p2[1]-p1[1])
    vp = (p[0]-p1[0], p[1]-p1[1])

    # Calculate dot products
    dot11 = v1[0]*v1[0] + v1[1]*v1[1]
    dot12 = v1[0]*v2[0] + v1[1]*v2[1]
    dot1p = v1[0]*vp[0] + v1[1]*vp[1]
    dot22 = v2[0]*v2[0] + v2[1]*v2[1]
    dot2p = v2[0]*vp[0] + v2[1]*vp[1]

    # Calculate barycentric coordinates
    invDenom = 1.0 / (dot11 * dot22 - dot12 * dot12)
    u = (dot22 * dot1p - dot12 * dot2p) * invDenom
    v = (dot11 * dot2p - dot12 * dot1p) * invDenom

    # Check if point is in triangle
    return (u >= 0) and (v >= 0) and (u + v < 1)



def get_triangles_for_point(point, quad_tree):
    triangles = []
    for node in quad_tree.get_leaf_nodes_containing_point(point):
        for triangle in node.triangles:
            if point_in_triangle(point, triangle):
                triangles.append(triangle)
    return triangles


# Example usage
points = [(1, 1), (2, 3), (4, 5)]
triangles = [((0, 0), (0, 4), (4, 0)), ((4, 4), (4, 0), (0, 4))]
quad_tree = Quadtree((0, 0, 4, 4))
for t in triangles:
    quad_tree.insert(t)

for p in points:
    triangles_for_point = get_triangles_for_point(p, quad_tree)
    print(f"Triangles containing point {p}: {triangles_for_point}")
