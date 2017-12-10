#!/usr/bin/env python3

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from multiprocessing import Queue
from Components.GUI.SolverThread import SolverThread


class SolverWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SolverWindow, self).__init__(parent)

        self.editor = parent
        self.queue = Queue()
        self.thread = SolverThread(self.queue, self)
        self.thread.finished.connect(self.editor.draw_path)

        self.bombs = QtWidgets.QLineEdit("0")
        self.solve_button = QtWidgets.QPushButton("DO IT!!!", self)
        self.full_button = QtWidgets.QPushButton("Yep", self)
        self.slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.progress = QtWidgets.QProgressBar(self)
        self.value = 0
        self.signal = ProgressSignal()
        self.signal.tick.connect(self.update_value)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)
        layout.addWidget(QtWidgets.QLabel("Bombs count: "), 1, 0)
        layout.addWidget(self.bombs, 1, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Draw path \nstep by step?"), 2, 0)
        layout.addWidget(self.full_button, 2, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("     bombs"), 3, 0)
        layout.addWidget(self.slider, 3, 1)
        layout.addWidget(QtWidgets.QLabel("      length    "), 3, 2)
        layout.addWidget(self.progress, 4, 0, 1, 3)
        layout.addWidget(self.solve_button, 5, 0, 1, 3)

        self.solve_button.clicked.connect(self.solve_maze)
        self.full_button.clicked.connect(self.set_draw_params)

        self.setLayout(layout)
        self.setFixedSize(350, 200)
        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())
        self.setWindowTitle("Maze Solver")

    def solve_maze(self):
        self.solve_button.setEnabled(False)
        maze = self.editor.mazeWidget.maze
        maze.bombs = int(self.bombs.text())
        alpha = self.slider.value()
        self.progress.setRange(0, (maze.bombs + 1) * maze.width * maze.height)
        self.progress.setValue(0)
        if self.check_solver_params():
            self.close()
            return
        self.thread.queue.put(maze)
        self.thread.queue.put(alpha)
        self.thread.start()

    def check_solver_params(self):
        error = ''
        if not isinstance(self.editor.mazeWidget.maze.bombs, int):
            error += 'Bombs value must be int, yours: {}\n'.format(
                self.editor.mazeWidget.maze.bombs)
        elif self.editor.mazeWidget.maze.bombs < 0:
            error += 'Bombs value must be >= 0, yours: {}\n'.format(
                self.editor.mazeWidget.maze.bombs)
        if not self.editor.mazeWidget.maze.start:
            error += "Can't solve maze without start =[\n"
        if not self.editor.mazeWidget.maze.finishes:
            error += "Can't solve maze without at least one finish =[\n"
        if error:
            QtWidgets.QMessageBox.critical(
                self, 'Solver params Error', error[:-1],
                QtWidgets.QMessageBox.Ok)
            return True

    def set_draw_params(self):
        self.editor.mazeWidget.draw_instantly = False
        self.full_button.setEnabled(False)

    def update_value(self):
        self.value += 1
        self.progress.setValue(self.value)


class ProgressSignal(QObject):
    tick = pyqtSignal()
