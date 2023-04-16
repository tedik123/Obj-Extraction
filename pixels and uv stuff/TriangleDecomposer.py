import math
import numpy as np


class TriangleDecomposer:

    def __init__(self, uv_p1, uv_p2, uv_p3, MAX_WIDTH, MAX_HEIGHT):
        self.uv_p1 = uv_p1
        self.uv_p2 = uv_p2
        self.uv_p3 = uv_p3
        # these will be our pixel points
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.MAX_WIDTH = MAX_WIDTH
        self.MAX_HEIGHT = MAX_HEIGHT
        self.create_pixel_coordinates()

    # I figure I should transform these to pixel coordinates again because pixels can only be integers
    def create_pixel_coordinates(self):
        p1_x, p1_y = self.uvs_to_pixels(self.uv_p1)
        self.p1 = {"x": p1_x, "y": p1_y}
        p2_x, p2_y = self.uvs_to_pixels(self.uv_p2)
        self.p2 = {"x": p2_x, "y": p2_y}
        p3_x, p3_y = self.uvs_to_pixels(self.uv_p3)
        self.p3 = {"x": p3_x, "y": p3_y}
        # for testing
        # self.p1 = {"x": 10, "y": 45}
        # self.p2 = {"x": 13, "y": 40}
        # self.p3 = {"x": 16, "y": 45}
        # print("pixel coords")
        # print("p1", self.p1)
        # print("p2", self.p2)
        # print("p3", self.p3)

    def uvs_to_pixels(self, uv):
        u = uv["x"]
        v = uv["y"]
        # since pixels are only ints we need to floor or use ceiling
        x = math.floor(u * self.MAX_WIDTH)
        # since 0, 0 is at the bottom left! very important
        y = math.floor((v - 1) * -self.MAX_HEIGHT)
        return x, y

    # https://stackoverflow.com/questions/37181829/determining-all-discrete-points-inside-a-triangle
    # this is I believe is called triangle rasterization
    def insideTriangle(self):
        # xs = np.array((x1, x2, x3), dtype=float)
        # ys = np.array((y1, y2, y3), dtype=float)
        # was float before but we only care about ints anyways!!!!
        xs = np.array((self.p1["x"], self.p2["x"], self.p3["x"]), dtype=int)
        ys = np.array((self.p1["y"], self.p2["y"], self.p3["y"]), dtype=int)

        # The possible range of coordinates that can be returned
        x_range = np.arange(np.min(xs), np.max(xs) + 1)
        y_range = np.arange(np.min(ys), np.max(ys) + 1)

        # Set the grid of coordinates on which the triangle lies. The centre of the
        # triangle serves as a criterion for what is inside or outside the triangle.
        X, Y = np.meshgrid(x_range, y_range)
        xc = np.mean(xs)
        yc = np.mean(ys)

        # From the array 'triangle', points that lie outside the triangle will be
        # set to 'False'.
        triangle = np.ones(X.shape, dtype=bool)
        for i in range(3):
            ii = (i + 1) % 3
            if xs[i] == xs[ii]:
                include = X * (xc - xs[i]) / abs(xc - xs[i]) > xs[i] * (xc - xs[i]) / abs(xc - xs[i])
            else:
                poly = np.poly1d(
                    [(ys[ii] - ys[i]) / (xs[ii] - xs[i]), ys[i] - xs[i] * (ys[ii] - ys[i]) / (xs[ii] - xs[i])])
                include = Y * (yc - poly(xc)) / abs(yc - poly(xc)) > poly(X) * (yc - poly(xc)) / abs(yc - poly(xc))
            triangle *= include

        # Output: 2 arrays with the x- and y- coordinates of the points inside the
        # triangle.
        return X[triangle], Y[triangle]

    # https://stackoverflow.com/questions/25837544/get-all-points-of-a-straight-line-in-python
    def get_line(self, x1, y1, x2, y2):
        points = []
        issteep = abs(y2 - y1) > abs(x2 - x1)
        if issteep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        deltax = x2 - x1
        deltay = abs(y2 - y1)
        error = int(deltax / 2)
        y = y1
        ystep = None
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            if issteep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax
        # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points

    def get_all_points_of_triangle(self):
        inside_x, inside_y = self.insideTriangle()
        inside = list(zip(inside_x, inside_y))
        line1 = self.get_line(self.p1["x"], self.p1["y"], self.p2["x"], self.p2["y"])
        line2 = self.get_line(self.p1["x"], self.p1["y"], self.p3["x"], self.p3["y"])
        line3 = self.get_line(self.p2["x"], self.p2["y"], self.p3["x"], self.p3["y"])
        # result = inside + line1 + line2 + line3
        # print(f"No set {len(result)}", result )
        # return inside + line1 + line2 + line3]
        # this removes all duplicates from the list!
        return list(set(inside + line1 + line2 + line3))

    # def edge_walk_algo(self):
    #     buffer = []
    #     # Sort vertices by y-coordinate
    #     vertices = [self.p1, self.p2, self.p3]
    #     vertices.sort(key=lambda p: p["y"])
    #     print(vertices)
    #     # vertices.sort(key=lambda p: p[1])
    #     # Initialize edge variables
    #     x1, y1 = vertices[0]
    #     x2, y2 = vertices[0]
    #     dx1 = (vertices[1]["x"] - vertices[0]["x"]) << 16
    #     dy1 = (vertices[1]["y"] - vertices[0]["y"]) << 16
    #     dx2 = (vertices[2]["x"] - vertices[0]["x"]) << 16
    #     dy2 = (vertices[2]["y"] - vertices[0]["y"]) << 16
    #     # Fill top half of triangle
    #     while y1 <= vertices[1]["y"]:
    #         for x in range(x1 >> 16, x2 >> 16 + 1):
    #             # buffer[x, y1] = color
    #             buffer.append((x, y1))
    #         x1 += dx1
    #         y1 += dy1
    #         x2 += dx2
    #         y2 += dy2
    #         if y1 == vertices[1]["y"]:
    #             dx1 = (vertices[2]["x"] - vertices[1]["x"]) << 16
    #             dy1 = (vertices[2]["y"] - vertices[1]["y"]) << 16
    #     # Initialize edge variables for bottom half of triangle
    #     x2, y2 = vertices[1]
    #     dx2 = (vertices[2]["x"] - vertices[1]["x"]) << 16
    #     dy2 = (vertices[2]["y"] - vertices[1]["y"]) << 16
    #     # Fill bottom half of triangle
    #     while y1 <= vertices[2]["y"]:
    #         for x in range(x1 >> 16, x2 >> 16 + 1):
    #             # buffer[x, y1] = color
    #             buffer.append((x, y1))
    #         x1 += dx1
    #         y1 += dy1
    #         x2 += dx2
    #         y2 += dy2
    #     return buffer
    def edge_walk_algo(self):
        buffer = []
        p1 = [self.p1["x"], self.p1["y"]]
        p2 = [self.p2["x"], self.p2["y"]]
        p3 = [self.p3["x"], self.p3["y"]]
        # Sort vertices by y-coordinate
        vertices = [p1, p2, p3]
        vertices.sort(key=lambda p: p[1])
        print(vertices)
        # Initialize edge variables
        x1, y1 = vertices[0]
        x2, y2 = vertices[0]
        dx1 = (vertices[1][0] - vertices[0][0]) << 16
        dy1 = (vertices[1][1] - vertices[0][1]) << 16
        dx2 = (vertices[2][0] - vertices[0][0]) << 16
        dy2 = (vertices[2][1] - vertices[0][1]) << 16

        # Fill top half of triangle
        while y1 <= vertices[1][1]:
            for x_cur in range(x1 >> 16, x2 >> 16 + 1):
                # buffer[x, y1] = color
                buffer.append((x_cur, y1))
                print(x_cur, y1)

            x1 += dx1
            y1 += dy1
            x2 += dx2
            y2 += dy2
            if y1 == vertices[1][1]:
                dx1 = (vertices[2][0] - vertices[1][0]) << 16
                dy1 = (vertices[2][1] - vertices[1][1]) << 16

        # Initialize edge variables for bottom half of triangle
        x2, y2 = vertices[1]
        dx2 = (vertices[2][0] - vertices[1][0]) << 16
        dy2 = (vertices[2][1] - vertices[1][1]) << 16

        # Fill bottom half of triangle
        while y1 <= vertices[2][1]:
            for x_cur in range(x1 >> 16, x2 >> 16 + 1):
                buffer.append((x_cur, y1))
            x1 += dx1
            y1 += dy1
            x2 += dx2
            y2 += dy2
        return buffer


