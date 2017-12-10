import sys
import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtMultimedia import QSound

from Components.GUI.Extra import Connection
from Components.GUI.LinesWidget import LinesWidget, HintsWidget
from Components.GUI.ParamsWindow import ParamsWindow
from Components.Scores.ScoresWidget import ScoresDialog


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(GameWindow, self).__init__(parent)
        self.params = ParamsWindow(self)
        self.params.accepted.connect(self.create_lines_widget)
        self.params.show()

        self.connection = Connection()
        self.connection.hints_signal.connect(self.update_hint)

        self.best_score = QtWidgets.QPushButton('Scores', self)

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setDigitCount(4)

        sound_file = filename = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "Sound.wav"))
        self.player = QSound(sound_file, self)

        self.statusBar()
        self.menu_bar = self.menuBar()

        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(8)
        self.layout.addWidget(self.lcd, 0, 1)

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)
        self.setWindowTitle("Lines")
        self.setStyleSheet("background-color: khaki")

    def create_lines_widget(self):
        next_colors = self.params.settings[1]
        self.linesWidget = LinesWidget(*self.params.settings, self)

        self.scores = ScoresDialog(
            (self.params.settings[0][0], self.params.settings[0][1]), self)
        self.scores.scoresWindow.get_scores()
        text = self.scores.scoresWindow.players[0][1] \
            if self.scores.scoresWindow.players else '0'
        self.best_score.setText('Best Score: {}'.format(text))
        self.best_score.clicked.connect(self.scores.show)

        self.hint = HintsWidget(20, next_colors, self)
        self.connection.hints_signal.emit()

        self.layout.addWidget(self.linesWidget, 1, 0, 1, 4)
        self.layout.addWidget(self.hint, 0, 0)
        self.layout.addWidget(self.best_score, 0, 2)

        self.resize(QSize(640, 640))
        self.create_menu()

        self.update_window()
        self.resize(QSize(650, 650))

    def update_window(self):
        self.norm_size = self.linesWidget.width() + 100, \
                         self.linesWidget.height() + 100
        self.setMinimumSize(*self.norm_size)
        self.move(QtWidgets.QApplication.desktop()
                  .screen().rect().center() - self.rect().center())
        self.show()

    def resizeEvent(self, event):
        if self.linesWidget:
            param1 = min(event.size().height(), event.size().width())
            param2 = min(self.linesWidget.field.height - 1,
                         self.linesWidget.field.width - 1)
            scale = (param1 - 150 - self.linesWidget.scale) // param2
            self.linesWidget.scale = scale
            self.hint.scale = scale
            self.linesWidget.resize_widget()
            self.hint.resize_widget()
            self.resize(event.size())

    def create_menu(self):
        self.blocker = QtWidgets.QAction('Turn ON Block cells', self)
        hint = QtWidgets.QAction('Show Hint', self)
        scores = QtWidgets.QAction('Show Scores', self)
        self.sound_action = QtWidgets.QAction('Play Music', self)
        scores_cheat = QtWidgets.QAction('Score cheat', self)

        self.blocker.triggered.connect(self.set_blocking_mode)
        hint.triggered.connect(self.switch_hints)
        scores.triggered.connect(self.scores.show)
        self.sound_action.triggered.connect(self.play_music)
        scores_cheat.triggered.connect(
            lambda: self.linesWidget.open_save_scores_dialog(True))

        menu = self.menu_bar.addMenu('Menu')
        menu.addAction(self.blocker)
        menu.addAction(hint)
        menu.addAction(scores)
        menu.addAction(self.sound_action)
        asd = menu.addMenu('Cheats')
        asd.addAction(scores_cheat)

    def set_blocking_mode(self):
        if self.blocker.text() == 'Turn ON Block cells':
            self.linesWidget.blocking = True
            self.blocker.setText('Turn OFF Block cells')
        else:
            self.linesWidget.blocking = False
            self.blocker.setText('Turn ON Block cells')


    def play_music(self):
        if self.player.isFinished():
            self.sound_action.setText('Stop Music')
            self.player.play()
        else:
            self.sound_action.setText('Play Music')
            self.player.stop()

    def update_hint(self):
        self.hint.next_colors = self.linesWidget.field.colors_to_spawn
        self.hint.update()

    def switch_hints(self):
        if self.hint.enabled and \
                        self.linesWidget.field.scores_coefficient != 1:
            self.linesWidget.field.scores_coefficient = 2
            self.hint.enabled = False
        else:
            self.linesWidget.field.scores_coefficient = 1
            self.hint.enabled = True

        self.hint.update()

    def closeEvent(self, *args, **kwargs):
        sys.exit(0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = GameWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
