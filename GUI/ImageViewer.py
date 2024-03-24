import sys
import os
# import qdarkstyle

from functools import partial

from PyQt6.QtCore import Qt, QDir, pyqtSignal, QObject, QPoint, QThread
from PyQt6.QtGui import QImage, QPixmap, QPalette, QPainter, QColor, QAction
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, \
    QGraphicsPixmapItem, QWidget, QVBoxLayout, QSpacerItem, QBoxLayout, QTabWidget
from PyQt6.QtWidgets import QApplication,  QFileDialog, QListWidget, QSplitter, QTextEdit

from PIL import Image

# CUSTOM
from MainController import MainController
from Base.LabelSelectorView import LabelSelectorView
from Base.LabelSelectorController import LabelSelectorController
from ImageContainerView import ImageContainerView
from PixelData.StartingPointsView import StartingPointsView
from PixelData.PixelDataController import PixelDataController
from PixelData.PixelDataModel import PixelDataModel
from PixelData.RgbView import RgbView
from ImageContainerController import ImageContainerController
from Workers.PixelGrabberWorker import PixelGrabberWorker
from ObjView.ObjView import ObjView
Home_Path = os.path.expanduser("~")


class QImageViewer(QMainWindow):
    obj_file_loaded = pyqtSignal(str)
    image_loaded = pyqtSignal(str)
    hide_main_model_signal = pyqtSignal()
    reset_camera_signal = pyqtSignal()
    def __init__(self):
        super().__init__()

        # TO BE CREATED
        self.obj_view = None
        self.main_controller = None
        self.pixel_data_controller = None
        self.label_selector_controller = None
        self.image_container_controller = None

        # i should reuse this for when I create the rgb one, it should use the same model
        self.label_model = PixelDataModel()

        # create and move pixel grabber worker to thread
        self.pixel_grabber_worker = PixelGrabberWorker(self.label_model)
        self.pixel_grabber_worker_thread = QThread()
        self.pixel_grabber_worker.moveToThread(self.pixel_grabber_worker_thread)
        self.pixel_grabber_worker_thread.start()

        self.textEdit = None
        self.imageContainer = None
        self.imageLabel = None
        self.label_selector = None

        self.scaleFactor = 0.0

        # creation section
        self.createWidgets()
        self.createLayouts()
        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Viewer")
        self.resize(1200, 800)

        # WARNING This is just for testing!
        self.set_default_img_and_obj()

    def createWidgets(self):
        self.pixel_data_controller = PixelDataController(self.label_model, StartingPointsView(), RgbView())
        self.label_selector_controller = LabelSelectorController(self.label_model, LabelSelectorView())
        self.obj_view = ObjView()
        self.createAndSetImageContainerToController()
        self.main_controller = MainController(self.pixel_data_controller,
                                              self.label_selector_controller,
                                              self.image_container_controller,
                                              self.label_model
                                              )

        # pass in the reference to the main controller so you can handle communication
        self.pixel_data_controller.set_main_controller(self.main_controller)
        self.label_selector_controller.set_main_controller(self.main_controller)

        self.createTextEdit()

    def createTextEdit(self):
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.setPlainText("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas ")

    def createAndSetImageContainerToController(self):
        self.imageContainer = QScrollArea()
        self.imageContainer.setBackgroundRole(QPalette.ColorRole.Dark)
        self.imageLabel = ImageContainerView()
        self.imageContainer.setWidget(self.imageLabel)
        self.imageContainer.setVisible(False)
        self.image_container_controller = ImageContainerController(self.imageLabel, pixel_data_model=self.label_model)
        self.image_container_controller.set_pixel_data_controller(self.pixel_data_controller)
        self.image_container_controller.set_pixel_grabber_work(self.pixel_grabber_worker)
        self.image_container_controller.set_obj_view(self.obj_view)
        # self to image container
        self.hide_main_model_signal.connect(self.image_container_controller.hide_main_model)
        self.reset_camera_signal.connect(self.image_container_controller.reset_camera)
        # this is literally just for testing!
        self.imageLabel.mouseMovePixelColor.connect(self.changeTextColor)


    def changeTextColor(self, point, color):
        # print("COLOR", color)
        self.textEdit.setTextBackgroundColor(color)
        self.textEdit.setPlainText("Point: %d, %d\nColor: %d, %d, %d" % (point.x(), point.y(), color.red(), color.green(), color.blue()))
        # change the background color of text edit
        self.textEdit.setStyleSheet("background-color: rgb(%d, %d, %d); font-size: 20px" % (color.red(), color.green(), color.blue()))

    def createLayouts(self):
        self.V_splitter = QSplitter(Qt.Orientation.Vertical)
        self.tab_view = QTabWidget()
        self.tab_view.addTab(self.imageContainer, "2D View")
        self.V_splitter.addWidget(self.tab_view)
        # self.obj_view.setParent(self)
        self.tab_view.addTab(self.obj_view, "3D View")
        self.V_splitter.addWidget(self.textEdit)
        self.V_splitter.setSizes([450, 150])

        print(self.obj_view.parentWidget())


        H_splitter = QSplitter(Qt.Orientation.Horizontal)

        # H_splitter.addWidget(self.pixelList)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.label_selector_controller.label_selector_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pixel_data_controller.starting_points_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pixel_data_controller.rgb_view)

        # combine the two splitters
        H_splitter.addWidget(self.V_splitter)
        H_splitter.setSizes([700])

        self.setCentralWidget(H_splitter)

    def listopen(self):
        self.open_image("list")

    # this is just for testing remove later!
    def set_default_img_and_obj(self):
        # fileName = "C:/Users/tedik/Downloads/frog_state.png"
        image_file_name = "C:/Users/tedik/PycharmProjects/RandomScripts/obj textures/diffuse.jpg"
        # obj_file_name = "C:/Users/tedik/Desktop/ecorche-male-musclenames-anatomy/source/zipEXCHANGE2/objEXCHANGE.OBJ"
        obj_file_name = "C:/Users/tedik/PycharmProjects/RandomScripts/obj files/decimated_model.obj"
        if image_file_name:
            image = QImage(image_file_name)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % image_file_name)
                return
            self.setWindowTitle("Image Viewer : " + image_file_name)
            self.image_container_controller.set_image(image, image_file_name)
            self.image_container_controller.set_obj_file(obj_file_name)

            self.scaleFactor = 1.0


            self.imageContainer.setVisible(True)
            self.fitToWidthAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.fitToWidth()

    def open_image(self, file_name):
        file_dialog = QFileDialog()
        options = file_dialog.options()
        current_path = QDir.homePath()
        file_name = Home_Path
        fileName, _ = QFileDialog.getOpenFileName(self, 'File Dialog - Select Image File Name', file_name,
                                                      'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        print("FILE NAME", fileName)
        if file_name != Home_Path:
            fileName = file_name

        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return
            self.setWindowTitle("Image Viewer : " + fileName)
            self.image_container_controller.set_image(image, fileName)

            self.scaleFactor = 1.0

            self.imageContainer.setVisible(True)
            self.fitToWidthAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.fitToWidth()
            # fixme this should be sending a signal

    def open_obj_file(self, file_name):
        file_dialog = QFileDialog()
        options = file_dialog.options()
        current_path = QDir.homePath()
        file_name = Home_Path
        fileName, _ = QFileDialog.getOpenFileName(self, 'File Dialog - Select Obj File', file_name,
                                                      '3D (*.obj *.OBJ)', options=options)
        if file_name != Home_Path:
            fileName = file_name

        if fileName:
            print("obj file bname?", fileName)
            self.image_container_controller.set_obj_file(fileName)

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0
        self.scaleImage(1.0)

    def fitToWidth(self):
        if self.imageContainer.width() > 0 and self.imageLabel.pixmap().width() > 0:
            zoomfactor = self.imageContainer.width() / self.imageLabel.pixmap().width()
        else:
            zoomfactor = 1

        self.imageLabel.adjustSize()
        self.scaleFactor = zoomfactor
        self.scaleImage(1.0)

        self.updateActions()

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.imageContainer.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                          "<p>The <b>Image Viewer</b> example shows how to combine "
                          "QLabel and QScrollArea to display an image. QLabel is "
                          "typically used for displaying text, but it can also display "
                          "an image. QScrollArea provides a scrolling view around "
                          "another widget. If the child widget exceeds the size of the "
                          "frame, QScrollArea automatically provides scroll bars.</p>"
                          "<p>The example demonstrates how QLabel's ability to scale "
                          "its contents (QLabel.scaledContents), and QScrollArea's "
                          "ability to automatically resize its contents "
                          "(QScrollArea.widgetResizable), can be used to implement "
                          "zooming and scaling features.</p>"
                          )

    def createActions(self):
        self.openAct = QAction("&Open Texture...", self, shortcut="Ctrl+O", triggered=self.open_image)
        self.openObj = QAction("&Open Obj...", self, shortcut="Ctrl+3", triggered=self.open_obj_file)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWidthAct = QAction("Fit to &Width", self, shortcut="Ctrl+w", enabled=False, triggered=self.fitToWidth)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.hide_main_obj = QAction("&Hide Main Obj", self, shortcut="Ctrl+H", triggered=self.hide_main_model_signal.emit)
        self.reset_camera = QAction("&Reset Camera", self, shortcut="Ctrl+R", triggered=self.reset_camera_signal.emit)
    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.openObj)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addAction(self.fitToWidthAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)
        self.view3D = QMenu("&3D", self)
        self.view3D.addAction(self.hide_main_obj)
        self.view3D.addAction(self.reset_camera)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.view3D)
        self.menuBar().addMenu(self.helpMenu)


    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.fitToWidthAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.imageContainer.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.imageContainer.verticalScrollBar(), factor)
        self.repaint()

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    imageViewer.show()

    # this awkwardness forces it to appear on the non-main monitor
    LEFT_MONITOR = app.screens()[-1]
    imageViewer.windowHandle().setScreen(LEFT_MONITOR)
    imageViewer.showFullScreen()
    imageViewer.showNormal()

    sys.exit(app.exec())

    # credit for the code that inspired this goes to the following:
    #
    # if you need 'Dual-Image' Synchronous Scrolling in the window by PyQt6 and Python 3
    # please visit https://gist.github.com/acbetter/e7d0c600fdc0865f4b0ee05a17b858f2
    #
    # base on https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
    #
