from PyQt5.QtWidgets import QAbstractSpinBox, QHBoxLayout, QGridLayout, QLabel, QSpinBox, QPushButton, QSpacerItem, \
    QSizePolicy, QWidget


class PixelStartingPointItem(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(7)
        self.main_layout.addLayout(self.grid_layout)

        self.start_x_label = QLabel()
        self.start_x_label.setText("X:")

        self.grid_layout.addWidget(self.start_x_label, 0, 4, 1, 1)

        self.max_x_input = QSpinBox()
        self.max_x_input.setAutoFillBackground(False)
        self.max_x_input.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.max_x_input.setMaximum(255)
        self.grid_layout.addWidget(self.max_x_input, 2, 6, 1, 1)

        self.min_y_label = QLabel()

        self.grid_layout.addWidget(self.min_y_label, 2, 7, 1, 1)

        self.delete_button = QPushButton()
        self.delete_button.setText("Delete")

        self.grid_layout.addWidget(self.delete_button, 0, 11, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.grid_layout.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.min_y_input = QSpinBox()
        self.min_y_input.setAutoFillBackground(False)
        self.min_y_input.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.min_y_input.setMaximum(255)

        self.grid_layout.addWidget(self.min_y_input, 2, 8, 1, 1)

        self.max_y_label = QLabel()

        self.grid_layout.addWidget(self.max_y_label, 2, 9, 1, 1)

        self.min_x_label = QLabel()

        self.grid_layout.addWidget(self.min_x_label, 2, 1, 1, 1)

        self.max_x_label = QLabel()
        self.max_x_label.setText("Max_X")

        self.grid_layout.addWidget(self.max_x_label, 2, 4, 1, 1)

        self.start_y_input = QSpinBox()
        self.start_y_input.setAutoFillBackground(False)
        self.start_y_input.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.start_y_input.setMaximum(255)

        self.grid_layout.addWidget(self.start_y_input, 0, 8, 1, 1)

        self.min_x_input = QSpinBox()
        self.min_x_input.setProperty("showGroupSeparator", False)
        self.min_x_input.setMaximum(255)

        self.grid_layout.addWidget(self.min_x_input, 2, 3, 1, 1)

        self.max_y_input = QSpinBox()
        self.max_y_input.setAutoFillBackground(False)
        self.max_y_input.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.max_y_input.setMaximum(255)

        self.grid_layout.addWidget(self.max_y_input, 2, 10, 1, 1)

        self.start_y_label = QLabel()
        self.start_y_label.setText("Y:")

        self.grid_layout.addWidget(self.start_y_label, 0, 7, 1, 1)

        self.start_x_input = QSpinBox()
        self.start_x_input.setProperty("showGroupSeparator", False)
        self.start_x_input.setMaximum(255)

        self.grid_layout.addWidget(self.start_x_input, 0, 6, 1, 1)

