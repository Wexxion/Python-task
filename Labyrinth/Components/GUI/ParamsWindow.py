#!/usr/bin/env python3

import os
from PyQt5 import QtWidgets
from Components.maze import Maze


class ParamsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ParamsWindow, self).__init__(parent)

        self.file = None
        self._width = QtWidgets.QLineEdit("30")
        self._height = QtWidgets.QLineEdit("20")
        self._scale = QtWidgets.QLineEdit("20")
        self.open_button = QtWidgets.QPushButton("Open File", self)
        self.ok_button = QtWidgets.QPushButton("Open Editor", self)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)
        layout.addWidget(QtWidgets.QLabel("Map Width: "), 1, 0)
        layout.addWidget(self._width, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Map Height: "), 2, 0)
        layout.addWidget(self._height, 2, 1)
        layout.addWidget(QtWidgets.QLabel("Map Scale*: "), 3, 0)
        layout.addWidget(self._scale, 3, 1)
        layout.addWidget(self.ok_button, 4, 0)
        layout.addWidget(self.open_button, 4, 1)

        self.ok_button.clicked.connect(self.save_params)
        self.open_button.clicked.connect(self.open_map)

        self.setLayout(layout)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())
        self.setWindowTitle("Open dialog")

    def save_params(self):
        size = QtWidgets.QDesktopWidget().screenGeometry(-1)
        curr_scale = int(self._scale.text())
        curr_width = int(self._width.text())
        curr_height = int(self._height.text())
        if curr_width * curr_scale + 50 > size.width() \
                or curr_height * curr_scale + 150 > size.height():
            return
        else:
            self.settings = curr_width, curr_height, curr_scale
            self.accepted.emit()
            self.hide()

    def open_map(self):
        directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../..', 'Resources'))
        openfile = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", directory, "Text files(*.txt)")[0]
        if openfile:
            self.file = Maze.open_map(openfile)
            self.accepted.emit()
            self.hide()
