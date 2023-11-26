from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QDockWidget
from abc import ABC, abstractmethod


class CustomDockWidget(QDockWidget):
    def __init__(self, title: str = None, parent=None):
        super().__init__(parent)
        # TODO remove this? or make it so you can scale it?
        self.setMinimumSize(400, 300)
        # self.setFeatures(QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
        self.setWindowTitle(title)
        self.setStyleSheet("QDockWidget { font-family: 'Roboto Lt'; font-size: 12pt; }")

        self.scrollArea = QScrollArea()
        # I Don't know if I even need this
        self.main_widget = QWidget()
        self.scrollArea.setWidget(self.main_widget)
        # set the scroll area so it vertically allows for scrolling
        self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.vertical_layout = QVBoxLayout()
        self.main_widget.setLayout(self.vertical_layout)
        self.vertical_layout.setSpacing(0)
        # self.vertical_layout.insertWidget(0, PixelStartingPointItem())

        self.vertical_layout.addStretch()
        self.setWidget(self.scrollArea)
        self.show()

    @abstractmethod
    def add_item_to_vertical_layout(self, item):
        """
        Add a widget to the vertical layout, it is added to the end
        :param item:
        :return:
        """
        pass
