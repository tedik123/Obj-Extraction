from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QSizePolicy


class PixelList(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        example_widget = QWidget()
        self.setWidget(example_widget)

        # set the scroll area so it vertically allows for scrolling
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        vertical_layout = QVBoxLayout()
        example_widget.setLayout(vertical_layout)
        example_label = QLabel()
        example_label.setText("Something random and long 1")
        # second example label widget
        example_label2 = QLabel()
        example_label2.setText("Something random and long 2")
        # create 10 more example_labels
        for i in range(100):
            example_label = QLabel()
            example_label.setText("Something random and long " + str(i))
            vertical_layout.insertWidget(0, example_label)
        # vertical_layout.insertWidget(0, example_label2)
        # vertical_layout.insertWidget(0, example_label)
        # this pushes everything to the top
        vertical_layout.addStretch()
        self.show()
