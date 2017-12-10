#!/usr/bin/env python3

import sys
import os
from Components.myMap import WorldMap
from Components.painter import paint_map
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets
from multiprocessing import Queue

WALL = 0
EMPTY = -1


class ParamsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ParamsWindow, self).__init__(parent)

        self.file = None
        self._width = QtWidgets.QLineEdit("70")
        self._height = QtWidgets.QLineEdit("70")
        self._scale = QtWidgets.QLineEdit("10")
        self.save_button = QtWidgets.QPushButton("Save", self)
        self.open_button = QtWidgets.QPushButton("Open", self)
        self.open_button.setFixedSize(38, 22)
        self.ok_button = QtWidgets.QPushButton("Open Editor", self)
        self.ok_button.setEnabled(False)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)
        layout.addWidget(QtWidgets.QLabel("Map Width: "), 1, 0)
        layout.addWidget(self._width, 1, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Map Height: "), 2, 0)
        layout.addWidget(self._height, 2, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Map Scale*: "), 3, 0)
        layout.addWidget(self._scale, 3, 1, 1, 2)
        layout.addWidget(self.ok_button, 4, 0)
        layout.addWidget(self.save_button, 4, 1)
        layout.addWidget(self.open_button, 4, 2)

        self.ok_button.clicked.connect(self.accept)
        self.save_button.clicked.connect(self.save_params)
        self.open_button.clicked.connect(self.open_map)
        self.open_button.clicked.connect(self.accept)

        self.setLayout(layout)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())

    def save_params(self):
        size = QtWidgets.QDesktopWidget().screenGeometry(-1)
        curr_scale = int(self._scale.text())
        curr_width = int(self._width.text())
        curr_height = int(self._height.text())
        if curr_width * curr_scale + 20 > size.width() \
                or curr_height * curr_scale + 150 > size.height():
            return
        else:
            self.ok_button.setEnabled(True)
            self.settings = curr_width, curr_height, curr_scale

    def open_map(self):
        directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'maps'))
        openfile = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", directory, "Text files(*.txt)")[0]
        self.file = WorldMap.open_map(openfile)
        self.ok_button.setEnabled(True)


