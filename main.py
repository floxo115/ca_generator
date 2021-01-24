import argparse
import logging
import pathlib
import sys

import cairo
import numpy as np

WIDTH = 1
HEIGHT = 1

logging.basicConfig(level=logging.DEBUG)


class ArgumentException(Exception):
    pass


def get_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("rule", type=int, help="the rule to apply")
    argparser.add_argument("rows", type=int, help="the number of output rows")
    argparser.add_argument("--filename", help="file for the seed", type=str)

    args = argparser.parse_args()
    check_args(args)

    return args


def check_args(args: argparse.Namespace):
    if not (0 <= args.rule <= 255):
        raise ArgumentException("rule has to be between 0 and 255!")

    if args.rows < 1:
        raise ArgumentException("the height has to be > 0!")

    if args.filename and not pathlib.Path(args.filename).exists():
        raise ArgumentException("the input file does not exist!")


def check_seed_string(data: str):
    for el in data:
        if el not in ('1', '0'):
            raise AttributeError("only 1 and 0 allowed in seed")


def get_seed(filename: str) -> str:
    if filename is not None:
        with open(filename, 'r') as f:
            data = f.read()

    else:
        data = sys.stdin.readline()

    data = data.strip('\n')

    check_seed_string(data)

    return data


def calculate_array(arr, rule) -> np.ndarray:
    for n_line in range(1, arr.shape[0]):
        for n_cell in range(arr.shape[1]):
            num = arr[n_line - 1, (n_cell - 1) % arr.shape[1]] * 2 ** 2 + \
                  arr[n_line - 1, n_cell % arr.shape[1]] * 2 ** 1 \
                  + arr[n_line - 1, (n_cell + 1) % arr.shape[1]] * 2 ** 0

            arr[n_line, n_cell] = 1 if rule & 2 ** num else 0

    return arr


def create_and_draw_surface(arr) -> cairo.Surface:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH * arr.shape[1], HEIGHT * arr.shape[0])
    ctx = cairo.Context(surface)
    for row in range(arr.shape[0]):
        for col in range(arr.shape[1]):
            ctx.set_source_rgb(0, 0, 0) if arr[row, col] == 1 else ctx.set_source_rgb(1, 1, 1)
            ctx.rectangle(col * WIDTH, row * HEIGHT, WIDTH, HEIGHT)
            ctx.fill()

    return surface


def main():
    args = get_args()
    logging.debug(f"parsed arguments: {args}")

    filename = args.filename
    rule = args.rule
    rows = args.rows

    seed = get_seed(filename)
    logging.debug(f"seed is '{seed}'")

    arr = np.array(list(seed), dtype=int)
    arr = np.vstack((arr, np.empty((rows - 1, len(seed)), dtype=int)))
    logging.debug(f"the starting array is: \n{arr}")

    arr = calculate_array(arr, rule)

    logging.debug(f"array after calculating: \n{arr}")

    surface = create_and_draw_surface(arr)

    surface.write_to_png("out.png")


if __name__ == '__main__':
    main()
