import unittest
from Components.Field import Field

SIZE = 9, 9
NEXT_COLORS = 3
START_BALLS = 3
DIFFICULTY = 100  # no help
COLORS = [1, 2, 3, 4, 5, 6, 7]


class TestField(unittest.TestCase):
    def test_amount_to_delete_9x9(self):
        field = Field((9, 9), NEXT_COLORS, START_BALLS, DIFFICULTY, COLORS)
        self.assertEqual(field.del_width, 3)
        self.assertEqual(field.del_height, 3)
        self.assertEqual(field.del_diagonal, 3)

    def test_amount_to_delete_9x16(self):
        field = Field((9, 16), NEXT_COLORS, START_BALLS, DIFFICULTY, COLORS)
        self.assertEqual(field.del_width, 3)
        self.assertEqual(field.del_height, 7)
        self.assertEqual(field.del_diagonal, 3)

    def test_generate_colors(self):
        field = Field((4, 4), NEXT_COLORS, START_BALLS, DIFFICULTY, COLORS)
        empty1 = field.get_cells()
        self.assertEqual(len(empty1), field.width * field.height - NEXT_COLORS)
        field.generate_colors()
        self.assertEqual(len(field.colors_to_spawn), 3)
        field.spawn_colors()
        empty2 = field.get_cells()
        self.assertEqual(len(empty1), len(empty2) + NEXT_COLORS)

    def test_blocked_cells(self):
        field = Field((4, 4), NEXT_COLORS, START_BALLS, DIFFICULTY, COLORS)
        field.add_blocked_cell(0, 0)
        field.add_blocked_cell(1, 0)
        self.assertEqual(len(field.empty_cells),
                         field.width * field.height - NEXT_COLORS - 2)
        field.remove_blocked_cell(0, 0)
        field.remove_blocked_cell(1, 0)
        self.assertEqual(len(field.empty_cells),
                         field.width * field.height - NEXT_COLORS)

    def test_movement(self):
        field = Field((4, 4), NEXT_COLORS, START_BALLS, DIFFICULTY, COLORS)
        field.clear_field()
        field[0][0] = 1
        field[3][3] = 2
        self.assertTrue(field.check_movement((3, 3), (1, 1)))  # empty way
        field.move(3, 3, 1, 1)
        field[0][1] = 2
        field[1][0] = 2
        self.assertFalse(field.check_movement((0, 0), (3, 3)))  # blocked way

    def test_check_all_lines(self):
        field = Field((4, 4), NEXT_COLORS, START_BALLS, DIFFICULTY, COLORS)
        field.clear_field()
        field[0][0] = 1
        field[1][1] = 1
        field[2][2] = 1
        field.check_all_lines(1, 1)  # we got 3 same -> delete them
        self.assertEqual(len(field.get_cells()), field.width * field.height)

    def test_negative_difficulty_column(self):
        difficulty = 0  # we help to spawn balls with same color
        field = Field((4, 4), NEXT_COLORS, START_BALLS, difficulty, COLORS)
        field.clear_field()
        field[0][0] = 1
        field[0][1] = 1
        field.empty_cells = field.get_cells()
        field.generate_colors()
        field.analyse_field()  # algo should spawn ball with color 1 in (0, 2)
        field.spawn_colors()
        self.assertEqual(field[0][2], 1)

    def test_negative_difficulty_row(self):
        difficulty = 0  # we help to spawn balls with same color
        field = Field((4, 4), NEXT_COLORS, START_BALLS, difficulty, COLORS)
        field.clear_field()
        field[0][0] = 3
        field[1][0] = 3
        field.empty_cells = field.get_cells()
        field.generate_colors()
        field.analyse_field()  # algo should spawn ball with color 1 in (2, 0)
        field.spawn_colors()
        self.assertEqual(field[2][0], 3)


if __name__ == '__main__':
    unittest.main()
