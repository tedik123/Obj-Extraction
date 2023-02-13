import json
import math
import multiprocessing
import time
from TriangleDecomposer import TriangleDecomposer


class PixelToFace:

    def __init__(self, target_file_path):
        # these are all arrays!!!!!!!!!
        self.target_file_path = target_file_path

        # where all the json files are for the geometry faces and uvs
        # self.json_data_directory = "geometry_files/"
        self.json_data_directory = "outputs/geometry_files"

        # FIXME I could use async for these tasks so the load is faster
        self.read_in_faces()
        self.read_in_normals()
        self.read_in_geometry_uvs()
        self.read_in_target_pixels()
        # this will be the dictionary that contains all points and which triangle they belong to
        # key = (x, y) in pixels
        # value = index of face that holds the uvs
        # since (0, 0) repeats a lot to start we're just gonna manually create it so we can just ignore it later
        self.point_to_triangle = {"(0, 0)": 0}

    def read_in_faces(self):
        print("Loading in faces")
        with open(f'{self.json_data_directory}/geometry_faces.json', 'r') as file:
            data = file.read()
        self.faces = json.loads(data)['faces']

    def read_in_normals(self):
        print("Loading normals")
        try:
            with open(f'{self.json_data_directory}/geometry_normals.json', 'r') as file:
                data = file.read()
            self.normals = json.loads(data)['normals']
        except FileNotFoundError:
            print("Couldn't find geometry normals file, ignoring it!")

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

    def decompose_all_triangles(self, max_width, max_height):
        print("Decomposing all triangles into points!")
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

    def find_faces_of_targets(self):
        self.muscle_faces = {}
        points_dict = self.read_in_points()
        print("Searching points for targets...")
        for muscle_name, targets in self.target_pixels_by_name.items():
            face_results = []
            normals_result = []
            # I don't think we care about uvs
            # uvs_result = []
            for target in targets:
                # need to convert these to pixel coordinates if using UVs as targets!!!
                # target = (uvs_to_pixels(target[0], target[1]))
                target = str(tuple(target))
                uv_does_exist = points_dict.get(target, None)
                if not uv_does_exist:
                    print(target)
                    # print(uv_does_exist)
                if uv_does_exist:
                    p0 = self.faces[uv_does_exist]["a"]
                    p1 = self.faces[uv_does_exist]["b"]
                    p2 = self.faces[uv_does_exist]["c"]
                    face_results.append(p0)
                    face_results.append(p1)
                    face_results.append(p2)
                    # n0 = self.normals[uv_does_exist]["a"]
                    # n1 = self.normals[uv_does_exist]["b"]
                    # n2 = self.normals[uv_does_exist]["c"]
                    # normals_result.append(n0)
                    # normals_result.append(n1)
                    # normals_result.append(n2)
            # self.muscle_faces[muscle_name] = {"vertices": face_results, "normals": normals_result}
            self.muscle_faces[muscle_name] = {"vertices": face_results}

        # print(face_results)
        # TODO match faces to muscle name or label whichever we want
        with open('outputs/faces_found_by_muscles.json', 'w') as fp:
            print("Muscles faces length", len(self.muscle_faces))
            json.dump(self.muscle_faces, fp)


def uvs_to_pixels(u, v):
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    # since pixels are only ints we need to floor or use ceiling
    x = math.floor(u * MAX_WIDTH)
    # since 0, 0 is at the bottom left! very important
    y = math.floor((v - 1) * -MAX_HEIGHT)
    return x, y

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
    TARGET_FILE = 'outputs/pixels_by_muscles.json'
    start = time.time()
    pixel_to_faces = PixelToFace(TARGET_FILE)
    end = time.time()
    print()
    print(f"Finished reading in geometries...Took {end - start} seconds")
    start1 = time.time()

    # create all the points within the class
    # IMPORTANT you can comment this out if it's already been done!
    pixel_to_faces.decompose_all_triangles()

    # then search through target_uvs
    pixel_to_faces.find_faces_of_targets()
    end = time.time()
    print(f"Triangle decompose and finding faces took {end-start} seconds.")
    print()
    print(f"Full task took {(end - start) / 60} minutes")
