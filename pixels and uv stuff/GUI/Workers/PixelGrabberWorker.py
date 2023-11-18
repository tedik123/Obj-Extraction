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

    def __init__(self):
        super().__init__()
        self.grabber = PixelGrabber(read_in_label_starts=False)
        # need to pass in self or it will kill itself immediately(!)
        self.load_image_thread: QThread | None = QThread(self)

    def load_image(self, file_name):
        # maybe i don't need a dangling thread if load image is only called sometimes
        try:
            print("trying again")
            if self.load_image_thread and self.load_image_thread.isRunning():
                # If the thread is already running, stop it before starting a new one
                self.load_image_thread.requestInterruption()
                print("pre-wait")
                self.load_image_thread.wait(200)
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

