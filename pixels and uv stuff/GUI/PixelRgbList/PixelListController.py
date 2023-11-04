from .PixelListModel import PixelListModel
from .PixelListView import PixelListView


class PixelListController:

    def __init__(self, model: PixelListModel, view: PixelListView):
        self.model = model
        self.view = view

    def handle_mouse_image_left_click(self, QPoint):
        self.model.add_starting_point(QPoint.x(), QPoint.y())
        self.view.add_starting_point(QPoint)