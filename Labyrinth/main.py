import argparse

from Components.GUI import Main_MapEditor
from Components import solver

gui_arg = 'gui'
console_arg = "console"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', default="console",
                        type=str, choices=['gui', 'console'],
                        help='choose mode', required=True)
    parser.add_argument('-f', default="Resources/maze.txt", type=str,
                        help='file with labyrinth')
    parser.add_argument('-b', default=0, type=int,
                        help='bombs count')
    parser.add_argument('-a', default=0, type=int,
                        help='alpha [0..100] parameter to choose path')
    args = parser.parse_args()

    check_args(args)


def check_args(args):
    if args.m == gui_arg:
        Main_MapEditor.main()
    if args.m == console_arg:
        console_solver(args.f, args.a, args.b)


def console_solver(filename, alpha, bombs):
    import os
    from Components.maze import Maze
    from Components.solver import solve_maze

    filepath = os.path.abspath(os.path.join(
        os.path.dirname(__file__), filename))
    file = Maze.open_map(filepath)
    maze = Maze(None, file)
    maze.bombs = bombs
    res = solve_maze(maze, alpha, None)
    if not res:
        print("Can't find path with this number of bombs: {}".format(bombs))
    else:
        used_bombs = res.pop(0)
        for point in res:
            if maze.is_wall(point[0], point[1]):
                maze[point[0]][point[1]] = '*'
            else:
                maze[point[0]][point[1]] = 'x'

        for finish in maze.finishes:
            maze[finish[0]][finish[1]] = 'F'
        maze[maze.start[0]][maze.start[1]] = 'S'

        for portals_pair in maze.portals:
            for portal in portals_pair:
                maze[portal[0]][portal[1]] = '@'

        for wall in maze.one_way_walls:
            maze[wall[0]][wall[1]] = '{'

        print(maze)
        print('Bombs: {}, Used: {}'.format(maze.bombs, used_bombs))
        print('Length: ' + str(len(res)))
        print('[x] - Path, [*] - Bomb used, [@] - Portals, [{] - One-Way Wall,'
              ' [S] - Start, [F] - Finish')


if __name__ == "__main__":
    parse_args()
