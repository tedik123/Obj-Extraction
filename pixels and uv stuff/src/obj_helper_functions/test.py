from obj_helper_functions import get_neighbors_from_point, get_neighbors_from_points, DFS

starting_coords = (50, 50)
# point_list = [(23, 72), (6, 94), (56, 84), (89, 50), (31, 17)]
# results = []
# for point in point_list:
#     result = get_neighbors_from_point(point[0], point[1], 100, 100)
#     results.append(result)
#
# for result in results:
#     print(result)
#
# result = get_neighbors_from_points(point_list, 100, 100)
# print("OKAY")
# for result in results:
#     print(result)

# * destructures it is NOT a pointer!
# result = get_neighbors_from_point(*point, 100, 100)
# print("Length of result", len(result))
# for pair in result:
#     print("{{" + f"{pair[0]}, {pair[1]}" + "}, {255, 0, 0}}")

label_name = "red"
# min_X, minY, max_X, max_Y = 0, 0, 4096, 4096
min_X, minY, max_X, max_Y = 49, 49, 51, 51
result = DFS(starting_coords, label_name, min_X, minY, max_X, max_Y)
print("Length of result", len(result))
print(result)
