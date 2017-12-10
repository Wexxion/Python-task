#!/usr/bin/env python3

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

WHITE = Qt.white
RED = Qt.red
GREEN = Qt.green
BLUE = Qt.blue
YELLOW = Qt.yellow
CYAN = Qt.cyan
MAGENTA = Qt.magenta


class ColorsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ColorsDialog, self).__init__(parent)

        self.params = parent

        self.colors_widget = ColorsWidget(self)
        self.add_button = QtWidgets.QPushButton('Add Color', self)
        self.del_button = QtWidgets.QPushButton('Del Color', self)
        self.save_button = QtWidgets.QPushButton('Save', self)

        self.add_button.clicked.connect(self.add_color)
        self.del_button.clicked.connect(self.del_color)
        self.save_button.clicked.connect(self.save)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)

        layout.addWidget(self.colors_widget, 0, 0, 1, 2)
        layout.addWidget(self.add_button, 1, 0)
        layout.addWidget(self.del_button, 1, 1)
        layout.addWidget(self.save_button, 2, 0, 1, 2)

        self.setLayout(layout)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())
        self.setWindowTitle("Game Colors")

    def save(self):
        self.params.colors = self.colors_widget.colors
        self.hide()

    def add_color(self):
        new_color = QtWidgets.QColorDialog.getColor().getRgb()
        color = QColor(new_color[0], new_color[1], new_color[2])
        self.colors_widget.append_color(color)

    def del_color(self):
        self.colors_widget.delete_color()


class ColorsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ColorsWidget, self).__init__(parent)
        self.colorsDialog = parent

        self.current_color = None
        self.current_pos = None
        self.scale = 30

        self.colors = [WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]

        self.setFixedSize(400, 35)

    def append_color(self, color):
        self.colors.append(color)
        self.current_color = self.current_pos = None
        self.update()

    def delete_color(self):
        if self.current_color and self.current_pos:
            self.colors.remove(self.current_color)
            self.current_color = self.current_pos = None
            self.update()

    def mousePressEvent(self, event):
        try:
            x, y = event.x() // self.scale, event.y() // self.scale
            if event.button() == Qt.LeftButton:
                if y == 0 and x < len(self.colors):
                    self.current_color = self.colors[x]
                    self.current_pos = x, y
            else:
                self.current_color = self.current_pos = None

        except IndexError:
            pass

        self.update()

    def paintEvent(self, event):
        drawer = QPainter()
        drawer.begin(self)

        for x in range(len(self.colors)):
            drawer.setPen(Qt.black)
            drawer.setBrush(self.colors[x])
            drawer.drawRect(x * self.scale, 0, self.scale, self.scale)

        if self.current_pos:
            pen = QPainter.pen(drawer)
            pen.setWidth(6)
            pen.setBrush(Qt.black)
            pen.setCapStyle(Qt.RoundCap)
            drawer.setPen(pen)
            drawer.setBrush(Qt.transparent)
            drawer.drawRect(self.current_pos[0] * self.scale,
                            self.current_pos[1] * self.scale,
                            self.scale, self.scale)

        drawer.end()
