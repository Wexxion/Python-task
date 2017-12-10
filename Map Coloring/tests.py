#!/usr/bin/env python3

from Components import painter
from Components.myMap import WorldMap
import unittest


file_map_4 = 'Tests/map_4.txt'
file_map_6 = 'Tests/map_6.txt'
file_map_9 = 'Tests/map_9.txt'
file_one_country_map = 'Tests/one_country_map.txt'
file_no_countries_map = 'Tests/no_countries_map.txt'


def prepare_for_algs(my_map):
    my_map.find_countries()
    my_map.find_neighbors()
    used_colors_optimal = max(
        painter.graph_coloring_optimal(my_map.neighbors).values())
    used_colors_appromeximate = max(
        painter.graph_coloring_approximate(my_map.neighbors).values())
    return used_colors_optimal, used_colors_appromeximate


class TestWorldMap_map_4(unittest.TestCase):
    def setUp(self):
        self.map_4 = WorldMap.open_map(file_map_4)

    def test_find_countries(self):
        my_map = WorldMap(None, map_file=self.map_4)
        my_map.find_countries()
        self.assertEqual(4, my_map.countries)

    def test_find_neighbors(self):
        my_map = WorldMap(None, map_file=self.map_4)
        my_map.find_countries()
        my_map.find_neighbors()
        self.assertEqual({1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3]},
                         my_map.neighbors)


class TestWorldMap_map_6(unittest.TestCase):
    def setUp(self):
        self.map_6 = WorldMap.open_map(file_map_6)

    def test_find_countries(self):
        my_map = WorldMap(None, map_file=self.map_6)
        my_map.find_countries()
        self.assertEqual(6, my_map.countries)

    def test_find_neighbors(self):
        my_map = WorldMap(None, map_file=self.map_6)
        my_map.find_countries()
        my_map.find_neighbors()

        self.assertEqual({1: [2, 4], 2: [1, 3, 5], 3: [2, 6], 4: [1, 5],
                             5: [2, 4, 6], 6: [3, 5]}, my_map.neighbors)


class TestWorldMap_one_country_map(unittest.TestCase):
    def setUp(self):
        self.one_country_map = WorldMap.open_map(file_one_country_map)

    def test_find_countries(self):
        my_map = WorldMap(None, map_file=self.one_country_map)
        my_map.find_countries()
        self.assertEqual(1, my_map.countries)

    def test_find_neighbors(self):
        my_map = WorldMap(None, map_file=self.one_country_map)
        my_map.find_countries()
        my_map.find_neighbors()

        self.assertEqual({}, my_map.neighbors)


class TestWorldMap_no_countries_map(unittest.TestCase):
    def setUp(self):
        self.no_countries_map = WorldMap.open_map(file_no_countries_map)

    def test_find_countries(self):
        my_map = WorldMap(None, map_file=self.no_countries_map)
        my_map.find_countries()
        self.assertEqual(0, my_map.countries)

    def test_find_neighbors(self):
        my_map = WorldMap(None, map_file=self.no_countries_map)
        my_map.find_countries()
        my_map.find_neighbors()

        self.assertEqual({}, my_map.neighbors)


class TestWorldMap(unittest.TestCase):
    def test_index_and_len(self):
        self.one_country_map = WorldMap.open_map(file_one_country_map)
        my_map = WorldMap(None, map_file=self.one_country_map)
        self.assertEqual(my_map[1][1], -1)
        self.assertEqual(len(my_map), 9)

    def test_prepare_for_painting_and_regions(self):
        file = WorldMap.open_map(file_map_9)
        my_map = WorldMap(None, map_file=file)
        my_map.regions = [[(4, 4), (10, 4)], [(3, 4), (7, 4)]]
        my_map.prepare_for_painting()
        self.assertEqual(my_map.neighbors,
                         {1: [2, 5, 7], 2: [3, 1, 5], 3: [2, 4, 5], 4: [3, 6],
                          5: [3, 1, 6, 2, 7], 6: [4, 5, 8], 7: [5, 1, 8],
                          8: [6, 7]})
        self.assertEqual(my_map.countries, 8)
        used_colors_optimal = max(
            painter.graph_coloring_optimal(my_map.neighbors).values())
        used_colors_appromeximate = max(
            painter.graph_coloring_approximate(my_map.neighbors).values())
        self.assertEqual(3, used_colors_optimal)
        self.assertEqual(used_colors_optimal <= used_colors_appromeximate,
                         True)


