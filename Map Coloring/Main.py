import argparse
from Components import painter
from MapEditor import editor

editor_arg = "editor"
console_arg = "console"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', default="console",
                        type=str, choices=['editor', 'console'],
                        help='choose mode', required=True)
    parser.add_argument('-f', default="MapEditor/maps/map.txt", type=str,
                        help='file with map for coloring')
    args = parser.parse_args()

    check_args(args)


def check_args(args):
    if args.m == editor_arg:
        editor.main()
    if args.m == console_arg:
        painter.main(args.f)

if __name__ == "__main__":
    parse_args()
