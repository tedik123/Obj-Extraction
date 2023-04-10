import json
import pickle
import time
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
from collections import deque
from multiprocessing import cpu_count

import numpy as np
from PIL import Image, ImageColor
from obj_helper_functions import get_neighbors_from_point, PixelGrabber_C


class PixelGrabber:
    # if label name is none we do all them otherwise it's all of them
    # takes in an array of label names to do
    def __init__(self, texture_file_path, label_names=None, pixel_deviation=0, ):
    # def __init__(self):
        self.pixel_deviation = pixel_deviation
        self.enable_default_color_range = True
        self.label_starts = self.read_in_label_starts()
        self.texture_file = 'obj textures/diffuse.jpg'
        # self.texture_file = texture_file_path
        self.label_names = label_names
        self.coords_dict, self.max_width, self.max_height, self.mode, self.pixels = None, None, None, None, None
        # self.coords_dict = {
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
        #
        # self.acceptable_colors_by_label = {
        #     "red": [(255, 0, 0), (128, 0, 0), (255, 99, 71)],
        #     "green": [[0, 255, 0], [0, 128, 0], [34, 139, 34]],
        #     "blue": [[0, 0, 255], [0, 0, 128], [65, 105, 225]],
        #     "yellow": [[255, 255, 0], [255, 215, 0], [255, 255, 224]],
        #     "purple": [[128, 0, 128], [75, 0, 130], [218, 112, 214]]
        # }
        #

        self.acceptable_colors_by_label = {}
        self.default_acceptable_colors_dict = {}

        #   temp remove later
        # self.neighbor_total_time = 0

    # opens the texture image and gets all the pixels and width as well the rgb by pixel coordinate
    def set_and_create_image_data(self):
        print("Grabbing pixels and rgbs....")
        self.coords_dict, self.max_width, self.max_height, self.mode, self.pixels = self.get_pixel_coords()

    def disable_default_color_range(self):
        self.enable_default_color_range = False

    def read_in_label_starts(self):
        print("Loading in label starts...")
        # testing line
        # with open('starts/test_template.json', 'r') as file:
        # this is the normal one to be used
        with open('starts/label_starts.json', 'r') as file:
            data = file.read()
        return json.loads(data)

    # creates the range of acceptable colors by label and stores it in a dictionary where the key is the label
    # takes in a default color that you want to be acceptable for ALL labels and a pixel deviation for the color
    # inputted it will not apply that deviation to your rgbs values provided from the json file
    def create_acceptable_colors_by_label(self, default_acceptable_colors=None, default_acceptable_deviation=0):
        print("Creating color ranges...")
        # set default range to white +/- 1
        self.create_default_acceptable_colors(default_acceptable_colors, default_acceptable_deviation)

        for label_name, label_data in self.label_starts.items():
            allowed_pixel_deviation = self.pixel_deviation
            # we need to check if a label start has a different pixel tolerance
            # assumes an int
            if "pixel_deviation" in label_data:
                allowed_pixel_deviation = label_data["pixel_deviation"]

            if type(allowed_pixel_deviation) is not int or allowed_pixel_deviation < 0:
                raise Exception(f"Pixel tolerance or deviation must be greater than 0, this failed on {label_name}")
            allow_default_color_range = self.enable_default_color_range

            if "enable_default_range" in label_data:
                allow_default_color_range = label_data["enable_default_range"]
            # this is a list of lists of rgb_values
            acceptable_colors = label_data["acceptable_colors_rgb"]
            # maybe a bit of an optimization or a waste of time not sure
            acceptable_colors_dict = self.create_acceptable_colors(acceptable_colors, allow_default_color_range,
                                                                   allowed_pixel_deviation)
            self.acceptable_colors_by_label[label_name] = acceptable_colors_dict
        print(self.acceptable_colors_by_label["Deltoid"])

    # for each label name it will extract all the pixels belonging to it using the label_starts.json
    def run_pixel_grabber(self):
        # the key will be the label_name,
        # and the value will be the array of pixels that make up the label
        self.pixels_by_label = {}
        # need to extract only the labels names we want if provided a list
        if self.label_names:
            change_label_starts = {}
            for label_name in self.label_names:
                label_data = self.label_starts[label_name]
                change_label_starts[label_name] = label_data
            self.label_starts = change_label_starts
        for label_name, label_data in self.label_starts.items():
            print(f"Starting run for DFS for label {label_name}")
            label = label_data["label"]
            starting_points = label_data["starting_points"]

            # the length of arrays starting_points, mins, and maxes must all be equal
            label_pixels = []
            for i, point in enumerate(starting_points):
                min_X, min_Y = 0, 0
                # we get the max width from the pic
                max_X, max_Y = self.max_width, self.max_height
                if "min_X" in label_data:
                    min_X = label_data["min_X"][i]
                if "min_Y" in label_data:
                    min_Y = label_data["min_Y"][i]
                if "max_X" in label_data:
                    max_X = label_data["max_X"][i]
                if "max_Y" in label_data:
                    max_Y = label_data["max_Y"][i]

                # combine results into one big array
                label_pixels += self.DFS(tuple(point), label_name, min_X, min_Y, max_X, max_Y)
                print("len label", len(label_pixels))
            self.pixels_by_label[label_name] = label_pixels
    # def run_pixel_grabber_C(self):
    #     print("Starting c code")
    #     type(self.acceptable_colors_by_label)
    #     C_executor = PixelGrabber_C(self.pixel_data, self.acceptable_colors_by_label)
    #     print("finished constructor", time.time() - start)
    #     # the key will be the label_name,
    #     # and the value will be the array of pixels that make up the label
    #     self.pixels_by_label = {}
    #     # need to extract only the labels names we want if provided a list
    #     if self.label_names:
    #         change_label_starts = {}
    #         for label_name in self.label_names:
    #             label_data = self.label_starts[label_name]
    #             change_label_starts[label_name] = label_data
    #         self.label_starts = change_label_starts
    #
    #     for label_name, label_data in self.label_starts.items():
    #         print(f"Starting run for DFS for label {label_name}")
    #         label = label_data["label"]
    #         starting_points = label_data["starting_points"]
    #
    #         # the length of arrays starting_points, mins, and maxes must all be equal
    #         label_pixels = []
    #         for i, point in enumerate(starting_points):
    #             min_X, min_Y = 0, 0
    #             # we get the max width from the pic
    #             max_X, max_Y = self.max_width, self.max_height
    #             if "min_X" in label_data:
    #                 min_X = label_data["min_X"][i]
    #             if "min_Y" in label_data:
    #                 min_Y = label_data["min_Y"][i]
    #             if "max_X" in label_data:
    #                 max_X = label_data["max_X"][i]
    #             if "max_Y" in label_data:
    #                 max_Y = label_data["max_Y"][i]
    #
    #             # combine results into one big array
    #             label_pixels += C_executor.DFS(tuple(point), label_name, min_X, min_Y, max_X, max_Y)
    #             # label_pixels += self.DFS(tuple(point), label_name, min_X, min_Y, max_X, max_Y)
    #             print("len label", len(label_pixels))
    #         self.pixels_by_label[label_name] = label_pixels

    def process_label_pixels(self, label_name, label_data, C_executor:PixelGrabber_C):
        print(f"Starting run for DFS for label {label_name}")
        label = label_data["label"]
        starting_points = label_data["starting_points"]

        # the length of arrays starting_points, mins, and maxes must all be equal
        label_pixels = []
        for i, point in enumerate(starting_points):
            min_X, min_Y = 0, 0
            # we get the max width from the pic
            max_X, max_Y = self.max_width, self.max_height
            if "min_X" in label_data:
                min_X = label_data["min_X"][i]
            if "min_Y" in label_data:
                min_Y = label_data["min_Y"][i]
            if "max_X" in label_data:
                max_X = label_data["max_X"][i]
            if "max_Y" in label_data:
                max_Y = label_data["max_Y"][i]

            # combine results into one big array
            label_pixels += C_executor.DFS(tuple(point), label_name, min_X, min_Y, max_X, max_Y)
            # label_pixels += self.DFS(tuple(point), label_name, min_X, min_Y, max_X, max_Y)
            print("len label", len(label_pixels))
        return label_name, label_pixels

    def run_pixel_grabber_C(self):
        print("Starting c code")
        start = time.time()
        type(self.acceptable_colors_by_label)
        C_executor = PixelGrabber_C(self.pixel_data, self.acceptable_colors_by_label, self.max_width, self.max_height)
        print("finished constructor", time.time() - start)
        # the key will be the label_name,
        # and the value will be the array of pixels that make up the label
        self.pixels_by_label = {}
        # need to extract only the labels names we want if provided a list
        if self.label_names:
            change_label_starts = {}
            for label_name in self.label_names:
                label_data = self.label_starts[label_name]
                change_label_starts[label_name] = label_data
            self.label_starts = change_label_starts
        thread_count = cpu_count() - 1
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            for label_name, label_data in self.label_starts.items():
                futures.append(executor.submit(self.process_label_pixels, label_name, label_data, C_executor))

            for future in as_completed(futures):
                label_name, label_pixels = future.result()
                self.pixels_by_label[label_name] = label_pixels

    # this is the searching algorithm for neighboring pixels that match
    def DFS(self, starting_coords: tuple, label_name: str, min_X: int, min_Y: int, max_X: int, max_Y: int):
        x, y = starting_coords
        # coords dict is a dict of x,y tuples, assume it exists do not pass it in
        # pixel_rgb = self.coords_dict[(x, y)]
        pixel_rgb = self.pixels[x, y]
        # dequeue is a doubly linked list, a normal vector is fine
        # queue is just a tuple list of coords
        queue = deque()
        # important that this is a dict it's much faster look up time!
        visited = {}
        # this can just be a normal list or vector
        accepted_pixels = deque()
        # add the start to the queue and the visited dict
        queue.append(starting_coords)
        # the value stored is arbitrary
        visited[starting_coords] = pixel_rgb
        accepted_pixels.append(starting_coords)
        acceptable_colors = self.acceptable_colors_by_label[label_name]
        while queue:
            current_coords = queue.popleft()
            x, y = current_coords
            # if current_coords not in self.coords_dict:
                # print("Starting coords do not exist in dict! Skipping this one!")
            # else:
            # pixel_rgb = self.coords_dict[(x, y)]
            pixel_rgb = self.pixels[x, y]
            # this is a function, do not rewrite this function assume it exists
            neighbors = self.get_neighbors(x, y)
            # print("neighbors", neighbors)
            # this is no more than 8 long at a time
            for neighbor in neighbors:
                current_x, current_y = neighbor
                # need to check that it's within the confines as well
                if max_X >= current_x >= min_X and max_Y >= current_y >= min_Y:
                    self.DFS_helper(neighbor, pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
        # return revealed which should be all matching pixels within range
        print("visited vs revealed")
        print(len(visited.values()))
        print(len(accepted_pixels))
        # if len(accepted_pixels) != len(set(accepted_pixels)):
        #     print("There are duplicates in the list.")
        # else:
        #     print("There are no duplicates in the list.")
        return accepted_pixels

    # this is the helper function for the search algorithm to make it more readable
    # def DFS_helper(self, current_coords: tuple, rgb: list, acceptable_colors: dict, queue: deque, visited: dict,
    #                accepted_pixels: deque):
    def DFS_helper(self, current_coords: tuple, rgb: tuple, acceptable_colors: dict, queue: deque, visited: dict,
                   accepted_pixels: deque):
        if current_coords not in visited:
            visited[current_coords] = rgb
            # if rgb value is not equal to the targeted rgb then we ignore it and don't continue searching from there
            if rgb not in acceptable_colors:
                # print("failed color")
                return
            # if it's acceptable then add to the queue to continue searching from there as well as you know that it's
            # an acceptable rgb value
            queue.append(current_coords)
            accepted_pixels.append(current_coords)
        return

    # simply gets the coordinates points 1 pixel away in all directions, returns a list
    def get_neighbors_original(self, x_given, y_given):
        neighbors = []
        # bottom left row_given+1, column_given - 1
        if not (x_given + 1 >= self.max_width) and not (y_given - 1 < 0):
            neighbors.append((x_given + 1, y_given - 1))
            # left column_given - 1
        if not (y_given - 1 < 0):
            neighbors.append((x_given, y_given - 1))
        # top left row_given-1, column_given-1
        if not (x_given - 1 < 0) and not (y_given - 1 < 0):
            neighbors.append((x_given - 1, y_given - 1))
        # top
        if not (x_given - 1 < 0):
            neighbors.append((x_given - 1, y_given))
        # top right row_given-1, column_given +1
        if not (x_given - 1 < 0) and not (y_given + 1 >= self.max_height):
            neighbors.append((x_given - 1, y_given + 1))
        # right row_given, column_given +1
        if not (y_given + 1 >= self.max_height):
            neighbors.append((x_given, y_given + 1))
        # bottom right row_given+1, column_given+1
        if not (x_given + 1 >= self.max_width) and not (y_given + 1 >= self.max_height):
            neighbors.append((x_given + 1, y_given + 1))
        # bottom row_given+1, column_given
        if not (x_given + 1 >= self.max_width):
            neighbors.append((x_given + 1, y_given))
        return neighbors

    # this is correct and works fine
    # returns a list of indicies representing the neighbors of the current coordinate
    def get_neighbors(self, x_given, y_given):
        neighbors = []
        # Define offsets for each direction
        offsets = [(1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0)]
        for dx, dy in offsets:
            # Calculate the x and y coordinates for the neighboring cell
            x, y = x_given + dx, y_given + dy
            # Check if the neighboring cell is within bounds
            if 0 <= x < self.max_width and 0 <= y < self.max_height:
                neighbors.append((x, y))
        return neighbors

    def get_neighbors_withC(self, x_given, y_given):
        start = time.perf_counter()
        neighbors = get_neighbors_from_point(x_given, y_given, self.max_width, self.max_height)
        end = time.perf_counter()
        self.neighbor_total_time += end - start
        return neighbors

    # TODO so you can do multiple colors at a time
    # takes in a HEX VALUE FOR COLOR! use '#hex_value'
    def change_pixels_test(self, color='#000000'):
        print("CHANGING SOMETHING", flush=True)
        img = Image.open(self.texture_file)
        image_pixels = img.load()
        for label_name, pixels in self.pixels_by_label.items():
            print(f"{label_name}: pixels length test", len(pixels), flush=True)
            # print("pixel type", type(pixels[0]))
            for pixel in pixels:
                image_pixels[pixel] = ImageColor.getcolor(color, "RGB")
        img.save('outputs/pixel_change_test.png')
        print("Finished saving change pixel test image.")

    def save_pixels_by_labels(self, output_file_name='pixels_by_labels.json'):
        print("SAVING PIXELS OR TRYING TO WHO KNOWS")
        start = time.time()
        with open("outputs/" + output_file_name, 'w') as fp:
            # uvs_list = list(uv_dict.values())
            # print("uvs_list", len(uvs_list))
            print("length of pixels by labels", len(self.pixels_by_label))
            json.dump(self.pixels_by_label, fp)
            print("Finished saving pixels by labels json file.")
            fp.flush()
        end = time.time()
        print(f"Full file JSON dump took {(end - start) / 60} minutes")

        start = time.time()
        print("Creating faces found by labels pickle file!")

        with open("outputs/" + "pixels_by_labels.bin", 'wb') as f:
            print("Writing STR tree binary")
            pickle.dump(self.pixels_by_label, f)
        end = time.time()
        print(f"Full file PICKLE dump took {(end - start) / 60} minutes")

    # this grabs each pixel coordinate and uses a tuple pair as key
    # and the value is the r, g, b at that pixel
    # probably not the best way to do this
    def get_pixel_coords(self):
        start = time.perf_counter()
        img = Image.open(self.texture_file)
        pixels = img.load()
        width, height = img.size
        mode = img.mode
        coords_dict = {}
        # print(type(pixels[100,100]), pixels[100,100])
        # for x in range(width):
        #     for y in range(height):
        #         # get rgb value by coords
        #         r, g, b = pixels[x, y]
        #         # coords_dict[(x, y)] = [r, g, b]
        #         # in case your image has an alpha channel
        #         # r, g, b, a = pixels[x, y]
        #         # print(x, y, f"#{r:02x}{g:02x}{b:02x}")
        img.close()
        end = time.perf_counter()
        print("Normal time took", end - start)
        return coords_dict, width, height, mode, pixels

    def open_Image_Pillow_numpy(self):
        # texture_file_path = "diffuse.jpg"
        start = time.perf_counter()
        print("Numpy image....")
        img = Image.open(self.texture_file)
        self.max_width, self.max_height = img.size
        self.pixel_data = np.array(img)
        end = time.perf_counter()
        print(f"NUMPY pillow Time {end - start}")
        # numpy is flipped!
        # print(data[10][10])
        # print(data[y][x])
        print(self.pixel_data.dtype)
        print(self.pixel_data.shape)
        # return data


    # this takes in a color that you want all your labels to accept, this is helpful if the label has some sort of
    # text in the center
    def create_default_acceptable_colors(self, default_acceptable_colors: list = None, pixel_tolerance_range: int = 0):
        if default_acceptable_colors is None:
            self.default_acceptable_colors_dict = {}
        if pixel_tolerance_range == 0:
            for rgb in default_acceptable_colors:
                self.default_acceptable_colors_dict[tuple(rgb)] = True
        else:
            # print(default_acceptable_colors)
            for rgb in default_acceptable_colors:
                self.create_close_enough_values(rgb, pixel_tolerance_range,
                                                self.default_acceptable_colors_dict)

    # returns a dictionary of acceptable color rgbs
    def create_acceptable_colors(self, acceptable_colors, enable_default_color_range, pixel_tolerance_range: int = 0):
        acceptable_colors_dict = {}
        # also add white as an acceptable color for the letter labels so there's not a hole
        # if enable_default_color_range:
        #     acceptable_colors_dict[(254, 255, 252)] = True
        #     acceptable_colors_dict[(255, 255, 252)] = True
        #     acceptable_colors_dict[(255, 255, 253)] = True
        #     acceptable_colors_dict[(254, 255, 255)] = True
        #     acceptable_colors_dict[(255, 254, 255)] = True
        # # default white
        # acceptable_colors_dict[(255, 255, 254)] = True
        # acceptable_colors_dict[(255, 255, 255)] = True
        if enable_default_color_range:
            # pipe symbol basically zip
            acceptable_colors_dict |= self.default_acceptable_colors_dict

        # if there's no tolerance ignore just use the given colors
        if pixel_tolerance_range == 0:
            for rgb in acceptable_colors:
                acceptable_colors_dict[tuple(rgb)] = True
        else:
            for rgb in acceptable_colors:
                self.create_close_enough_values(rgb, pixel_tolerance_range, acceptable_colors_dict)
        return acceptable_colors_dict

    # creates the range of RGB values acceptable and stores it in the dict provided nothing is returned
    def create_close_enough_values(self, rgb_values, tolerance_range, dict_to_store, max_acceptable_range=256,
                                   min_acceptable_range=0):
        # this gives us the proper range including the middle coordinate we want
        min_ranges = [x - tolerance_range for x in rgb_values]
        max_ranges = [x + tolerance_range + 1 for x in rgb_values]
        min_ranges = [min_acceptable_range if x < min_acceptable_range else x for x in min_ranges]
        max_ranges = [max_acceptable_range if x > max_acceptable_range else x for x in max_ranges]
        # print(min_ranges)
        # print(max_ranges)

        max_r, max_g, max_b = max_ranges
        min_r, min_g, min_b = min_ranges

        for r in range(min_r, max_r):
            for g in range(min_g, max_g):
                for b in range(min_b, max_b):
                    current_result = (r, g, b)
                    dict_to_store[current_result] = True

    # ignore this because it returns a dictionary which we don't want
    def convert_pixel_coords_to_uv(self, coords: dict, width, height):
        # u is width, v is height
        # coords tuple will be key
        uv_dict = {}
        for coord, rgb in coords.items():
            x, y = coord
            r, g, b = rgb
            u = x / width
            # since 0, 0 is at the bottom left! very important
            v = 1 - y / height
            uv_dict[coord] = (u, v)
        return uv_dict

    # we actually don't need to use this because in the end we only use pixels not uvs!
    # also the way it is now needs to be changed as it won't work with the updated version
    def convert_pixel_coords_to_uv_list(self, coords: list, width, height):
        # u is width, v is height
        uvs_list = []
        for coord in coords:
            x, y = coord
            # r, g, b = rgb
            u = x / width
            # since 0, 0 is at the bottom left! very important
            v = 1 - y / height
            uvs_list.append([u, v])
        return uvs_list


# these two need to be static functions because how processes need
# to pickle data as it's returned, and if it's in a class
# like it was before it fails the pickling process
def run_change_pixels_test(texture_file, pixels_by_label, color='#000000'):
    print("Running pixel change test!")
    img = Image.open(texture_file)
    image_pixels = img.load()
    for label_name, pixels in pixels_by_label.items():
        print(f"{label_name}: pixels length test", len(pixels), flush=True)
        # print("pixel type", type(pixels[0]))
        for pixel in pixels:
            image_pixels[pixel] = ImageColor.getcolor(color, "RGB")
    img.save('outputs/pixel_change_test.png')
    print("Finished saving change pixel test image.", flush=True)


def save_pixels_by_labels(pixels_by_label, output_file_name='pixels_by_labels'):
    print("Saving pixels by labels", flush=True)
    # start = time.time()
    # with open("outputs/" + output_file_name, 'w') as fp:
    #     # uvs_list = list(uv_dict.values())
    #     # print("uvs_list", len(uvs_list))
    #     print("length of pixels by labels", len(pixels_by_label), flush=True)
    #     json.dump(pixels_by_label, fp)
    #     print("Finished saving pixels by labels json file.", flush=True)
    #     fp.flush()
    #
    # end = time.time()
    # print(f"Full file JSON dump took {(end - start) } seconds")

    start = time.time()
    print("Creating faces found by labels pickle file!")
    with open("outputs/" + f"{output_file_name}.bin", 'wb') as f:
        print("Writing label binary")
        pickle.dump(pixels_by_label, f, protocol=pickle.HIGHEST_PROTOCOL)
    end = time.time()
    print(f"Full file PICKLE dump took {(end - start)} seconds")


if __name__ == "__main__":
    # start = time.perf_counter()
    test_mode = True
    start = time.time()
    # IMPORTANT  this is an array of strings, if it's empty it will do all of them
    label_names_to_test = []
    #
    # # if there's a fade or variation in color you will want to raise this to loosen what is an acceptable color
    default_pixel_deviation = 3
    #
    texture_file_path = 'obj textures/diffuse.jpg'
    #
    # # set white as the default acceptable colors
    default_acceptable_colors = [[255, 255, 255]]
    deviation_default_colors = 2

    # first create the object which simply loads in the texture picture and relevant data
    # also reads in the label starts
    # allows for a default color range to capture more of the label (if you have it), disable it if too aggressive
    # pixel_grabber.disable_default_color_range
    pixel_grabber = PixelGrabber(texture_file_path, label_names_to_test, default_pixel_deviation)

    # although this takes forever it is not worth optimizing as it is a task that must be waited on
    # before anything else is run
    if not test_mode:
        pixel_grabber.set_and_create_image_data()
    else:
        # for the C code we need this
        pixel_grabber.open_Image_Pillow_numpy()

    # testing
    # pixel_grabber.get_pixel_coords()
    # pixel_grabber.get_pixel_coords_numpy()

    # creates the range of acceptable colors by label, in this case just white basically
    pixel_grabber.create_acceptable_colors_by_label(default_acceptable_colors, deviation_default_colors)
    start = time.perf_counter()
    #
    # # starting_coords = (50, 50)
    # # result = pixel_grabber.DFS(starting_coords, "red", 49, 49, 51, 51)
    if not test_mode:
        pixel_grabber.run_pixel_grabber()
    else:
        pixel_grabber.run_pixel_grabber_C()
    # print(pixel_grabber.pixels_by_label.keys())
    # # print(result)
    end = time.perf_counter()
    # end = time.time()
    print()
    print(f"Finished finding pixels...Took {end - start} seconds")