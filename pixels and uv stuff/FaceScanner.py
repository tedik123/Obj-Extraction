import json
import multiprocessing
import time


class FaceScanner:
    def __init__(self):
        # these are all arrays!!!!!!!!!
        self.faces = self.read_in_faces()
        self.normals = self.read_in_normals()
        self.uvs = self.read_in_geometry_uvs()
        self.target_uvs = self.read_in_target_uvs()

    def read_in_faces(self):
        with open('geometry_files/geometry_faces.json', 'r') as file:
            data = file.read()
        return json.loads(data)['faces']

    def read_in_normals(self):
        with open('geometry_files/geometry_normals.json', 'r') as file:
            data = file.read()
        return json.loads(data)['normals']

    def read_in_geometry_uvs(self):
        with open('geometry_files/geometry_uvs.json', 'r') as file:
            data = file.read()
        return json.loads(data)['uvs']

    def read_in_target_uvs(self):
        with open('geometry_files/target_uvs.json', 'r') as file:
            data = file.read()
        return json.loads(data)['uvs']

    def find_faces_of_target_uvs(self):
        face_result = []
        for target_uv in self.target_uvs:
            target_uv = {"x": target_uv[0], "y": target_uv[1]}
            for i in range(len(self.faces)):
                uv0 = self.uvs[i]["a"]
                uv1 = self.uvs[i]["b"]
                uv2 = self.uvs[i]["c"]
                if self.isPtInTriangle(target_uv, uv0, uv1, uv2):
                    p0 = self.faces[i]["a"]
                    p1 = self.faces[i]["b"]
                    p2 = self.faces[i]["c"]
                    face_result.append(p0)
                    face_result.append(p1)
                    face_result.append(p2)
                    break
        print(face_result)

    def isPtInTriangle(self, p, p0, p1, p2):
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

    with open('faces_found.json', 'w') as fp:
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
        counter+=1
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
    # test = FaceScanner()
    # print("Finished reading...starting search")
    start = time.time()
    print("Start time", start)
    # test.find_faces_of_target_uvs()
    # print("BYE")
    # run all the processes
    processor_controller()
    end = time.time()
    print(end - start)
