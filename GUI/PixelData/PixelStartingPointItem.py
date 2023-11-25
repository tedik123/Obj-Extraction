from PyQt6.QtWidgets import QWidget

from PyQt6.QtCore import QPoint, pyqtSignal

from generated_design import Ui_StartingPointItem


class PixelStartingPointItem(QWidget, Ui_StartingPointItem):
    # should i pass in the self index for the signals here idk....
    changed_point_value = pyqtSignal(str, int, int)
    changed_max_or_min = pyqtSignal(str, int, int)

    def __init__(self, index, point: QPoint = None) -> None:
        super().__init__()
        self.setupUi(self)
        self.point = point
        self.index = index
        self.name_label.setText(f"Starting Point {index + 1}")
        self.set_x_and_y_starts()
        self.set_events()

    def set_x_and_y_starts(self, point=None):
        if point:
            self.point = point
        if self.point:
            self.blockSignals(True)
            self.start_x_input.setValue(self.point.x())
            self.start_y_input.setValue(self.point.y())
            self.blockSignals(False)

    def set_max_or_min_value(self, minMaxXY, value):
        self.blockSignals(True)
        match minMaxXY:
            case "min_X":
                self.min_x_input.setValue(value)
            case "max_X":
                self.max_x_input.setValue(value)
            case "min_Y":
                self.min_y_input.setValue(value)
            case "max_Y":
                self.max_y_input.setValue(value)
            case _:
                print("NO can do with that max or min")
        self.blockSignals(False)

    def set_events(self):
        # starts
        self.start_x_input.valueChanged.connect(lambda x: self.changed_point_value.emit("x", x, self.index))
        self.start_y_input.valueChanged.connect(lambda x: self.changed_point_value.emit("y", x, self.index))
        # max and min ranges
        self.min_x_input.valueChanged.connect(lambda x: self.changed_max_or_min.emit("min_X", x, self.index))
        self.max_x_input.valueChanged.connect(lambda x: self.changed_max_or_min.emit("max_X", x, self.index))
        self.min_y_input.valueChanged.connect(lambda x: self.changed_max_or_min.emit("min_Y", x, self.index))
        self.max_y_input.valueChanged.connect(lambda x: self.changed_max_or_min.emit("max_Y", x, self.index))
