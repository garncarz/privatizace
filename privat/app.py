import argparse
import asyncio

from . import curses


arg_parser = argparse.ArgumentParser(
    description='The Great Privatization, a logical game.',
)
arg_parser.add_argument('--width', default=8, type=int,
                        help='Width of the board.')
arg_parser.add_argument('--height', default=8, type=int,
                        help='Height of the board.')
arg_parser.add_argument('--players', default=4, type=int,
                        help='Number of players.')
arg_parser.add_argument('--load', metavar='DUMPED_STRING',
                        help='Load dumped board.')


def main():
    args = arg_parser.parse_args()

    app = curses.App(args.width, args.height, args.players)

    if args.load:
        app.board.load(args.load)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.run())
