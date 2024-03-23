from PyQt6.QtCore import QObject

from MainScripts.PixelToFace import PixelToFace
from MainScripts.ObjToGeometryFiles import ObjToGeometryFiles

from PyQt6.QtCore import pyqtSignal

from PyQt5.QtCore import QThread


class PixelToFaceWorker(QObject):
    # this is used to load and create them, once it's done we should redirect to create the actual pixeltoface
    finished_building_tree = pyqtSignal()
    finished_finding_faces = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.str_tree_loaded = None
        self.pixel_to_face: PixelToFace | None = None
        self.obj_to_geometry_files = None
        self.max_width, self.max_height = None, None

    def set_obj_file(self, obj_file_path, hash_str):
        file_path_prefix = "../"
        directory = hash_str
        self.obj_to_geometry_files = ObjToGeometryFiles(obj_file_path, file_path_prefix=file_path_prefix,
                                                        directory=directory)
        self.obj_to_geometry_files.read_in_OBJ_file()
        self.obj_to_geometry_files.insert_face_data()
        self.obj_to_geometry_files.create_geometry_files()
        # cause we're in GUI we want to go UP one directory
        self.create_pixel_to_face(file_path_prefix, hash_str)

    def set_max_width_and_height(self, width, height):
        print("getting called to set", width, height)
        self.max_width, self.max_height = width, height
        if self.pixel_to_face:
            self.pixel_to_face.set_max_width_and_height(width, height)

    def create_pixel_to_face(self, file_path_prefix, directory):
        print("creating pixel to face!")
        # fixme for development this do be real nice
        preload_str_tree = False

        self.pixel_to_face = PixelToFace(save_uvs=True, preload_STRtree=preload_str_tree,
                                         disable_target_pixels_load=True,
                                         file_path_prefix=file_path_prefix, directory=directory)
        # we know geometry stuff is loaded in here by this point
        self.pixel_to_face.pass_in_geometry_data(self.obj_to_geometry_files.face_data,
                                                 self.obj_to_geometry_files.normals_data,
                                                 self.obj_to_geometry_files.uvs_data)
        print("pre-check max width", self.max_width, self.max_height)
        if self.max_width and self.max_height:
            self.pixel_to_face.set_max_width_and_height(self.max_width, self.max_height)

        if not preload_str_tree:
            self.pixel_to_face.build_str_tree()
        self.str_tree_loaded = True
        self.finished_building_tree.emit()

    def search_for_new_pixels(self, label, pixels):
        if not self.str_tree_loaded:
            print("no tree loaded")
            return
        if not (self.max_width and self.max_height):
            print("wtf are you doing kid")
            return
        self.pixel_to_face.pass_in_target_pixels({label: pixels})
        # 1 thread because we'll only be searching for one a time anyways

        faces_by_label = self.pixel_to_face.find_faces_of_targets(save_output=False, thread_count=5)
        print(len(faces_by_label))
        key, value = next(iter(faces_by_label.items()))
        print("key", key)
        # print("value", value)

        self.finished_finding_faces.emit(faces_by_label)

        # probs should emit a signal to the model and have it update
