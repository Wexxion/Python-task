from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtCore import Qt
import os


class ScoresDialog(QtWidgets.QDialog):
    def __init__(self, size, parent=None):
        super(ScoresDialog, self).__init__(parent)

        self.gameWindow = parent

        self.scoresWindow = ScoresWidget(size, self)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())
        self.setWindowTitle("Scores")

    def showEvent(self, event):
        self.scoresWindow.get_scores()


class ScoresWidget(QtWidgets.QWidget):
    def __init__(self, size, parent=None):
        super(ScoresWidget, self).__init__(parent)

        self.scoresDialog = parent
        self.size = size
        self.setFixedSize(300, self.scoresDialog.gameWindow.height() - 20)

        self.players = []

    def get_scores(self):
        self.players = []
        file = []
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                'Rec{}x{}.txt'.format(
                                                    *self.size)))
        try:
            with open(filename, 'r') as file:
                file = file.read().split('\n')[1:]
        except FileNotFoundError:
            with open(filename, 'w') as new_file:
                new_file.write('Name : Score')

        for line in file:
            information = line.split(':')
            name = information[0].strip()
            score = int(information[1].strip())
            self.players.append((name, score))

        self.players = sorted(self.players, key=lambda k: k[1],
                              reverse=True)
        self.players = self.players[:9]

    def paintEvent(self, e):
        drawer = QPainter()
        drawer.begin(self)

        pen = QPainter.pen(drawer)
        pen.setColor(Qt.black)
        pen.setWidth(10)
        pen.setCapStyle(Qt.RoundCap)
        drawer.setPen(pen)
        drawer.setBrush(QColor(255, 215, 0))
        drawer.drawRect(0, 0, 300, self.height())

        drawer.setPen(Qt.black)
        drawer.setFont(QFont('Arial', 25))
        drawer.drawText(10, 10, 280, 40, 5, 'High Scores:')

        for i in range(len(self.players)):
            drawer.setPen(Qt.red)
            drawer.setFont(QFont('Arial', 25))
            drawer.drawText(10, (i * 45) + 55, 280, 45, 5,
                            '{}) {} : {}'.format(i + 1, *self.players[i]))

        drawer.end()
