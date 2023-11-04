import typing
from typing import Optional

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QApplication


# https://gist.github.com/acbetter/32c575803ec361c3e82064e60db4e3e0
# modified by converting to label instead
# create pixel signal
# and emit it when mouse moves
class ImageContainerView(QLabel):
    mouseMovePixelColor = pyqtSignal(QPoint, QColor)
    mouseLeftClick = pyqtSignal(QPoint)

    # this might be useful?
    # https://stackoverflow.com/questions/69869064/how-to-get-pixel-location-and-draw-a-dot-on-that-location-using-pyqt5

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
        point = self.getMousePositionOnImage(event.pos())
        color = QColor(self.QImage.pixel(point.x(), point.y()))
        print("Moved!!", color.getRgb(), point)
        r, g, b, a = color.getRgb()
        self.mouseMovePixelColor.emit(point, QColor(r, g, b, a))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        point = self.getMousePositionOnImage(event.pos())
        color = QColor(self.QImage.pixel(point.x(), point.y()))
        print("Pressed!", color.getRgb(), point)
        r, g, b, a = color.getRgb()
        if event.button() == Qt.LeftButton:
            self.mouseLeftClick.emit(point)
        if event.button() == Qt.MiddleButton:
            print("Middle button pressed")
        if event.button() == Qt.RightButton:
            print("Right button pressed")
        super().mousePressEvent(event)

    # this is the hover mouse event
    def enterEvent(self, event):
        QApplication.setOverrideCursor(Qt.CrossCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def getMousePositionOnImage(self, pos) -> QtCore.QPoint or None:
        # https://stackoverflow.com/questions/59611751/pyqt5-image-coordinates
        # consider the widget contents margins
        contentsRect = QtCore.QRectF(self.contentsRect())
        if pos not in contentsRect:
            # outside widget margins, ignore!
            return

        # adjust the position to the contents margins
        pos -= contentsRect.topLeft()

        pixmapRect = self.pixmap().rect()
        if self.hasScaledContents():
            x = pos.x() * pixmapRect.width() / contentsRect.width()
            y = pos.y() * pixmapRect.height() / contentsRect.height()
            pos = QtCore.QPoint(int(x), int(y))


        else:
            align = self.alignment()
            # for historical reasons, QRect (which is based on integer values),
            # returns right() as (left+width-1) and bottom as (top+height-1),
            # and so their opposite functions set/moveRight and set/moveBottom
            # take that into consideration; using a QRectF can prevent that; see:
            # https://doc.qt.io/qt-5/qrect.html#right
            # https://doc.qt.io/qt-5/qrect.html#bottom
            pixmapRect = QtCore.QRectF(pixmapRect)

            # the pixmap is not left aligned, align it correctly
            if align & QtCore.Qt.AlignRight:
                pixmapRect.moveRight(contentsRect.x() + contentsRect.width())
            elif align & QtCore.Qt.AlignHCenter:
                pixmapRect.moveLeft(contentsRect.center().x() - pixmapRect.width() / 2)
            # the pixmap is not top aligned (note that the default for QLabel is
            # Qt.AlignVCenter, the vertical center)
            if align & QtCore.Qt.AlignBottom:
                pixmapRect.moveBottom(contentsRect.y() + contentsRect.height())
            elif align & QtCore.Qt.AlignVCenter:
                pixmapRect.moveTop(contentsRect.center().y() - pixmapRect.height() / 2)

            if not pos in pixmapRect:
                # outside image margins, ignore!
                return
            # translate coordinates to the image position and convert it back to
            # a QPoint, which is integer based
            pos = (pos - pixmapRect.topLeft()).toPoint()

        print('X={}, Y={}'.format(pos.x(), pos.y()))
        return pos
