from PyQt5 import QtWidgets
import os


class SaveScoresDialog(QtWidgets.QDialog):
    def __init__(self, size, score, parent=None):
        super(SaveScoresDialog, self).__init__(parent)

        self.linesWidget = parent
        self.filename = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..',
            'Scores/Rec{}x{}.txt'.format(*size)))

        self.name = QtWidgets.QLineEdit('', self)
        self.score = score
        self.new_score = None

        self.save_button = QtWidgets.QPushButton('Save', self)
        self.save_button.clicked.connect(self.save)

        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(5)
        self.layout.addWidget(QtWidgets.QLabel("Name: "), 0, 0)
        self.layout.addWidget(self.name, 0, 1)
        self.layout.addWidget(self.save_button, 1, 0, 1, 2)

        self.setLayout(self.layout)

        self.move(QtWidgets.QApplication.desktop().screen().rect().center() -
                  self.rect().center())
        self.setWindowTitle("Save Scores")

    def cheat_score(self):
        self.new_score = QtWidgets.QLineEdit('', self)
        self.layout.addWidget(QtWidgets.QLabel("Score: "), 1, 0)
        self.layout.addWidget(self.new_score, 1, 1)
        self.layout.removeWidget(self.save_button)
        self.layout.addWidget(self.save_button, 2, 0, 1, 2)

    def save(self):
        with open(self.filename, 'r+') as file:
            if not file.read():
                file.write('Name : Score')
            file.write('\n{} : {}'.format(self.name.text(), int(
                self.new_score.text()) if self.new_score else self.score))
        self.hide()
