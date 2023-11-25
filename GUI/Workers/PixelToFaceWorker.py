from PyQt6.QtCore import QObject

from MainScripts.PixelToFace import PixelToFace
from MainScripts.ObjToGeometryFiles import ObjToGeometryFiles

from PyQt6.QtCore import pyqtSignal

from PyQt5.QtCore import QThread


class PixelToFaceWorker(QObject):
    # this is used to load and create them, once it's done we should redirect to create the actual pixeltoface
    finished_loading_geometry_files = pyqtSignal()
    finished_building_tree = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pixel_to_face = None
        self.obj_to_geometry_files = None
        self.max_width, self.max_height = None, None

    def set_obj_file(self, obj_file_path):
        file_path_prefix = "../"
        self.obj_to_geometry_files = ObjToGeometryFiles(obj_file_path, file_path_prefix=file_path_prefix)
        self.obj_to_geometry_files.read_in_OBJ_file()
        self.obj_to_geometry_files.insert_face_data()
        self.obj_to_geometry_files.create_geometry_files()
        # cause we're in GUI we want to go UP one directory
        self.create_pixel_to_face(file_path_prefix)

    def create_pixel_to_face(self, file_path_prefix):
        print("creating pixel to face!")
        self.pixel_to_face = PixelToFace(disable_target_pixels_load=True, file_path_prefix=file_path_prefix)
        # we know geometry stuff is loaded in here by this point
        self.pixel_to_face.pass_in_geometry_data(self.obj_to_geometry_files.face_data,
                                                 self.obj_to_geometry_files.normals_data,
                                                 self.obj_to_geometry_files.uvs_data)
        self.pixel_to_face.build_str_tree()
