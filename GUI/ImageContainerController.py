import time
from dataclasses import asdict

from PyQt6.QtCore import QPoint, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap

from ImageContainerView import ImageContainerView
from Workers.PixelGrabberWorker import PixelGrabberWorker
from ObjView.ObjView import ObjView
import json
import sys
import hashlib

class ImageContainerController(QObject):
    hide_main_model_signal = pyqtSignal()
    reset_camera_signal = pyqtSignal()
    def __init__(self, image_container_view: ImageContainerView, pixel_data_controller=None, pixel_data_model=None):
        super().__init__()
        self.obj_view: ObjView | None = None
        self.pixel_grabber_worker: PixelGrabberWorker | None = None
        self.pixel_data_controller = pixel_data_controller
        # don't get confused this is actually just a QLabel!
        self.image_container_view = image_container_view
        self.pixel_data_model = pixel_data_model
        self.create_pixel_data_model_connections()

    def set_pixel_data_controller(self, pixel_data_controller):
        self.pixel_data_controller = pixel_data_controller
        self.image_container_view.mouseLeftClick.connect(self.pixel_data_controller.add_selected_point)
        self.image_container_view.mouseRightClick.connect(self.pixel_data_controller.add_selected_color)
        self.create_pixel_data_event_connections()

    def set_obj_view(self, obj_view):
        self.obj_view: ObjView = obj_view
        self.obj_view.attribute_data_loaded.connect(self.pixel_grabber_worker.save_attributes)
        self.obj_view.triangle_selected.connect(self.pixel_grabber_worker.handle_triangle_selected)
        self.image_container_view.points_drawn.connect(self.obj_view.update_texture_with_image)
        # some helpful things
        self.hide_main_model_signal.connect(self.obj_view.hide_main_model)
        self.reset_camera_signal.connect(self.obj_view.reset_camera)
        # warning idk if this should be here; communicate to obj_view but maybe this should be to model first?
        self.pixel_grabber_worker.new_obj_files_created.connect(self.obj_view.handle_new_obj_files_created)

    def set_image(self, image, file_name):
        #FIXME this right here is why it's slow! it should be sending a signal not definitely controlling it here!!!
        self.image_container_view.setPixmap(QPixmap.fromImage(image))
        self.image_container_view.setQImage()
        self.pixel_grabber_worker.load_image(file_name)
        self.obj_view.set_texture_file(file_name)

    def set_obj_file(self, file_name):
        # we're gonna do some hashing rq, this will be used to see if we've seen this file before!
        BUF_SIZE = 65536  # let's read stuff in 64kb chunks!
        start = time.time()
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
        print("MD5: {0}".format(md5.hexdigest()))
        end = time.time()
        print("Hashing took: ", end - start)
        self.pixel_data_model.set_obj_file_hash(md5.hexdigest())
        #FIXME this right here is why it's slow! it should be sending a signal not definitely controlling it here!!!
        self.obj_view.set_obj_file(file_name)
        self.pixel_grabber_worker.set_obj_file(file_name, md5.hexdigest())

    def hide_main_model(self):
        self.hide_main_model_signal.emit()

    def reset_camera(self):
        self.reset_camera_signal.emit()

    def create_pixel_data_event_connections(self):
        # self.image_container_view.mouseLeftClick.connect(self.handle_mouse_image_left_click)
        pass

    def create_pixel_data_model_connections(self):
        self.pixel_data_model.point_updated.connect(self.handle_point_updated)

    # this runs the pixel grabber eagerly on click/point update!
    def handle_point_updated(self):
        print("image container point update")
        # tell pixel grabber to run after getting the label from pixel data controller
        label = self.pixel_data_controller.get_label()
        label_data = self.pixel_data_model.get_label_data(label)
        # convert label_data to json
        json_data = asdict(label_data)
        self.pixel_grabber_worker.grab_pixels(label, json_data)

    def set_pixel_grabber_work(self, pixel_grabber_worker: PixelGrabberWorker):
        self.pixel_grabber_worker = pixel_grabber_worker
        self.pixel_grabber_worker.draw_pixel_chunks.connect(self.image_container_view.draw_points)
        self.pixel_grabber_worker.mark_point.connect(self.image_container_view.draw_point)



        def add_point_and_color(point, color):
            # order matters here if we add point first it'll eagerly run the search without our new color
            self.pixel_data_controller.add_selected_color(color)
            self.pixel_data_controller.add_selected_point(point)

        self.pixel_grabber_worker.point_on_model_chosen.connect(add_point_and_color)
        # add another connection

    # this is for when a label changes! we need to update the image view!
    def update_label_points(self, label):
        # for efficiency purposes this should be a signal later but whatever
        self.image_container_view.draw_points(self.pixel_data_model.get_pixel_data_by_label(label), True,
                                              clear_old=True)
