from PyQt5.QtWidgets import QAbstractSpinBox, QHBoxLayout, QGridLayout, QLabel, QSpinBox, QPushButton, QSpacerItem, \
    QSizePolicy, QWidget

from generated_design import Ui_StartingPointItem


class PixelStartingPointItem(QWidget, Ui_StartingPointItem):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