class MapEditor(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MapEditor, self).__init__(parent)

        self.params_dialog = ParamsWindow(parent=self)
        self.params_dialog.setModal(True)
        self.params_dialog.accepted.connect(self.create_map_widget)
        self.params_dialog.rejected.connect(self.close)
        self.params_dialog.show()

        self.queue = Queue()
        self.thread = PaintThread(self.queue)
        self.thread.finished.connect(self.paint_map)

        self.save_button = QtWidgets.QPushButton("Save Map", self)
        self.paint_button = QtWidgets.QPushButton("Paint Map", self)
        self.add_button = QtWidgets.QPushButton("New Line", self)
        self.clear_button = QtWidgets.QPushButton("Clear Regions", self)
        self.region_button = QtWidgets.QPushButton("Add Region", self)
        self.close_button = QtWidgets.QPushButton("Exit", self)
        self.continue_button = QtWidgets.QPushButton("Continue", self)
        self.screenshot_button = QtWidgets.QPushButton("Screenshot", self)

        self.paint_button.setFixedSize(400, 25)

        self.save_button.clicked.connect(self.save_map)
        self.paint_button.clicked.connect(self.choose_painter)
        self.add_button.clicked.connect(self.add_line)
        self.clear_button.clicked.connect(self.clear_regions)
        self.region_button.clicked.connect(self.add_region)
        self.close_button.clicked.connect(self.close)
        self.continue_button.clicked.connect(self.continue_edit)
        self.screenshot_button.clicked.connect(self.save_picture)

        self.messages = QtWidgets.QLineEdit()
        self.messages.setReadOnly(True)
        self.messages.setText("Hello, i'm ready to start =] Left click"
                              " - draw line, Right - clear point")
        self.messages.setMaximumSize(450, 25)
        self.hints = QtWidgets.QLabel("Hints: ")
        self.hints.setFixedSize(25, 25)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(5)
        top_layout.addWidget(self.hints)
        top_layout.addWidget(self.messages)
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.region_button)
        top_layout.addWidget(self.clear_button)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setSpacing(5)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.screenshot_button)
        bottom_layout.addWidget(self.paint_button)
        bottom_layout.addWidget(self.continue_button)
        bottom_layout.addWidget(self.close_button)

        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(8)
        self.layout.addLayout(top_layout, 0, 0)
        self.layout.addLayout(bottom_layout, 3, 0)

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)
        self.setWindowTitle("MapEditor")

    def create_map_widget(self):
        try:
            if self.params_dialog.file:
                current_map = WorldMap(None, map_file=self.params_dialog.file)
            else:
                current_map = WorldMap(self.params_dialog.settings)

            self.mapWidget = MapWidget(current_map)
            self.layout.addWidget(self.mapWidget, 1, 0)

            self.update_window()
        except Exception as e:
            print(e)

    def update_window(self):
        width = self.mapWidget.width + 20
        height = self.mapWidget.height + 90
        self.setFixedSize(width, height)
        self.move(QtWidgets.QApplication.desktop()
                  .screen().rect().center() - self.rect().center())
        self.show()

    def save_map(self):
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save File", 'maps/map.txt', "Text files(*.txt)")[0]
            self.mapWidget.map.save_map(filename, self.mapWidget.map.scale)
            self.messages.setText("Map saved")
        except Exception as e:
            self.messages.setText("Map saving Exception: " + str(e))

    def save_picture(self):
        try:
            filename = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save Picture", 'screenshots/map.bmp', "Image(*.bmp)")[0]
            p = self.mapWidget.grab()
            p.save(filename, 'bmp')
            self.messages.setText("Screenshot saved")
        except Exception as e:
            self.messages.setText("Screenshot Exception: " + str(e))

    def choose_painter(self):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Question)

        optimal_button = QtWidgets.QPushButton("Optimal", self)
        approximate_button = QtWidgets.QPushButton("Approximate", self)

        self.msg.addButton(optimal_button, QtWidgets.QMessageBox.YesRole)
        self.msg.addButton(approximate_button, QtWidgets.QMessageBox.NoRole)

        self.msg.setWindowTitle("Question")
        self.msg.setText("Which algorithm painter should use?")
        self.msg.setDetailedText("Optimal returns better result "
                                 "than the approximate one")

        optimal_button.clicked.connect(lambda: self.prepare_map(True))
        approximate_button.clicked.connect(lambda: self.prepare_map(False))

        self.msg.exec_()

    def prepare_map(self, optimal):
        self.mapWidget.map.regions = self.mapWidget.regions
        self.thread.queue.put(self.mapWidget.map)
        self.thread.queue.put(optimal)
        self.thread.start()

    def paint_map(self):
        self.mapWidget.painting = True
        self.mapWidget.countries_colors = self.queue.get()
        self.mapWidget.map = self.queue.get()
        self.mapWidget.update()
        self.messages.setText('Map coloring completed. Used colors: ' +
                              str(max(
                                  self.mapWidget.countries_colors.values())))

    def continue_edit(self):
        self.mapWidget.painting = False
        self.mapWidget.firstPos = True
        self.mapWidget.countries_colors = {}
        self.mapWidget.update()
        self.messages.setText('You can continue editing')

    def add_line(self):
        self.messages.setText(
            "Choose first position and draw limited area using lines")
        self.mapWidget.firstPos = True
        self.mapWidget.clicking = False

    def add_region(self):
        self.mapWidget.clicking = True
        self.mapWidget.regions.append([])
        self.messages.setText(
            "Click limited area and choose regions. Click new line to stop.")

    def clear_regions(self):
        self.mapWidget.regions = [[]]
        self.messages.setText("Regions cleared")
        self.update()


