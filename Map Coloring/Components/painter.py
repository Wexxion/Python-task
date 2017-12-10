#!/usr/bin/env python3

from Components.myMap import WorldMap


def graph_coloring_approximate(graph):
    result = {0: 0}
    colors = [1]

    def coloring(node, color):
        for neighbor in graph[node]:
            color_of_neighbor = result.get(neighbor, None)
            if color_of_neighbor == color:
                return False
        return True

    def get_color(node):
        for color in colors:
            if coloring(node, color):
                return color
            else:
                color = colors[-1] + 1
                colors.append(color)

    if graph == {}:
        result[1] = 1
    else:
        for node in graph.keys():
            result[node] = get_color(node)
    return result


def graph_coloring_optimal(graph):
    result = {0: 0}
    colors = [1]

    def sort_edges(graph):
        sorted_keys = sorted(graph, key=lambda k: len(graph[k]), reverse=True)
        result = []
        for key in sorted_keys:
            result.append((key, len(graph[key])))
        return result

    def coloring():
        def remove_color():
            for color in colors:
                if color not in color_stack:
                    return color
            color = colors[-1] + 1
            colors.append(color)
            return color

        for key in sorted_edges:
            color_stack = []
            for key2 in graph[key[0]]:
                if key2 in result:
                    color_stack.append(result[key2])
            color = remove_color()
            result[key[0]] = color

    if graph == {}:
        result[1] = 1
    else:
        sorted_edges = sort_edges(graph)
        coloring()
    return result


def paint_map(my_map, optimal):
    my_map.prepare_for_painting()
    if optimal:
        return graph_coloring_optimal(my_map.neighbors)
    return graph_coloring_approximate(my_map.neighbors)


def main(filename):z
    import os
    filepath = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", filename))
    file = WorldMap.open_map(filepath)
    my_map = WorldMap(None, map_file=file)
    my_map.prepare_for_painting()
    print(my_map)
    print()
    print('Countries count:', my_map.countries)
    print('Optimal algorithm result:', paint_map(my_map, True))
    print('Approximate algorithm result:', paint_map(my_map, False))


if __name__ == "__main__":
    main("MapEditor/maps/map.txt")
