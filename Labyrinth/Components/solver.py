import queue as qu
from Components.extra import Node, Direction


NOT_FOUND = -1
Directions = Direction()


def solve_maze(maze, alpha, progress_signal=None):
    if not maze.finishes or not maze.start or maze.bombs < 0:
        raise ValueError('incorrect params(start, finish, bombs) !!!')
    res = []
    start = Node(maze.start[0], maze.start[1], maze.bombs)
    path_length = create_all_path_lengths(maze, start)
    queue = qu.Queue()
    queue.put(start)
    visited = {start: True}
    traceback = {start: -1}
    while not queue.empty():
        current = queue.get()
        for neighbor in get_neighbors(maze, current):
            if visited.get(neighbor):
                continue
            path_length[neighbor] = path_length[current] + 1
            queue.put(neighbor)
            visited[neighbor] = True
            traceback[neighbor] = current
            if progress_signal:
                progress_signal.tick.emit()

    for finish in all_possible_finish_nodes(maze):
        if path_length[finish] != NOT_FOUND:
            res.append([])
            current = finish
            while current != start:
                res[-1].append((current.x, current.y))
                current = traceback[current]
            res[-1].append(maze.start)
            res[-1].append(maze.bombs - finish.bombs)

    if not res:
        return None

    res.sort(key=len)
    beta = 100 // len(res)
    index = alpha // beta
    return res[index][::-1] if index < len(res) else res[-1][::-1]


def create_all_path_lengths(maze, start):
    path_length = {}
    for x in range(maze.width):
        for y in range(maze.height):
            for b in range(maze.bombs + 1):
                path_length[Node(x, y, b)] = NOT_FOUND
    path_length[start] = 0
    return path_length


def all_possible_finish_nodes(maze):
    for finish in maze.finishes:
        for bombs in range(0, maze.bombs + 1):
            yield Node(finish[0], finish[1], bombs)


def get_neighbors(maze, node):
    res = []
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for i, j in neighbors:
        x, y = node.x + i, node.y + j
        if maze.is_in_map(x, y):
            if maze.is_portal(x, y):
                res.append(Node(x, y, node.bombs))
                portal_x, portal_y = maze.get_another_portal(x, y)
                portal = Node(portal_x, portal_y, node.bombs)
                res.extend(get_neighbors(maze, portal))
            elif not maze.is_wall(x, y):
                res.append(Node(x, y, node.bombs))
            elif node.bombs != 0:
                res.append(Node(x, y, node.bombs - 1))
            if maze.one_way_walls:
                for wall in maze.one_way_walls:
                    if (x, y) == (wall[0], wall[1]):
                        if wall[2] == Directions.get_direction(i, j):
                            res.append(Node(x, y, node.bombs))
                        elif node.bombs != 0:
                            res.append(Node(x, y, node.bombs - 1))
    return res

