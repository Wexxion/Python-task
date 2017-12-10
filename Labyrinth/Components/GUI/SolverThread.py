#!/usr/bin/env python3

from PyQt5.QtCore import QThread
from Components.solver import solve_maze


class SolverThread(QThread):
    def __init__(self, queue, parent=None):
        QThread.__init__(self)
        self.queue = queue
        self.solver_window = parent

    def __del__(self):
        self.wait()

    def run(self):
        try:
            maze = self.queue.get()
            alpha = self.queue.get()
            res = solve_maze(maze, alpha, self.solver_window.signal)
            self.queue.put(res)
        except Exception as e:
            self.queue.put('Solver exception: {}'.format(e))
