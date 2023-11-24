import copy
import pickle
import queue
import time
from array import array

from PyQt6.Qt3DCore import QEntity, QTransform, QGeometry, QBuffer, QAttribute
from PyQt6 import QtOpenGL
from PyQt6 import Qt3DInput
from PyQt6.Qt3DExtras import Qt3DWindow, QOrbitCameraController, \
    QTextureMaterial
from PyQt6.Qt3DInput import QMouseDevice, QMouseHandler
from PyQt6.Qt3DRender import QTextureLoader, QRayCaster, QScreenRayCaster, QPickingSettings, QPickEvent, \
    QPickTriangleEvent, QMesh
from PyQt6.QtGui import QVector3D, QColor
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6 import Qt3DRender
from PyQt6.QtCore import QUrl, QDir, QSize, Qt, QByteArray, pyqtSignal, QThread


def read_geometry_faces(filename):
    with open('../outputs/geometry_files/geometry_faces.bin', 'rb') as file:
        faces = pickle.load(file)["faces"]
        return faces


class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, geometry, float_values):
        super(WorkerThread, self).__init__()
        self.geometry = geometry
        self.float_values = float_values
        self.task_queue = queue.Queue()

    def run(self):
        while True:
            try:
                # Get the next task from the queue, block if the queue is empty
                e = self.task_queue.get()
                index = e["index"]
                print('\nstart:')
                print("index", index)
                v1 = e["v1"]
                v2 = e["v2"]
                v3 = e["v3"]
                print("Task found!", e)
                attributes = self.geometry.attributes()
                points_per_triangle = 3
                # https://stackoverflow.com/questions/46667975/qt3d-reading-raw-vertex-data-from-qgeometry?rq=3
                for attribute in attributes:
                    print(attribute.name())
                    if attribute.name() == "vertexTexCoord":
                        print(attribute.vertexBaseType())
                        # this is equal to 3
                        print("vertex size", attribute.vertexSize())
                        print("vertexPosition found!")
                        # why bytestride https://stackoverflow.com/questions/64546908/properties-of-the-stride-in-a-gltf-file
                        print("byte stride", attribute.byteStride())
                        print("byte offset", attribute.byteOffset())

                        # bytestride is // 4 because bytestride is variable depending on the obj file
                        # but 4 is the size of bytes which is fixed
                        # look at "the why bytestride" comment for more
                        # but basically since we converted this to an array of floats we need to multiply by the stride / memory
                        # to get where the next vertex data starts
                        vertexOffset = v1 * (attribute.byteStride() // 4)
                        # i think you need to divide the byteoffset by 4 here too for the same reason as above
                        offset = vertexOffset + (attribute.byteOffset() // 4)
                        print("sample", self.float_values[offset:offset + points_per_triangle])
                        # multiply the offset index value by 2 and set it
                        self.float_values[offset] = 0
                        self.float_values[offset + 1] = 0
                        self.float_values[offset + 2] = 0

                        # convert back to bytes and save it
                        bytes_array = self.float_values.tobytes()
                        self.geometry.attributes()[0].buffer().setData(bytes_array)
                print("Task completed")

            except Exception as e:
                print("Exception in worker thread:", str(e))

            # Notify that the task is completed
        self.finished.emit()

    def add_task(self, task):
        # Add a task to the queue
        self.task_queue.put(task)


# this is kinda useful https://www.kdab.com/new-in-qt-3d-5-11-generalized-ray-casting/
# also this https://stackoverflow.com/questions/66472858/pick-event-is-wrong-sometimes-but-ray-cast-hit-is-always-correct
# https://stackoverflow.com/questions/49794161/qpickpointevent-when-mouse-cursor-do-something-above-points-in-python-qt-3d
# this one looks like the most promising!
# https://stackoverflow.com/questions/49944259/qobjectpicker-in-qt3d-and-setting-pointpicking-does-not-work?rq=3
class ObjView(QWidget):
    def __init__(self):
        super().__init__()
        self.float_values = None
        self.raw_data = None
        self.anatomy_geometry = None
        self.view = Qt3DWindow()
        self.setMouseTracking(True)
        self.view.defaultFrameGraph().setClearColor(QColor(0, 0, 0))
        self.container = self.createWindowContainer(self.view)

        self.faces = read_geometry_faces("wahtever")

        self.scene = self.createScene()
        # I don't know why, but you need to add it to the layout for it to be rendered.
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.initialiseCamera(self.view, self.scene)
        self.view.setRootEntity(self.scene)
        self.view.mousePressEvent = self._mousePressEvent

        # later you need to attach it to the entity you want to pick from otherwise no bueno!
        self.picker = Qt3DRender.QObjectPicker()
        # you need(!) to grab the already created render settings or you'll have weird behavior
        picking_settings = self.view.renderSettings().pickingSettings()
        picking_settings.setFaceOrientationPickingMode(
            QPickingSettings.FaceOrientationPickingMode.FrontAndBackFace)
        # set QObjectPicker to PointPicking:
        picking_settings.setPickMethod(
            QPickingSettings.PickMethod.TrianglePicking)
        picking_settings.setPickResultMode(
            QPickingSettings.PickResultMode.NearestPick)
        picking_settings.setWorldSpaceTolerance(.1)

        self.picker.setHoverEnabled(True)
        self.picker.setDragEnabled(True)
        self.picker.moved.connect(self.mouse_event_thread)
        self.anatomyEntity.addComponent(self.picker)
        self.extracted_data_exists = False
        # self.show()

    def create_worker_thread(self):
        self.worker_thread = WorkerThread(self.anatomy_geometry, self.float_values)
        self.worker_thread.finished.connect(lambda x: print("Oh, goodbye!"))
        self.worker_thread.start()
        # Add the task to the worker thread's queue


    # if set to triangle picking the event will a QPickTriangleEvent!
    def mouse_event(self, e: QPickTriangleEvent):
        # local intersection is true to the entity and doesn't change if the entity's code doesn't change
        # isn't affected by transforms or scaling (apparently)
        print(e.localIntersection())
        # Note: In the case of indexed rendering, the point indices are relative to the array of coordinates, not the array of indices.
        try:
            index = e.triangleIndex()
            print('\nstart:')
            print("index", index)
            v1 = e.vertex1Index()
            v2 = e.vertex2Index()
            v3 = e.vertex3Index()
        except Exception:
            print("not a triangle")
            return


        geometry: QGeometry = self.anatomyMesh.geometry()
        attributes = geometry.attributes()
        print("default", QAttribute.defaultPositionAttributeName())
        points_per_triangle = 3
        # https://stackoverflow.com/questions/46667975/qt3d-reading-raw-vertex-data-from-qgeometry?rq=3
        for attribute in attributes:
            print(attribute.name())
            if attribute.name() == "vertexPosition":
                print(attribute.vertexBaseType())
                # this is equal to 3
                print("vertex size", attribute.vertexSize())
                print("vertexPosition found!")
                # why bytestride https://stackoverflow.com/questions/64546908/properties-of-the-stride-in-a-gltf-file
                print("byte stride", attribute.byteStride())
                print("byte offset", attribute.byteOffset())
                # this is an array of mixed data not only points!
                data: QByteArray = attribute.buffer().data()
                print("buffer data length", len(data))

                float_values = array('f')
                float_values.frombytes(data)
                print("first value", float_values[0])

                print("arr len", len(float_values))

                # vertexOffset = v1 * attribute.byteStride()
                # bytestride is // 4 because bytestride is variable depending on the obj file
                # but 4 is the size of bytes which is fixed
                # look at "the why bytestride" comment for more
                # but basically since we converted this to an array of floats we need to multiply by the stride / memory
                # to get where the next vertex data starts
                vertexOffset = v1 * (attribute.byteStride() // 4)
                # i think you need to divide the byteoffset by 4 here too for the same reason as above
                offset = vertexOffset + (attribute.byteOffset() // 4)
                print("sample", float_values[offset:offset + points_per_triangle])
                # multiply the offset index value by 2 and set it
                float_values[offset] *= 2
                float_values[offset + 1] *= 2
                float_values[offset + 2] *= 2

                # convert back to bytes and save it
                bytes_array = float_values.tobytes()
                geometry.attributes()[0].buffer().setData(bytes_array)

        print("normal lookup", self.faces[index])
        print("end\n")
        # maybe don't use uvw?
        # print(e.uvw())

    def mouse_event_UV(self, e: QPickTriangleEvent):
        if not self.extracted_data_exists:
            self.extract_geometry_data_from_model()
            self.extracted_data_exists = True
        # local intersection is true to the entity and doesn't change if the entity's code doesn't change
        # isn't affected by transforms or scaling (apparently)
        print(e.localIntersection())
        # Note: In the case of indexed rendering, the point indices are relative to the array of coordinates, not the array of indices.
        try:
            index = e.triangleIndex()
            print('\nstart:')
            print("index", index)
            v1 = e.vertex1Index()
            v2 = e.vertex2Index()
            v3 = e.vertex3Index()

        except Exception:
            print("not a triangle")
            return

        geometry: QGeometry = self.anatomyMesh.geometry()
        attributes = geometry.attributes()
        points_per_triangle = 3
        # https://stackoverflow.com/questions/46667975/qt3d-reading-raw-vertex-data-from-qgeometry?rq=3
        for attribute in attributes:
            print(attribute.name())
            if attribute.name() == "vertexTexCoord":
                print(attribute.vertexBaseType())
                # this is equal to 3
                print("vertex size", attribute.vertexSize())
                print("vertexPosition found!")
                # why bytestride https://stackoverflow.com/questions/64546908/properties-of-the-stride-in-a-gltf-file
                print("byte stride", attribute.byteStride())
                print("byte offset", attribute.byteOffset())

                # bytestride is // 4 because bytestride is variable depending on the obj file
                # but 4 is the size of bytes which is fixed
                # look at "the why bytestride" comment for more
                # but basically since we converted this to an array of floats we need to multiply by the stride / memory
                # to get where the next vertex data starts
                vertexOffset = v1 * (attribute.byteStride() // 4)
                # i think you need to divide the byteoffset by 4 here too for the same reason as above
                offset = vertexOffset + (attribute.byteOffset() // 4)
                print("sample", self.float_values[offset:offset + points_per_triangle])
                # multiply the offset index value by 2 and set it
                self.float_values[offset] = 0
                self.float_values[offset + 1] = 0
                self.float_values[offset + 2] = 0

                # convert back to bytes and save it
                bytes_array = self.float_values.tobytes()
                geometry.attributes()[0].buffer().setData(bytes_array)

        print("end\n")
        # maybe don't use uvw?
        # print(e.uvw())'

    def mouse_event_thread(self, e:QPickTriangleEvent):
        print("thread")
        print()
        if not self.extracted_data_exists:
            self.extract_geometry_data_from_model()
            self.extracted_data_exists = True
            self.create_worker_thread()

        print(e.localIntersection())
        try:
            # deep copy e QPickTriangle event
            task = {"index": e.triangleIndex(), "v1": e.vertex1Index(), "v2": e.vertex2Index(), "v3": e.vertex3Index()}
            # deep copy event
            # e_cp = copy.deepcopy(e)
            # print(task)
            self.worker_thread.add_task(task)
        except Exception:
            print("not a triangle")
            return
        print("end\n")


    def _mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("hi")
        Qt3DWindow.mousePressEvent(self.view, event)

    def extract_geometry_data_from_model(self):
        self.anatomy_geometry: QGeometry = self.anatomyMesh.geometry()
        self.attributes = self.anatomy_geometry.attributes()
        self.buffer = self.attributes[0].buffer()
        self.buffer.destroyed.connect(lambda x: self.extract_geometry_data_from_model)


        # arbitrarily select the first one since it's the same buffer
        self.raw_data: QByteArray = self.buffer.data()
        self.float_values = array('f')
        # this is an array of mixed data not only points!
        self.float_values.frombytes(self.raw_data)

    def createScene(self):
        # Root entity.
        rootEntity = QEntity()

        self.anatomyEntity = QEntity(rootEntity)
        self.anatomyMesh = QMesh(rootEntity)

        self.anatomy_scale = QTransform()
        self.anatomy_scale.setScale3D(QVector3D(5, 5, 5))

        # self.anatomyMesh.setSource(QUrl.fromLocalFile(QDir.currentPath() + "/anatomy.OBJ"))
        # Get the current directory
        current_directory = QDir.currentPath()
        file_path = QDir(current_directory).filePath("../obj files/anatomy.obj")
        print("file path",file_path)
        self.anatomyMesh.setSource(QUrl.fromLocalFile(file_path))

        # this also needs to be set to root entity so the matrix transformation can be applied as you move around
        anatomyTextureLoader = QTextureLoader(rootEntity)
        anatomyMaterial = QTextureMaterial(rootEntity)
        print("texture path",QDir(current_directory).filePath("../obj textures/diffuse.jpg"))
        anatomyTextureLoader.setSource(QUrl.fromLocalFile(QDir(current_directory).filePath("../obj textures/diffuse.jpg")))
        anatomyMaterial.setTexture(anatomyTextureLoader)

        self.anatomyEntity.addComponent(self.anatomyMesh)

        self.anatomyEntity.addComponent(self.anatomy_scale)
        self.anatomyEntity.addComponent(anatomyMaterial)
        # anatomyEntity.addComponent(lightEntity)
        # anatomyEntity.addComponent(material)

        return rootEntity

    def initialiseCamera(self, view, scene):
        # Camera.
        self.camera = view.camera()
        self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        self.camera.setPosition(QVector3D(0.0, 5, 15.0))
        self.camera.setViewCenter(QVector3D(0.0, 5.5, 0.0))

        # For camera controls.
        camController = QOrbitCameraController(scene)
        camController.setLinearSpeed(25.0)
        camController.setLookSpeed(150.0)
        camController.setCamera(self.camera)
