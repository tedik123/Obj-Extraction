from PyQt6.QtCore import QObject
from MainScripts.PixelIndexer import PixelIndexer


class PixelIndexerWorker(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixel_indexer = PixelIndexer(read_in_faces_found_file=False)

    def set_output_directory(self, directory):
        self.pixel_indexer.set_output_path(directory)

    def set_label_names(self, label_names: list):
        self.pixel_indexer.set_label_names(label_names)

    def set_faces_found_by_labels(self, faces_found_by_labels: dict):
        # i think we can assume the keys of the dict will be the label_names we care about sooo
        self.pixel_indexer.set_faces_found_by_labels(faces_found_by_labels)
        self.set_label_names(list(faces_found_by_labels.keys()))
        # then we can run the indexer?
        self.pixel_indexer.create_indexed_faces()
