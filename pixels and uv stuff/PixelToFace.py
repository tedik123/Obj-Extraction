import concurrent.futures

import json
import time

from Triangles import Triangle
from shapely import STRtree, points as Points
import pickle
from multiprocessing import cpu_count
from obj_helper_functions import pixel_coords_to_uv as pixel_coords_to_uv_c


class PixelToFace:

    def __init__(self, target_file_path, max_width, max_height, preload_STRtree=False, save_normals=True,
                 save_uvs=True, disable_target_pixels_load=False):
        # these are all arrays!!!!!!!!!
        self.target_file_path = target_file_path

        # where all the json files are for the geometry faces and uvs
        # self.json_data_directory = "geometry_files/"
        self.json_data_directory = "outputs/geometry_files"

        self.save_normals = save_normals
        self.save_uvs = save_uvs
        # These must be defined first or the threads won't like it
        self.target_pixels_by_name = None
        self.faces = None
        self.normals = None
        self.uvs = None
        self.str_tree: STRtree = None

        self.max_width = max_width
        self.max_height = max_height

        # FIXME I could use async for these tasks so the load is faster
        # self.read_in_faces()
        # if save_normals:
        #     self.read_in_normals()
        # self.read_in_geometry_uvs()
        # self.read_in_target_pixels()

        thread_count = 5
        # self.read_in_target_pixels()
        # self.convert_pixels_to_points()
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            if not disable_target_pixels_load:
                target_pixel_future = executor.submit(self.read_in_target_pixels)
            # set the callback to run convert pixels, since it's dependent
            # target_pixel_future.add_done_callback(lambda future: executor.submit(self.convert_pixels_to_points))
                futures.append(target_pixel_future)

            # the only time you wouldn't preload STR tree is if you're passing it in and creating new geometry files
            # i.e. you have a new object file
            if preload_STRtree:
                futures.append(executor.submit(self.read_in_str_tree))
                futures.append(executor.submit(self.read_in_geometry_uvs))
                futures.append(executor.submit(self.read_in_faces))
                if save_normals:
                    futures.append(executor.submit(self.read_in_normals))
            # Set a callback for important_future to submit dependent_function
            concurrent.futures.wait(futures)
        print("Finished loading files")
        # self.convert_pixels_to_points()

        # this is data for the STR tree
        self.triangle_data = []

    def read_in_faces(self):
        # print("Loading in faces")
        # with open(f'{self.json_data_directory}/geometry_faces.json', 'r') as file:
        #     data = file.read()
        # self.faces = json.loads(data)['faces']
        print("Loading in faces")
        with open(f'{self.json_data_directory}/geometry_faces.bin', 'rb') as file:
            self.faces = pickle.load(file)["faces"]

    def read_in_normals(self):
        if self.save_normals:
            print("Loading normals")
            try:
                # with open(f'{self.json_data_directory}/geometry_normals.json', 'r') as file:
                #     data = file.read()
                # self.normals = json.loads(data)['normals']
                with open(f'{self.json_data_directory}/geometry_normals.bin', 'rb') as file:
                    self.normals = pickle.load(file)["normals"]
            except FileNotFoundError:
                print("Couldn't find geometry normals file, ignoring it!")
        else:
            print("Normals not loaded")

    def read_in_geometry_uvs(self):
        print("Loading geometry uvs")
        # with open(f'{self.json_data_directory}/geometry_uvs.json', 'r') as file:
        #     data = file.read()
        # self.uvs = json.loads(data)['uvs']
        with open(f'{self.json_data_directory}/geometry_uvs.bin', 'rb') as file:
            self.uvs = pickle.load(file)["uvs"]

    def read_in_target_pixels(self):
        print("Loading target pixels")
        # start = time.time()
        # with open(self.target_file_path, 'r') as file:
        #     data = file.read()
        # self.target_pixels_by_name = json.loads(data)
        # end = time.time()
        # print(f"Reading JSON file took {(end - start)} seconds")

        start = time.time()
        with open("outputs/pixels_by_labels.bin", 'rb') as file:
            self.target_pixels_by_name = pickle.load(file)
        end = time.time()
        print(f"Reading PICKLE file took {(end - start)} seconds")

    def pass_in_geometry_data(self,  faces, normals, uvs):
        self.faces = faces["faces"]
        self.normals = normals["normals"]
        self.uvs = uvs["uvs"]

    def pass_in_target_pixels(self, target_pixels):
        self.target_pixels_by_name = target_pixels

    def read_in_str_tree(self):
        print("Reading in STR tree")
        with open("outputs/STRtree.bin", "rb") as f:
            self.str_tree = pickle.load(f)

    # builds a tree of all the triangles that make up the obj file for faster search
    def build_str_tree(self):
        print("Building STR Tree!")
        triangle_list = []
        node_capacity = 10
        # we'll store the full object (Triangle Class) here in parallel
        # triangle_data = []
        for index, uv_face in enumerate(self.uvs):
            # coord_point_sum = uv_face["a"]["x"] + uv_face["a"]["y"] + uv_face["b"]["x"] + uv_face["b"]["y"] + \
            #                   uv_face["c"]["x"] + uv_face["b"]["y"]
            # we'll ignore all 0 points which only happens at the beginning in our case
            # if coord_point_sum != 0:
            # triangle = TriangleDecomposer(uv_face["a"], uv_face["b"], uv_face["c"], max_width, max_height)
            p1 = (uv_face["a"]["x"], uv_face["a"]["y"])
            p2 = (uv_face["b"]["x"], uv_face["b"]["y"])
            p3 = (uv_face["c"]["x"], uv_face["c"]["y"])
            # I don't remember if index should start at 0 or 1
            triangle = Triangle(p1, p2, p3, index)
            triangle_list.append(triangle.triangle)
            # self.triangle_data.append(triangle)
        self.str_tree = STRtree(triangle_list, node_capacity)
        print("Finished building STR TREE")
        print("Saving STR related Data")
        with open("outputs/STRtree.bin", "wb") as f:
            print("Writing STR tree binary")
            pickle.dump(self.str_tree, f)
        print(self.str_tree)

    # searches the STR tree for the targets given!
    def find_faces_of_targets(self, thread_count: int = None):
        if not thread_count:
            thread_count = cpu_count() - 1
        print(f"Using {thread_count} threads to query tree!")
        time_for_indexing = 0.0
        self.label_faces = {}
        # print("Creating Process Queue And Event")
        # queue = Queue()
        # process_result = Queue()

        print("Beginning search process")

        # STR load stuff if not in memory
        if self.str_tree is None:
            # TODO i could move these reads and writes to their own function
            self.read_in_str_tree()
        # convert all points to Point objects
        # self.convert_pixels_to_points()
        work_by_thread = split_dict(self.target_pixels_by_name, thread_count)
        start = time.time()
        print("Creating threads")
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            for i in range(thread_count):
                futures.append(executor.submit(self.str_query_thread, work_by_thread[i], i))

            # take them as they finish instead of waiting around
            # https://stackoverflow.com/questions/52082665/store-results-threadpoolexecutor
            for future in concurrent.futures.as_completed(futures):
                thread_start_time = time.time()
                result = future.result()
                # results.append(future.result())
                print("finished")
                for name, indices in result.items():
                    self.get_geometries_by_index_list(self.label_faces, name, indices)
                thread_end_time = time.time()
                time_for_indexing += thread_end_time - thread_start_time
            print("TIME FOR INDEXING ALL GEOMETRIES", time_for_indexing)
        # It doesn't really matter if it goes inside the threadpool executor or not...
        # for result in results:
        #     for name, indices in result.items():
        #         self.get_geometries_by_index_list(self.label_faces, name, indices)
        end = time.time()
        print(f"Threading task took {(end - start) / 60} minutes")

        start = time.time()
        print("Creating faces found by labels pickle file!")
        with open('outputs/faces_found_by_labels.bin', 'wb') as fp:
            print("labels faces length", len(self.label_faces))
            pickle.dump(self.label_faces, fp)
        end = time.time()
        print(f"Full file PICKLE dump took {(end - start) / 60} minutes")

    # converts all target points to Point objects
    # FIXME this is a huge bottleneck!!!!
    #   Brought down to 6.5 seconds by using PointS instead of just point
    #   Perhaps multithreading will increase the speed
    #   Perhaps we can hide this slowness by throwing it in the file loads
    def convert_pixels_to_points(self):
        print("Starting conversion of pixels to points")
        start = time.time()
        for name, pixel_list in self.target_pixels_by_name.items():
            # no longer need to convert to tuple since pickling saves tuples unlike json
            # uv_list = [pixel_coords_to_uv(tuple(pixel)) for pixel in pixel_list]
            uv_list = pixel_coords_to_uv(pixel_list, self.max_width, self.max_height)

            self.target_pixels_by_name[name] = Points(uv_list)
        end = time.time()
        print(f"Conversion of pixels to UV Points {(end - start)} seconds")

    # returns only the indexes associated with each face
    def str_query_thread(self, target_pixels_by_name: dict, thread_count):
        label_indexes = {}
        print(f"Thread {thread_count + 1} is searching points for targets of {len(list(target_pixels_by_name.keys()))}")
        # missed_values = 0
        # pixels_to_find_count = 0
        # one idea here would be to combine all the targets in one giant list and save the length associated
        # with each label and then slice it out when it returns that way more time is spent in C code rather than
        # python code? maybe...
        for label_name, targets in target_pixels_by_name.items():
            # pixels_to_find_count += len(targets)
            # store the list returned
            uv_list = pixel_coords_to_uv_c(targets, self.max_width, self.max_height)
            target_points = Points(uv_list)
            label_indexes[label_name] = self.str_tree.nearest(target_points)

        # print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        # print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        return label_indexes

    def test_pixel_to_coords(self):
        original_start = time.perf_counter()
        original_end = time.perf_counter()
        for name, pixel_list in self.target_pixels_by_name.items():
            uv_list = pixel_coords_to_uv(pixel_list, self.max_width, self.max_height)
        print("Time for original", original_end - original_start)

        vector_start = time.perf_counter()
        vector_end = time.perf_counter()
        for name, pixel_list in self.target_pixels_by_name.items():
            uv_list = pixel_coords_to_uv_c(pixel_list, self.max_width, self.max_height)
        print("Time for vector", vector_end - vector_start)

    def get_geometries_by_index_list(self, label_faces: dict, label_name: str, list_of_indices: list):
        face_results = []
        normals_result = []
        uvs_result = []
        for index in list_of_indices:
            # print(index)
            # index = index[0]
            p0 = self.faces[index]["a"]
            p1 = self.faces[index]["b"]
            p2 = self.faces[index]["c"]
            face_results.append(p0)
            face_results.append(p1)
            face_results.append(p2)
            if self.save_normals and self.normals:
                n0 = self.normals[index]["a"]
                n1 = self.normals[index]["b"]
                n2 = self.normals[index]["c"]
                normals_result.append(n0)
                normals_result.append(n1)
                normals_result.append(n2)
            if self.save_uvs:
                uv0 = list(self.uvs[index]["a"].values())
                uv1 = list(self.uvs[index]["b"].values())
                uv2 = list(self.uvs[index]["c"].values())
                uvs_result.append(uv0)
                uvs_result.append(uv1)
                uvs_result.append(uv2)
        if self.save_uvs:
            if self.save_normals:
                label_faces[label_name] = {"vertices": face_results, "normals": normals_result,
                                           "uvs": uvs_result}
            else:
                label_faces[label_name] = {"vertices": face_results, "uvs": uvs_result}
        elif self.save_normals:
            label_faces[label_name] = {"vertices": face_results, "normals": normals_result}
        else:
            label_faces[label_name] = {"vertices": face_results}


