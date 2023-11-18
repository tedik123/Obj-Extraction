from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap

from ImageContainerView import ImageContainerView


class ImageContainerController:

    def __init__(self, image_container_view: ImageContainerView, pixel_data_controller=None):
        self.pixel_data_controller = pixel_data_controller
        # don't get confused this is actually just a QLabel!
        self.image_container_view = image_container_view

    def set_pixel_data_controller(self, pixel_data_controller):
        self.pixel_data_controller = pixel_data_controller
        self.image_container_view.mouseLeftClick.connect(self.pixel_data_controller.handle_mouse_image_left_click)
        self.image_container_view.mouseRightClick.connect(self.pixel_data_controller.handle_mouse_image_right_click)
        self.create_pixel_data_event_connections()

    def set_image(self, image):
        self.image_container_view.setPixmap(QPixmap.fromImage(image))
        self.image_container_view.setQImage()

    def create_pixel_data_event_connections(self):
        self.image_container_view.mouseLeftClick.connect(self.handle_mouse_image_left_click)

    def handle_mouse_image_left_click(self, point: QPoint):
        # tell pixel grabber to run after getting the label from pixel data controller
        label = self.pixel_data_controller.get_label()

