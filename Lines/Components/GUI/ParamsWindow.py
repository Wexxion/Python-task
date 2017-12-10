#!/usr/bin/env python3

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from Components.GUI.ColorsDialog import ColorsDialog
from Components.Field import Field


class ParamsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ParamsWindow, self).__init__(parent)

        self.game_window = parent
        self.colors_dialog = ColorsDialog(self)
        self.settings = None

        self.f_width = QtWidgets.QLineEdit("9")
        self.f_height = QtWidgets.QLineEdit("9")
        self.next_colors = QtWidgets.QLineEdit("3")
        self.start_balls = QtWidgets.QLineEdit("3")
        self.ok_button = QtWidgets.QPushButton("Start", self)
        self.colors_button = QtWidgets.QPushButton('Choose Colors', self)
        self.slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider.setValue(100)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(8)
        layout.addWidget(QtWidgets.QLabel("Field width: "), 0, 0, )
        layout.addWidget(self.f_width, 0, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Field height: "), 1, 0, )
        layout.addWidget(self.f_height, 1, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Colors to spawn: "), 2, 0)
        layout.addWidget(self.next_colors, 2, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Start balls: "), 3, 0)
        layout.addWidget(self.start_balls, 3, 1, 1, 2)
        layout.addWidget(
            QtWidgets.QLabel("                       Negative Difficulty"),
            4, 0, 1, 3)
        layout.addWidget(QtWidgets.QLabel("        -100"), 5, 0)
        layout.addWidget(self.slider, 5, 1)
        layout.addWidget(QtWidgets.QLabel("      0    "), 5, 2)
        layout.addWidget(self.colors_button, 6, 0, 1, 3)
        layout.addWidget(self.ok_button, 7, 0, 1, 3)

        self.ok_button.clicked.connect(self.save_params)
        self.colors_button.clicked.connect(self.choose_colors)
        self.rejected.connect(self.game_window.close)

        self.setLayout(layout)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())
        self.setWindowTitle("Game Params")

    def choose_colors(self):
        self.colors_dialog.raise_()
        self.colors_dialog.show()

    def save_params(self):
        colors = self.colors_dialog.colors_widget.colors
        width, height = int(self.f_width.text()), int(self.f_height.text())
        next_colors = int(self.next_colors.text())
        start_balls = int(self.start_balls.text())
        difficulty = self.slider.value()
        if not Field.MIN_NEXT <= next_colors <= Field.MAX_NEXT:
            QtWidgets.QMessageBox.critical(
                self, 'Next colors Error',
                '{} <= Colors to spawn <= {}'.format(Field.MIN_NEXT,
                                                     Field.MAX_NEXT),
                QtWidgets.QMessageBox.Ok)
        elif width < 4:
            QtWidgets.QMessageBox.critical(
                self, 'Field Size Error', 'Minimal width: 4',
                QtWidgets.QMessageBox.Ok)
        elif height < 4:
            QtWidgets.QMessageBox.critical(
                self, 'Field Size Error', 'Minimal height: 4',
                QtWidgets.QMessageBox.Ok)
        elif start_balls > width * height - 2:
            QtWidgets.QMessageBox.critical(
                self, 'Start balls Error',
                '{} is too much'.format(start_balls),
                QtWidgets.QMessageBox.Ok)
        else:
            self.settings = (
                (width, height), next_colors, start_balls, difficulty, colors)
            self.accepted.emit()
            self.hide()
