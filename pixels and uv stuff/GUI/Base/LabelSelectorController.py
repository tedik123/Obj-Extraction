from PixelData.PixelDataModel import PixelDataModel
from .LabelSelectorView import LabelSelectorView


class LabelSelectorController:
    def __init__(self, model: PixelDataModel, label_selector_view: LabelSelectorView) -> None:
        self.model: PixelDataModel = model
        self.label_selector_view: LabelSelectorView = label_selector_view
        self.current_label = None
        self.main_controller = None

        self.label_selector_view.new_label_added.connect(self.add_new_label)
        self.label_selector_view.edited_abr.connect(self.edit_abr)

    def set_main_controller(self, main_controller):
        self.main_controller = main_controller
        self.create_main_connections()

    def create_main_connections(self):
        self.label_selector_view.drop_down_item_selected.connect(self.main_controller.change_current_label)
        self.label_selector_view.edited_label.connect(self.main_controller.edit_label)

    """Adds a new label,
     if is_initial is true will ignore adding to model (flag should only be used for initialization)"""
    def add_new_label(self, label_name: str, is_initial=False):
        if is_initial:
            self.label_selector_view.handle_new_label_added(label_name)
            self.current_label = label_name
            return
        try:
            self.model.add_new_label(label_name)
            self.label_selector_view.handle_new_label_added(label_name)
        except ValueError:
            print("Label already exists ignoring")

    def change_current_label(self, label_name: str, abr:str):
        self.current_label = label_name
        self.label_selector_view.change_current_label(label_name, abr)

    def edit_label(self, label_name):
        self.label_selector_view.edit_label(label_name)

    def reset_current_label(self):
        self.label_selector_view.reset_current_label()

    def edit_abr(self, abr):
        self.model.edit_abr(self.current_label, abr)
        self.label_selector_view.edit_abr(abr)



