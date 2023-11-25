import json
import pickle
import time
from collections import OrderedDict

import os


class PixelIndexer:

    def __init__(self, label_names=None,
                 faces_found_by_label=None,
                 save_normals=False,
                 save_uvs=False,
                 read_in_faces_found_file=True
                 ):
        self.output_path = 'outputs/'
        self.faces_found_file_path = 'outputs/faces_found_by_labels'
        self.faces_found_by_labels = None
        if faces_found_by_label is None and read_in_faces_found_file:
            self.read_in_faces_found_by_labels(True)
        else:
            self.faces_found_by_labels = faces_found_by_label
        self.label_names = label_names
        self.save_normals = save_normals
        self.save_uvs = save_uvs

    def set_label_names(self, label_names: list):
        self.label_names = label_names

    def set_faces_found_by_labels(self, faces_found_by_labels: dict):
        self.faces_found_by_labels = faces_found_by_labels


    def set_output_path(self, directory):
        self.output_path = '../outputs/' + directory + "/"
        self.faces_found_file_path = self.output_path + "faces_found_by_labels"

    def read_in_faces_found_by_labels(self, read_binary=False):
        print("Reading in faces by labels")
        if not read_binary:
            print(f"Opening {self.faces_found_file_path}")
            with open(self.faces_found_file_path + ".json", 'r') as file:
                data = file.read()
                self.faces_found_by_labels = json.loads(data)
        else:
            print("Reading binary version")
            print(f"Opening outputs/faces_found_by_labels" + ".bin")
            with open('../pixels and uv stuff/outputs/faces_found_by_labels.bin', 'rb') as file:
                self.faces_found_by_labels = pickle.load(file)

    def create_indexed_faces(self):
        print("Starting indexing of faces!")
        if self.label_names:
            labels_to_do = {}
            for label in self.label_names:
                temp = self.faces_found_by_labels[label]
                labels_to_do[label] = temp
            # overwrite it to only the labels we care about
            self.faces_found_by_labels = labels_to_do
        # this will have to change later, so we can handle normals, faces, and uvs?
        for label_name, values in self.faces_found_by_labels.items():
            vertices = values["vertices"]
            indexed_vertex_list, vertex_map = self.create_indexed_list(vertices)
            if len(indexed_vertex_list) % 3 != 0:
                raise Exception("Something went wrong the list must be divisible by 3!")

            # so now we have our label with an indexed list of values
            # we'll use the keys to create the UNIQUE vertices
            # and then the indexed_vertex_list will help us create the faces
            # remove nones from list and cleans up duplicates and returns a list of tuples of size 3
            vertex_index_tuples = self.format_indices(indexed_vertex_list)
            print(len(vertices))
            # default none
            normal_map, normal_index_tuples, uvs_index_tuples, uvs_map = None, None, None, None
            if self.save_normals and len(values["normals"]) > 0:
                normals = values["normals"]
                indexed_normals_list, normal_map = self.create_indexed_list(normals)
                normal_index_tuples = self.format_indices(indexed_normals_list)
            if self.save_uvs and len(values["uvs"]) > 0:
                uvs = values["uvs"]
                indexed_uvs_list, uvs_map = self.create_indexed_list(uvs)
                uvs_index_tuples = self.format_indices(indexed_uvs_list)
            # then write to file!
            self.create_obj_file(label_name, vertex_map, vertex_index_tuples,
                                 normal_map, normal_index_tuples,
                                 uvs_index_tuples, uvs_map)

    # FIXME this is the bottleneck to this code!
    def create_indexed_list(self, geometry_list):
        # we need to preserve the order the keys & indices were inserted
        geometry_map = OrderedDict()
        # WE MUST start at 1 because that's how .obj files are interpreted
        geometry_index = 1
        # this can be no longer than the amount of vertices
        indexed_geometry_list = [None] * len(geometry_list)
        for i, geometry in enumerate(geometry_list):
            t_geometry = tuple(geometry)
            # if it already exists we just need to grab the original geometry index
            if t_geometry in geometry_map:
                index_of_original_geometry = geometry_map[t_geometry]
                indexed_geometry_list[i] = index_of_original_geometry
            # if it doesn't exist we need to create it and update the index
            else:
                geometry_map[t_geometry] = geometry_index
                indexed_geometry_list[i] = geometry_index
                geometry_index += 1
        return indexed_geometry_list, geometry_map

    # for some reason the indices are duplicated,
    # I think it's because a point slightly shifted will still be in the same face as another
    # FIXME so the fix is to fix PixelToFace but we can cheat here
    def format_indices(self, indexed_geometry_list):
        cleaned_indexed_geometry_list = list(filter(lambda v: v is not None, indexed_geometry_list))
        print("test", cleaned_indexed_geometry_list[-1])
        # do we need an ordered dict? no but it's nice for readability later in the .obj file
        index_map = OrderedDict()
        for i in range(0, len(cleaned_indexed_geometry_list), 3):
            g_index_1 = cleaned_indexed_geometry_list[i]
            g_index_2 = cleaned_indexed_geometry_list[i + 1]
            g_index_3 = cleaned_indexed_geometry_list[i + 2]
            g_idx_tuple = (g_index_1, g_index_2, g_index_3)
            if g_idx_tuple not in index_map:
                index_map[g_idx_tuple] = True
        # so now we only have UNIQUE faces in the form of keys in the form of tuples in the dict
        return index_map.keys()

    def create_obj_file(self, label_name, vertex_map, vertex_index_tuples, normal_map, normal_index_tuples,
                        uvs_index_tuples, uvs_map):
        # https://en.wikipedia.org/wiki/Wavefront_.obj_file
        label_name_stripped = str(label_name).replace(" ", "")
        # check if directory exists, if not create it
        if not os.path.exists(f'{self.output_path}OBJ files/'):
            os.makedirs(f'{self.output_path}OBJ files/')

        with open(f'{self.output_path}OBJ files/{label_name}.obj', 'w') as file:
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
            # just check one of the normal objects to see if we have anything to work with
            if self.save_normals and normal_map:
                for normal, value in normal_map.items():
                    file.write(f'vn {normal[0]} {normal[1]} {normal[2]}\n')
            if self.save_uvs:
                for uvs, value in uvs_map.items():
                    file.write(f'vt {uvs[0]} {uvs[1]}\n')

            # then we write the faces where it takes 3 to make on face!
            # so we iterate by 3 here starting at 0
            # save everything
            # TODO simplify this plz
            # check if normal_index_tuple exists in case they're asking to save normals but normals don't exist
            # in the base file
            if self.save_uvs and self.save_normals and normal_index_tuples:
                for vertex_tuple, normal_tuple, uvs_tuple in zip(vertex_index_tuples, normal_index_tuples,
                                                                 uvs_index_tuples):
                    file.write(f'f {vertex_tuple[0]}/{uvs_tuple[0]}/{normal_tuple[0]} '
                               f'{vertex_tuple[1]}/{uvs_tuple[1]}/{normal_tuple[1]} '
                               f'{vertex_tuple[2]}/{uvs_tuple[2]}/{normal_tuple[2]}\n')
            elif not self.save_uvs and self.save_normals and normal_index_tuples:
                for vertex_tuple, normal_tuple in zip(vertex_index_tuples, normal_index_tuples):
                    file.write(f'f {vertex_tuple[0]}//{normal_tuple[0]} '
                               f'{vertex_tuple[1]}//{normal_tuple[1]} '
                               f'{vertex_tuple[2]}//{normal_tuple[2]}\n')
            elif self.save_uvs and not self.save_normals and uvs_index_tuples:
                for vertex_tuple, uvs_tuple in zip(vertex_index_tuples, uvs_index_tuples):
                    file.write(f'f {vertex_tuple[0]}/{uvs_tuple[0]} '
                               f'{vertex_tuple[1]}/{uvs_tuple[1]} '
                               f'{vertex_tuple[2]}/{uvs_tuple[2]}\n')
            else:
                for vertex_tuple in vertex_index_tuples:
                    file.write(f'f {vertex_tuple[0]} {vertex_tuple[1]} {vertex_tuple[2]}\n')

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
