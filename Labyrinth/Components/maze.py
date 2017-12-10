import re
import sys
import json


class Maze:
    def __init__(self, params, data=None):
        self.width = None
        self.height = None
        self.map = []
        self.bombs = 0
        self.scale = None
        self.start = None
        self.finishes = []
        self.portals = []
        self.one_way_walls = []

        self.EMPTY = ' '
        self.WALL = '#'

        self.params_error = False

        if data:
            self.portals = data['Portals']
            self.one_way_walls = data['One-way walls']
            self.map = data['Maze']
            self.bombs = data['Bombs']
            self.start = data['Start']
            self.finishes = data['Finishes']
            self.scale = data['Scale']
            self.width = len(self.map)
            self.height = len(self.map[0])
            self.parse_data()
        elif params:
            self.width = params[0] + 2
            self.height = params[1] + 2
            self.scale = params[2]
            self.map = [[self.EMPTY] * self.height for i in range(self.width)]
            for x in range(self.width):
                for y in range(self.height):
                    if x == 0 or y == 0 or x == self.width - 1 \
                            or y == self.height - 1:
                        self.map[x][y] = self.WALL
        else:
            raise ValueError('Incorrect input')

    def __getitem__(self, index1, index2=None):
        if index2:
            return self.map[index1][index2]
        else:
            return self.map[index1]

    def __len__(self):
        return len(self.map)

    def __str__(self):
        res = []
        for y in range(self.height):
            for x in range(self.width):
                res.append(self.map[x][y])
            res.append('\n')
        return ''.join(res)

    def is_in_map(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def is_wall(self, x, y):
        return self.map[x][y] == self.WALL

    def is_portal(self, x, y):
        for portal_pair in self.portals:
            if (x, y) in portal_pair:
                return True
        return False

    def get_another_portal(self, x, y):
        for portal_pair in self.portals:
            if (x, y) in portal_pair:
                for portal in portal_pair:
                    if portal != (x, y):
                        return portal

    def save_map(self, filename):
        if self.bombs >= 0 and self.start and self.finishes and self.scale:
            data = {'Portals': self.portals,
                    'One-way walls': self.one_way_walls,
                    'Maze': self.map, 'Bombs': self.bombs, 'Start': self.start,
                    'Finishes': self.finishes, 'Scale': self.scale}
        else:
            raise ValueError('Not all params')
        with open(filename, 'w') as file:
            json.dump(data, file)

    @staticmethod
    def open_map(filename):
        try:
            with open(filename, 'r') as file:
                data = file.read()
                maze = json.loads(data)
        except ValueError:
            return None
        return maze

    def parse_data(self):
        one_way_walls = []
        for wall in self.one_way_walls:
            one_way_walls.append(tuple(wall))
        self.one_way_walls = one_way_walls

        finishes = []
        for finish in self.finishes:
            finishes.append(tuple(finish))
        self.finishes = finishes

        portals = []
        for portal_pair in self.portals:
            portals.append([])
            for portal in portal_pair:
                portals[-1].append(tuple(portal))
        self.portals = portals

        start = tuple(self.start)
        self.start = start
