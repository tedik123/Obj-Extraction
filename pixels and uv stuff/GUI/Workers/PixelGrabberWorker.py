import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from MainScripts.PixelGrabber import PixelGrabber

from functools import partial


# this class is a wrapper around pixel grabber to sync with pyqt5
# it should provide async behavior to help with loading and stuff

class PixelGrabberWorker(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.grabber = PixelGrabber(read_in_label_starts=False)

    def load_image(self, file_name):
        try:
            # Create a worker thread
            # need to pass in self or it will kill itself immediately(!)
            self.thread = QThread(self)
            self.thread.started.connect(partial(self._load_image, file_name))
            self.thread.finished.connect(self.finished.emit)

            # Start the thread
            self.thread.start()
        except Exception as e:
            print(f"Error in loading image: {str(e)}")
        # no need for cleanup because pyqt handles it for you?

    def _load_image(self, file_name):
        time.sleep(5)
        # Run the time-consuming operation in this method
        self.grabber.set_texture_file_path(file_name)
        self.grabber.read_in_image_data()
        # need to explicitly kill it
        self.thread.quit()

