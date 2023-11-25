import json
import os
import time
import pickle


class ObjToGeometryFiles:
    def __init__(self, obj_file_path, file_path_prefix= "", directory = ""):
        self.obj_file_path = obj_file_path
        self.file_path_prefix = file_path_prefix
        self.directory = directory
        # set to None so values start at 1 instead of 0 like normal
        self.vertices = [None]
        self.normals = [None]
        self.uvs = [None]
        # this just stores indices to all the other vertices, normals, and uvs
        # also I don't think this needs to start at None but just to be consistent
        self.faces_pointers = [None]
        # this will actually store the vertex and stuff
        self.faces_data = []

    def read_in_OBJ_file(self):
        # vertex
        # fh = ["v 0.43952997 1.25646808 -0.0251",
        #         "v -0.43952997 1.25646808 -0.0251",
        #         "v 0.11119099 0.33366699 -0.106435",
        #         "v -0.11119099 0.33366699 -0.106435",
        #         "v 0.20456198 0.46900499 0.00128"]
        # vt
        # fh = ["vt 0.76863 0.42459",
        #       "vt 0.7689 0.4227",
        #       "vt 0.76424 0.42418",
        #       "vt 0.76268 0.42215",
        #       "vt 0.76228 0.4181"]
        # f
        # fh = [
        #     "f 325753/1 326701/1 329702/1",
        #     "f 325747/1 327473/1 332052/1",
        #     "f 327474/1 327511/1 332053/1",
        #     "f 327155/1 325600/1 325103/1",
        # ]
        start =  time.time()
        with open(self.obj_file_path) as fh:
            for line in fh:
                # print()
                line = line.rstrip()
                match line[:2]:
                    case "f ":
                        self.save_and_format_face_values(line)
                    case "v ":
                        # print("vertex")
                        self.save_and_format_vertices(line)
                    case "vt":
                        # print("texture")
                        self.save_and_format_vertex_textures(line)
                    case "vn":
                        self.save_and_format_normals(line)
                    # ignores EOF, and comments, might need to fix later to remember the name?
                    case _:
                        continue
        end = time.time()
        print(f"Read in and conversion of OBJ file took {(end - start)} seconds")
        # print(self.vertices)
        # print(self.uvs)
        # print(self.faces)

    # vertex line is the string line containing the vertex information
    def save_and_format_vertices(self, vertex_line: str):
        vertices = vertex_line.split()
        # skip the 'v' keep the rest while converting everything to a float
        self.vertices.append([float(i) for i in vertices[1:]])
        # print(vertices[1:])

    def save_and_format_vertex_textures(self, vt_line: str):
        vt = vt_line.split()
        # skip the 'vt' keep the rest while converting everything to a float
        self.uvs.append([float(i) for i in vt[1:]])
        # print(vt[1:])

    def save_and_format_normals(self, normal_line: str):
        vn = normal_line.split()
        # skip the 'vn' keep the rest while converting everything to a float
        self.normals.append([float(i) for i in vn[1:]])

    def save_and_format_face_values(self, face_line: str):
        face = face_line[2:]
        face = face.split()
        face_format = {
            "vertex_index": [],
            "uvs_index": [],
            "normals_index": []
        }
        for pairs in face:
            pairs = pairs.split("/")
            # means there's at most 3 v1,vt1,vn1
            # but could also be v1,None, vn1 ignoring that for now with the v1//vn1 syntax
            face_format["vertex_index"].append(int(pairs[0]))
            if len(pairs) > 1:
                face_format["uvs_index"].append(int(pairs[1]))
            if len(pairs) > 2:
                face_format["normals_index"].append(int(pairs[2]))

        self.faces_pointers.append(face_format)

    # this actually stores the vertex values and such for the faces instead of just indices
    def insert_face_data(self):
        for face_data in self.faces_pointers[1:]:
            face = {
                "vertices": [],
                "uvs": [],
                "normals": []
            }
            for vertex_index in face_data["vertex_index"]:
                face["vertices"].append(self.vertices[vertex_index])

            for uv_index in face_data["uvs_index"]:
                face["uvs"].append(self.uvs[uv_index])

            for normal_index in face_data["normals_index"]:
                face["normals"].append(self.normals[normal_index])
            self.faces_data.append(face)
        # print(self.faces_data[0]["uvs"])

    # here it splits the faces, normals, and uvs into seperate files
    def create_geometry_files(self):
        start = time.time()
        # I can probably create threads for this by saving it to a class variable instead of going linearly
        self.create_and_save_face_data()
        self.create_and_save_uv_data()
        self.create_and_save_normal_data()
        end = time.time()
        print(f"Writing geometry files took {(end - start)} seconds")

    # stores the vertices making up each face in the right format
    def create_and_save_face_data(self):
        output_file_name = "geometry_faces"
        self.face_data = {"faces": []}
        for face in self.faces_data:
            vertex_data = \
                {
                    "a": [],
                    "b": [],
                    "c": []
                }
            vertices = face["vertices"]
            # save the vertex data in the right format
            # this might cause issues later if data doesn't get overwritten properly same with uvs and normals
            vertex_data["a"] = vertices[0]
            vertex_data["b"] = vertices[1]
            vertex_data["c"] = vertices[2]
            self.face_data["faces"].append(vertex_data)
        print("Writing face data to json file.")
        # with open("outputs/" + output_file_name, 'w') as fp:
        #     json.dump(face_data, fp)
        self.write_binary_file(output_file_name, self.face_data)
        print("Finished writing face data!")

    def create_and_save_uv_data(self):
        output_file_name = "geometry_uvs"
        self.uvs_data = {"uvs": []}
        for face in self.faces_data:
            uv_format = \
                {
                    "a": {
                        "x": 0,
                        "y": 0
                    },
                    "b": {
                        "x": 0,
                        "y": 0
                    },
                    "c": {
                        "x": 0,
                        "y": 0
                    }
                }
            uvs = face["uvs"]
            uv_format["a"]["x"] = uvs[0][0]
            uv_format["a"]["y"] = uvs[0][1]

            uv_format["b"]["x"] = uvs[1][0]
            uv_format["b"]["y"] = uvs[1][1]

            uv_format["c"]["x"] = uvs[2][0]
            uv_format["c"]["y"] = uvs[2][1]
            self.uvs_data["uvs"].append(uv_format)
        print("Writing uv data to json file.")
        # with open("outputs/" + output_file_name, 'w') as fp:
        #     json.dump(self.uvs_data, fp)
        self.write_binary_file(output_file_name, self.uvs_data)

        print("Finished writing uv data!")

    def create_and_save_normal_data(self):
        output_file_name = "geometry_normals"
        self.normals_data = {"normals": []}
        # just checking if the first one has normals if it does then it's good enough ig
        if len(self.faces_data[0]["normals"]) > 1:
            for face in self.faces_data:
                normal_data = \
                    {
                        "a": [],
                        "b": [],
                        "c": []
                    }
                normals = face["normals"]
                normal_data["a"] = normals[0]
                normal_data["b"] = normals[1]
                normal_data["c"] = normals[2]
                self.normals_data["normals"].append(normal_data)
            print("Writing normals data to json file.")
            # with open("outputs/" + output_file_name, 'w') as fp:
            #     json.dump(self.normals_data, fp)
            self.write_binary_file(output_file_name, self.normals_data)
            print("Finished writing normals data!")

    def write_binary_file(self, output_file_name, data):
        if self.directory != "":
            output_dir = f"{self.file_path_prefix}outputs/{self.directory}/geometry_files"
        else:
            output_dir = f"{self.file_path_prefix}outputs/geometry_files"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_dir + "/" + output_file_name + ".bin", 'wb') as fp:
            pickle.dump(data, fp)


if __name__ == "__main__":
    start = time.time()
    base_obj_file_path = "../pixels and uv stuff/obj files/Anatomy.OBJ"
    obj_to_json = ObjToGeometryFiles(base_obj_file_path)
    obj_to_json.read_in_OBJ_file()
    obj_to_json.insert_face_data()
    obj_to_json.create_geometry_files()

    end = time.time()
    print()
    print(f"Finished creating geometry files...Took {end - start} seconds")
