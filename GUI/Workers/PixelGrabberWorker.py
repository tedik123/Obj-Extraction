import time
from array import array

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QByteArray, QPoint

from MainScripts.PixelGrabber import PixelGrabber

from functools import partial
import shapely
from MainScripts.UtilityFunctions import uvs_to_pixels

from PyQt6.QtGui import QColor

from .PixelIndexerWorker import PixelIndexerWorker
from .PixelToFaceWorker import PixelToFaceWorker


# this class is a wrapper around pixel grabber to sync with pyqt5
# it should provide async behavior to help with loading and stuff
# this is really just another controller but on a seperate thread

class PixelGrabberWorker(QObject):
    finished = pyqtSignal()
    finished_loading_image = pyqtSignal(int, int)
    draw_pixel_chunks = pyqtSignal(list, bool)
    # these are both for when something on the 3d model is chosen
    # mark_point marks it and is mostly for testing, point_on_model_chosen is for the actual product
    mark_point = pyqtSignal(QPoint)
    point_on_model_chosen = pyqtSignal(QPoint, QColor)
    obj_file_chosen = pyqtSignal(str, str)

    new_obj_files_created = pyqtSignal(list)
    def __init__(self, pixel_model):
        super().__init__()
        self.pixel_model = pixel_model
        # defaults
        self.obj_attributes = None
        self.geometry_buffer = None
        self.geometry_float_values = None
        self.image_width, self.image_height = 0, 0
        # pixel grabber work
        self.grabber = PixelGrabber(read_in_label_starts=False)

        # build pixel indexer first since it's independent of everything else
        self.pixel_indexer = PixelIndexerWorker()
        self.pixel_indexer_thread = QThread()
        self.pixel_indexer.moveToThread(self.pixel_indexer_thread)
        # add connections here
        self.pixel_indexer_thread.start()

        # face worker established
        self.face_finder = PixelToFaceWorker()
        self.face_finder_thread = QThread()
        self.face_finder.moveToThread(self.face_finder_thread)
        self.face_finder_connections()
        self.face_finder_thread.start()

        # need to pass in self or it will kill itself immediately(!)
        self.load_image_thread: QThread | None = QThread(self)
        self.grab_pixels_thread: QThread | None = QThread(self)

    def face_finder_connections(self):
        # parent to child connections
        self.obj_file_chosen.connect(self.face_finder.set_obj_file)
        # child to parent connections
        self.face_finder.finished_building_tree.connect(lambda: print("FINISHED LOADING STR TREE!"))
        self.pixel_indexer.indexed_faces_finished.connect(self.new_obj_files_created.emit)

        # other connections
        self.face_finder.finished_finding_faces.connect(self.pixel_indexer.set_faces_found_by_labels)
        self.finished_loading_image.connect(self.face_finder.set_max_width_and_height)
        self.pixel_model.new_pixels_added.connect(self.face_finder.search_for_new_pixels)

        if self.image_height and self.image_width:
            print("trying to pre-set image hiehgt and width", self.image_height, self.image_width)
            self.face_finder.set_max_width_and_height(self.image_width, self.image_height)

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
        self.image_width, self.image_height = self.grabber.read_in_image_data()
        print("read in width and height", self.image_height, self.image_width)

        self.finished_loading_image.emit(self.image_width, self.image_height)

        # need to explicitly kill it
        # self.load_image_thread.quit()

    def set_obj_file(self, file_name, hash_str):
        print('set obj file')
        self.grabber.set_output_directory(hash_str)
        self.pixel_indexer.set_output_directory(hash_str)
        # emit the signal for self.face_finder instead of calling the function directly or else bad :( and sad
        self.obj_file_chosen.emit(file_name, hash_str)

    def grab_pixels(self, label, label_data):
        # this is incredibly shitty! but i don't know how to fix it yet
        try:
            if self.grab_pixels_thread and self.grab_pixels_thread.isRunning():
                # If the thread is already running, stop it before starting a new one
                # if you don't disconnect it no happy :(
                try:
                    self.grab_pixels_thread.requestInterruption()
                    self.grab_pixels_thread.wait(1)
                    self.grab_pixels_thread.disconnect()
                    self.grab_pixels_thread.quit()
                except Exception as e:
                    print(f"Error disconnecting thread, moving on: {str(e)}")
                finally:
                    self.grab_pixels_thread = QThread(self)
            # self.grab_pixels_thread.quit()

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
            total_length = len(pixels)
            is_final_chunk = False
            for index, chunk in enumerate(pixels):
                if total_length - index == 1:
                    is_final_chunk = True
                self.draw_pixel_chunks.emit(chunk, is_final_chunk)
                time.sleep(pause_time)
                total_pixels += len(chunk)
        if len(pixels_by_label[label]) != total_pixels:
            raise ValueError(
                f"Pixels by labels {len(pixels_by_label[label])} does not match total pixels {total_pixels}")
        self.pixel_model.set_pixel_data_by_label(pixels_by_label)

    def save_attributes(self, attributes):
        print('saving attributes')
        self.obj_attributes = attributes
        data: QByteArray = self.obj_attributes[0].buffer().data()
        self.geometry_float_values = array('f')
        self.geometry_float_values.frombytes(data)

    def handle_triangle_selected(self, triangle_data: dict):
        print("woah, i got a triangle!", triangle_data)
        points_per_triangle = 3
        # warning keep in mind we have e.index that can help us find the face in our own custom data

        # https://stackoverflow.com/questions/46667975/qt3d-reading-raw-vertex-data-from-qgeometry?rq=3
        for attribute in self.obj_attributes:
            print(attribute.name())
            if attribute.name() == "vertexTexCoord":
                print(attribute.vertexBaseType())
                uv_list = []
                print("first value", self.geometry_float_values[0])
                for vertex in ["v1", "v2", "v3"]:
                    # bytestride is // 4 because bytestride is variable depending on the obj file
                    # but 4 is the size of bytes which is fixed
                    # why bytestride https://stackoverflow.com/questions/64546908/properties-of-the-stride-in-a-gltf-file
                    # but basically since we converted this to an array of floats we need to multiply by the stride / memory
                    # to get where the next vertex data starts
                    vertexOffset = triangle_data[vertex] * (attribute.byteStride() // 4)
                    # i think you need to divide the byteoffset by 4 here too for the same reason as above
                    offset = vertexOffset + (attribute.byteOffset() // 4)
                    # 2 because it's UV and this offers us a UVW which i don't think we care about at all
                    print("sample", self.geometry_float_values[offset:offset + 2])
                    # copy self.geometry_float_values to uv_list
                    uv_list.append(self.geometry_float_values[offset:offset + 2])
                # create triangle and we'll use the centroid to guess what they chose
                triangle = shapely.Polygon(uv_list)
                centroid = triangle.centroid
                x, y = uvs_to_pixels(centroid.x, centroid.y, max_width=self.image_width, max_height=self.image_height)
                point = QPoint(x, y)
                self.mark_point.emit(point)
                # then let's add the point to list and rgb_to_list
                # first let's get the rgb, fortunately pixel_grabber stores that for us in pixel_data
                # important notice the lookup is backwards! y,x instead of x,y
                r, g, b = self.grabber.pixel_data[y][x]
                color = QColor(r, g, b)
                self.point_on_model_chosen.emit(point, color)