class MapWidget(QtWidgets.QWidget):
    def __init__(self, input_map):
        super().__init__()

        self.map = input_map
        self.width = self.map.width * self.map.scale
        self.height = self.map.height * self.map.scale
        self.prevPoint = 0, 0
        self.firstPos = True
        self.painting = False
        self.clicking = False

        self.regions = []
        self.countries_colors = {}
        self.colors = [QColor(0, 0, 0), QColor(255, 0, 0),
                       QColor(0, 255, 0), QColor(0, 0, 255),
                       QColor(0, 255, 255), QColor(255, 255, 0),
                       QColor(255, 0, 255), QColor(128, 0, 128),
                       QColor(255, 128, 0), QColor(255, 0, 255),
                       QColor(128, 128, 128), QColor(128, 255, 0),
                       QColor(255, 255, 255)]

    def mousePressEvent(self, CurrQMouseEvent):
        x = CurrQMouseEvent.x() // self.map.scale
        y = CurrQMouseEvent.y() // self.map.scale

        if CurrQMouseEvent.button() == 1:
            if self.clicking:
                self.add_region(x, y)
            else:
                self.left_click(x, y)

        elif CurrQMouseEvent.button() == 2:
            if self.clicking:
                self.del_region(x, y)
            else:
                self.right_click(x, y)

        self.update()

    def left_click(self, x, y):
        if self.firstPos:
            self.map[x][y] = WALL
            self.prevPoint = x, y
            self.firstPos = False
        else:
            self.create_line(self.prevPoint, (x, y))
            self.prevPoint = x, y

    def right_click(self, x, y):
        self.map[x][y] = EMPTY
        self.firstPos = True

    def del_region(self, x, y):
        if self.regions:
            for i in range(len(self.regions)):
                if (x, y) in self.regions[i]:
                    self.regions[i].remove((x, y))

    def add_region(self, x, y):
        if (x, y) not in self.regions[-1] and not self.map[x][y] == WALL:
            self.regions[-1].append((x, y))

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_widget(qp)
        qp.end()

    def draw_widget(self, drawer):
        try:
            for x in range(self.map.width):
                for y in range(self.map.height):
                    if self.painting:
                        self.draw_painted_map(drawer, x, y)
                    elif self.map[x][y] == WALL:
                        drawer.setPen(QColor(255, 255, 255))
                        drawer.setBrush(QColor(0, 0, 0))
                        drawer.drawRect(x * self.map.scale, y * self.map.scale,
                                        self.map.scale, self.map.scale)
                    elif self.map[x][y] == EMPTY:
                        drawer.setPen(QColor(200, 200, 200))
                        drawer.setBrush(QColor(255, 255, 255))
                        drawer.drawRect(x * self.map.scale, y * self.map.scale,
                                        self.map.scale, self.map.scale)
            if self.regions:
                self.draw_multiple_countries(drawer)
        except Exception as e:
            print(e)

    def draw_painted_map(self, drawer, x, y):
        color = self.colors[
            self.countries_colors[self.map.processed_map[x][y]]]
        drawer.setPen(color)
        drawer.setBrush(color)
        drawer.drawRect(x * self.map.scale, y * self.map.scale, self.map.scale,
                        self.map.scale)

    def draw_multiple_countries(self, drawer):
        for region in range(len(self.regions)):
            for x, y in self.regions[region]:
                drawer.setPen(QColor(0, 0, 0))
                drawer.setBrush(self.colors[region + 1])
                drawer.drawRect(x * self.map.scale, y * self.map.scale,
                                self.map.scale, self.map.scale)

    def create_line(self, prevP, currP):
        if prevP == currP:
            return
        line = []
        alpha = max(abs(prevP[0] - currP[0]), abs(prevP[1] - currP[1]))
        for i in range(alpha + 1):
            delta = i / alpha
            x = round(delta * (currP[0] - prevP[0]) + prevP[0])
            y = round(delta * (currP[1] - prevP[1]) + prevP[1])
            line.append((x, y))
        for point in line:
            self.map[point[0]][point[1]] = WALL


class PaintThread(QThread):
    def __init__(self, queue):
        QThread.__init__(self)
        self.queue = queue

    def __del__(self):
        self.wait()

    def run(self):
        my_map = self.queue.get()
        optimal = self.queue.get()
        countries_colors = paint_map(my_map, optimal)
        self.queue.put(countries_colors)
        self.queue.put(my_map)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MapEditor()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
