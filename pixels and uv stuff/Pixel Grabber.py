import json
import time

from PIL import Image, ImageColor


class PixelGrabber:
    # if muscle name is none we do all them otherwise it's all of them
    # takes in an array of muscle names to do
    def __init__(self, muscle_names=None):
        self.muscle_starts = self.read_in_muscle_starts()
        self.texture_file = '../images/diffuse.jpg'
        self.muscle_names = muscle_names
        print("Grabbing pixels and rgbs....")
        self.coords_dict, self.max_width, self.max_height, self.mode, self.pixels = self.get_pixel_coords()

    def read_in_muscle_starts(self):
        print("Loading in muscle starts...")
        # testing line
        with open('starts/test_template.json', 'r') as file:
        # this is the normal one to be used
        # with open('starts/muscle_starts.json', 'r') as file:
            data = file.read()
        return json.loads(data)

    # for each muscle name it will extract all the pixels belonging to it using the muscle_starts.json
    def run_pixel_grabber(self):
        # the key will be the muscle_name,
        # and the value will be the array of pixels that make up the muscle
        self.pixels_by_muscle = {}
        # need to extract only the muscles names we want if provided a list
        if self.muscle_names:
            change_muscle_starts = {}
            for muscle_name in self.muscle_names:
                muscle_data = self.muscle_starts[muscle_name]
                change_muscle_starts[muscle_name] = muscle_data
            self.muscle_starts = change_muscle_starts
        for muscle_name, muscle_data in self.muscle_starts.items():
            print(f"Starting run for DFS for muscle {muscle_name}")
            label = muscle_data["label"]
            starting_points = muscle_data["starting_points"]
            # the length of arrays starting_points, mins, and maxes must all be equal
            muscle_pixels = []
            for i, point in enumerate(starting_points):
                min_X = muscle_data["min_X"][i]
                min_Y = muscle_data["min_Y"][i]
                max_X = muscle_data["max_X"][i]
                max_Y = muscle_data["max_Y"][i]
                # this is a list of lists of rgb_values
                acceptable_colors = muscle_data["acceptable_colors_rgb"]
                # combine results into one big array
                muscle_pixels += self.DFS(tuple(point), acceptable_colors, min_X, min_Y, max_X, max_Y)
                print("len muscle", len(muscle_pixels))
            self.pixels_by_muscle[muscle_name] = muscle_pixels

    # this is the searching algorithm for neighboring pixels that match
    def DFS(self, starting_coords, acceptable_colors, min_X, min_Y, max_X, max_Y):
        x, y = starting_coords
        pixel_rgb = self.coords_dict[(x, y)]
        # IMPORTANT why the fuck is it reading in the blue value one color off from intellij's thing
        # maybe a bit of an optimization or a waste of time not sure
        acceptable_colors_dict = {}
        for rgb in acceptable_colors:
            acceptable_colors_dict[tuple(rgb)] = True
        # also add white as an acceptable color for the letter labels so there's not a hole
        acceptable_colors_dict[(255, 254, 255)] = True
        # color = (220, 156, 190)
        # acceptable_colors = {color: True}
        queue = []
        # important that this is a dict it's much faster!
        visited = {}
        accepted_pixels = []
        # add it to the queue and the visited
        queue.append(starting_coords)
        # idk what value to store it's arbitrary
        visited[starting_coords] = pixel_rgb
        accepted_pixels.append(starting_coords)
        while queue:
            # queue is just a tuple list of coords
            current_coords = queue.pop(0)
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
                    self.DFS_helper(neighbor, pixel_rgb, acceptable_colors_dict, queue, visited, accepted_pixels)
        # return revealed which should be all matching pixels within range
        print("visited vs revealed")
        print(len(visited.values()))
        print(len(accepted_pixels))
        return accepted_pixels

    # TODO needs to take in starting colors, maxs and mins
    # def DFS(self, starting_coords, acceptable_colors, min_X, min_Y, max_X, max_Y):
    #     x, y = starting_coords
    #     pixel_rgb = self.coords_dict[(x, y)]
    #     # IMPORTANT why the fuck is it reading in the blue value one color off from intellij's thing
    #     # maybe a bit of an optimization or a waste of time not sure
    #     acceptable_colors_dict = {}
    #     for rgb in acceptable_colors:
    #         acceptable_colors_dict[tuple(rgb)] = True
    #     # color = (220, 156, 190)
    #     # acceptable_colors = {color: True}
    #     queue = []
    #     # important that this is a dict it's much faster!
    #     visited = {}
    #     accepted_pixels = []
    #     # add it to the queue and the visited
    #     queue.append(starting_coords)
    #     # idk what value to store it's arbitrary
    #     visited[starting_coords] = pixel_rgb
    #     accepted_pixels.append(starting_coords)
    #     while queue:
    #         # queue is just a tuple list of coords
    #         current_coords = queue.pop(0)
    #         x, y = current_coords
    #         pixel_rgb = self.coords_dict[(x, y)]
    #         # print(queue)
    #         # print(pixel_rgb)
    #         # print(color)
    #         # bottom left row+1, col - 1
    #         if not (x + 1 >= self.max_width) and not (y - 1 < 0):
    #             self.DFS_helper((x + 1, y - 1), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #         # left col - 1
    #         if not (y - 1 < 0):
    #             self.DFS_helper((x, y - 1), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #
    #         # top left row-1, col-1
    #         if not (x - 1 < 0) and not (y - 1 < 0):
    #             self.DFS_helper((x - 1, y - 1), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #
    #         # top
    #         if not (x - 1 < 0):
    #             self.DFS_helper((x - 1, y), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #
    #         # top right row-1, col +1
    #         if not (x - 1 < 0) and not (y + 1 >= self.max_height):
    #             self.DFS_helper((x - 1, y + 1), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #
    #         # right row, col +1
    #         if not (y + 1 >= self.max_height):
    #             self.DFS_helper((x, y + 1), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #
    #         # bottom right row+1, col+1
    #         if not (x + 1 >= self.max_width) and not (y + 1 >= self.max_height):
    #             self.DFS_helper((x + 1, y + 1), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #
    #         # bottom row+1, col
    #         if not (x + 1 >= self.max_width):
    #             self.DFS_helper((x + 1, y), pixel_rgb, acceptable_colors, queue, visited, accepted_pixels)
    #     # return revealed which should be all matching pixels within range
    #     print("visited vs revealed")
    #     print(len(visited.values()))
    #     print(len(accepted_pixels))
    #     return accepted_pixels
    # this is the helper function for the search algorithm to make it more readable
    def DFS_helper(self, current_coords, rgb, acceptable_colors: dict, queue, visited: dict, revealed):
        if current_coords not in visited:
            visited[current_coords] = rgb
            # if rgb value is not equal to the targeted rgb then we ignore it and don't continue searching from there
            if tuple(rgb) not in acceptable_colors:
                return
            # if it's acceptable then add to the queue to continue searching from there as well as you know that it's
            # an acceptable rgb value
            queue.append(current_coords)
            revealed.append(current_coords)
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
        img = Image.open('../images/diffuse.jpg')
        image_pixels = img.load()
        for muscle_name, pixels in self.pixels_by_muscle.items():
            print("pixels length test", len(pixels))
            print("pixel type", type(pixels[0]))
            for pixel in pixels:
                image_pixels[pixel] = ImageColor.getcolor(color, "RGB")
        img.save('outputs/pixel_change_test.png')

    def save_pixels_by_muscles(self, output_file_name='pixels_by_muscles.json'):
        with open("outputs/" + output_file_name, 'w') as fp:
            # uvs_list = list(uv_dict.values())
            # print("uvs_list", len(uvs_list))
            print("length of pixels by muscles", len(self.pixels_by_muscle))
            json.dump(self.pixels_by_muscle, fp)

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
        return coords_dict, width, height, mode, pixels

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


if __name__ == "__main__":
    start = time.time()
    # IMPORTANT  this is an array of strings, if it's empty it will do all of them
    muscle_names_to_test = []
    # first create the object which simply loads in the diffuse.jpg and relevant data
    # also reads in the muscle starts
    pixel_grabber = PixelGrabber(muscle_names_to_test)
    # then run the actual pixel_grabber algo
    pixel_grabber.run_pixel_grabber()
    # to save the pixels by muscle
    # you can specify an output file name as an argument if you want (optional)
    pixel_grabber.save_pixels_by_muscles()
    # if you are testing, you can visualize the changes with
    # you can specify a specific hex color default is '#000000'
    pixel_grabber.change_pixels_test()

    end = time.time()
    print()
    print(f"Finished finding pixels...Took {end - start} seconds")

