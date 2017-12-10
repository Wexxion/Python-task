from PyQt5.QtCore import pyqtSignal, QObject


class Connection(QObject):
    hints_signal = pyqtSignal()
