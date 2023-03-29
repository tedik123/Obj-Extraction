import json
import math
import time
from TriangleDecomposer import TriangleDecomposer
import bresenham_triangle_class
# from QuadTree3 import QuadTreeNode, Triangle, Boundary, print_tree
from QuadTree4 import QuadTreeNode, Triangle, Boundary, print_tree
from shapely.geometry import Point, Polygon
from shapely import STRtree
import pickle

class PixelToFace:

    def __init__(self, target_file_path, save_normals=True, save_uvs=True):
        # these are all arrays!!!!!!!!!
        self.target_file_path = target_file_path

        # where all the json files are for the geometry faces and uvs
        # self.json_data_directory = "geometry_files/"
        self.json_data_directory = "outputs/geometry_files"

        self.save_normals = save_normals
        self.save_uvs = save_uvs
        self.normals = None
        self.uvs = None

        # FIXME I could use async for these tasks so the load is faster
        self.read_in_faces()
        if save_normals:
            self.read_in_normals()
        self.read_in_geometry_uvs()
        self.read_in_target_pixels()

        # this will be the dictionary that contains all points and which triangle they belong to
        # key = (x, y) in pixels
        # value = index of face that holds the uvs
        # since (0, 0) repeats a lot to start we're just gonna manually create it so we can just ignore it later
        self.point_to_triangle = {"(0, 0)": 0}
        self.point_to_triangle_C = {"(0, 0)": 0}

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
            if coord_point_sum != 0:
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
    def decompose_all_triangles_STRTree(self, max_width, max_height):

        print("Decomposing all triangles into points using a STR Tree")
        triangle_list = []
        # we'll store the full object here in parallel
        triangle_data = []
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
            triangle_data.append(triangle)
        str_tree = STRtree(triangle_list)
        with open("outputs/STRtree.bin", "wb") as f:
            print("Writing STR tree binary")
            pickle.dump(str_tree, f)
        with open("outputs/triangle_data.bin", "wb") as f:
            print("Writing triangle data binary")
            pickle.dump(triangle_data, f)
        print(str_tree)
        return str_tree, triangle_list, triangle_data

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
        with open('outputs/faces_found_by_labels.json', 'w') as fp:
            print("labels faces length", len(self.label_faces))
            json.dump(self.label_faces, fp)

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
                        print(f"{percent*100}%")
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
    def find_faces_of_targets_STRTree_original(self, stree: STRtree, triangle_list:list, triangle_data:list):
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

    def find_faces_of_targets_STRTree(self, stree: STRtree, triangle_list:list, triangle_data:list):
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

    print("Starting STR tree version")
    start = time.time()
    pixel_to_faces = PixelToFace(TARGET_FILE)
    end = time.time()
    print()
    print(f"Finished reading in geometries...Took {end - start} seconds")
    start1 = time.time()

    # decompose with quad tree
    str_tree_root, triangle_list, triangle_data = pixel_to_faces.decompose_all_triangles_STRTree(max_width, max_height)
    pixel_to_faces.find_faces_of_targets_STRTree(str_tree_root, triangle_list, triangle_data)
    end = time.time()
    print(f"Triangle decompose and finding faces using STRtree took {end - start} seconds.")
    print()
    print(f"Full task took {(end - start) / 60} minutes")
