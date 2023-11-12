from PixelData.PixelDataController import PixelDataController
from Base.LabelSelectorController import LabelSelectorController
from PixelData.PixelDataModel import PixelDataModel

class MainController:
    """This is used to handle communication between all the different controllers"""

    def __init__(self, pixel_data_controller: PixelDataController, label_selector_controller: LabelSelectorController,
                 pixel_data_model: PixelDataModel):
        self._pixel_data_controller = pixel_data_controller
        self._label_selector_controller = label_selector_controller
        self._pixel_data_model = pixel_data_model
        # syncs the current label with all other components
        self.current_label = "Your Label"
        self._pixel_data_controller.add_new_label(self.current_label, True)
        self._label_selector_controller.add_new_label(self.current_label, True)


    def change_current_label(self, name):
        self._pixel_data_controller.change_current_label(name)
        self._label_selector_controller.change_current_label(name)
        self.current_label = name

    def edit_label(self, new_label_name):
        # you can assume that the current label selected is the one you should edit
        # first try to change the model if it errors then don't allow the change
        try:
            self._pixel_data_model.edit_label(self.current_label, new_label_name)
            self._pixel_data_controller.edit_label(new_label_name)
            self._label_selector_controller.edit_label(new_label_name)
            self.current_label = new_label_name
            print("updated label", self.current_label)
        except ValueError:
            print("nope key already exists")
            # reset
            self._label_selector_controller.reset_current_label()
