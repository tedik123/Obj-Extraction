import copy
import pickle
import queue
import time
from array import array

from PyQt6.Qt3DCore import QEntity, QTransform, QGeometry, QBuffer, QAttribute
from PyQt6 import QtOpenGL
from PyQt6 import Qt3DInput
from PyQt6.Qt3DExtras import Qt3DWindow, QOrbitCameraController, \
    QTextureMaterial, QPhongMaterial
from PyQt6.Qt3DInput import QMouseDevice, QMouseHandler
from PyQt6.Qt3DRender import QTextureLoader, QRayCaster, QScreenRayCaster, QPickingSettings, QPickEvent, \
    QPickTriangleEvent, QMesh, QCamera, QTextureImage, QAbstractTexture
from PyQt6.QtGui import QVector3D, QColor, QImage
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
    attribute_data_loaded = pyqtSignal(list)
    triangle_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.anatomyEntity: QEntity| None = None
        self.copied_camera = None
        self.camera = None
        self.extracted_data_exists = False
        self.picker = None
        self.scene = None
        self.texture_file = None
        self.obj_file = None
        self.attributes = None
        self.float_values = None
        self.raw_data = None
        self.anatomy_geometry = None
        self.view = Qt3DWindow()
        self.setMouseTracking(True)
        self.view.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view.defaultFrameGraph().setClearColor(QColor(20, 20, 20))
        self.container = self.createWindowContainer(self.view)

        # todo remove later
        self.faces = read_geometry_faces("wahtever")

        # I don't know why, but you need to add it to the layout for it to be rendered.
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.setup_3d_view()

        # self.show()

    def setup_3d_view(self):
        self.scene = self.createScene()
        self.initialiseCamera(self.view, self.scene)
        self.view.setRootEntity(self.scene)

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
        self.picker.clicked.connect(self.mouse_event_thread)
        self.anatomyEntity.addComponent(self.picker)
        self.extracted_data_exists = False

    def create_worker_thread(self):
        self.worker_thread = WorkerThread(self.anatomy_geometry, self.float_values)
        self.worker_thread.finished.connect(lambda x: print("Oh, goodbye!"))
        self.worker_thread.start()
        # Add the task to the worker thread's queue

    def hide_main_model(self):
        if self.anatomyEntity:
            self.anatomyEntity.setEnabled(not self.anatomyEntity.isEnabled())

    # this returns the attribute data
    def get_attribute_data(self):
        return self.attributes

    def set_texture_file(self, file_path):
        # current_directory = QDir.currentPath()
        # file_path = QDir(current_directory).filePath("../obj textures/diffuse.jpg")
        old_texture_file = self.texture_file
        self.texture_file = file_path
        if old_texture_file:
            self.anatomyTextureLoader.setSource(QUrl.fromLocalFile(self.texture_file))
            self.anatomyMaterial.setTexture(self.anatomyTextureLoader)
            # self.anatomyMesh.setTexture(self.texture_file)

    # this is for the drawing it updates the image textrue
    def update_texture_with_image(self):
        print("Updating texture on 3D with new point data!")
        current_directory = QDir.currentPath()
        file_path = QDir(current_directory).filePath("../outputs/latest_points.jpg")
        # i don't know if it's okay to just overwrite it but if we don't the image fails to update after the first time
        # i assume under the hood it's just comparing the url and if it hasn't changed it won't update.... not sure
        self.anatomyTextureLoader = QTextureLoader()
        self.texture_file = file_path
        self.anatomyTextureLoader.setSource(QUrl.fromLocalFile(file_path))
        self.anatomyMaterial.setTexture(self.anatomyTextureLoader)

    def set_obj_file(self, file_path):
        # Get the current directory
        # current_directory = QDir.currentPath()
        # file_path = QDir(current_directory).filePath("../obj files/anatomy.obj")
        print("file path", file_path)
        self.obj_file = file_path

        self.setup_3d_view()


    # if set to triangle picking the event will a QPickTriangleEvent!
    def mouse_event_thread(self, e: QPickTriangleEvent):
        print("thread")
        print()
        if not self.extracted_data_exists:
            self.extract_geometry_data_from_model()
            self.extracted_data_exists = True
            # self.create_worker_thread()

        print(e.localIntersection())
        try:
            # deep copy e QPickTriangle event
            task = {"index": e.triangleIndex(), "v1": e.vertex1Index(), "v2": e.vertex2Index(), "v3": e.vertex3Index()}
            self.triangle_selected.emit(task)
        except Exception:
            print("not a triangle")
            return
        print("end\n")

    def extract_geometry_data_from_model(self):
        self.anatomy_geometry: QGeometry = self.anatomyMesh.geometry()
        self.attributes = self.anatomy_geometry.attributes()
        self.buffer = self.attributes[0].buffer()

        # arbitrarily select the first one since it's the same buffer
        self.raw_data: QByteArray = self.buffer.data()
        self.float_values = array('f')
        # this is an array of mixed data not only points!
        self.float_values.frombytes(self.raw_data)
        self.attribute_data_loaded.emit(self.attributes)

    def createScene(self):
        # Root entity.
        rootEntity = QEntity()
        self.anatomyEntity = QEntity(rootEntity)
        self.anatomyMesh = QMesh(rootEntity)

        self.anatomy_scale = QTransform()
        self.anatomy_scale.setScale3D(QVector3D(5, 5, 5))
        if self.obj_file:
            self.anatomyMesh.setSource(QUrl.fromLocalFile(self.obj_file))
        if self.texture_file:
            self.anatomyMaterial = QTextureMaterial(rootEntity)
            # this also needs to be set to root entity so the matrix transformation can be applied as you move around
            self.anatomyTextureLoader = QTextureLoader(rootEntity)
            self.anatomyTextureLoader.setSource(QUrl.fromLocalFile(self.texture_file))
            self.anatomyMaterial.setTexture(self.anatomyTextureLoader)
        else:
            self.anatomyMaterial = QPhongMaterial(rootEntity)
            self.anatomyMaterial.setDiffuse(QColor(0, 255, 0))
            self.anatomyMaterial.setAmbient(QColor(255, 0, 0))
            self.anatomyMaterial.setSpecular(QColor(0, 0, 255))
            self.anatomyMaterial.setShininess(100)

        self.anatomyEntity.addComponent(self.anatomyMesh)
        self.anatomyEntity.addComponent(self.anatomy_scale)
        self.anatomyEntity.addComponent(self.anatomyMaterial)
        return rootEntity

    def set_camera_position(self):
        self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        self.camera.setPosition(QVector3D(0.0, 5, 15.0))
        self.camera.setViewCenter(QVector3D(0.0, 5.5, 0.0))

    def deep_copy_camera(self, original_camera):
        self.copied_camera = QCamera()
        self.copied_camera.setAspectRatio(original_camera.aspectRatio())
        self.copied_camera.setBottom(original_camera.bottom())
        self.copied_camera.setExposure(original_camera.exposure())
        self.copied_camera.setFarPlane(original_camera.farPlane())
        self.copied_camera.setFieldOfView(original_camera.fieldOfView())
        self.copied_camera.setLeft(original_camera.left())
        self.copied_camera.setNearPlane(original_camera.nearPlane())
        self.copied_camera.setPosition(original_camera.position())
        self.copied_camera.setProjectionMatrix(original_camera.projectionMatrix())
        self.copied_camera.setProjectionType(original_camera.projectionType())
        self.copied_camera.setRight(original_camera.right())
        self.copied_camera.setTop(original_camera.top())
        self.copied_camera.setUpVector(original_camera.upVector())
        self.copied_camera.setViewCenter(original_camera.viewCenter())
        return self.copied_camera

    def reset_camera(self):
        self.camera.setAspectRatio(self.copied_camera.aspectRatio())
        self.camera.setBottom(self.copied_camera.bottom())
        self.camera.setExposure(self.copied_camera.exposure())
        self.camera.setFarPlane(self.copied_camera.farPlane())
        self.camera.setFieldOfView(self.copied_camera.fieldOfView())
        self.camera.setLeft(self.copied_camera.left())
        self.camera.setNearPlane(self.copied_camera.nearPlane())
        self.camera.setPosition(self.copied_camera.position())
        self.camera.setProjectionMatrix(self.copied_camera.projectionMatrix())
        self.camera.setProjectionType(self.copied_camera.projectionType())
        self.camera.setRight(self.copied_camera.right())
        self.camera.setTop(self.copied_camera.top())
        self.camera.setUpVector(self.copied_camera.upVector())
        self.camera.setViewCenter(self.copied_camera.viewCenter())

    def initialiseCamera(self, view, scene):
        self.camera: QCamera = view.camera()
        self.set_camera_position()
        if not self.copied_camera:
            self.deep_copy_camera(self.camera)
        else:
            self.reset_camera()
        # For camera controls.
        camController = QOrbitCameraController(scene)
        camController.setLinearSpeed(15.0)

        print("acceleration", camController.acceleration())
        camController.setLookSpeed(150.0)
        camController.setCamera(self.camera)