class TestPainter(unittest.TestCase):
    def test_algorithms_on_map_4(self):
        my_map = WorldMap.open_map(file_map_4)
        self.assert_algorithms(my_map, 2)

    def test_algorithms_on_map_6(self):
        my_map = WorldMap.open_map(file_map_6)
        self.assert_algorithms(my_map, 2)

    def test_algorithms_on_one_country_map(self):
        my_map = WorldMap.open_map(file_one_country_map)
        self.assert_algorithms(my_map, 1)

    def test_algorithms_on_no_countries_map(self):
        my_map = WorldMap.open_map(file_no_countries_map)
        self.assert_algorithms(my_map, 1)

    def assert_algorithms(self, map_file, expected_result):
        my_map = WorldMap(None, map_file=map_file)
        used_colors_optimal, used_colors_appromeximate = prepare_for_algs(
            my_map)

        self.assertEqual(expected_result, used_colors_optimal)
        self.assertEqual(used_colors_optimal <= used_colors_appromeximate,
                         True)

    def test_algorithms_om_graphs(self):
        # Petersen graph (see picture in Tests folder,
        # https://en.wikipedia.org/wiki/Petersen_graph)
        graph = {1: [2, 5, 7], 2: [1, 3, 8], 3: [2, 4, 9], 4: [3, 5, 10],
                 5: [1, 4, 6], 6: [5, 8, 9], 7: [1, 9, 10], 8: [2, 6, 10],
                 9: [3, 7, 6], 10: [4, 7, 8]}
        used_colors_optimal = max(
            painter.graph_coloring_optimal(graph).values())
        used_colors_appromeximate = max(
            painter.graph_coloring_approximate(graph).values())
        self.assertEqual(3, used_colors_optimal)
        self.assertEqual(used_colors_optimal <= used_colors_appromeximate,
                         True)

        # Complete graph, n = 4(see picture in Tests folder)
        graph = {1: [2, 3, 4], 2: [1, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3]}
        used_colors_optimal = max(
            painter.graph_coloring_optimal(graph).values())
        used_colors_appromeximate = max(
            painter.graph_coloring_approximate(graph).values())
        self.assertEqual(4, used_colors_optimal)
        self.assertEqual(used_colors_optimal <= used_colors_appromeximate,
                         True)

        # graph(see picture in Tests folder)
        graph = {1: [2], 2: [1, 3, 4, 5, 6], 3: [2, 7], 4: [2], 5: [2, 6],
                 6: [2, 5, 7], 7: [3, 6]}
        used_colors_optimal = max(
            painter.graph_coloring_optimal(graph).values())
        used_colors_appromeximate = max(
            painter.graph_coloring_approximate(graph).values())
        self.assertEqual(3, used_colors_optimal)
        self.assertEqual(used_colors_optimal <= used_colors_appromeximate,
                         True)

    def test_paint_map(self):
        file = WorldMap.open_map(file_map_9)
        my_map = WorldMap(None, map_file=file)

        optimal = painter.paint_map(my_map, True)
        optimal_algo = painter.graph_coloring_optimal(my_map.neighbors)
        self.assertEqual(optimal, optimal_algo)

        appromeximate = painter.paint_map(my_map, False)
        appromeximate_algo = painter.graph_coloring_approximate(
            my_map.neighbors)
        self.assertEqual(appromeximate, appromeximate_algo)

    def test_main(self):
        self.assertRaises(FileNotFoundError, painter.main, 'nothing')


def main():
    unittest.main()


if __name__ == "__main__":
    main()
