import curses

from . import engine


class App:

    def __init__(self):
        self.board = engine.Board()
        self.board.listeners.append(self)

    async def _run(self):
        self.screen.clear()

        for x, column in enumerate(self.board):
            for y, square in enumerate(column):
                self.screen.addch(y, x, str(square.value))

        while True:
            ev = self.screen.getch()

            if ev in [ord('q'), ord('Q')]:
                break

            if ev == curses.KEY_MOUSE:
                _, x, y, _, m_ev = curses.getmouse()
                if m_ev & curses.BUTTON1_RELEASED:
                    await self.board[x][y].increment()
                    await self.board.process()

    def refresh_square(self, square):
        self.screen.addch(square.y, square.x, str(square.value))

    async def run(self):
        try:
            self.screen = curses.initscr()

            curses.noecho()
            curses.cbreak()
            self.screen.keypad(1)

            curses.start_color()

            curses.mousemask(1)

            await self._run()

        finally:
            self.screen.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
