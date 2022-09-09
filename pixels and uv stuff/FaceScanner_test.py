import json
import math
import multiprocessing
import time
from TriangleDecomposer import TriangleDecomposer
import threading


class FaceScanner:
    def __init__(self):
        # these are all arrays!!!!!!!!!
        # self.faces = self.read_in_faces()
        # self.normals = self.read_in_normals()
        # self.uvs = self.read_in_geometry_uvs()
        # self.target_uvs = self.read_in_target_uvs()
        self.read_in_faces()
        self.read_in_normals()
        self.read_in_geometry_uvs()
        self.read_in_target_uvs()
        # this will be the dictionary that contains all points and which triangle they belong to
        # key = (x, y) in pixels
        # value = index of face that holds the uvs
        # since (0, 0) repeats a lot to start we're just gonna manually create it so we can just ignore it later
        # self.read_in_files()
        self.point_to_triangle = {"(0, 0)": 0}


    # apparently in our use case threading to read in files is absolutely useless
    def read_in_files(self):
        t1 = threading.Thread(target=self.read_in_faces)
        t2 = threading.Thread(target=self.read_in_normals)
        t3 = threading.Thread(target=self.read_in_geometry_uvs)
        t4 = threading.Thread(target=self.read_in_target_uvs)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()


    def read_in_faces(self):
        print("Loading in faces")
        with open('geometry_files/geometry_faces.json', 'r') as file:
            data = file.read()
        self.faces = json.loads(data)['faces']


    def read_in_normals(self):
        print("Loading normals")
        with open('geometry_files/geometry_normals.json', 'r') as file:
            data = file.read()
        self.normals = json.loads(data)['normals']


    def read_in_geometry_uvs(self):
        print("Loading geometry uvs")
        with open('geometry_files/geometry_uvs.json', 'r') as file:
            data = file.read()
        self.uvs = json.loads(data)['uvs']


    def read_in_target_uvs(self):
        print("Loading targets")
        with open('geometry_files/target_uvs.json', 'r') as file:
            data = file.read()
        self.target_uvs = json.loads(data)['uvs']


    def read_in_points(self):
        with open('all_points.json', 'r') as file:
            print("length of points", len(self.point_to_triangle))
            data = file.read()
        return json.loads(data)


    def decompose_all_triangles(self):
        print("Decomposing all triangles into points!")
        for index, uv_face in enumerate(self.uvs):
            coord_point_sum = uv_face["a"]["x"] + uv_face["a"]["y"] + uv_face["b"]["x"] + uv_face["b"]["y"] + \
                              uv_face["c"]["x"] + uv_face["b"]["y"]
            # we'll ignore all 0 points which only happens at the beginning in our case
            if coord_point_sum != 0:
                triangle = TriangleDecomposer(uv_face["a"], uv_face["b"], uv_face["c"], 4096, 4096)
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
        with open('all_points.json', 'w') as fp:
            print("length of points", len(self.point_to_triangle))
            print("dumping to points file")
            json.dump(self.point_to_triangle, fp)


    def find_faces_of_target_uvs(self):
        face_results = []
        print("Loading points...")
        points_dict = self.read_in_points()
        print("Searching points for targets...")
        for target_uv in self.target_uvs:
            # TODO need to convert these to pixel coordinates!!!
            target_uv = (uvs_to_pixels(target_uv[0], target_uv[1]))
            target_uv = str(target_uv)
            print(target_uv)
            uv_does_exist = points_dict.get(target_uv, None)
            print(uv_does_exist)
            if uv_does_exist:
                p0 = self.faces[uv_does_exist]["a"]
                p1 = self.faces[uv_does_exist]["b"]
                p2 = self.faces[uv_does_exist]["c"]
                face_results.append(p0)
                face_results.append(p1)
                face_results.append(p2)
        # print(face_results)

        with open('faces_found_fast.json', 'w') as fp:
            print("result length", len(face_results))
            json.dump({"results": face_results}, fp)


def uvs_to_pixels(u, v):
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    # since pixels are only ints we need to floor or use ceiling
    x = math.floor(u * MAX_WIDTH)
    # since 0, 0 is at the bottom left! very important
    y = math.floor((v - 1) * -MAX_HEIGHT)
    return x, y


def processor_controller():
    data = FaceScanner()
    # need manager so the shared variable can be updated properly
    # a normal dict will NOT work!
    manager = multiprocessing.Manager()
    # this is the amount of faces/normals/uvs there are
    # MAX_VALUE = 664284
    MAX_VALUE = 235872  # this is the number of TARGET uvs
    # I can probs move this up to 8 or 9 since each one takes about 10.4%
    process_count = 9  # i had it at 10 before but 6 should be better since less switching
    work_per_thread = MAX_VALUE / process_count
    processes = [None] * process_count
    results = manager.dict()
    for i in range(process_count):
        min_val = int(i * work_per_thread)
        max_val = int((i + 1) * work_per_thread)
        print(f"Process {i}, start:", min_val)
        print(f"Process {i}, end:", max_val)
        print("diff", max_val - min_val)
        # target uvs need to be divided, this might skip values...i'm not sure i think it's okay?
        target_uvs = data.target_uvs[min_val:max_val]
        print(len(data.target_uvs))
        processes[i] = multiprocessing.Process(target=find_faces_of_target_uvs,
                                               args=(target_uvs, data.faces, data.normals, data.uvs, results, i))
        processes[i].start()

    for i in range(process_count):
        processes[i].join()

    with open('faces_found_fast.json', 'w') as fp:
        print("result length", len(results))
        json.dump(dict(results), fp)


def find_faces_of_target_uvs(target_uvs, faces, normals, uvs, results, index):
    print(f"Process {index} ends at {len(target_uvs)} UVs.")
    progress = 0
    # create the class and run the test within bounds
    face_result = []
    counter = 0
    for target_uv in target_uvs:
        target_uv = {"x": target_uv[0], "y": target_uv[1]}
        if counter % 8736 == 0:
            print(f"{time.time()} Process {index} is {progress}/3 of the way through")
            progress += 1
        for i in range(len(faces)):
            uv0 = uvs[i]["a"]
            uv1 = uvs[i]["b"]
            uv2 = uvs[i]["c"]
            if isPtInTriangle(target_uv, uv0, uv1, uv2):
                p0 = faces[i]["a"]
                p1 = faces[i]["b"]
                p2 = faces[i]["c"]
                face_result.append(p0)
                face_result.append(p1)
                face_result.append(p2)
                break
        counter += 1
    # print(face_result)
    results[str(index)] = face_result


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
    start = time.time()
    test = FaceScanner()
    end = time.time()
    print()
    print(f"Finished reading in geometries...Took {end - start} seconds")
    start = time.time()
    # create all the points within the class
    test.decompose_all_triangles()
    # then search through target_uvs
    test.find_faces_of_target_uvs()
    end = time.time()
    print(end - start)
    print(f"Full task took {(end - start)/60} minutes")
