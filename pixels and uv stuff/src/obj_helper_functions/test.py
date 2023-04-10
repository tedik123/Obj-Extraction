import time
import time
import numpy as np
from PIL import Image
from obj_helper_functions import get_neighbors_from_point, get_neighbors_from_points, PixelGrabber_C, \
    test_numpy_index, test_numpy_3D_print

# starting_coords = (50, 50)
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

# label_name = "red"
# # min_X, minY, max_X, max_Y = 0, 0, 4096, 4096
# min_X, minY, max_X, max_Y = 49, 49, 51, 51
# result = DFS(starting_coords, label_name, min_X, minY, max_X, max_Y)
# print("Length of result", len(result))
# print(result)


# start = time.perf_counter()
#
# coords_dict = {
#     (50, 50): (255, 0, 0),  # matches to red acceptable colors
#     (51, 49): (255, 0, 0),
#     (50, 49): (255, 0, 0),
#     (49, 49): (255, 0, 0),
#     (49, 50): (255, 0, 0),
#     (49, 51): (255, 0, 0),
#     (50, 51): (255, 0, 0),
#     (51, 51): (255, 0, 0),
#     (51, 50): (255, 0, 0)
# }
acceptable_colors_by_label = {
    "red": {(255, 0, 0): True, (128, 0, 0): True, (255, 99, 71): True},
    # "green": [[0, 255, 0], [0, 128, 0], [34, 139, 34]],
    # "blue": [[0, 0, 255], [0, 0, 128], [65, 105, 225]],
    # "yellow": [[255, 255, 0], [255, 215, 0], [255, 255, 224]],
    # "purple": [[128, 0, 128], [75, 0, 130], [218, 112, 214]]
}
# pixel_grabber = PixelGrabber_C(coords_dict, acceptable_colors_by_label)
# min_X, minY, max_X, max_Y = 49, 49, 51, 51
# label_name = "red"
# result = pixel_grabber.DFS(starting_coords, label_name, min_X, minY, max_X, max_Y)
# print("Length of result", len(result))
# print(result)
#
# end = time.perf_counter()
# print()
# print(f"Finished finding pixels...Took {end - start} seconds")

y, x = 50, 550
# y, x = 10, 10

def open_Image_Pillow_numpy():
    texture_file_path = "diffuse.jpg"
    start = time.perf_counter()
    print("Numpy image....")
    img = Image.open(texture_file_path)
    data = np.array(img)
    end = time.perf_counter()
    print(f"NUMPY pillow Time {end - start}")
    # numpy is flipped!
    # print(data[10][10])
    print(data[y][x])
    print(data.dtype)
    print(data.shape)
    return data


data = open_Image_Pillow_numpy()
test_numpy_index(data, y, x)
# test_numpy_3D_print(data)
pixel_grabber_test = PixelGrabber_C(data, acceptable_colors_by_label)
pixel_grabber_test.pixel_indexer(x, y)
