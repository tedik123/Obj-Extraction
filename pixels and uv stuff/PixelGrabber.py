import json
import time
from concurrent.futures.process import ProcessPoolExecutor
from collections import deque
from PIL import Image, ImageColor


class PixelGrabber:
    # if label name is none we do all them otherwise it's all of them
    # takes in an array of label names to do
    def __init__(self, texture_file_path, label_names=None, pixel_deviation=0, ):
        self.pixel_deviation = pixel_deviation
        self.enable_default_color_range = True
        self.label_starts = self.read_in_label_starts()
        # self.texture_file = 'obj textures/diffuse.jpg'
        self.texture_file = texture_file_path
        self.label_names = label_names
        self.coords_dict, self.max_width, self.max_height, self.mode, self.pixels = None, None, None, None, None
        self.acceptable_colors_by_label = {}
        self.default_acceptable_colors_dict = {}

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

    # this is the searching algorithm for neighboring pixels that match
    def DFS(self, starting_coords, label_name, min_X, min_Y, max_X, max_Y):
        x, y = starting_coords
        pixel_rgb = self.coords_dict[(x, y)]

        # color = (220, 156, 190)
        # acceptable_colors = {color: True}
        # dequeue is a doubly linked list
        queue = deque()
        # important that this is a dict it's much faster!
        visited = {}
        # accepted_pixels = []
        accepted_pixels = deque()
        # add it to the queue and the visited
        queue.append(starting_coords)
        # idk what value to store it's arbitrary
        visited[starting_coords] = pixel_rgb
        accepted_pixels.append(starting_coords)
        acceptable_colors = self.acceptable_colors_by_label[label_name]
        while queue:
            # queue is just a tuple list of coords
            # current_coords = queue.pop(0)
            current_coords = queue.popleft()
            x, y = current_coords
            pixel_rgb = self.coords_dict[(x, y)]
            # print(queue)
            # print(pixel_rgb)
            # print(color)
            neighbors = self.get_neighbors(x, y)
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
        return accepted_pixels

    # this is the helper function for the search algorithm to make it more readable
    def DFS_helper(self, current_coords, rgb, acceptable_colors: dict, queue, visited: dict, accepted_pixels):
        if current_coords not in visited:
            visited[current_coords] = rgb
            # if rgb value is not equal to the targeted rgb then we ignore it and don't continue searching from there
            if tuple(rgb) not in acceptable_colors:
                return
            # if it's acceptable then add to the queue to continue searching from there as well as you know that it's
            # an acceptable rgb value
            queue.append(current_coords)
            accepted_pixels.append(current_coords)
        return

    # simply gets the coordinates points 1 pixel away in all directions, returns a list
    def get_neighbors(self, x_given, y_given):
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
        with open("outputs/" + output_file_name, 'w') as fp:
            # uvs_list = list(uv_dict.values())
            # print("uvs_list", len(uvs_list))
            print("length of pixels by labels", len(self.pixels_by_label))
            json.dump(self.pixels_by_label, fp)
            print("Finished saving pixels by labels json file.")
            fp.flush()

    # this grabs each pixel coordinate and uses a tuple pair as key
    # and the value is the r, g, b at that pixel
    # probably not the best way to do this
    def get_pixel_coords(self):
        img = Image.open(self.texture_file)
        pixels = img.load()
        width, height = img.size
        mode = img.mode
        coords_dict = {}
        for x in range(width):
            for y in range(height):
                # get rgb value by coords
                r, g, b = pixels[x, y]
                coords_dict[(x, y)] = [r, g, b]
                # in case your image has an alpha channel
                # r, g, b, a = pixels[x, y]
                # print(x, y, f"#{r:02x}{g:02x}{b:02x}")
        img.close()
        return coords_dict, width, height, mode, pixels

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


def save_pixels_by_labels(pixels_by_label, output_file_name='pixels_by_labels.json'):
    print("Saving pixels by labels", flush=True)
    with open("outputs/" + output_file_name, 'w') as fp:
        # uvs_list = list(uv_dict.values())
        # print("uvs_list", len(uvs_list))
        print("length of pixels by labels", len(pixels_by_label), flush=True)
        json.dump(pixels_by_label, fp)
        print("Finished saving pixels by labels json file.", flush=True)
        fp.flush()


if __name__ == "__main__":
    start = time.time()
    # IMPORTANT  this is an array of strings, if it's empty it will do all of them
    label_names_to_test = []

    # if there's a fade or variation in color you will want to raise this to loosen what is an acceptable color
    default_pixel_deviation = 3

    texture_file_path = 'obj textures/diffuse.jpg'

    # set white as the default acceptable colors
    default_acceptable_colors = [[255, 255, 255]]
    deviation_default_colors = 2

    # first create the object which simply loads in the texture picture and relevant data
    # also reads in the label starts
    # allows for a default color range to capture more of the label (if you have it), disable it if too aggressive
    # pixel_grabber.disable_default_color_range
    pixel_grabber = PixelGrabber(texture_file_path, label_names_to_test, default_pixel_deviation)

    # this is for the future processes
    executor = ProcessPoolExecutor(max_workers=2)

    # although this takes forever it is not worth optimizing as it is a task that must be waited on
    # before anything else is run
    pixel_grabber.set_and_create_image_data()

    # creates the range of acceptable colors by label, in this case just white basically
    pixel_grabber.create_acceptable_colors_by_label(default_acceptable_colors, deviation_default_colors)

    # then run the actual pixel_grabber algo
    pixel_grabber.run_pixel_grabber()

    # print("Saving pixels by labels file!")
    #  to save the pixels by label
    # you can specify an output file name as an argument if you want (optional)
    output_file_name = "pixels_by_labels.json"
    futures = [executor.submit(save_pixels_by_labels, pixel_grabber.pixels_by_label, output_file_name)]
    # pixel_grabber.save_pixels_by_labels() # run for better print statements without process pool

    # print("Running change pixels test!")
    # if you are testing, you can visualize the changes with the change_pixels_test
    # you can specify a specific hex color default is '#000000'
    hex_color = '#000000'
    futures.append(
        executor.submit(run_change_pixels_test, pixel_grabber.texture_file, pixel_grabber.pixels_by_label,
                        hex_color))
    # for future in as_completed(futures):
    #     print("finished")

    # print(futures[0].result())
    # wait(futures)
    # pixel_grabber.change_pixels_test() # run for better print statements without process pool
    executor.shutdown(wait=True, cancel_futures=False)
    print("Finished saving pixel change test file and pixel by label.json file")
    end = time.time()
    print()
    print(f"Finished finding pixels...Took {end - start} seconds")
