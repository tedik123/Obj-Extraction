import json
import time
from collections import OrderedDict


class PixelIndexer:

    def __init__(self, label_names):
        self.faces_found_file_path = 'outputs/faces_found_by_labels.json'
        self.faces_found_by_labels = None
        self.read_in_faces_found_by_labels()
        self.label_names = label_names

    def read_in_faces_found_by_labels(self):
        print("Reading in faces by labels")
        print(f"Opening {self.faces_found_file_path}")
        with open(self.faces_found_file_path, 'r') as file:
            data = file.read()
            self.faces_found_by_labels = json.loads(data)

    def create_indexed_faces(self):
        print("Starting indexing of faces!")
        if self.label_names:
            labels_to_do = {}
            for label in self.label_names:
                temp = self.faces_found_by_labels[label]
                labels_to_do[label] = temp
            # overwrite it to only the labels we care about
            self.faces_found_by_labels = labels_to_do
        # this will have to change later so we can handle normals, faces, and uvs?
        for label_name, values in self.faces_found_by_labels.items():
            vertices = values["vertices"]
            print(len(vertices))
            # normals = values["normals"]

            # we need to preserve the order the keys & indices were inserted
            vertex_map = OrderedDict()
            # WE MUST start at 1 because that's how .obj files are interpreted
            vertex_index = 1
            # this can be no longer than the amount of vertices
            indexed_vertex_list = [None] * len(vertices)

            # FIXME if we need normals you should abstract this to it's own function
            for i, vertex in enumerate(vertices):
                t_vertex = tuple(vertex)
                # if it already exists we just need to grab the original vertex index
                if t_vertex in vertex_map:
                    index_of_original_vertex = vertex_map[t_vertex]
                    indexed_vertex_list[i] = index_of_original_vertex
                # if it doesn't exist we need to create it and update the index
                else:
                    vertex_map[t_vertex] = vertex_index
                    indexed_vertex_list[i] = vertex_index
                    vertex_index += 1
            # so now we have our label with an indexed list of values
            # we'll use the keys to create the UNIQUE vertices
            # and then the indexed_vertex_list will help us create the faces
            if len(indexed_vertex_list) % 3 != 0:
                raise Exception("Something went wrong the list must be divisible by 3!")
            # remove nones from list and cleans up duplicates and returns a list of tuples of size 3
            index_tuples = self.format_indices(indexed_vertex_list)
            # then write to file!
            self.create_obj_file(label_name, vertex_map, index_tuples)

    # for some reason the indices are duplicated,
    # I think it's because a point slightly shifted will still be in the same face as another
    # FIXME so the fix is to fix PixelToFace but we can cheat here
    def format_indices(self, indexed_vertex_list):
        cleaned_indexed_vertex_list = list(filter(lambda v: v is not None, indexed_vertex_list))
        print("test", cleaned_indexed_vertex_list[-1])
        # do we need an ordered dict? no but it's nice for readability later in the .obj file
        index_map = OrderedDict()
        for i in range(0, len(cleaned_indexed_vertex_list), 3):
            v_index_1 = cleaned_indexed_vertex_list[i]
            v_index_2 = cleaned_indexed_vertex_list[i + 1]
            v_index_3 = cleaned_indexed_vertex_list[i + 2]
            v_idx_tuple = (v_index_1, v_index_2, v_index_3)
            if v_idx_tuple not in index_map:
                index_map[v_idx_tuple] = True
        # so now we only have UNIQUE faces in the form of keys in the form of tuples in the dict
        return index_map.keys()


    def create_obj_file(self, label_name, vertex_map, index_tuple_list):
        # https://en.wikipedia.org/wiki/Wavefront_.obj_file
        label_name_stripped = str(label_name).replace(" ", "")
        with open(f'outputs/OBJ files/{label_name}.obj', 'w') as file:
            print(f"Writing {label_name}.obj file!")
            file.write("#Custom Object for fun-times-saga2\n")
            # .obj files don't allow spaces for names!
            file.write(f'#Name: {label_name}\n')
            # object
            file.write(f'o {label_name_stripped}\n')
            # then group name
            file.write(f'g {label_name_stripped}\n')
            # first write the vertices that are UNIQUE!
            for vertex, value in vertex_map.items():
                file.write(f'v {vertex[0]} {vertex[1]} {vertex[2]}\n')
            # then we write the faces where it takes 3 to make on face!
            # so we iterate by 3 here starting at 0
            for index_tuple in index_tuple_list:
                file.write(f'f {index_tuple[0]} {index_tuple[1]} {index_tuple[2]}\n')
            print(f"Finished writing {label_name}.obj file!")


if __name__ == "__main__":
    start = time.time()
    label_names = []
    indexer = PixelIndexer(label_names)
    end = time.time()
    print()
    print(f"Finished reading in faces...Took {end - start} seconds")
    # start = time.time()
    # this creates and writes to file
    indexer.create_indexed_faces()
    end = time.time()
    print(end - start)
    print(f"Full task took {(end - start) / 60} minutes")


