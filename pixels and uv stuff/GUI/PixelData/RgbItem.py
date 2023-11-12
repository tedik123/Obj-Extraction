from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QColorDialog

from generated_design import Ui_RgbItem
from PyQt5.QtCore import QPoint, pyqtSignal


class RgbItem(QWidget, Ui_RgbItem):
    color_chosen = pyqtSignal(list, int)
    rgb_value_incremented = pyqtSignal(int, int, int)

    def __init__(self, index, rgb: tuple = None) -> None:
        super().__init__()
        self.setupUi(self)
        # this is the index it should be in the list
        self.index = index
        # color class field with r g b properties
        self.color = None
        if not rgb:
            self.set_rgb_value(0, 0, 0)
        else:
            self.set_rgb_value(rgb[0], rgb[1], rgb[2])

        self.preview_color_btn.clicked.connect(self.handle_color_chosen)
        self.connect_rgb_value_changed()

    def set_rgb_value(self, r, g, b):
        self.color = [r, g, b]
        # block signals so it doesn't trigger changes
        self.r_input_value.blockSignals(True)
        self.g_input_value.blockSignals(True)
        self.b_input_value.blockSignals(True)

        self.r_input_value.setValue(r)
        self.g_input_value.setValue(g)
        self.b_input_value.setValue(b)

        # unblock signals so they can continue emitting
        self.r_input_value.blockSignals(False)
        self.g_input_value.blockSignals(False)
        self.b_input_value.blockSignals(False)

        # update button color
        self.preview_color_btn.setStyleSheet(f"background-color: rgb({r}, {g}, {b})")

    def handle_color_chosen(self):
        color_dialog = QColorDialog(QColor(self.color[0], self.color[1], self.color[2]), parent=self)
        # open color dialog
        color = color_dialog.getColor()
        if color.isValid():
            r, g, b, a = color.getRgb()
            self.color_chosen.emit([r, g, b], self.index)

    def connect_rgb_value_changed(self):
        # IMPORTANT this is where you left off, connect these value changes back to the model
        # where 0,1,2 are indexes for r,g,b
        self.r_input_value.valueChanged.connect(lambda color: self.rgb_value_incremented.emit(color, 0, self.index))
        self.g_input_value.valueChanged.connect(lambda color: self.rgb_value_incremented.emit(color, 1, self.index))
        self.b_input_value.valueChanged.connect(lambda color: self.rgb_value_incremented.emit(color, 2, self.index))

    def set_single_color_value(self, color_value: int, color_index: int):
        self.color[color_index] = color_value
        r, g, b = self.color
        self.set_rgb_value(r, g, b)

    def test(self, value):
        print(value)
