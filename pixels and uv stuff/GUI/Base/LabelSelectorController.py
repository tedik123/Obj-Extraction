from PixelData.PixelDataModel import PixelDataModel
from .LabelSelectorView import LabelSelectorView


class LabelSelectorController:
    def __init__(self, model: PixelDataModel, label_selector_view: LabelSelectorView) -> None:
        self.model: PixelDataModel = model
        self.label_selector_view: LabelSelectorView = label_selector_view
        self.main_controller = None

        self.label_selector_view.new_label_added.connect(self.add_new_label)

    def set_main_controller(self, main_controller):
        self.main_controller = main_controller
        self.create_main_connections()

    def create_main_connections(self):
        self.label_selector_view.drop_down_item_selected.connect(self.main_controller.change_current_label)
        self.label_selector_view.edited_label.connect(self.main_controller.edit_label)

    def add_new_label(self, label_name: str):
        try:
            self.model.add_new_label(label_name)
            self.label_selector_view.handle_new_label_added(label_name)
        except ValueError:
            print("Label already exists ignoring")

    def change_current_label(self, label_name: str):
        self.label_selector_view.change_current_label(label_name)

    def edit_label(self, label_name):
        self.label_selector_view.edit_label(label_name)

    def reset_current_label(self):
        self.label_selector_view.reset_current_label()


