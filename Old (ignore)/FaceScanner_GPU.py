import json
import multiprocessing
import time

import numpy
from numba import jit, cuda, vectorize


class FaceScanner:
    def __init__(self):
        # these are all arrays!!!!!!!!!
        self.faces = numpy.array(self.read_in_faces(), dtype= numpy.float64)
        # print(self.faces[2])
        self.normals = numpy.array(self.read_in_normals(),dtype= numpy.float64)
        self.uvs = numpy.array(self.read_in_geometry_uvs(),dtype= numpy.float64)
        self.target_uvs = numpy.array(self.read_in_target_uvs(),dtype= numpy.float64)

    def read_in_faces(self):
        with open('geometry_files/geometry_faces.json', 'r') as file:
            data = file.read()
        faces = json.loads(data)['faces']
        result = []
        for face in faces:

            result.append(list(face.values()))
        return result

    def read_in_normals(self):
        with open('geometry_files/geometry_normals.json', 'r') as file:
            data = file.read()
        normals = json.loads(data)['normals']
        result = []
        for normal in normals:
            result.append(list(normal.values()))
        return result

    def read_in_geometry_uvs(self):
        with open('geometry_files/geometry_uvs.json', 'r') as file:
            data = file.read()
        uvs = json.loads(data)['uvs']
        result = []
        for uv in uvs:
            values = list(uv.values())
            uv1 = list(values[0].values())
            uv2 = list(values[1].values())
            uv3 = list(values[2].values())
            # print([uv1, uv2, uv3])
            result.append([uv1, uv2, uv3])
        return result

    # I'm inconsistent and just saved this as a 2d array
    def read_in_target_uvs(self):
        with open('geometry_files/target_uvs.json', 'r') as file:
            data = file.read()
        # result = []
        return json.loads(data)['uvs']
        # for uv in uvs:
        #     result.append(list(uv.values()))
        # return result


@jit(nopython=True, target_backend='cuda')
def find_faces_of_target_uvs(target_uvs, faces, normals, uvs):
    # idk the dimensions it should be
    # create a 2d array of ~650k where each index contains 3 values
    face_result = numpy.zeros(shape=[664284, 3], dtype= numpy.float64)
    np_index = 0
    for target_uv in target_uvs:
        # target_uv = {"x": target_uv[0], "y": target_uv[1]}
        for i in range(len(faces)):
            uv0 = uvs[i][0]
            uv1 = uvs[i][1]
            uv2 = uvs[i][2]
            if isPtInTriangle(target_uv, uv0, uv1, uv2):
                p0 = faces[i][0]
                p1 = faces[i][1]
                p2 = faces[i][2]
                face_result[np_index] = p0
                np_index += 1
                face_result[np_index] = p1
                np_index += 1
                face_result[np_index] = p2
                np_index += 1
                break
    # print(face_result)


@jit(nopython=True)
def isPtInTriangle(p, p0, p1, p2):
    x0 = p[0]
    y0 = p[1]
    x1 = p0[0]
    y1 = p0[1]
    x2 = p1[0]
    y2 = p1[1]
    x3 = p2[0]
    y3 = p2[1]
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

        return False
    return False

if __name__ == "__main__":
    test = FaceScanner()
    print("Finished reading...starting search")
    start = time.time()
    # test.find_faces_of_target_uvs()
    find_faces_of_target_uvs(test.target_uvs, test.faces, test.normals, test.uvs)
    # print("BYE")
    # run all the processes
    # processor_controller()
    end = time.time()
    print(end - start)
