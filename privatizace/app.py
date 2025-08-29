import argparse
import asyncio

# Import curses conditionally to avoid unnecessary dependency issues
try:
    from . import curses
except ImportError:
    curses = None


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
arg_parser.add_argument('--web', action='store_true',
                        help='Run as web server instead of ncurses.')
arg_parser.add_argument('--host', default='127.0.0.1',
                        help='Web server host (default: 127.0.0.1).')
arg_parser.add_argument('--port', default=8000, type=int,
                        help='Web server port (default: 8000).')


def main():
    args = arg_parser.parse_args()

    if args.web:
        # Import web module only when needed to avoid dependency issues
        from . import web

        # Create default game with specified parameters
        web.game_manager.create_game(
            width=args.width,
            height=args.height,
            players=args.players,
            bots=args.bots
        )

        if args.load:
            board = web.game_manager.ensure_default_game()
            board.load(args.load)

        web.run_server(host=args.host, port=args.port)
    else:
        if not curses:
            raise ImportError("The curses module is required for ncurses mode but is not available.")

        # Original ncurses mode
        app = curses.App(width=args.width, height=args.height,
                         players=args.players, bots=args.bots)

        if args.load:
            app.board.load(args.load)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run())
