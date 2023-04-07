import bresenham_triangle_class

x1 = 2469
y1 = 362
x2 = 2470
y2 = 365
x3 = 2473
y3 = 365

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

print("slope method")
sloped = bresenham_triangle_class.BresenhamTriangle(MAX_WIDTH, MAX_HEIGHT)
print(type(x1),
      type(x1),
      type(y1),
      type(x2),
      type(y2),
      type(x3),
      type(y3),
      type(MAX_HEIGHT),
      type(MAX_WIDTH),
      )
filled_triangle_result = sloped.fill_triangle_by_slope(x1, y1, x2, y2, x3, y3)
print(filled_triangle_result, len(filled_triangle_result))

print("##### CLASS LOGIC #####")
# bresenham = bresenham_triangle_class.BresenhamTriangle()
# filled_triangle_result = bresenham.fill_triangle(x1, y1, x2, y2, x3, y3)
# print(filled_triangle_result)
bresenham = bresenham_triangle_class.BresenhamTriangle(MAX_WIDTH, MAX_HEIGHT)
x1, y1 = test_points["p1"]["x"], test_points["p1"]["y"]
# print(x1, y1, type(x1), type(y1))
x2, y2 = test_points["p2"]["x"], test_points["p2"]["y"]
x3, y3 = test_points["p3"]["x"], test_points["p3"]["y"]
filled_triangle_result = bresenham.fill_UV_triangle(x1, y1, x2, y2, x3, y3)
print(filled_triangle_result)
