from PyQt6.QtWidgets import QComboBox, QLineEdit
from PyQt6.QtCore import QPoint, pyqtSignal, Qt

# I do this ugliness because pycharm intellisense is just not working :( and i want intellisense
try:
    from SubComponents import CustomDockWidget
except ImportError:
    from ..SubComponents import CustomDockWidget
from generated_design import Ui_LabelSelector


class LabelSelectorView(CustomDockWidget, Ui_LabelSelector):
    # emit for when enter is pressed
    new_label_added = pyqtSignal(str)
    drop_down_item_selected = pyqtSignal(str)
    edited_label = pyqtSignal(str)
    edited_abr = pyqtSignal(str)

    # if we inherit CustomDockWidget and then do self.setupUI(self.scrollArea) I think we get what we want
    def __init__(self) -> None:
        super().__init__(title="Label Selection")
        self.setMinimumSize(400, 125)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setupUi(self.scrollArea)

        # naughty naught override, but oh well can't get it to work otherwise
        self.dropdown.keyPressEvent = self.drop_down_key_press_event
        self.name_input.keyPressEvent = self.name_input_key_event
        self.abr_input.keyPressEvent = self.abr_input_key_event

        # self.dropdown.addItem("Your Label")
        # self.name_input.setText("Your Label")
        self.dropdown.currentIndexChanged.connect(
            lambda index: self.drop_down_item_selected.emit(self.dropdown.itemText(index)))

    def add_item_to_vertical_layout(self, item):
        pass

    def handle_new_label_added(self, text):
        # Add the new item to the combo box and select it
        self.dropdown.addItem(text)
        index = self.dropdown.findText(text)
        self.dropdown.setCurrentIndex(index)
        self.dropdown.clearFocus()
        self.set_name_input(text)

    def change_current_label(self, text, abr):
        index = self.dropdown.findText(text)
        self.dropdown.setCurrentIndex(index)
        self.name_input.setText(text)
        self.blockSignals(True)
        self.abr_input.setText(abr)
        self.blockSignals(False)

    def edit_label(self, text):
        self.update_dropdown_item_text(text)

    def edit_abr(self, text):
        self.blockSignals(True)
        self.abr_input.setText(text)
        self.blockSignals(False)

    def reset_current_label(self):
        text = self.selector.dropdown.currentText()
        # block signal first
        self.set_name_input(text)

    def drop_down_key_press_event(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.on_dropdown_return_pressed()
            return
        else:
            QComboBox.keyPressEvent(self.dropdown, event)

    def on_dropdown_return_pressed(self):
        text = self.dropdown.currentText()
        if text and text not in [self.dropdown.itemText(i) for i in range(self.dropdown.count())]:
            self.new_label_added.emit(text)

    def name_input_key_event(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.on_name_input_return_pressed()
            return
        else:
            QLineEdit.keyPressEvent(self.name_input, event)

    def on_name_input_return_pressed(self):
        text = self.name_input.text()
        self.name_input.clearFocus()
        self.edited_label.emit(text)

    def abr_input_key_event(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.on_abr_input_return_pressed()
            return
        else:
            QLineEdit.keyPressEvent(self.abr_input, event)
            return

    def on_abr_input_return_pressed(self):
        text = self.abr_input.text()
        self.abr_input.clearFocus()
        self.edited_abr.emit(text)
        return

    def set_name_input(self, text):
        print("reseting text", text)
        self.blockSignals(True)
        self.name_input.setText(text)
        self.blockSignals(False)

    def update_dropdown_item_text(self, text):
        index = self.dropdown.currentIndex()
        print("dropdown index", index)
        self.blockSignals(True)
        print("dropdown set item text", text)
        self.dropdown.setItemText(index, text)
        self.blockSignals(False)
        self.set_name_input(text)
