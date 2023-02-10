import json

class ObjToJSON:
    def __init__(self):
        self.obj_file_path = "obj files/Anatomy.OBJ"
        # set to None so values start at 1 instead of 0 like normal
        self.vertices = [None]
        self.normals = [None]
        self.uvs = [None]
        # this just stores indices to all the other vertices, normals, and uvs
        # also I don't think this needs to start at None but just to be consistent
        self.faces_pointers = [None]
        # this will actually store the vertex and stuff
        self.faces_data = [None]

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
                        print("normal")
                    case _:
                        print("default")
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
                face_format["normals_index"].append(pairs[2])

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
        print(self.faces_data)

    # here it splits the faces, normals, and uvs into seperate files
    def create_json_files(self):
        normals_data = {"normals": []}
        uvs_data = {"uvs": []}
        # these are dumb formats I know. I should change it later
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
        normal_format = \
            {
                "a": [],
                "b": [],
                "c": []
            }
        self.create_and_save_face_data()

    # stores the vertices making up each face in the right format
    def create_and_save_face_data(self):
        output_file_name = "geometry_files/geometry_faces.json"
        face_data = {"faces": []}
        vertex_data = \
            {
                "a": [],
                "b": [],
                "c": []
            }
        for face in self.faces_data:
            vertices = face["vertices"]
            # save the vertex data in the right format
            # this might cause issues later if data doesn't get overwritten properly same with uvs and normals
            vertex_data["a"] = vertices[0]
            vertex_data["b"] = vertices[1]
            vertex_data["c"] = vertices[2]
            face_data["faces"].append(vertex_data)
        print("Writing face data to json file.")
        with open("outputs/" + output_file_name, 'w') as fp:
            json.dump(face_data, fp)
        print("Finished writing face data!")



if __name__ == "__main__":
    obj_to_json = ObjToJSON()
    obj_to_json.read_in_OBJ_file()
    obj_to_json.insert_face_data()
