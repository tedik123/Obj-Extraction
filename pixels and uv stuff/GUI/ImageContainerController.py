from dataclasses import asdict

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPixmap

from ImageContainerView import ImageContainerView
from Workers.PixelGrabberWorker import PixelGrabberWorker
from ObjView.ObjView import ObjView
import json


class ImageContainerController:

    def __init__(self, image_container_view: ImageContainerView, pixel_data_controller=None, pixel_data_model=None):
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

    def set_image(self, image):
        self.image_container_view.setPixmap(QPixmap.fromImage(image))
        self.image_container_view.setQImage()

    def create_pixel_data_event_connections(self):
        # self.image_container_view.mouseLeftClick.connect(self.handle_mouse_image_left_click)
        pass

    def create_pixel_data_model_connections(self):
        self.pixel_data_model.point_updated.connect(self.handle_point_updated)

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

    # this is for when a label changes! we need to update the image view!
    def update_label_points(self, label):
        self.image_container_view.draw_points(self.pixel_data_model.get_pixel_data_by_label(label), clear_old=True)
