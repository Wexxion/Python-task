#!/usr/bin/env python3

from PyQt5.QtGui import QPainter, QColor
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize
from Components.Field import Field
from Components.GUI.SaveScoresDialog import SaveScoresDialog


class LinesWidget(QtWidgets.QWidget):
    def __init__(self, size, next_colors, start_balls, difficulty, colors,
                 parent=None):
        super(LinesWidget, self).__init__(parent)
        self.gameWindow = parent
        self.scale = 20
        self.score_saved = False

        self.field = Field(size, next_colors, start_balls, difficulty, colors)
        self.field.generate_colors()

        self.blocking = False
        self.firstPos = None
        self.autoFillBackground()

        self.resize_widget()

    def resize_widget(self):
        size = QSize(self.field.width * self.scale + 1,
                     self.field.height * self.scale + 1)
        self.setFixedSize(size)

        self.resize(size)

    def open_save_scores_dialog(self, cheat):
        save = SaveScoresDialog((self.field.width, self.field.height),
                                self.field.scores, self)
        if cheat:
            save.cheat_score()
        save.show()

    def mousePressEvent(self, event):
        try:
            x = event.x() // self.scale
            y = event.y() // self.scale
            if event.button() == Qt.LeftButton:
                if self.blocking:
                    self.field.add_blocked_cell(x, y)
                else:
                    self.left_click((x, y))
            elif event.button() == Qt.RightButton and self.blocking:
                    self.field.remove_blocked_cell(x, y)
            else:
                self.firstPos = None

            if self.field.is_full() and not self.score_saved:
                self.score_saved = True
                self.open_save_scores_dialog(False)
        except IndexError:
            pass

        self.update()

    def left_click(self, point):
        if not self.firstPos and self.field[point[0]][point[1]]:
            self.firstPos = point
        elif point and self.firstPos:
            if self.field.check_movement(self.firstPos, point):
                self.field.move(*self.firstPos, *point)
                if not self.field.check_all_lines(*point):
                    self.field.spawn_colors()
                    self.field.generate_colors()
                self.gameWindow.connection.hints_signal.emit()
                self.gameWindow.lcd.display(self.field.scores)
                self.firstPos = None
        else:
            self.firstPos = None

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        self.draw_field(qp)
        if self.firstPos:
            self.draw_selected_point(qp)

        qp.end()

    def draw_field(self, drawer):
        drawer.setPen(Qt.black)
        drawer.setBrush(Qt.white)
        drawer.drawRect(0, 0, self.width(), self.height())

        for x in range(self.field.width):
            for y in range(self.field.height):
                self.draw_grid(drawer, x, y)
                if self.field[x][y] == self.field.BLOCKED:
                    self.draw_blocked_cell(drawer, x, y)
                elif self.field[x][y]:
                    self.draw_ball(drawer, x, y, self.field[x][y])

    def draw_grid(self, drawer, x, y):
        drawer.setPen(Qt.black)
        drawer.setBrush(Qt.gray)
        drawer.drawRect(x * self.scale, y * self.scale, self.scale, self.scale)

    def draw_ball(self, drawer, x, y, color):
        drawer.setBrush(color)
        drawer.drawEllipse(x * self.scale, y * self.scale,
                           self.scale, self.scale)

    def draw_blocked_cell(self, drawer, x, y):
        drawer.setPen(Qt.gray)
        drawer.setBrush(Qt.black)
        drawer.drawRect(x * self.scale, y * self.scale, self.scale, self.scale)

    def draw_selected_point(self, drawer):
        pen = QPainter.pen(drawer)
        pen.setWidth(3.5)
        pen.setBrush(Qt.red)
        pen.setCapStyle(Qt.RoundCap)
        drawer.setPen(pen)
        drawer.setBrush(Qt.transparent)
        drawer.drawRect(self.firstPos[0] * self.scale,
                        self.firstPos[1] * self.scale,
                        self.scale, self.scale)


class HintsWidget(QtWidgets.QWidget):
    def __init__(self, scale, to_spawn, parent=None):
        super(HintsWidget, self).__init__(parent)

        self.enabled = False
        self.scale = scale
        self.to_spawn = to_spawn
        self.next_colors = []
        self.resize(self.to_spawn * self.scale + 1, self.scale + 1)

    def resize_widget(self):
        size = QSize(self.to_spawn * self.scale + 1, self.scale + 1)
        self.setFixedSize(size)
        self.resize(size)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        qp.setPen(Qt.black)
        for x in range(self.to_spawn):
            qp.setBrush(Qt.gray)
            qp.drawRect(x * self.scale, 0, self.scale, self.scale)
            if self.enabled and len(self.next_colors) > x:
                qp.setBrush(self.next_colors[x])
                qp.drawEllipse(x * self.scale, 0, self.scale, self.scale)

        qp.end()
