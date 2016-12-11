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
arg_parser.add_argument('--bots', default=0, type=int,
                        help='Number of bots (from players).')
arg_parser.add_argument('--load', metavar='DUMPED_STRING',
                        help='Load dumped board.')


def main():
    args = arg_parser.parse_args()

    app = curses.App(width=args.width, height=args.height,
                     players=args.players, bots=args.bots)

    if args.load:
        app.board.load(args.load)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.run())
