from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import QPoint

from generated_design import Ui_StartingPointItem


class PixelStartingPointItem(QWidget, Ui_StartingPointItem):
    def __init__(self, index, point: QPoint = None) -> None:
        super().__init__()
        self.setupUi(self)
        self.point = point
        self.index = index
        self.name_label.setText(f"Starting Point {index+1}")
        self.set_x_and_y_starts()

    def set_x_and_y_starts(self):
        if self.point:
            self.start_x_input.setValue(self.point.x())
            self.start_y_input.setValue(self.point.y())
