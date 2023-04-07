import concurrent.futures

import json
import math
import time
from TriangleDecomposer import TriangleDecomposer
import bresenham_triangle_class
# from QuadTree3 import QuadTreeNode, Triangle, Boundary, print_tree
from QuadTree4 import QuadTreeNode, Triangle, Boundary, print_tree
from shapely.geometry import Point
from shapely import STRtree
import pickle
from multiprocessing import cpu_count, Process, Queue, Event
import queue as normal_queue


class PixelToFace:

    def __init__(self, target_file_path, preload_STRtree=False, save_normals=True, save_uvs=True):
        # these are all arrays!!!!!!!!!
        self.target_file_path = target_file_path

        # where all the json files are for the geometry faces and uvs
        # self.json_data_directory = "geometry_files/"
        self.json_data_directory = "outputs/geometry_files"

        self.save_normals = save_normals
        self.save_uvs = save_uvs
        # These must be defined first or the threads won't like it
        self.target_pixels_by_name = None
        self.normals = None
        self.uvs = None
        self.str_tree = None
        self.faces = None

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
            futures = [executor.submit(self.read_in_target_pixels)]
            if preload_STRtree:
                futures.append(executor.submit(self.read_in_str_tree))

            futures.append(executor.submit(self.read_in_geometry_uvs))
            futures.append(executor.submit(self.read_in_faces))
            if save_normals:
                futures.append(executor.submit(self.read_in_normals))
            concurrent.futures.wait(futures)
            print("Finished loading files")

        # this will be the dictionary that contains all points and which triangle they belong to
        # key = (x, y) in pixels
        # value = index of face that holds the uvs
        # since (0, 0) repeats a lot to start we're just gonna manually create it so we can just ignore it later
        self.point_to_triangle = {"(0, 0)": 0}
        self.point_to_triangle_C = {"(0, 0)": 0}

        # this is data for the STR tree
        self.triangle_data = []

    def read_in_faces(self):
        print("Loading in faces")
        with open(f'{self.json_data_directory}/geometry_faces.json', 'r') as file:
            data = file.read()
        self.faces = json.loads(data)['faces']

    def read_in_normals(self):
        if self.save_normals:
            print("Loading normals")
            try:
                with open(f'{self.json_data_directory}/geometry_normals.json', 'r') as file:
                    data = file.read()
                self.normals = json.loads(data)['normals']
            except FileNotFoundError:
                print("Couldn't find geometry normals file, ignoring it!")
        else:
            print("Normals not loaded")

    def read_in_geometry_uvs(self):
        print("Loading geometry uvs")
        with open(f'{self.json_data_directory}/geometry_uvs.json', 'r') as file:
            data = file.read()
        self.uvs = json.loads(data)['uvs']

    def read_in_target_pixels(self):
        print("Loading target pixels")
        with open(self.target_file_path, 'r') as file:
            data = file.read()
        self.target_pixels_by_name = json.loads(data)

    # this is a dictionary of pixel coordinates (x,y) that map to the obj face
    # produced by the triangle decomposer
    def read_in_points(self):
        print("Loading points...")
        with open('outputs/all_points_from_model.json', 'r') as file:
            print("length of points", len(self.point_to_triangle))
            data = file.read()
        return json.loads(data)

    def read_in_str_tree(self):
        print("Reading in STR tree")
        with open("outputs/STRtree.bin", "rb") as f:
            self.str_tree = pickle.load(f)

    def decompose_all_triangles_Ccode(self, max_width, max_height):
        print("Decomposing all triangles into points! C++ code")
        for index, uv_face in enumerate(self.uvs):
            coord_point_sum = uv_face["a"]["x"] + uv_face["a"]["y"] + uv_face["b"]["x"] + uv_face["b"]["y"] + \
                              uv_face["c"]["x"] + uv_face["b"]["y"]
            # we'll ignore all 0 points which only happens at the beginning in our case
            if coord_point_sum != 0:
                x1, y1 = uv_face["a"]["x"], uv_face["a"]["y"]
                # print(x1, y1, type(x1), type(y1))
                x2, y2 = uv_face["b"]["x"], uv_face["b"]["y"]
                x3, y3 = uv_face["c"]["x"], uv_face["b"]["y"]
                bresenham = bresenham_triangle_class.BresenhamTriangle(max_width, max_height)
                all_points = bresenham.fill_UV_triangle(x1, y1, x2, y2, x3, y3)
                # triangle 14299 has points {'x': 2998, 'y': 1801}, {'x': 2998, 'y': 1804}, {'x': 2999, 'y': 1801} and UVS of: {'x': 0.7321699857711792, 'y': 0.560259997844696}, {'x': 0.7320399880409241, 'y': 0.5595099925994873}, {'x': 0.7322999835014343, 'y': 0.5602999925613403}
                # triangle 14302 has points {'x': 3001, 'y': 1803}, {'x': 3003, 'y': 1802}, {'x': 2999, 'y': 1801} and UVS of: {'x': 0.7327700257301331, 'y': 0.559660017490387}, {'x': 0.7333499789237976, 'y': 0.5600100159645081}, {'x': 0.7322999835014343, 'y': 0.5602999925613403}
                # if index == 14302 or index == 14299:
                #     print(f"triangle {index} has points {triangle.p1}, {triangle.p2}, {triangle.p3} and UVS of:"
                #           f" {triangle.uv_p1}, {triangle.uv_p2}, {triangle.uv_p3}")
                for point in all_points:
                    # if point in self.point_to_triangle:
                    #     print(f"duplicate point {point} at index {index}. "
                    #           f"Original belongs to index {self.point_to_triangle[point]}")
                    # unfortunately to save it to a json we need to convert it to a string first
                    # if point:
                    key = str(point)
                    self.point_to_triangle_C[key] = index
                    # else:
                    #     print("cringe")

        # then let's save all the points to a json
        # with open('outputs/all_points_from_model_C.json', 'w') as fp:
        #     print("length of points", len(self.point_to_triangle))
        #     print("dumping to points file")
        #     json.dump(self.point_to_triangle, fp)
        with open('outputs/all_points_from_model.json', 'w') as fp:
            print("length of points", len(self.point_to_triangle_C))
            print("dumping to points file")
            json.dump(self.point_to_triangle_C, fp)

    def decompose_all_triangles(self, max_width, max_height):
        print("Decomposing all triangles into points python code")
        for index, uv_face in enumerate(self.uvs):
            coord_point_sum = uv_face["a"]["x"] + uv_face["a"]["y"] + uv_face["b"]["x"] + uv_face["b"]["y"] + \
                              uv_face["c"]["x"] + uv_face["b"]["y"]
            # we'll ignore all 0 points which only happens at the beginning in our case
            # if coord_point_sum != 0:
            triangle = TriangleDecomposer(uv_face["a"], uv_face["b"], uv_face["c"], max_width, max_height)
            all_points = triangle.get_all_points_of_triangle()
            # triangle 14299 has points {'x': 2998, 'y': 1801}, {'x': 2998, 'y': 1804}, {'x': 2999, 'y': 1801} and UVS of: {'x': 0.7321699857711792, 'y': 0.560259997844696}, {'x': 0.7320399880409241, 'y': 0.5595099925994873}, {'x': 0.7322999835014343, 'y': 0.5602999925613403}
            # triangle 14302 has points {'x': 3001, 'y': 1803}, {'x': 3003, 'y': 1802}, {'x': 2999, 'y': 1801} and UVS of: {'x': 0.7327700257301331, 'y': 0.559660017490387}, {'x': 0.7333499789237976, 'y': 0.5600100159645081}, {'x': 0.7322999835014343, 'y': 0.5602999925613403}
            # if index == 14302 or index == 14299:
            #     print(f"triangle {index} has points {triangle.p1}, {triangle.p2}, {triangle.p3} and UVS of:"
            #           f" {triangle.uv_p1}, {triangle.uv_p2}, {triangle.uv_p3}")
            for point in all_points:
                # if point in self.point_to_triangle:
                #     print(f"duplicate point {point} at index {index}. "
                #           f"Original belongs to index {self.point_to_triangle[point]}")
                # unfortunately to save it to a json we need to convert it to a string first
                # if point:
                key = str(point)
                self.point_to_triangle[key] = index
                # else:
                #     print("cringe")

        # then let's save all the points to a json
        with open('outputs/all_points_from_model.json', 'w') as fp:
            print("length of points", len(self.point_to_triangle))
            print("dumping to points file")
            json.dump(self.point_to_triangle, fp)

    def decompose_all_triangles_QuadTree(self, max_width, max_height):

        print("Decomposing all triangles into points using a Quad Tree")
        boundary = Boundary(.0, .0, 1.0, 1.0)
        quad_tree = QuadTreeNode(boundary)

        for index, uv_face in enumerate(self.uvs):
            coord_point_sum = uv_face["a"]["x"] + uv_face["a"]["y"] + uv_face["b"]["x"] + uv_face["b"]["y"] + \
                              uv_face["c"]["x"] + uv_face["b"]["y"]
            # we'll ignore all 0 points which only happens at the beginning in our case
            if coord_point_sum != 0:
                # triangle = TriangleDecomposer(uv_face["a"], uv_face["b"], uv_face["c"], max_width, max_height)
                p1 = (uv_face["a"]["x"], uv_face["a"]["y"])
                p2 = (uv_face["b"]["x"], uv_face["b"]["y"])
                p3 = (uv_face["c"]["x"], uv_face["c"]["y"])
                # I don't remember if index should start at 0 or 1
                triangle = Triangle(p1, p2, p3, index)
                quad_tree.insert_triangle(triangle)
        print_tree(quad_tree, 0)
        return quad_tree

    def decompose_all_triangles_STRTree(self):
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
        # with open("outputs/triangle_data.bin", "wb") as f:
        #     print("Writing triangle data binary")
        #     pickle.dump(self.triangle_data, f)
        print(self.str_tree)
        # return str_tree, triangle_list, triangle_data

    def find_faces_of_targets(self):
        self.label_faces = {}
        points_dict = self.read_in_points()
        print("Searching points for targets...")
        missed_values = 0
        pixels_to_find_count = 0

        for label_name, targets in self.target_pixels_by_name.items():
            face_results = []
            normals_result = []
            uvs_result = []
            pixels_to_find_count += len(targets)
            # I don't think we care about uvs
            # uvs_result = []
            for target in targets:
                # need to convert these to pixel coordinates if using UVs as targets!!!
                # target = (uvs_to_pixels(target[0], target[1]))
                target = str(tuple(target))
                uv_does_exist = points_dict.get(target, None)
                if not uv_does_exist:
                    # print(target)
                    missed_values += 1
                    # print(uv_does_exist)
                if uv_does_exist:
                    p0 = self.faces[uv_does_exist]["a"]
                    p1 = self.faces[uv_does_exist]["b"]
                    p2 = self.faces[uv_does_exist]["c"]
                    face_results.append(p0)
                    face_results.append(p1)
                    face_results.append(p2)
                    if self.save_normals and self.normals:
                        n0 = self.normals[uv_does_exist]["a"]
                        n1 = self.normals[uv_does_exist]["b"]
                        n2 = self.normals[uv_does_exist]["c"]
                        normals_result.append(n0)
                        normals_result.append(n1)
                        normals_result.append(n2)
                    if self.save_uvs:
                        uv0 = list(self.uvs[uv_does_exist]["a"].values())
                        uv1 = list(self.uvs[uv_does_exist]["b"].values())
                        uv2 = list(self.uvs[uv_does_exist]["c"].values())
                        # print(uv0, uv1, uv2)
                        uvs_result.append(uv0)
                        uvs_result.append(uv1)
                        uvs_result.append(uv2)
            if self.save_uvs:
                if self.save_normals:
                    self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result,
                                                    "uvs": uvs_result}
                else:
                    self.label_faces[label_name] = {"vertices": face_results, "uvs": uvs_result}
            elif self.save_normals:
                self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result}
            else:
                self.label_faces[label_name] = {"vertices": face_results}

        print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        # print(face_results)
        # TODO match faces to label name or label whichever we want
        print("Creating faces found by labels json file!")
        # with open('outputs/faces_found_by_labels.json', 'w') as fp:
        #     print("labels faces length", len(self.label_faces))
        #     json.dump(self.label_faces, fp)

    # mixed you get the worst of both of worlds it's really bad!
    def find_faces_of_targets_mixed(self):
        self.label_faces = {}
        points_dict = self.read_in_points()
        print("Searching points for targets...")
        missed_values = 0
        pixels_to_find_count = 0

        if self.str_tree is None:
            print("Reading in STR tree")
            # TODO i could move these reads and writes to their own function
            self.read_in_str_tree()

        for label_name, targets in self.target_pixels_by_name.items():
            face_results = []
            normals_result = []
            uvs_result = []
            pixels_to_find_count += len(targets)
            # I don't think we care about uvs
            # uvs_result = []
            for target in targets:
                # need to convert these to pixel coordinates if using UVs as targets!!!
                # target = (uvs_to_pixels(target[0], target[1]))
                target_tuple = tuple(target)
                target = str(target_tuple)
                uv_does_exist = points_dict.get(target, None)
                if not uv_does_exist:
                    # print(target)
                    # missed_values += 1
                    target = pixel_coords_to_uv(target_tuple)
                    uv_does_exist = self.str_tree.nearest(Point(target))
                    # print(uv_does_exist)
                if uv_does_exist:
                    p0 = self.faces[uv_does_exist]["a"]
                    p1 = self.faces[uv_does_exist]["b"]
                    p2 = self.faces[uv_does_exist]["c"]
                    face_results.append(p0)
                    face_results.append(p1)
                    face_results.append(p2)
                    if self.save_normals and self.normals:
                        n0 = self.normals[uv_does_exist]["a"]
                        n1 = self.normals[uv_does_exist]["b"]
                        n2 = self.normals[uv_does_exist]["c"]
                        normals_result.append(n0)
                        normals_result.append(n1)
                        normals_result.append(n2)
                    if self.save_uvs:
                        uv0 = list(self.uvs[uv_does_exist]["a"].values())
                        uv1 = list(self.uvs[uv_does_exist]["b"].values())
                        uv2 = list(self.uvs[uv_does_exist]["c"].values())
                        # print(uv0, uv1, uv2)
                        uvs_result.append(uv0)
                        uvs_result.append(uv1)
                        uvs_result.append(uv2)
            if self.save_uvs:
                if self.save_normals:
                    self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result,
                                                    "uvs": uvs_result}
                else:
                    self.label_faces[label_name] = {"vertices": face_results, "uvs": uvs_result}
            elif self.save_normals:
                self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result}
            else:
                self.label_faces[label_name] = {"vertices": face_results}

        print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        # print(face_results)
        # TODO match faces to label name or label whichever we want
        print("Creating faces found by labels json file!")
        # with open('outputs/faces_found_by_labels.json', 'w') as fp:
        #     print("labels faces length", len(self.label_faces))
        #     json.dump(self.label_faces, fp)
        print("Creating faces found by labels pickle file!")
        with open('outputs/faces_found_by_labels.bin', 'wb') as fp:
            print("labels faces length", len(self.label_faces))
            pickle.dump(self.label_faces, fp)

    def find_faces_of_targets_quadTree(self, quadTree: QuadTreeNode):
        labels_to_test = ["Deltoid"]
        self.label_faces = {}
        # points_dict = self.read_in_points()
        print("Searching points for targets...")
        missed_values = 0
        pixels_to_find_count = 0
        count = 0
        percent = .1
        print("UV length:", len(self.uvs))
        max_uvs = len(self.target_pixels_by_name["Deltoid"])
        for label_name, targets in self.target_pixels_by_name.items():
            if label_name in labels_to_test:
                face_results = []
                normals_result = []
                uvs_result = []
                pixels_to_find_count += len(targets)
                # I don't think we care about uvs
                # uvs_result = []
                for target in targets:
                    # need to convert these to pixel coordinates if using UVs as targets!!!
                    # target = (uvs_to_pixels(target[0], target[1]))
                    # cast to a tuple it's what is expected
                    target = tuple(target)
                    target = pixel_coords_to_uv(target)
                    uv_does_exist = quadTree.query(target)
                    if not uv_does_exist:
                        # print(target)
                        missed_values += 1
                    count += 1
                    if count == int(max_uvs * percent):
                        print(f"{percent * 100}%")
                        percent += .1
                        # print(uv_does_exist)
                    if uv_does_exist:
                        # print("uv does exist",type(uv_does_exist), uv_does_exist)
                        # print("uv does exist item 1",type(uv_does_exist[0]), uv_does_exist[0])
                        index = uv_does_exist[0].index_value
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
                            # print(uv0, uv1, uv2)
                            uvs_result.append(uv0)
                            uvs_result.append(uv1)
                            uvs_result.append(uv2)
                    else:
                        print(uv_does_exist)
                if self.save_uvs:
                    if self.save_normals:
                        self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result,
                                                        "uvs": uvs_result}
                    else:
                        self.label_faces[label_name] = {"vertices": face_results, "uvs": uvs_result}
                elif self.save_normals:
                    self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result}
                else:
                    self.label_faces[label_name] = {"vertices": face_results}

        print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        # print(face_results)
        # TODO match faces to label name or label whichever we want
        print("Creating faces found by labels json file!")
        with open('outputs/faces_found_by_labels.json', 'w') as fp:
            print("labels faces length", len(self.label_faces))
            json.dump(self.label_faces, fp)

    def find_faces_of_targets_STRTree_original(self, stree: STRtree, triangle_list: list, triangle_data: list):
        labels_to_test = ["Deltoid", "Pectoralis Major"]
        self.label_faces = {}
        # points_dict = self.read_in_points()
        print("Searching points for targets...")
        missed_values = 0
        pixels_to_find_count = 0
        print("UV length:", len(self.uvs))
        for label_name, targets in self.target_pixels_by_name.items():
            if label_name in labels_to_test:
                face_results = []
                normals_result = []
                uvs_result = []
                pixels_to_find_count += len(targets)
                # I don't think we care about uvs
                # uvs_result = []
                for target in targets:
                    # need to convert these to pixel coordinates if using UVs as targets!!!
                    # target = (uvs_to_pixels(target[0], target[1]))
                    # cast to a tuple it's what is expected
                    target = tuple(target)
                    target = pixel_coords_to_uv(target)
                    # should it be nearest
                    uv_does_exist = stree.nearest(Point(target))
                    if not uv_does_exist:
                        # print(target)
                        missed_values += 1
                    if uv_does_exist:
                        # print("uv does exist",type(uv_does_exist), uv_does_exist)
                        # print("uv does exist item 1",type(uv_does_exist[0]), uv_does_exist[0])
                        index = uv_does_exist
                        # current_tri = self.uvs[index]
                        # print(current_tri)
                        real_index = triangle_data[index].index_value
                        if real_index - index != 0:
                            raise Exception("Real index not the same as default index", index, real_index)
                        # index = triangle_data[uv_does_exist].index_value
                        # current_tri = self.uvs[real_index]
                        # print(current_tri)
                        # print(triangle_data[index].vertices)
                        # print(triangle_data[index].index_value)
                        # # print(triangle_data[index-1].vertices)
                        # # print(triangle_data[index+1].vertices)
                        # print(triangle_list[index])
                        # print(stree.geometries[index])
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
                            # print(uv0, uv1, uv2)
                            uvs_result.append(uv0)
                            uvs_result.append(uv1)
                            uvs_result.append(uv2)
                    else:
                        print(uv_does_exist)
                if self.save_uvs:
                    if self.save_normals:
                        self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result,
                                                        "uvs": uvs_result}
                    else:
                        self.label_faces[label_name] = {"vertices": face_results, "uvs": uvs_result}
                elif self.save_normals:
                    self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result}
                else:
                    self.label_faces[label_name] = {"vertices": face_results}

        print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        # # print(face_results)
        # # TODO match faces to label name or label whichever we want
        print("Creating faces found by labels json file!")
        with open('outputs/faces_found_by_labels.json', 'w') as fp:
            print("labels faces length", len(self.label_faces))
            json.dump(self.label_faces, fp)

    def find_faces_of_targets_STRTree(self):
        # labels_to_test = ["Deltoid", "Pectoralis Major"]
        self.label_faces = {}

        # points_dict = self.read_in_points()
        missed_values = 0
        pixels_to_find_count = 0

        print("Beginning search process")
        print("UV length:", len(self.uvs))

        # STR load stuff if not in memory
        if self.str_tree is None:
            print("Reading in STR tree")
            # TODO i could move these reads and writes to their own function
            self.read_in_str_tree()
        # if not self.triangle_data:
        #     print("Reading in Triangle Data")
        #     with open("outputs/triangle_data.bin", "rb") as f:
        #         self.triangle_data = pickle.load(f)

        print("Searching points for targets...")
        for label_name, targets in self.target_pixels_by_name.items():
            # if label_name in labels_to_test:
            if True:
                face_results = []
                normals_result = []
                uvs_result = []
                pixels_to_find_count += len(targets)
                # I don't think we care about uvs
                # uvs_result = []
                for target in targets:
                    # need to convert these to pixel coordinates if using UVs as targets!!!
                    # target = (uvs_to_pixels(target[0], target[1]))
                    # cast to a tuple it's what is expected
                    target = tuple(target)
                    target = pixel_coords_to_uv(target)
                    # should it be nearest?
                    # either way returns an index to that geometry object found
                    uv_does_exist = self.str_tree.nearest(Point(target))
                    if not uv_does_exist:
                        # print(target)
                        missed_values += 1
                    if uv_does_exist:
                        # print("uv does exist",type(uv_does_exist), uv_does_exist)
                        # print("uv does exist item 1",type(uv_does_exist[0]), uv_does_exist[0])
                        index = uv_does_exist
                        # current_tri = self.uvs[index]
                        # print(current_tri)
                        # real_index = self.triangle_data[index].index_value
                        # if real_index - index != 0:
                        #     raise Exception("Real index not the same as default index", index, real_index)
                        # index = triangle_data[uv_does_exist].index_value
                        # current_tri = self.uvs[real_index]
                        # print(current_tri)
                        # print(triangle_data[index].vertices)
                        # print(triangle_data[index].index_value)
                        # # print(triangle_data[index-1].vertices)
                        # # print(triangle_data[index+1].vertices)
                        # print(triangle_list[index])
                        # print(stree.geometries[index])
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
                            # print(uv0, uv1, uv2)
                            uvs_result.append(uv0)
                            uvs_result.append(uv1)
                            uvs_result.append(uv2)
                    else:
                        print(uv_does_exist)
                if self.save_uvs:
                    if self.save_normals:
                        self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result,
                                                        "uvs": uvs_result}
                    else:
                        self.label_faces[label_name] = {"vertices": face_results, "uvs": uvs_result}
                elif self.save_normals:
                    self.label_faces[label_name] = {"vertices": face_results, "normals": normals_result}
                else:
                    self.label_faces[label_name] = {"vertices": face_results}

        print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        # # print(face_results)
        # # TODO match faces to label name or label whichever we want
        # print("Creating faces found by labels json file!")
        # with open('outputs/faces_found_by_labels.json', 'w') as fp:
        #     print("labels faces length", len(self.label_faces))
        #     json.dump(self.label_faces, fp)
        with open('outputs/faces_found_by_labels.bin', 'wb') as fp:
            print("labels faces length", len(self.label_faces))
            pickle.dump(self.label_faces, fp)

    # time to beat 7.5 minutes
    def find_faces_of_targets_STRTree_processes(self):
        thread_count = 5  # n-1? cores best not threads
        self.label_faces = {}

        # points_dict = self.read_in_points()

        print("Beginning search process")
        # print("UV length:", len(self.uvs))

        # STR load stuff if not in memory
        if self.str_tree is None:
            print("Reading in STR tree")
            # TODO i could move these reads and writes to their own function
            self.read_in_str_tree()
        work_by_thread = split_dict(self.target_pixels_by_name, thread_count)
        with concurrent.futures.ProcessPoolExecutor(max_workers=thread_count) as executor:
            # executor.map(self.str_query, {"test": "hi"})
            futures = []
            for i in range(thread_count):
                futures.append(executor.submit(self.str_query, work_by_thread[i], i))
            # results = [future.result() for future in futures]
            # take them as they finish instead of waiting around
            # https://stackoverflow.com/questions/52082665/store-results-threadpoolexecutor
            for future in concurrent.futures.as_completed(futures):
                self.label_faces |= future.result()

        # # print(face_results)
        # # TODO match faces to label name or label whichever we want

        # start = time.time()
        # print("Creating faces found by labels json file!")
        # with open('outputs/faces_found_by_labels.json', 'w') as fp:
        #     print("labels faces length", len(self.label_faces))
        #     json.dump(self.label_faces, fp)
        # end = time.time()
        # print(f"Full file JSON dump took {(end - start) / 60} minutes")
        #
        start = time.time()
        print("Creating faces found by labels pickle file!")
        with open('outputs/faces_found_by_labels.bin', 'wb') as fp:
            print("labels faces length", len(self.label_faces))
            pickle.dump(self.label_faces, fp)
        end = time.time()
        print(f"Full file PICKLE dump took {(end - start) / 60} minutes")

    def str_query(self, target_pixels_by_name: dict, thread_count):
        label_faces = {}
        print("Searching points for targets...")
        print(len(list(target_pixels_by_name.keys())))
        print(thread_count)
        missed_values = 0
        pixels_to_find_count = 0
        for label_name, targets in target_pixels_by_name.items():
            face_results = []
            normals_result = []
            uvs_result = []
            pixels_to_find_count += len(targets)

            for target in targets:
                # need to convert these to pixel coordinates if using UVs as targets!!!
                # cast to a tuple it's what is expected
                target = tuple(target)
                target = pixel_coords_to_uv(target)
                # should it be nearest?
                # either way returns an index to that geometry object found
                uv_does_exist = self.str_tree.nearest(Point(target))
                if not uv_does_exist:
                    # print(target)
                    missed_values += 1
                if uv_does_exist:
                    index = uv_does_exist
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
                        # print(uv0, uv1, uv2)
                        uvs_result.append(uv0)
                        uvs_result.append(uv1)
                        uvs_result.append(uv2)
                else:
                    print(uv_does_exist)
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
        print(
            f"Thread: {thread_count}\nMissed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        return label_faces

    # 3.2 minutes to beat against processes, THIS IS MUCH SLOWER and is the same as using no threads it might even be worse
    def find_faces_of_targets_STRTree_threaded(self):
        thread_count = 12
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
        self.convert_pixels_to_points()
        work_by_thread = split_dict(self.target_pixels_by_name, thread_count)
        results = []
        start = time.time()
        print("Creating threads")

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:

            futures = []
            for i in range(thread_count):
                futures.append(executor.submit(self.str_query_thread, work_by_thread[i], i))

            # # # CREATE THE PROCESS WHILE THREADS DO WORK
            # consumer_process = Process(target=self.consumer, args=(queue, thread_count, process_result))
            # consumer_process.start()

            # results = [future.result() for future in futures]
            # take them as they finish instead of waiting around
            # https://stackoverflow.com/questions/52082665/store-results-threadpoolexecutor
            for future in concurrent.futures.as_completed(futures):
                thread_start_time = time.time()
                print("finished")
                result = future.result()
                # results.append(future.result())
                # queue.put(result)
                for name, indices in result.items():
                    self.get_geometries_by_index_list(self.label_faces, name, indices)
                thread_end_time = time.time()
                time_for_indexing += thread_end_time - thread_start_time
            print("TIME FOR INDEXING ALL GEOMETRIES", time_for_indexing)

        end = time.time()
        print(f"Threading task took {(end - start) / 60} minutes")
        # for result in results:
        #     for name, indices in result.items():
        #         self.get_geometries_by_index_list(self.label_faces, name, indices)

        # fix later, get
        # self.label_faces = process_result.get(block=True)

        # Wait for the consumer process to finish
        # I NEED TO CALL JOIN AFTER WHY?
        # consumer_process.join()
        # print("Consumer finished")
        # # print(face_results)
        # # TODO match faces to label name or label whichever we want

        # start = time.time()
        # print("Creating faces found by labels json file!")
        # with open('outputs/faces_found_by_labels.json', 'w') as fp:
        #     print("labels faces length", len(self.label_faces))
        #     json.dump(self.label_faces, fp)
        # end = time.time()
        # print(f"Full file JSON dump took {(end - start) / 60} minutes")

        start = time.time()
        print("Creating faces found by labels pickle file!")
        with open('outputs/faces_found_by_labels.bin', 'wb') as fp:
            print("labels faces length", len(self.label_faces))
            pickle.dump(self.label_faces, fp)
        end = time.time()
        print(f"Full file PICKLE dump took {(end - start) / 60} minutes")

    # converts all target points to Point objects
    def convert_pixels_to_points(self):
        start = time.time()
        for name, pixel_list in self.target_pixels_by_name.items():
            for count, pixel in enumerate(pixel_list):
                pixel_list[count] = Point(pixel_coords_to_uv(tuple(pixel)))
        end = time.time()
        print(f"Conversion of pixels to UV Points {(end - start)} seconds")

    # returns only the indexes associated with each face
    def str_query_thread(self, target_pixels_by_name: dict, thread_count):
        label_indexes = {}
        print(f"Thread {thread_count+1} is searching points for targets of {len(list(target_pixels_by_name.keys()))}")
        missed_values = 0
        pixels_to_find_count = 0
        for label_name, targets in target_pixels_by_name.items():
            pixels_to_find_count += len(targets)
            # create the inital empty array
            label_indexes[label_name] = []
            label_indexes[label_name] = self.str_tree.nearest(targets)

        print(f"Missed {round((missed_values / pixels_to_find_count) * 100, 2)}% of target pixels.")
        print(f"Missed {missed_values} out of {pixels_to_find_count}, could not find their matching faces.")
        return label_indexes
        # return {"indices_list": label_indexes, "label_name": label_name}

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

    def consumer(self, queue: Queue, threads_created_count, process_result):
        print("CONSUMER")
        label_faces = {}
        work_received_counter = 0
        while True:
            # Wait indefinitely until there is work to be done
            try:
                # removes the data from the queue
                data = queue.get(timeout=.1)
                work_received_counter += 1
            except normal_queue.Empty:
                # No work to be done, keep waiting
                continue

            for label_name, list_of_indices in data.items():
                # Do something with the result
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
            if work_received_counter == threads_created_count:
                print("Received and processed all work loads")
                process_result.put(label_faces)
                break


def uvs_to_pixels(u, v):
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    # since pixels are only ints we need to floor or use ceiling
    x = math.floor(u * MAX_WIDTH)
    # since 0, 0 is at the bottom left! very important
    y = math.floor((v - 1) * -MAX_HEIGHT)
    return x, y


def pixel_coords_to_uv(coord):
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    # u is width, v is height
    # coords tuple will be key
    x, y = coord
    u = x / MAX_WIDTH
    # since 0, 0 is at the bottom left! very important
    v = 1 - y / MAX_HEIGHT
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
    # start = time.time()
    # pixel_to_faces = PixelToFace(TARGET_FILE)
    # end = time.time()
    # print()
    # print(f"Finished reading in geometries...Took {end - start} seconds")
    # start1 = time.time()
    #
    # # create all the points within the class
    # # IMPORTANT you can comment this out if it's already been done!
    # pixel_to_faces.decompose_all_triangles(max_width, max_height)
    #
    # # then search through target_uvs
    # pixel_to_faces.find_faces_of_targets()
    # end = time.time()
    # print(f"Triangle decompose and finding faces took {end - start} seconds.")
    # print()
    # print(f"Full task took {(end - start) / 60} minutes")

    # print("Starting Quad Tree version")
    # start = time.time()
    # pixel_to_faces = PixelToFace(TARGET_FILE)
    # end = time.time()
    # print()
    # print(f"Finished reading in geometries...Took {end - start} seconds")
    # start1 = time.time()
    #
    # # decompose with quad tree
    # quad_tree_root = pixel_to_faces.decompose_all_triangles_QuadTree(max_width, max_height)
    # pixel_to_faces.find_faces_of_targets_quadTree(quad_tree_root)
    # end = time.time()
    # print(f"Triangle decompose and finding faces using quadtree took {end - start} seconds.")
    # print()
    # print(f"Full task took {(end - start) / 60} minutes")

    # print("Starting STR tree version")
    # start = time.time()
    # pixel_to_faces = PixelToFace(TARGET_FILE, save_normals=False, save_uvs=False)
    # end = time.time()
    # print()
    # print(f"Finished reading in geometries...Took {end - start} seconds")
    # start1 = time.time()
    #
    # # TODO CLEAN UP ALOT OF MISC CODE
    # #   Seperate out the triangle class
    # #   make find faces faster either through threads or processes I want to reduce the run time to under a minute
    #
    # # decompose with stree
    # start = time.time()
    # pixel_to_faces = PixelToFace(TARGET_FILE, save_normals=False, save_uvs=False)
    # # str_tree_root, triangle_list, triangle_data = pixel_to_faces.decompose_all_triangles_STRTree(max_width, max_height)
    # pixel_to_faces.decompose_all_triangles_STRTree()
    # # find closest point
    # pixel_to_faces.find_faces_of_targets_STRTree()
    # end = time.time()
    # print(f"Triangle decompose and finding faces using STRtree took {end - start} seconds.")
    # print()
    # print(f"Full task took {(end - start) / 60} minutes")

    # start = time.time()
    # pixel_to_faces = PixelToFace(TARGET_FILE, save_normals=False, save_uvs=False)
    # # pixel_to_faces.decompose_all_triangles_STRTree()
    # pixel_to_faces.find_faces_of_targets_STRTree_processes()
    # end = time.time()
    # print(f"Full task took {(end - start) / 60} minutes")

    start = time.time()
    pixel_to_faces = PixelToFace(TARGET_FILE, preload_STRtree=True, save_normals=False, save_uvs=False)
    # pixel_to_faces.decompose_all_triangles_STRTree()
    # pixel_to_faces.find_faces_of_targets_STRTree_threaded()
    end = time.time()
    print(f"Full task took {(end - start) / 60} minutes")
