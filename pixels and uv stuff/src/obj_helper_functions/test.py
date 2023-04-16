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
# acceptable_colors_by_label = {
#     "red": {(255, 0, 0): True, (128, 0, 0): True, (255, 99, 71): True},
#     # "green": [[0, 255, 0], [0, 128, 0], [34, 139, 34]],
#     # "blue": [[0, 0, 255], [0, 0, 128], [65, 105, 225]],
#     # "yellow": [[255, 255, 0], [255, 215, 0], [255, 255, 224]],
#     # "purple": [[128, 0, 128], [75, 0, 130], [218, 112, 214]]
# }

acceptable_colors_by_label = {
    "Deltoid": {(253, 253, 253): True, (253, 253, 254): True, (253, 253, 255): True, (253, 254, 253): True,
                (253, 254, 254): True, (253, 254, 255): True, (253, 255, 253): True, (253, 255, 254): True,
                (253, 255, 255): True, (254, 253, 253): True, (254, 253, 254): True, (254, 253, 255): True,
                (254, 254, 253): True, (254, 254, 254): True, (254, 254, 255): True, (254, 255, 253): True,
                (254, 255, 254): True, (254, 255, 255): True, (255, 253, 253): True, (255, 253, 254): True,
                (255, 253, 255): True, (255, 254, 253): True, (255, 254, 254): True, (255, 254, 255): True,
                (255, 255, 253): True, (255, 255, 254): True, (255, 255, 255): True, (217, 153, 187): True,
                (217, 153, 188): True, (217, 153, 189): True, (217, 153, 190): True, (217, 153, 191): True,
                (217, 153, 192): True, (217, 153, 193): True, (217, 154, 187): True, (217, 154, 188): True,
                (217, 154, 189): True, (217, 154, 190): True, (217, 154, 191): True, (217, 154, 192): True,
                (217, 154, 193): True, (217, 155, 187): True, (217, 155, 188): True, (217, 155, 189): True,
                (217, 155, 190): True, (217, 155, 191): True, (217, 155, 192): True, (217, 155, 193): True,
                (217, 156, 187): True, (217, 156, 188): True, (217, 156, 189): True, (217, 156, 190): True,
                (217, 156, 191): True, (217, 156, 192): True, (217, 156, 193): True, (217, 157, 187): True,
                (217, 157, 188): True, (217, 157, 189): True, (217, 157, 190): True, (217, 157, 191): True,
                (217, 157, 192): True, (217, 157, 193): True, (217, 158, 187): True, (217, 158, 188): True,
                (217, 158, 189): True, (217, 158, 190): True, (217, 158, 191): True, (217, 158, 192): True,
                (217, 158, 193): True, (217, 159, 187): True, (217, 159, 188): True, (217, 159, 189): True,
                (217, 159, 190): True, (217, 159, 191): True, (217, 159, 192): True, (217, 159, 193): True,
                (218, 153, 187): True, (218, 153, 188): True, (218, 153, 189): True, (218, 153, 190): True,
                (218, 153, 191): True, (218, 153, 192): True, (218, 153, 193): True, (218, 154, 187): True,
                (218, 154, 188): True, (218, 154, 189): True, (218, 154, 190): True, (218, 154, 191): True,
                (218, 154, 192): True, (218, 154, 193): True, (218, 155, 187): True, (218, 155, 188): True,
                (218, 155, 189): True, (218, 155, 190): True, (218, 155, 191): True, (218, 155, 192): True,
                (218, 155, 193): True, (218, 156, 187): True, (218, 156, 188): True, (218, 156, 189): True,
                (218, 156, 190): True, (218, 156, 191): True, (218, 156, 192): True, (218, 156, 193): True,
                (218, 157, 187): True, (218, 157, 188): True, (218, 157, 189): True, (218, 157, 190): True,
                (218, 157, 191): True, (218, 157, 192): True, (218, 157, 193): True, (218, 158, 187): True,
                (218, 158, 188): True, (218, 158, 189): True, (218, 158, 190): True, (218, 158, 191): True,
                (218, 158, 192): True, (218, 158, 193): True, (218, 159, 187): True, (218, 159, 188): True,
                (218, 159, 189): True, (218, 159, 190): True, (218, 159, 191): True, (218, 159, 192): True,
                (218, 159, 193): True, (219, 153, 187): True, (219, 153, 188): True, (219, 153, 189): True,
                (219, 153, 190): True, (219, 153, 191): True, (219, 153, 192): True, (219, 153, 193): True,
                (219, 154, 187): True, (219, 154, 188): True, (219, 154, 189): True, (219, 154, 190): True,
                (219, 154, 191): True, (219, 154, 192): True, (219, 154, 193): True, (219, 155, 187): True,
                (219, 155, 188): True, (219, 155, 189): True, (219, 155, 190): True, (219, 155, 191): True,
                (219, 155, 192): True, (219, 155, 193): True, (219, 156, 187): True, (219, 156, 188): True,
                (219, 156, 189): True, (219, 156, 190): True, (219, 156, 191): True, (219, 156, 192): True,
                (219, 156, 193): True, (219, 157, 187): True, (219, 157, 188): True, (219, 157, 189): True,
                (219, 157, 190): True, (219, 157, 191): True, (219, 157, 192): True, (219, 157, 193): True,
                (219, 158, 187): True, (219, 158, 188): True, (219, 158, 189): True, (219, 158, 190): True,
                (219, 158, 191): True, (219, 158, 192): True, (219, 158, 193): True, (219, 159, 187): True,
                (219, 159, 188): True, (219, 159, 189): True, (219, 159, 190): True, (219, 159, 191): True,
                (219, 159, 192): True, (219, 159, 193): True, (220, 153, 187): True, (220, 153, 188): True,
                (220, 153, 189): True, (220, 153, 190): True, (220, 153, 191): True, (220, 153, 192): True,
                (220, 153, 193): True, (220, 154, 187): True, (220, 154, 188): True, (220, 154, 189): True,
                (220, 154, 190): True, (220, 154, 191): True, (220, 154, 192): True, (220, 154, 193): True,
                (220, 155, 187): True, (220, 155, 188): True, (220, 155, 189): True, (220, 155, 190): True,
                (220, 155, 191): True, (220, 155, 192): True, (220, 155, 193): True, (220, 156, 187): True,
                (220, 156, 188): True, (220, 156, 189): True, (220, 156, 190): True, (220, 156, 191): True,
                (220, 156, 192): True, (220, 156, 193): True, (220, 157, 187): True, (220, 157, 188): True,
                (220, 157, 189): True, (220, 157, 190): True, (220, 157, 191): True, (220, 157, 192): True,
                (220, 157, 193): True, (220, 158, 187): True, (220, 158, 188): True, (220, 158, 189): True,
                (220, 158, 190): True, (220, 158, 191): True, (220, 158, 192): True, (220, 158, 193): True,
                (220, 159, 187): True, (220, 159, 188): True, (220, 159, 189): True, (220, 159, 190): True,
                (220, 159, 191): True, (220, 159, 192): True, (220, 159, 193): True, (221, 153, 187): True,
                (221, 153, 188): True, (221, 153, 189): True, (221, 153, 190): True, (221, 153, 191): True,
                (221, 153, 192): True, (221, 153, 193): True, (221, 154, 187): True, (221, 154, 188): True,
                (221, 154, 189): True, (221, 154, 190): True, (221, 154, 191): True, (221, 154, 192): True,
                (221, 154, 193): True, (221, 155, 187): True, (221, 155, 188): True, (221, 155, 189): True,
                (221, 155, 190): True, (221, 155, 191): True, (221, 155, 192): True, (221, 155, 193): True,
                (221, 156, 187): True, (221, 156, 188): True, (221, 156, 189): True, (221, 156, 190): True,
                (221, 156, 191): True, (221, 156, 192): True, (221, 156, 193): True, (221, 157, 187): True,
                (221, 157, 188): True, (221, 157, 189): True, (221, 157, 190): True, (221, 157, 191): True,
                (221, 157, 192): True, (221, 157, 193): True, (221, 158, 187): True, (221, 158, 188): True,
                (221, 158, 189): True, (221, 158, 190): True, (221, 158, 191): True, (221, 158, 192): True,
                (221, 158, 193): True, (221, 159, 187): True, (221, 159, 188): True, (221, 159, 189): True,
                (221, 159, 190): True, (221, 159, 191): True, (221, 159, 192): True, (221, 159, 193): True,
                (222, 153, 187): True, (222, 153, 188): True, (222, 153, 189): True, (222, 153, 190): True,
                (222, 153, 191): True, (222, 153, 192): True, (222, 153, 193): True, (222, 154, 187): True,
                (222, 154, 188): True, (222, 154, 189): True, (222, 154, 190): True, (222, 154, 191): True,
                (222, 154, 192): True, (222, 154, 193): True, (222, 155, 187): True, (222, 155, 188): True,
                (222, 155, 189): True, (222, 155, 190): True, (222, 155, 191): True, (222, 155, 192): True,
                (222, 155, 193): True, (222, 156, 187): True, (222, 156, 188): True, (222, 156, 189): True,
                (222, 156, 190): True, (222, 156, 191): True, (222, 156, 192): True, (222, 156, 193): True,
                (222, 157, 187): True, (222, 157, 188): True, (222, 157, 189): True, (222, 157, 190): True,
                (222, 157, 191): True, (222, 157, 192): True, (222, 157, 193): True, (222, 158, 187): True,
                (222, 158, 188): True, (222, 158, 189): True, (222, 158, 190): True, (222, 158, 191): True,
                (222, 158, 192): True, (222, 158, 193): True, (222, 159, 187): True, (222, 159, 188): True,
                (222, 159, 189): True, (222, 159, 190): True, (222, 159, 191): True, (222, 159, 192): True,
                (222, 159, 193): True, (223, 153, 187): True, (223, 153, 188): True, (223, 153, 189): True,
                (223, 153, 190): True, (223, 153, 191): True, (223, 153, 192): True, (223, 153, 193): True,
                (223, 154, 187): True, (223, 154, 188): True, (223, 154, 189): True, (223, 154, 190): True,
                (223, 154, 191): True, (223, 154, 192): True, (223, 154, 193): True, (223, 155, 187): True,
                (223, 155, 188): True, (223, 155, 189): True, (223, 155, 190): True, (223, 155, 191): True,
                (223, 155, 192): True, (223, 155, 193): True, (223, 156, 187): True, (223, 156, 188): True,
                (223, 156, 189): True, (223, 156, 190): True, (223, 156, 191): True, (223, 156, 192): True,
                (223, 156, 193): True, (223, 157, 187): True, (223, 157, 188): True, (223, 157, 189): True,
                (223, 157, 190): True, (223, 157, 191): True, (223, 157, 192): True, (223, 157, 193): True,
                (223, 158, 187): True, (223, 158, 188): True, (223, 158, 189): True, (223, 158, 190): True,
                (223, 158, 191): True, (223, 158, 192): True, (223, 158, 193): True, (223, 159, 187): True,
                (223, 159, 188): True, (223, 159, 189): True, (223, 159, 190): True, (223, 159, 191): True,
                (223, 159, 192): True, (223, 159, 193): True}

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
# test_numpy_index(data, y, x)
# test_numpy_3D_print(data)
pixel_grabber_test = PixelGrabber_C(data, acceptable_colors_by_label)
# pixel_grabber_test.pixel_indexer(x, y)
start_time = time.perf_counter()

starting_points = [[155, 2164], [1377, 2355]]
results = []
for start in starting_points:
    result = pixel_grabber_test.DFS(start, "Deltoid", 0, 0, 4096, 4096)
    results.append(result)
sum_result = 0
for result in results:
    sum_result += len(result)
print("Length of results", sum_result)
end = time.perf_counter()
print()
print(f"Finished finding pixels...Took {end - start_time} seconds")