def pixel_coords_to_uv(pixel_list, max_width, max_height):
    # u is width, v is height
    result = []
    for pixel in pixel_list:
        x, y = pixel
        u = x / max_width
        # since 0, 0 is at the bottom left! very important
        v = 1 - y / max_height
        result.append((u, v))
    return result


def pixel_coord_to_uv(pixel, max_width, max_height):
    # u is width, v is height
    # coords tuple will be key
    # if type(coord) != tuple:
    #     print("File contains not a tuple, skipping", coord)
    #     return None
    # else:
    #     print("okay", coord)
    x, y = pixel
    u = x / max_width
    # since 0, 0 is at the bottom left! very important
    v = 1 - y / max_height
    return u, v


# This is a standard barycentric coordinate function.
# I don't know how this works...
# I think it checks if a point is all to one side of each line
# does it matter in which orientation things are?
# https://stackoverflow.com/questions/20248076/how-do-i-check-if-a-point-is-inside-a-triangle-on-the-line-is-ok-too
def isPtInTriangle(p, p0, p1, p2):
    x0 = p["x"]
    y0 = p["y"]
    x1 = p0["x"]
    y1 = p0["y"]
    x2 = p1["x"]
    y2 = p1["y"]
    x3 = p2["x"]
    y3 = p2["y"]
    # print(x0, y0, x1, y1, x2, y2, x3, y3)
    b0 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    # There's a lot of uvs that are 0 in the model that we absolutely don't care about
    # because it means (I think) that they're untextured points
    if b0 != 0:
        b1 = ((x2 - x0) * (y3 - y0) - (x3 - x0) * (y2 - y0)) / b0
        b2 = ((x3 - x0) * (y1 - y0) - (x1 - x0) * (y3 - y0)) / b0
        b3 = ((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / b0
        if b1 > 0 and b2 > 0 and b3 > 0:
            # return [b1, b2, b3];
            return True
        else:
            # return [];
            return False
    return False


# returns a list of dictionaries that are roughly split evenly
def split_dict_simple(dictionary, n):
    # there has to be a more efficient way to split a dict!
    size = len(dictionary)
    chunk_size = (size // n) + (size % n > 0)
    dictionary_list = list(dictionary.items())
    list_of_dicts = []
    for i in range(0, size, chunk_size):
        list_of_dicts.append(dict(dictionary_list[i:i + chunk_size]))
    # returns the dict sorted so the longest list of pixel values are first
    return sorted(list_of_dicts, key=lambda d: sum(map(len, d.values())), reverse=True)


# attempts to split the dictionary into equal parts by length of value arrays not amount of keys
def split_dict_greater_than3(dictionary, n):
    if n < 3:
        raise Exception("N must be greater than or equal to 3")
    # Calculate the total length of the values in the dictionary
    total_length = sum(map(lambda x: len(x), dictionary.values()))

    # Calculate the target length for each split
    target_length = total_length // (n - 1)

    # Initialize variables
    current_length = 0
    current_dict = {}
    list_of_dicts = []

    # Iterate over the dictionary items and split them into smaller dictionaries
    for key, value in dictionary.items():
        value_length = len(value)

        # If adding the current key-value pair to the current dictionary would
        # exceed the target length, start a new dictionary
        if current_length + value_length > target_length and len(current_dict) > 0:
            list_of_dicts.append(current_dict)
            current_dict = {}
            current_length = 0

        # Add the current key-value pair to the current dictionary
        current_dict[key] = value
        current_length += value_length

    # Add the last dictionary to the list
    if len(current_dict) > 0:
        list_of_dicts.append(current_dict)

    # Sort the list of dictionaries by total length of the values
    result = sorted(list_of_dicts, key=lambda d: sum(map(len, d.values())), reverse=True)
    if len(result) > n:
        result[-2] |= result[-1]
        result.pop()

    result = sorted(result, key=lambda d: sum(map(len, d.values())), reverse=True)
    result_str = ""
    for split in result:
        length = 0
        for key, value in split.items():
            length += len(value)
        result_str += str(length) + ","

    print(result_str)
    return result


def split_dict(dictionary: dict, n: int):
    if n <= 2:
        return split_dict_simple(dictionary, n)
    return split_dict_greater_than3(dictionary, n)


if __name__ == "__main__":
    max_width, max_height = 4096, 4096
    TARGET_FILE = 'outputs/pixels_by_labels.json'

    start = time.time()
    pixel_to_faces = PixelToFace(TARGET_FILE, max_width, max_height, preload_STRtree=True, save_normals=False,
                                 save_uvs=False)
    # pixel_to_faces.decompose_all_triangles_STRTree()
    pixel_to_faces.find_faces_of_targets()
    # pixel_to_faces.test_pixel_to_coords()
    end = time.time()
    print(f"Full task took {(end - start) / 60} minutes, ({end - start} seconds)")
