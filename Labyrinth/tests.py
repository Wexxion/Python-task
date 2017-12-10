import unittest

from Components.maze import Maze
from Components.solver import solve_maze
from Components.extra import Direction


straight_maze = 'Tests/test_straight.txt'
no_bombs_maze = 'Tests/test_wall_no_bombs.txt'
wall_maze = 'Tests/test_wall.txt'
Directions = Direction()


class TestMazeSolver(unittest.TestCase):
    def test_maze_straight_line(self):
        text_file = Maze.open_map(straight_maze)
        lb = Maze(None, text_file)
        path = solve_maze(lb, 0)
        path.pop(0)
        self.assertEqual(len(path), 38)

    def test_maze_wall_no_bombs(self):
        text_file = Maze.open_map(no_bombs_maze)
        lb = Maze(None, text_file)
        path = solve_maze(lb, 0)
        self.assertEqual(None, path)

    def test_maze_wall(self):
        text_file = Maze.open_map(wall_maze)
        lb = Maze(None, text_file)
        path = solve_maze(lb, 0)
        path.pop(0)
        self.assertEqual(len(path), 38)

    def test_2_finishes(self):
        text_file = Maze.open_map(wall_maze)
        lb = Maze(None, text_file)
        lb.finishes = [(1, 1), (38, 1)]

        lb.start = (20, 1)
        path = solve_maze(lb, 0)
        path.pop(0)
        self.assertEqual(path[-1], (38, 1))  # second finish is closer

        lb.start = (15, 1)
        path = solve_maze(lb, 0)
        path.pop(0)
        self.assertEqual(path[-1], (1, 1))  # first finish is closer

    def test_portals(self):
        text_file = Maze.open_map(wall_maze)
        lb = Maze(None, text_file)
        lb.portals = [[(4, 1), (34, 1)]]
        lb.bombs = 0
        path = solve_maze(lb, 0)
        path.pop(0)
        self.assertEqual(len(path), 7)

    def test_file_save(self):
        text_file = Maze.open_map(straight_maze)
        lb = Maze(None, text_file)
        lb.save_map('Tests/saved_straight_maze.txt')
        new_text_file = Maze.open_map('Tests/saved_straight_maze.txt')
        self.assertEqual(text_file, new_text_file)

    def test_maze_params(self):
        lb = Maze((25, 25, 25))
        self.assertEqual(lb.width, 27)  # 25+2 because I create frame
        self.assertEqual(lb.height, 27)
        self.assertEqual(lb.scale, 25)

    def test_incorrect_maze_params(self):
        text_file = Maze.open_map(straight_maze)
        lb = Maze(None, text_file)
        lb.start = None
        lb.finishes = [None]
        lb.bombs = -1
        self.assertRaises(ValueError, lambda: solve_maze(lb, 0))

    def test_alpha(self):
        text_file = Maze.open_map('Tests/test_alpha.txt')
        lb = Maze(None, text_file)
        path = solve_maze(lb, 0)  # ALPHA = 0
        bombs_used = path.pop(0)
        self.assertEqual(bombs_used, lb.bombs)
        self.assertEqual(len(path), 38)  # Used all bombs, shorter path
        path = solve_maze(lb, 100)  # ALPHA = 100
        bombs_used = path.pop(0)
        self.assertEqual(bombs_used, 0)  # 0 bombs used, longest path
        self.assertEqual(len(path), 44)

    def test_simple_map(self):
        text_file = Maze.open_map('Tests/simple_test.txt')
        lb = Maze(None, text_file)
        path = solve_maze(lb, 0)
        bombs_used = path.pop(0)
        self.assertEqual(bombs_used, 1)
        self.assertEqual(len(path), 9)

    def test_one_way_walls(self):
        text_file = Maze.open_map(wall_maze)
        lb = Maze(None, text_file)
        #  instead of wall we have one-way wall
        lb[5][1] = lb.EMPTY
        lb.one_way_walls.append((5, 1, Directions.right))
        path = solve_maze(lb, 0)
        bombs_used = path.pop(0)
        self.assertEqual(bombs_used, 1)  # we have wall, but don't use bombs
        self.assertEqual(len(path), 38)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
