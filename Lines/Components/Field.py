import queue as py_queue
from random import randint, choice as rand_choice
import math


class Field:
    MIN_NEXT = 3
    MAX_NEXT = 5
    BLOCKED = -1

    def __init__(self, size, next_colors, start_balls, difficulty, colors):
        self.width, self.height = size
        self.game_colors = colors
        self.spawn_count = next_colors
        self.difficulty = difficulty
        self.map = [[None] * self.height for i in range(self.width)]

        self.del_width = round((math.ceil(
            self.width / 2) if (
        self.width % 2 == 1) else self.width / 2 + 1) - 2)
        self.del_height = round((math.ceil(
            self.height / 2) if (
        self.height % 2 == 1) else self.height / 2 + 1) - 2)
        self.del_diagonal = round(min(self.del_height, self.del_width))

        self.empty_cells = self.get_cells()
        self.colors_to_spawn = []
        self.spawn_positions = []

        self.generate_colors(start_balls)
        self.spawn_colors()

        self.scores = 0
        self.scores_coefficient = 2

    def __getitem__(self, index1, index2=None):
        return self.map[index1][index2] if index2 else self.map[index1]

    def __len__(self):
        return len(self.map)

    def add_blocked_cell(self, x, y):
        self[x][y] = self.BLOCKED
        if (x, y) in self.empty_cells:
            self.empty_cells.remove((x, y))

    def remove_blocked_cell(self, x, y):
        self[x][y] = None
        if (x, y) not in self.empty_cells:
            self.empty_cells.append((x, y))

    def calculate_scores(self, deleted):
        if deleted == min(
                [self.del_height, self.del_width, self.del_diagonal]):
            self.scores += round(deleted * self.scores_coefficient) + 1
        elif deleted > min(
                [self.del_height, self.del_width, self.del_diagonal]):
            self.scores += round(deleted * (deleted - self.del_width) *
                                 self.scores_coefficient) + 1

    def move(self, x1, y1, x2, y2):
        color = self[x1][y1]
        self[x1][y1] = None
        self.empty_cells.append((x1, y1))

        self[x2][y2] = color
        self.empty_cells.remove((x2, y2))

    def check_movement(self, start, finish):
        if start == finish:
            return None
        res = []
        queue = py_queue.Queue()
        queue.put(start)
        visited = {start: True}
        traceback = {start: None}
        while not queue.empty():
            current = queue.get()
            for neighbor in self.get_neighbors(*current):
                if visited.get(neighbor):
                    continue
                queue.put(neighbor)
                visited[neighbor] = True
                traceback[neighbor] = current

        current = finish

        try:
            while current != start:
                res.append(current)
                current = traceback[current]
        except KeyError:
            return None
        res.append(start)

        return res[::-1]

    def get_neighbors(self, x1, y1):
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            x, y = x1 + dx, y1 + dy
            if self.is_in_map(x, y) and not self[x][y] and (
                        self[x][y] != self.BLOCKED):
                yield (x, y)

    def generate_colors(self, num=None):
        if num:
            to_generate = num
        else:
            to_generate = len(self.empty_cells) if len(
                self.empty_cells) < self.spawn_count else self.spawn_count
        for i in range(to_generate):
            color = rand_choice(self.game_colors)
            self.colors_to_spawn.append(color)

    def spawn_colors(self):
        chance = randint(0, 101)

        if chance > self.difficulty:
            self.analyse_field()
            for i in range(len(self.colors_to_spawn)):
                if self.spawn_positions:
                    x, y, color = self.spawn_positions.pop()
                    if (x, y) in self.empty_cells:
                        self.empty_cells.remove((x, y))
                    self[x][y] = color
                    self.check_all_lines(x, y)
                else:
                    self.random_spawn()
        else:
            for i in range(len(self.colors_to_spawn)):
                self.random_spawn()

    def random_spawn(self):
        color = self.colors_to_spawn.pop()
        x, y = rand_choice(self.empty_cells)
        self.empty_cells.remove((x, y))
        self[x][y] = color
        self.check_all_lines(x, y)

    def analyse_field(self):
        founded = []
        balls_positions = self.get_cells(False)
        for cur_x, cur_y in balls_positions:
            founded.extend(self.get_same_balls_in_col(cur_x, cur_y))
            founded.extend(self.get_same_balls_in_row(cur_x, cur_y))
        self.spawn_positions = founded[-self.spawn_count:]

    def get_same_balls_in_row(self, cur_x, cur_y):
        res = []
        x_balls = [(cur_x, cur_y)]
        for dx in [-1, 1]:
            x_balls.extend(self.horiz_and_vert(cur_x, cur_y, dx, 0))
        if len(x_balls) >= 2:
            x_balls = sorted(x_balls, key=lambda k: k[0])
            lft, rgt = x_balls[0], x_balls[-1]

            if lft[0] != 0 and not self[lft[0] - 1][lft[1]]:
                res.append((lft[0] - 1, lft[1], self[lft[0]][lft[1]]))
                self.colors_to_spawn.pop(0)
                self.colors_to_spawn.append(self[lft[0]][lft[1]])

            elif rgt[0] != self.width - 1 and not self[rgt[0] + 1][rgt[1]]:
                res.append((rgt[0] + 1, rgt[1], self[rgt[0]][rgt[1]]))
                self.colors_to_spawn.pop(0)
                self.colors_to_spawn.append(self[rgt[0]][rgt[1]])
        return res

    def get_same_balls_in_col(self, cur_x, cur_y):
        res = []
        y_balls = [(cur_x, cur_y)]
        for dy in [1, -1]:
            y_balls.extend(self.horiz_and_vert(cur_x, cur_y, 0, dy))
        if len(y_balls) >= 2:
            y_balls = sorted(y_balls, key=lambda k: k[1])
            top, btm = y_balls[0], y_balls[-1]

            if top[1] != 0 and not self[top[0]][top[1] - 1]:
                res.append((top[0], top[1] - 1, self[top[0]][top[1]]))
                self.colors_to_spawn.pop(0)
                self.colors_to_spawn.append(self[top[0]][top[1]])

            elif btm[1] != self.height - 1 and not self[btm[0]][
                        btm[1] + 1]:
                res.append((btm[0], btm[1] + 1, self[btm[0]][btm[1]]))
                self.colors_to_spawn.pop(0)
                self.colors_to_spawn.append(self[btm[0]][btm[1]])
        return res

    def check_all_lines(self, x, y):
        to_delete = []

        to_delete.extend(self.to_del_horiz_and_vert(x, y))
        to_delete.extend(self.to_del_diagonal(x, y))

        if to_delete:
            to_delete.append((x, y))
            length = len(to_delete)
            to_delete = list(set(to_delete))

            for i, j in to_delete:
                self[i][j] = None
                self.empty_cells.append((i, j))

            self.calculate_scores(length)

            return True
        else:
            return False

    def to_del_horiz_and_vert(self, x, y):
        res = []
        to_delete_dx = []
        to_delete_dy = []

        for dx in [1, -1]:
            to_delete_dx.extend(self.horiz_and_vert(x, y, dx, 0))
        if len(to_delete_dx) > self.del_width:
            res.extend(to_delete_dx)

        for dy in [1, -1]:
            to_delete_dy.extend(self.horiz_and_vert(x, y, 0, dy))
        if len(to_delete_dy) > self.del_height:
            res.extend(to_delete_dy)

        return res

    def to_del_diagonal(self, x, y):
        res = []

        to_delete_diagonal = self.diagonal(x, y, [(1, 1), (-1, -1)])
        if len(to_delete_diagonal) > self.del_diagonal:
            res.extend(to_delete_diagonal)

        to_delete_diagonal = self.diagonal(x, y, [(1, -1), (-1, 1)])
        if len(to_delete_diagonal) > self.del_diagonal:
            res.extend(to_delete_diagonal)

        return res

    def horiz_and_vert(self, x, y, step_x, step_y):
        if self[x][y] and self[x][y] != self.BLOCKED:
            res = []
            dx, dy = step_x, step_y
            while self.is_in_map(x + dx, y + dy) \
                    and self[x + dx][y + dy] == self[x][y]:
                res.append((x + dx, y + dy))
                dx += step_x
                dy += step_y
            return res
        else:
            return None

    def diagonal(self, x, y, diagonal):
        if self[x][y] and self[x][y] != self.BLOCKED:
            res = []
            max_length = self.height * self.width
            for i in range(1, max_length):
                for temp_dx, temp_dy in diagonal:
                    dx, dy = temp_dx * i, temp_dy * i
                    if self.is_in_map(x + dx, y + dy) \
                            and self[x + dx][y + dy] == self[x][y]:
                        res.append((x + dx, y + dy))
            return res
        else:
            return None

    def is_in_map(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cells(self, empty=True):
        res = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] != self.BLOCKED:
                    if empty and not self[x][y]:
                        res.append((x, y))
                    elif not empty and self[x][y]:
                        res.append((x, y))
        return res

    def clear_field(self):
        for x in range(self.width):
            for y in range(self.height):
                self[x][y] = None

    def is_full(self):
        return not self.empty_cells
