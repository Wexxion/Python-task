class Node:
    def __init__(self, x, y, bombs):
        self.x = x
        self.y = y
        self.bombs = bombs

    def __eq__(self, other):
        res = self.x == other.x \
              and self.y == other.y \
              and self.bombs == other.bombs
        return res

    def __hash__(self):
        return 1000000 * self.x + 10000 * self.y + self.bombs

    def __str__(self):
        return '{} {} {}'.format(self.x, self.y, self.bombs)


class Direction:
    def __init__(self):
        self.up = 0
        self.right = 1
        self.down = 2
        self.left = 3

    def get_direction(self, dx, dy):
        sum_d = abs(dx) + abs(dy)
        if sum_d != 2 and sum_d != 0:
            if dx == 1:
                return self.right
            if dx == -1:
                return self.left
            if dy == 1:
                return self.down
            if dy == -1:
                return self.up
        return None
