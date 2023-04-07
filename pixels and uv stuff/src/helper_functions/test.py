from obj_helper_functions import get_neighbors_from_point, get_neighbors_from_points

point_list = [(23, 72), (6, 94), (56, 84), (89, 50), (31, 17)]
results = []
for point in point_list:
    result = get_neighbors_from_point(point[0], point[1], 100, 100)
    results.append(result)

for result in results:
    print(result)

result = get_neighbors_from_points(point_list, 100, 100)
print("OKAY")
for result in results:
    print(result)