# https://print-graph-paper.com/virtual-graph-paper
if __name__ == "__main__":
    MAX_HEIGHT = 4096
    MAX_WIDTH = 4096
    test_points = {
        "p1": {
            "x": 0.6029899716377258,
            "y": 0.9115300178527832
        },
        "p2": {
            "x": 0.6031299829483032,
            "y": 0.910830020904541
        },
        "p3": {
            "x": 0.6038500070571899,
            "y": 0.9107900261878967
        }
    }
    uv_p1 = test_points["p1"]
    uv_p2 = test_points["p2"]
    uv_p3 = test_points["p3"]
    decompose = TriangleDecomposer(uv_p1, uv_p2, uv_p3, MAX_WIDTH, MAX_HEIGHT)
    x, y = decompose.insideTriangle()
    print(type(x))
    print(x)
    print(y)
    coords = list(zip(x, y))
    print(coords)
    # line_points = decompose.get_line(10, 45, 16, 45)
    # TODO we need to do this for each line that connects to form the triangle...so 3 times!
    #   and also call inside triangle and that should give us every single point that makes up the triangle...I hope
    line_points = decompose.get_line(25, 30, 27, 28)
    print("line points", line_points)
    all_points = decompose.get_all_points_of_triangle()
    print(f"all lines {len(all_points)}", all_points)
    just_inside = list(zip(decompose.insideTriangle()))
    print(f"just inside {len(just_inside)}", just_inside)

    print("########")
    edge_walk_result = [(2469, 362), (2469, 363) ,(2470, 363), (2470, 364), (2471, 364), (2472, 364), (2470, 365), (2471, 365), (2472, 365), (2473, 365)]
    print(edge_walk_result, len(edge_walk_result))
    print("edge walk")
    print(decompose.edge_walk_algo())
