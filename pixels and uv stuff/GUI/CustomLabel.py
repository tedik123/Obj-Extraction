from typing import Optional

from PyQt5.QtCore import Qt, QPoint, QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QApplication


class LogObject(QObject):
    MousePixmapSignal = pyqtSignal(QPoint, QColor)


# https://gist.github.com/acbetter/32c575803ec361c3e82064e60db4e3e0
# modified by converting to label instead
# create pixel signal
# and emit it when mouse moves
class CustomLabel(QLabel):
    mouseMovePixelColor = pyqtSignal(QPoint, QColor)

    # TODO converting QT coordinates to pixel coordinates with scaling consideration!
    # https://stackoverflow.com/questions/59611751/pyqt5-image-coordinates

    # this might be useful?
    # https://stackoverflow.com/questions/69869064/how-to-get-pixel-location-and-draw-a-dot-on-that-location-using-pyqt5

    # and this?
    # https://stackoverflow.com/questions/63378825/coordinates-of-an-image-pyqt

    # def __init__(self, log, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        # self.setAcceptHoverEvents(True)
        self.setMouseTracking(True)
        self.QImage = None
        # self.mouseMoveEvent()
        # self.log = log

    def setQImage(self):
        self.QImage = self.pixmap().toImage()

    def mouseMoveEvent(self, event):
        point = event.pos()
        color = QColor(self.QImage.pixel(point.x(), point.y()))
        # self.log.MousePixmapSignal.emit(point, color)
        print("Moved!!", color.getRgb(), point)
        QLabel.mouseMoveEvent(self, event)
        r, g, b, a = color.getRgb()
        self.mouseMovePixelColor.emit(point, QColor(r, g, b, a))

    # this is the hover mouse event
    def enterEvent(self, event):
        QApplication.setOverrideCursor(Qt.CrossCursor)
        QLabel.enterEvent(self, event)

    def leaveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        QLabel.leaveEvent(self, event)
