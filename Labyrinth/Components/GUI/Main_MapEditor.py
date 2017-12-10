#!/usr/bin/env python3

import sys
from Components.maze import Maze
from Components.GUI.MazeWidget import MazeWidget
from Components.GUI.ParamsWindow import ParamsWindow
from Components.GUI.SolverWindow import SolverWindow
from Components.extra import Direction
from PyQt5 import QtWidgets

Directions = Direction()


class MapEditor(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MapEditor, self).__init__(parent)

        self.params_dialog = ParamsWindow(parent=self)
        self.params_dialog.setModal(True)
        self.params_dialog.accepted.connect(self.create_maze_widget)
        self.params_dialog.rejected.connect(self.close)
        self.params_dialog.show()

        self.solver = SolverWindow(parent=self)

        self.add_start_button = QtWidgets.QPushButton("Add Start", self)
        self.add_finish_button = QtWidgets.QPushButton("Add Finish", self)
        self.portals_button = QtWidgets.QPushButton("Add Portals", self)
        self.one_way_menu = QtWidgets.QMenuBar(self)
        self.continue_button = QtWidgets.QPushButton("Continue", self)
        self.save_button = QtWidgets.QPushButton("Save Map", self)
        self.close_button = QtWidgets.QPushButton("Exit", self)
        self.solve_button = QtWidgets.QPushButton('Solve', self)

        self.create_menu()

        # self.add_start_button.setFixedWidth(60)
        # self.add_finish_button.setFixedWidth(60)

        self.add_start_button.clicked.connect(self.add_start)
        self.add_finish_button.clicked.connect(self.add_finish)
        self.portals_button.clicked.connect(self.add_portals)
        self.continue_button.clicked.connect(self.continue_editing)
        self.save_button.clicked.connect(self.save_maze)
        self.close_button.clicked.connect(self.close)
        self.solve_button.clicked.connect(self.prepare_for_solving)

        self.messages = QtWidgets.QLineEdit()
        self.messages.setReadOnly(True)
        self.messages.setText("Hello, i'm ready to start =]")
        self.hints = QtWidgets.QLabel("Hints: ")
        self.hints.setFixedSize(25, 25)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(5)
        top_layout.addWidget(self.hints)
        top_layout.addWidget(self.messages)
        top_layout.addWidget(self.add_start_button)
        top_layout.addWidget(self.add_finish_button)
        top_layout.addWidget(self.portals_button)
        top_layout.addWidget(self.one_way_menu)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setSpacing(5)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.solve_button)
        bottom_layout.addWidget(self.continue_button)
        bottom_layout.addWidget(self.close_button)

        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(8)
        self.layout.addLayout(top_layout, 0, 0)
        self.layout.addLayout(bottom_layout, 2, 0)

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)
        self.setWindowTitle("MazeEditor")

    def create_maze_widget(self):
        if self.params_dialog.file:
            maze = Maze(None, self.params_dialog.file)
        else:
            maze = Maze(self.params_dialog.settings)
        self.mazeWidget = MazeWidget(maze, self)
        self.layout.addWidget(self.mazeWidget, 1, 0)

        self.update_window()

    def create_menu(self):
        up_wall = QtWidgets.QAction('Up', self)
        right_wall = QtWidgets.QAction('Right', self)
        down_wall = QtWidgets.QAction('Down', self)
        left_wall = QtWidgets.QAction('Left', self)
        up_wall.triggered.connect(lambda: self.add_wall(Directions.up))
        right_wall.triggered.connect(lambda: self.add_wall(Directions.right))
        down_wall.triggered.connect(lambda: self.add_wall(Directions.down))
        left_wall.triggered.connect(lambda: self.add_wall(Directions.left))

        wall_menu = self.one_way_menu.addMenu('One-Way Wall')
        wall_menu.addAction(up_wall)
        wall_menu.addAction(right_wall)
        wall_menu.addAction(down_wall)
        wall_menu.addAction(left_wall)

        self.one_way_menu.setMaximumSize(92, 21)

    def update_window(self):
        msg_width = round(self.mazeWidget.width * 0.43)
        self.messages.setFixedSize(msg_width, 25)
        width = self.mazeWidget.width + 20
        height = self.mazeWidget.height + 80
        self.setFixedSize(width, height)
        self.move(QtWidgets.QApplication.desktop()
                  .screen().rect().center() - self.rect().center())
        self.show()

    def save_maze(self):
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save File", '../../Resources/new_maze.txt',
                "Text files(*.txt)")[0]
            self.mazeWidget.maze.save_map(filename)
            self.messages.setText("Maze saved")
        except Exception as e:
            self.messages.setText("Maze saving Exception: " + str(e))

    def prepare_for_solving(self):
        self.solver.solve_button.setEnabled(True)
        self.solver.full_button.setEnabled(True)
        self.mazeWidget.draw_instantly = True
        self.solver.progress.setValue(0)
        self.solver.value = 0
        self.solver.show()
        self.continue_editing()

    def add_start(self):
        self.mazeWidget.start = True
        self.messages.setText('Click point to create Start')

    def add_finish(self):
        self.mazeWidget.finish = True
        self.messages.setText('Click point to create Finish,'
                              'Several finishes are allowed')

    def add_portals(self):
        if len(self.mazeWidget.maze.portals) == 6:
            self.portals_button.setEnabled(False)
            return
        self.mazeWidget.portals = True
        self.messages.setText('Left click point to create Portal1, '
                              'Right click point to create Portal2')

    def add_wall(self, direction):
        self.mazeWidget.wall = True
        self.mazeWidget.direction = direction
        self.messages.setText('Click point to create One-Way wall')

    def draw_path(self):
        self.solver.hide()
        self.mazeWidget.path = self.solver.thread.queue.get()
        if isinstance(self.mazeWidget.path, str):
            QtWidgets.QMessageBox.critical(
                self, 'Solver Error', self.mazeWidget.path,
                QtWidgets.QMessageBox.Ok)
            self.mazeWidget.path = None
        elif not self.mazeWidget.path:
            self.messages.setText("Can't find path with this number of bombs:"
                                  " {}".format(self.mazeWidget.maze.bombs))
        else:
            used_bombs = self.mazeWidget.path.pop(0)
            bombs = self.mazeWidget.maze.bombs
            length = len(self.mazeWidget.path)
            self.messages.setText('Path length: {}, bombs allowed: {},'
                                  ' bombs used: {}'
                                  .format(length, bombs, used_bombs))
        self.solver.solve_button.setEnabled(True)

    def continue_editing(self):
        self.mazeWidget.path = []
        self.mazeWidget.count = 0


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MapEditor()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
