#!/usr/bin/env python3

from PyQt5.QtGui import QPainter, QColor
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from Components.extra import Direction

Directions = Direction()


class MazeWidget(QtWidgets.QWidget):
    def __init__(self, input_maze, parent=None):
        super().__init__()
        self.map_editor = parent
        self.setMouseTracking(True)

        self.maze = input_maze
        self.width = self.maze.width * self.maze.scale + 3
        self.height = self.maze.height * self.maze.scale + 10

        self.prevPoint = 0, 0
        self.firstPos = True

        self.draw_instantly = True
        self.count = 0
        self.path = []

        self.wall = False
        self.direction = None

        self.start = False
        self.finish = False
        self.portals = False
        self.portal1 = None

    def mouseMoveEvent(self, event):
        try:
            x = event.x() // self.maze.scale if event.x() > 0 else None
            y = event.y() // self.maze.scale if event.y() > 0 else None

            if x and y:
                if event.buttons() == Qt.NoButton:
                    self.firstPos = True
                elif event.buttons() == Qt.LeftButton:
                    self.left_click(x, y)
                elif event.buttons() == Qt.RightButton:
                    self.right_click(x, y)
        except IndexError:
            pass

        self.update()

    def mousePressEvent(self, event):
        try:
            x = event.x() // self.maze.scale
            y = event.y() // self.maze.scale

            if event.button() == Qt.LeftButton:
                self.left_click(x, y)
            elif event.button() == Qt.RightButton:
                self.right_click(x, y)
        except IndexError:
            pass
        self.update()

    def left_click(self, x, y):
        if self.start:
            self.add_start(x, y)
        elif self.finish:
            self.add_finish(x, y)
        elif self.portals:
            self.add_portals(x, y, True)
        elif self.wall:
            self.add_one_way_wall(x, y, self.direction)
        elif self.firstPos:
            self.maze[x][y] = self.maze.WALL
            self.prevPoint = x, y
            self.firstPos = False
        else:
            self.create_line(self.prevPoint, (x, y))
            self.prevPoint = x, y

    def right_click(self, x, y):
        if (x, y) == self.maze.start:
            self.maze.start = None

        for finish in self.maze.finishes:
            if (x, y) == finish:
                self.maze.finishes.remove(finish)

        if self.portal1:
            self.add_portals(x, y, False)
        else:
            for portal_pair in self.maze.portals:
                if (x, y) in portal_pair:
                    self.maze.portals.remove(portal_pair)
                    self.map_editor.portals_button.setEnabled(True)
                    break

        if self.maze.one_way_walls:
            for wall in self.maze.one_way_walls:
                if (x, y) == (wall[0], wall[1]):
                    self.maze.one_way_walls.remove(wall)

        self.maze[x][y] = self.maze.EMPTY
        self.firstPos = True

    def add_start(self, x, y):
        self.maze[x][y] = self.maze.EMPTY
        self.maze.start = x, y
        self.start = False

    def add_finish(self, x, y):
        self.maze[x][y] = self.maze.EMPTY
        self.maze.finishes.append((x, y))
        self.finish = False

    def add_portals(self, x, y, first):
        if first:
            self.maze[x][y] = self.maze.EMPTY
            self.portal1 = x, y
        else:
            self.maze.portals.append([(x, y), self.portal1])
            self.portals = False
            self.portal1 = None

    def add_one_way_wall(self, x, y, direction):
        self.maze[x][y] = self.maze.EMPTY
        self.maze.one_way_walls.append((x, y, direction))
        self.wall = False

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        self.draw_maze(qp)
        self.draw_path(qp)
        self.draw_portals(qp)
        self.draw_start_and_finish(qp)
        self.draw_one_way_walls(qp)

        qp.end()

    def draw_maze(self, drawer):
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                if self.maze[x][y] == self.maze.WALL:
                    drawer.setPen(Qt.white)
                    drawer.setBrush(Qt.black)
                    drawer.drawRect(x * self.maze.scale,
                                    y * self.maze.scale,
                                    self.maze.scale,
                                    self.maze.scale)
                elif self.maze[x][y] == self.maze.EMPTY:
                    drawer.setPen(QColor(200, 200, 200))
                    drawer.setBrush(Qt.white)
                    drawer.drawRect(x * self.maze.scale,
                                    y * self.maze.scale,
                                    self.maze.scale,
                                    self.maze.scale)

    def draw_start_and_finish(self, drawer):
        if self.maze.start:
            drawer.setPen(Qt.white)
            drawer.setBrush(Qt.green)
            drawer.drawRect(self.maze.start[0] * self.maze.scale,
                            self.maze.start[1] * self.maze.scale,
                            self.maze.scale,
                            self.maze.scale)
        if self.maze.finishes:
            drawer.setPen(Qt.white)
            drawer.setBrush(Qt.blue)
            for finish in self.maze.finishes:
                drawer.drawRect(finish[0] * self.maze.scale,
                                finish[1] * self.maze.scale,
                                self.maze.scale,
                                self.maze.scale)

    def draw_portals(self, drawer):
        colors = [QColor(0, 255, 255), QColor(255, 128, 0),
                  QColor(255, 0, 128), QColor(0, 102, 0),
                  QColor(0, 0, 102), QColor(153, 204, 255)]
        drawer.setPen(Qt.black)
        if self.portal1:
            drawer.setBrush(colors[len(self.maze.portals)])
            drawer.drawRect(self.portal1[0] * self.maze.scale,
                            self.portal1[1] * self.maze.scale,
                            self.maze.scale,
                            self.maze.scale)
        for i in range(len(self.maze.portals)):
            drawer.setBrush(colors[i])
            for portal in self.maze.portals[i]:
                drawer.drawRect(portal[0] * self.maze.scale,
                                portal[1] * self.maze.scale,
                                self.maze.scale,
                                self.maze.scale)

    def draw_one_way_walls(self, drawer):
        for wall in self.maze.one_way_walls:
            if wall[2] == Directions.up:
                self.draw_partial(drawer, wall, 0, 0, 1, 2, 0,
                                  self.maze.scale // 2, 1, 2)
            elif wall[2] == Directions.right:
                self.draw_partial(drawer, wall, self.maze.scale // 2, 0,
                                  2, 1, 0, 0, 2, 1)
            elif wall[2] == Directions.down:
                self.draw_partial(drawer, wall, 0, self.maze.scale // 2, 1,
                                  2, 0, 0, 1, 2)
            elif wall[2] == Directions.left:
                self.draw_partial(drawer, wall, 0, 0, 2, 1,
                                  self.maze.scale // 2, 0, 2, 1)

    def draw_partial(self, drawer, wall, bx, by, bs1, bs2, wx, wy, ws1, ws2):
        drawer.setPen(Qt.white)
        drawer.setBrush(Qt.black)
        drawer.drawRect(wall[0] * self.maze.scale + bx,
                        wall[1] * self.maze.scale + by,
                        self.maze.scale // bs1,
                        self.maze.scale // bs2)
        drawer.setPen(Qt.black)
        drawer.setBrush(Qt.white)
        drawer.drawRect(wall[0] * self.maze.scale + wx,
                        wall[1] * self.maze.scale + wy,
                        self.maze.scale // ws1,
                        self.maze.scale // ws2)

    def draw_path(self, drawer):
        if self.path:
            if self.draw_instantly:
                for point in self.path:
                    if self.maze.is_wall(point[0], point[1]):
                        self.set_color(drawer, Qt.red)
                    else:
                        self.set_color(drawer, Qt.yellow)
                    drawer.drawRect(point[0] * self.maze.scale,
                                    point[1] * self.maze.scale,
                                    self.maze.scale,
                                    self.maze.scale)
            else:
                for i in range(self.count):
                    if self.maze.is_wall(self.path[i][0], self.path[i][1]):
                        self.set_color(drawer, Qt.red)
                    else:
                        self.set_color(drawer, Qt.yellow)
                    drawer.drawRect(self.path[i][0] * self.maze.scale,
                                    self.path[i][1] * self.maze.scale,
                                    self.maze.scale,
                                    self.maze.scale)
                self.count += 1
                if self.count > len(self.path) - 1:
                    self.count = len(self.path) - 1
            self.update()

    @staticmethod
    def set_color(drawer, color):
        drawer.setPen(Qt.black)
        drawer.setBrush(color)

    def create_line(self, prev, curr):
        if prev == curr:
            return
        line = []
        alpha = max(abs(prev[0] - curr[0]), abs(prev[1] - curr[1]))
        for i in range(alpha + 1):
            delta = i / alpha
            x = round(delta * (curr[0] - prev[0]) + prev[0])
            y = round(delta * (curr[1] - prev[1]) + prev[1])
            line.append((x, y))
        for point in line:
            self.maze[point[0]][point[1]] = self.maze.WALL
