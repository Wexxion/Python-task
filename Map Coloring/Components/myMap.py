#!/usr/bin/env python3

import copy


class WorldMap:
    def __init__(self, params, map_file=None):
        wall = 0
        empty = -1
        if map_file:
            self.width = len(map_file) - 1
            self.height = len(map_file[0])
            self.scale = int(map_file[len(map_file) - 1])
            self.original_map = [[empty] * self.height for i in
                                 range(self.width)]
            for x in range(self.width):
                for y in range(self.height):
                    if map_file[x][y] == '#':
                        self.original_map[x][y] = wall
        elif params:
            self.width = params[0] + 2
            self.height = params[1] + 2
            self.scale = params[2]
            self.original_map = [[empty] * self.height for i in
                                 range(self.width)]
            for x in range(self.width):
                for y in range(self.height):
                    if x == 0 or y == 0 or x == self.width - 1 \
                            or y == self.height - 1:
                        self.original_map[x][y] = wall
        else:
            raise ValueError('Incorrect params')

        self.neighbors = {}
        self.countries = 0
        self.common_area = {}
        self.regions = []
        self.processed_map = copy.deepcopy(self.original_map)

    def __getitem__(self, index1, index2=None):
        if index2:
            return self.original_map[index1][index2]
        else:
            return self.original_map[index1]

    def __len__(self):
        return len(self.original_map)

    def __str__(self):
        res = []
        for x in range(self.width):
            for y in range(self.height):
                if self.processed_map[x][y] < 0:
                    res.extend(str(self.processed_map[x][y]) + ' ')
                elif self.processed_map[x][y] > 9:
                    res.extend(str(self.processed_map[x][y]) + ' ')
                else:
                    res.extend(str(self.processed_map[x][y]) + '  ')
            res.extend('\n')
        return ''.join(res)

    @staticmethod
    def open_map(filepath):
        with open(filepath, 'r') as file:
            text = file.read().split('\n')
        return text

    def save_map(self, filename, scale):
        with open(filename, 'w') as file:
            for x in range(self.width):
                for y in range(self.height):
                    if self[x][y] == 0:
                        file.write('#')
                    elif self[x][y] == -1:
                        file.write(' ')
                file.write('\n')
            file.write(str(scale))

    def update_map(self):
        self.processed_map = copy.deepcopy(self.original_map)

    def find_common_regions(self):
        if len(self.regions) < 2:
            return

        common_dict = {}
        region_dict = {}
        for region in self.regions:
            for x, y in region:
                region_dict[x, y] = self.processed_map[x][y]
        for i in range(len(self.regions)):
            for j in range(len(self.regions)):
                if i < j:
                    for x1, y1 in self.regions[i]:
                        for x2, y2 in self.regions[j]:
                            if region_dict[x1, y1] == region_dict[x2, y2]:
                                if (x1, y1) not in common_dict:
                                    common_dict[x1, y1] = {j + 1, i + 1}
                                else:
                                    for ter in common_dict:
                                        if (x1, y1) == ter:
                                            common_dict[ter].add(i + 1)
                                            common_dict[ter].add(j + 1)
        for key in common_dict:
            common_dict[key] = list(common_dict[key])
        keys = sorted(common_dict, key=lambda k: len(common_dict[k]),
                      reverse=False)

        for key in keys:
            self.bfs(key, None, num_list=common_dict[key])

    def find_regions(self):
        if not self.regions:
            return

        count = 0
        for part in self.regions:
            count += 1
            for x, y in part:
                self.bfs((x, y), count)

    def find_countries(self):
        count = len(self.regions) + 1
        for x in range(self.width):
            for y in range(self.height):
                if self.processed_map[x][y] != 0 and self.processed_map[x][y] \
                        == -1:
                    self.bfs((x, y), count)
                    count += 1
        self.countries = count - 1

    def find_neighbors(self):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.processed_map[x][y] == 0:
                    curr_neighbors = set()
                    for i, j in neighbors:
                        if self.processed_map[x + i][y + j] != 0:
                            curr_neighbors.add(
                                self.processed_map[x + i][y + j])
                            if self.processed_map[x + i][y + j] \
                                    not in self.neighbors:
                                self.neighbors[
                                    self.processed_map[x + i][y + j]] = []
                    if len(curr_neighbors) > 1:
                        self.add_neighbor(curr_neighbors)

    def add_neighbor(self, curr_neighbors):
        for neighbor1 in curr_neighbors:
            for neighbor2 in curr_neighbors:
                if neighbor1 != neighbor2:
                    if neighbor2 not in self.neighbors[neighbor1]:
                        self.neighbors[neighbor1].append(neighbor2)

    def bfs(self, start, number, num_list=None):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        finished = False
        curr_num = 0
        visited = {start: True}
        wave = 0
        traceback = [[]]
        traceback[0].append(start)
        self.processed_map[start[0]][start[1]] = num_list[
            curr_num] if num_list else number
        while not finished:
            traceback.append([])
            for current in traceback[wave]:
                for i, j in neighbors:
                    neighbor = current[0] + i, current[1] + j
                    if 0 <= neighbor[0] < self.width:
                        if 0 <= neighbor[1] < self.height:
                            if visited.get(neighbor):
                                continue
                            if self.processed_map[neighbor[0]][neighbor[1]]\
                                    != 0:
                                if num_list:
                                    self.processed_map[neighbor[0]][
                                        neighbor[1]] = num_list[curr_num]
                                    curr_num += 1
                                    if curr_num == len(num_list):
                                        curr_num = 0
                                else:
                                    self.processed_map[neighbor[0]][
                                        neighbor[1]] = number
                                visited[neighbor] = True
                                traceback[wave + 1].append(neighbor)
            wave += 1
            if traceback[wave - 1] == traceback[wave]:
                finished = True

    def prepare_for_painting(self):
        if self.original_map:
            self.update_map()
            self.find_regions()
            self.find_countries()
            self.find_common_regions()
            self.find_neighbors()
