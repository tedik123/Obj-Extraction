import sys
import os

from PyQt5.QtCore import Qt, QDir, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QColor
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    QGraphicsPixmapItem
from PyQt5.QtWidgets import QApplication, qApp, QFileDialog, QListWidget, QSplitter, QTextEdit, QFileSystemModel

from PIL import Image

# CUSTOM
from CustomLabel import CustomLabel

Home_Path = os.path.expanduser("~")


class QImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scaleFactor = 0.0

        self.createWidgets()
        self.createLayouts()
        self.createActions()
        self.createMenus()
        self.fileList.setEnabled(True)

        self.setWindowTitle("Image Viewer")
        self.resize(1200, 800)

    def createWidgets(self):
        self.imageLabel = CustomLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.mouseMovePixelColor.connect(self.changeTextColor)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.directoryList = QListWidget()
        # self.directoryModel = QFileSystemModel()
        # self.directoryModel.setRootPath('')
        # self.directoryList.setRootIndex(self.directoryModel.index(QDir.homePath()))
        self.populateDirectoryList('')
        self.directoryList.doubleClicked.connect(self.selectDirectory)

        self.fileList = QListWidget(self)
        self.fileList.setSelectionMode(QListWidget.SingleSelection)
        self.fileList.setEnabled(False)
        self.populateFileList(Home_Path)
        self.fileList.itemClicked.connect(self.listopen)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.setPlainText("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas ")

        self.imageName = QTextEdit()
        self.imageName.setAlignment(Qt.AlignCenter)
        self.imageName.setReadOnly(True)

    def changeTextColor(self, point, color):
        print("COLOR", color)
        self.textEdit.setTextBackgroundColor(color)
        #change the background color of text edit
        self.textEdit.setStyleSheet("background-color: rgb(%d, %d, %d)" % (color.red(), color.green(), color.blue()))

    def createLayouts(self):
        V_splitter = QSplitter(Qt.Vertical)
        V_splitter.addWidget(self.imageName)
        V_splitter.addWidget(self.scrollArea)
        V_splitter.addWidget(self.textEdit)
        V_splitter.setSizes([5, 450, 150])

        H_splitter = QSplitter(Qt.Horizontal)
        H_splitter.addWidget(self.directoryList)
        H_splitter.addWidget(self.fileList)

        # combine the two splitters
        H_splitter.addWidget(V_splitter)
        H_splitter.setSizes([130, 130, 700])

        self.setCentralWidget(H_splitter)

    def populateDirectoryList(self, new_path):
        home = QDir.homePath()
        self.directoryList.clear()

        if len(new_path) > 0 and new_path != '':
            path = new_path
        else:
            path = home

        self.directoryList.addItem(new_path)
        self.directoryList.addItem("..")

        # store the directory information in a list to be sorted
        dir_list = os.listdir(path)
        dir_list.sort()

        for this_dir in dir_list:
            # filter out the files and hidden directories - only show directories
            if os.path.isdir(os.path.join(path, this_dir)) and not this_dir.startswith('.'):
                self.directoryList.addItem(path + "/" + this_dir)

        # self.repaint()

    def selectDirectory(self, item):
        self.fileList.clear()
        directory = self.directoryList.currentItem().text()
        # print (directory)

        if directory == "..":
            directory = os.path.expanduser("~")

        self.populateDirectoryList(directory)
        self.populateFileList(directory)

    def populateFileList(self, directory):
        self.fileList.clear()
        for file in os.listdir(directory):
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith(
                    '.bmp') or file.endswith('.gif'):
                self.fileList.addItem(file)

    def listopen(self):
        self.open("list")

    def open(self, file_name):
        options = QFileDialog.Options()
        current_path = self.directoryList.item(0).text()

        # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        try:
            if file_name == "list":
                file_name = self.fileList.currentItem().text()
                # print('List File Select ', file_name)
                file_name = os.path.join(current_path, self.fileList.currentItem().text())
            else:
                file_name = Home_Path
                fileName, _ = QFileDialog.getOpenFileName(self, 'File Dialog - Select Image File Name', file_name,
                                                          'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        except:
            # print('Error File Select ', file_name)
            file_name = Home_Path
            fileName, _ = QFileDialog.getOpenFileName(self, 'File Dialog - Select Image File Name', file_name,
                                                      'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)

        if file_name != Home_Path:
            fileName = file_name

        if fileName:
            # self.textEdit.clear()
            self.imageName.setPlainText(fileName)

            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return
            self.setWindowTitle("Image Viewer : " + fileName)
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.imageLabel.setQImage()

            self.scaleFactor = 1.0

            self.scrollArea.setVisible(True)
            self.fitToWidthAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.fitToWidth()


    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0
        self.scaleImage(1.0)

    def fitToWidth(self):
        if self.scrollArea.width() > 0 and self.imageLabel.pixmap().width() > 0:
            zoomfactor = self.scrollArea.width() / self.imageLabel.pixmap().width()
        else:
            zoomfactor = 1

        self.imageLabel.adjustSize()
        self.scaleFactor = zoomfactor
        self.scaleImage(1.0)

        self.updateActions()

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
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
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWidthAct = QAction("Fit to &Width", self, shortcut="Ctrl+w", enabled=False, triggered=self.fitToWidth)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addAction(self.fitToWidthAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.fitToWidthAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
        self.repaint()

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))

    def populateimageList(self, directory):
        self.imageList.clear()
        for file in os.listdir(directory):
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith(
                    '.bmp') or file.endswith('.gif'):
                self.imageList.addItem(file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())

    # credit for the code that inspired this goes to the following:
    #
    # if you need 'Dual-Image' Synchronous Scrolling in the window by PyQt5 and Python 3
    # please visit https://gist.github.com/acbetter/e7d0c600fdc0865f4b0ee05a17b858f2
    #
    # base on https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
    #
