import curses

from . import engine


class App:

    def __init__(self):
        self.board = engine.Board()
        self.board.listeners.append(self)

    async def _run(self):
        self.screen.clear()

        for square in self.board:
            self.refresh_square(square)

        while True:
            ev = self.screen.getch()

            if ev in [ord('q'), ord('Q')]:
                break

            if ev == curses.KEY_MOUSE:
                _, x, y, _, m_ev = curses.getmouse()
                if m_ev & curses.BUTTON1_RELEASED:
                    try:
                        await self.board[x, y].increment()
                        await self.board.process()
                    except engine.SquareException:
                        pass

    def refresh_square(self, square):
        self.screen.addnstr(square.y, square.x, str(square.value), 1,
                            curses.color_pair(square.color))

    async def run(self):
        try:
            self.screen = curses.initscr()

            curses.noecho()
            curses.cbreak()
            self.screen.keypad(1)

            curses.start_color()
            bg = curses.COLOR_BLACK
            curses.init_pair(1, curses.COLOR_BLUE, bg)
            curses.init_pair(2, curses.COLOR_RED, bg)
            curses.init_pair(3, curses.COLOR_GREEN, bg)
            curses.init_pair(4, curses.COLOR_YELLOW, bg)  # original uses BLACK

            curses.mousemask(1)

            await self._run()

        finally:
            self.screen.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
