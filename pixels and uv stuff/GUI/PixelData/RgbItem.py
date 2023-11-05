from PyQt5.QtWidgets import QWidget, QColorDialog

from generated_design import Ui_RgbItem
from PyQt5.QtCore import QPoint, pyqtSignal


class RgbItem(QWidget, Ui_RgbItem):
    color_chosen = pyqtSignal(list)

    def __init__(self, index, rgb: tuple = None) -> None:
        super().__init__()
        self.setupUi(self)
        self.index = index
        # color class field with r g b properties
        self.color = None
        if not rgb:
            self.set_rgb_value(0, 0, 0)
        else:
            self.set_rgb_value(rgb[0], rgb[1], rgb[2])

        self.preview_color_btn.clicked.connect(self.handle_color_chosen)

    def set_rgb_value(self, r, g, b):
        self.color = [r, g, b]
        # update button color
        self.preview_color_btn.setStyleSheet(f"background-color: rgb({r}, {g}, {b})")

    def handle_color_chosen(self):
        # open color dialog
        r, g, b, a = QColorDialog.getColor().getRgb()
        self.set_rgb_value(r, g, b)
        self.color_chosen.emit(self.color)
        print(self.color)
        return self.color
