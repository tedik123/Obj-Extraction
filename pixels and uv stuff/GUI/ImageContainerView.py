import typing
from typing import Optional

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint, QObject, pyqtSignal, QPointF
from PyQt6.QtGui import QColor, QPalette, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel, QApplication


# https://gist.github.com/acbetter/32c575803ec361c3e82064e60db4e3e0
# modified by converting to label instead
# create pixel signal
# and emit it when mouse moves
class ImageContainerView(QLabel):
    mouseMovePixelColor = pyqtSignal(QPoint, QColor)
    mouseLeftClick = pyqtSignal(QPoint)
    mouseRightClick = pyqtSignal(QColor)

    # this might be useful?
    # https://stackoverflow.com/questions/69869064/how-to-get-pixel-location-and-draw-a-dot-on-that-location-using-pyqt5

    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        # self.setAcceptHoverEvents(True)
        self.setMouseTracking(True)
        self.QImage = None
        self.point_set = None
        # self.mouseMoveEvent()
        self.setBackgroundRole(QPalette.ColorRole.Base)
        self.setScaledContents(True)
        # self.log = log

    def setQImage(self):
        self.QImage = self.pixmap().toImage()

    def mouseMoveEvent(self, event):
        point = self.getMousePositionOnImage(event.pos())
        color = QColor(self.QImage.pixel(point.x(), point.y()))
        # print("Moved!!", color.getRgb(), point)
        r, g, b, a = color.getRgb()
        self.mouseMovePixelColor.emit(point, QColor(r, g, b, a))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        point = self.getMousePositionOnImage(event.pos())
        color = QColor(self.QImage.pixel(point.x(), point.y()))
        print("Pressed!", color.getRgb(), point)
        r, g, b, a = color.getRgb()
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouseLeftClick.emit(point)
            self.draw_point(point)

        if event.button() == Qt.MouseButton.MiddleButton:
            print("Middle button pressed")
        if event.button() == Qt.MouseButton.RightButton:
            print("Right button pressed")
            self.mouseRightClick.emit(color)
        super().mousePressEvent(event)

    # this is the hover mouse event
    def enterEvent(self, event):
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # as the name implies this actually restores the cursor to whatever it should actually be
        QApplication.restoreOverrideCursor()
        super().leaveEvent(event)

    def getMousePositionOnImage(self, pos) -> QtCore.QPoint or None:
        # https://stackoverflow.com/questions/59611751/pyqt5-image-coordinates
        # consider the widget contents margins
        # contentsRect = QtCore.QRectF(self.contentsRect())
        contentsRect = QtCore.QRectF(self.contentsRect())
        pos = QPointF(pos)
        if pos not in contentsRect:
            # outside widget margins, ignore!
            return

        # adjust the position to the contents margins
        pos -= contentsRect.topLeft()

        pixmapRect = self.pixmap().rect()
        if self.hasScaledContents():
            x = pos.x() * pixmapRect.width() / contentsRect.width()
            y = pos.y() * pixmapRect.height() / contentsRect.height()
            pos = QtCore.QPoint(round(x), round(y))


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
            if align & QtCore.Qt.AlignmentFlag.AlignRight:
                pixmapRect.moveRight(contentsRect.x() + contentsRect.width())
            elif align & QtCore.Qt.AlignmentFlag.AlignHCenter:
                pixmapRect.moveLeft(contentsRect.center().x() - pixmapRect.width() / 2)
            # the pixmap is not top aligned (note that the default for QLabel is
            # Qt.AlignmentFlag.AlignVCenter, the vertical center)
            if align & QtCore.Qt.AlignmentFlag.AlignBottom:
                pixmapRect.moveBottom(contentsRect.y() + contentsRect.height())
            elif align & QtCore.Qt.AlignmentFlag.AlignVCenter:
                pixmapRect.moveTop(contentsRect.center().y() - pixmapRect.height() / 2)

            if not pos in pixmapRect:
                # outside image margins, ignore!
                return
            # translate coordinates to the image position and convert it back to
            # a QPoint, which is integer based
            pos = (pos - pixmapRect.topLeft())
            pos = QtCore.QPoint(round(pos.x), round(pos.y))

        # print('X={}, Y={}'.format(pos.x(), pos.y()))
        return pos

    def draw_point(self, point):
        pixmap = self.pixmap().copy()
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QColor("black"))
        length = 10
        rect = QtCore.QRect(10, 10, length, length)
        rect.moveCenter(point)
        painter.drawEllipse(rect)
        painter.end()
        self.setPixmap(pixmap)

    def draw_points(self, points, clear_old=False):
        if clear_old:
            self.point_set = None
            self.setPixmap(self.pixmap().copy())
            pixmap = QPixmap.fromImage(self.QImage)
        else:
            pixmap = self.pixmap().copy()
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QColor("black"))

        # check which points are new
        if self.point_set:
            new_points = [x for x in points if x not in self.point_set]
        else:
            new_points = points
        # draw the points then save them locally on next call check only which new points to draw
        for point in new_points:
            painter.drawPoint(point[0], point[1])
        if self.point_set is None:
            self.point_set = set(points)
        else:
            # add new points to set
            self.point_set.update(points)
        painter.end()
        self.setPixmap(pixmap)
        self.parentWidget().update()
