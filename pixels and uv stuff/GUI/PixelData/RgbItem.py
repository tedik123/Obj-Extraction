from PyQt5.QtWidgets import QWidget

from generated_design import Ui_RgbItem
from PyQt5.QtCore import QPoint


class RgbItem(QWidget, Ui_RgbItem):
    def __init__(self, index) -> None:
        super().__init__()
        self.setupUi(self)
        self.index = index
        # color class field with r g b properties
        self.color = None
        self.set_rgb_value(0, 0, 0)

    def set_rgb_value(self, r, g, b):
        self.color = [r, g, b]
        # update button color
        self.preview_color_btn.setStyleSheet(f"background-color: rgb({r}, {g}, {b})")