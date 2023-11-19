import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from MainScripts.PixelGrabber import PixelGrabber

from functools import partial


# this class is a wrapper around pixel grabber to sync with pyqt5
# it should provide async behavior to help with loading and stuff
# this is really just another controller but on a seperate thread

class PixelGrabberWorker(QObject):
    finished = pyqtSignal()
    finished_loading_image = pyqtSignal()
    draw_pixel_chunks = pyqtSignal(list)

    def __init__(self, pixel_model):
        super().__init__()
        self.grabber = PixelGrabber(read_in_label_starts=False)
        self.pixel_model = pixel_model
        # need to pass in self or it will kill itself immediately(!)
        self.load_image_thread: QThread | None = QThread(self)
        self.grab_pixels_thread: QThread | None = QThread(self)

    def load_image(self, file_name):
        # maybe i don't need a dangling thread if load image is only called sometimes
        try:
            print("trying again")
            if self.load_image_thread and self.load_image_thread.isRunning():
                # If the thread is already running, stop it before starting a new one
                # self.load_image_thread.requestInterruption()
                print("pre-wait")
                # if you don't disconnect it no happy :(
                self.load_image_thread.disconnect()
                self.load_image_thread.quit()

                print('post wait')
            # Create a worker thread
            # i need to destroy previous slots

            self.load_image_thread.started.connect(partial(self._load_image, file_name))
            # self.load_image_thread.finished.connect(self.finished.emit)

            # Start the thread
            self.load_image_thread.start()
        except Exception as e:
            print(f"Error in loading image: {str(e)}")
        # no need for cleanup because pyqt handles it for you?

    def _load_image(self, file_name):
        # time.sleep(1)
        print("wakey-wakey eggs and bakey")
        # Run the time-consuming operation in this method
        self.grabber.set_texture_file_path(file_name)
        self.grabber.read_in_image_data()
        self.finished_loading_image.emit()
        # need to explicitly kill it
        # self.load_image_thread.quit()

    def grab_pixels(self, label, label_data):
        try:
            if self.grab_pixels_thread and self.grab_pixels_thread.isRunning():
                # force kill the old thread

                # If the thread is already running, stop it before starting a new one
                # if you don't disconnect it no happy :(
                try:
                    self.grab_pixels_thread.requestInterruption()
                    self.grab_pixels_thread.disconnect()
                except Exception as e:
                    print(f"Error disconnecting thread, moving on: {str(e)}")
                self.grab_pixels_thread.quit()

            self.grab_pixels_thread.started.connect(partial(self._grab_pixels, label, label_data))
            # Start the thread
            self.grab_pixels_thread.start()
        except Exception as e:
            print(f"Error in grabbing pixels from image: {str(e)}")
        # no need for cleanup because pyqt handles it for you?

    def _grab_pixels(self, label, label_data, chunk_size=None):
        # self.grabber.label_data = {label: label_data}
        # creates the range of acceptable colors by label, in this case just white basically
        # set white as the default acceptable colors
        formatted_data = {label: label_data}

        pixels_by_label = self.grabber.run_pixel_grabber(label_data=formatted_data, thread_count=1)

        pause_time = .05
        if not chunk_size:
            # set chunk size so it always takes 1 second
            chunk_size = int(len(pixels_by_label[label]) // (1 / pause_time)) + 1
            print(f"chunk size: {chunk_size}")
        total_pixels = 0
        for label, pixels in pixels_by_label.items():
            pixels = [pixels[i:i + chunk_size] for i in range(0, len(pixels), chunk_size)]
            for chunk in pixels:
                self.draw_pixel_chunks.emit(chunk)
                time.sleep(pause_time)
                total_pixels += len(chunk)
        if len(pixels_by_label[label]) != total_pixels:
            raise ValueError(
                f"Pixels by labels {len(pixels_by_label[label])} does not match total pixels {total_pixels}")
        self.pixel_model.set_pixel_data_by_label(pixels_by_label)
