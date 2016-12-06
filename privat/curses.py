import curses
import logging

from . import engine


logger = logging.getLogger(__name__)


class App:

    def __init__(self):
        self.board = engine.Board()
        self.board.listeners.append(self)

    async def _run(self):
        self.refresh()

        while True:
            ev = self.screen.getch()

            if ev in [ord('q'), ord('Q')]:
                break

            elif ev == curses.KEY_RESIZE:
                self.refresh()

            elif ev == curses.KEY_MOUSE:
                _, x, y, _, m_ev = curses.getmouse()
                if m_ev & curses.BUTTON1_RELEASED:
                    try:
                        await self.board[x, y].increment()
                        await self.board.process()
                    except engine.SquareException:
                        pass

                    self.refresh_info()

    def refresh(self):
        self.screen.clear()

        self.board_window = self.screen.subwin(
            self.board.height + 1,
            self.board.width + 1,
            0,
            0,
        )
        self.info_window = self.screen.subwin(
            0,
            max(self.board.width + 2, self.screen.getmaxyx()[1] // 2),
        )

        self.refresh_info()

        for square in self.board:
            self.refresh_square(square, refresh_info=False)

    def refresh_square(self, square, refresh_info=True):
        self.board_window.addnstr(square.y, square.x, str(square.value), 1,
                                  curses.color_pair(square.color))
        self.board_window.refresh()

        if refresh_info:
            self.refresh_info()

    def refresh_info(self):
        win = self.info_window

        for player in self.board.players:
            color = curses.color_pair(player.color)
            if player == self.board.actual_player:
                color = color | curses.A_BOLD

            win.addstr(player.number * 3, 0, player.name, color)
            win.addstr(player.number * 3 + 1, 0,
                       '%5d' % player.amount if player.active
                          else '-'*5,
                       color)

        win.refresh()

    async def run(self):
        try:
            self.screen = curses.initscr()

            curses.noecho()
            curses.cbreak()
            self.screen.keypad(1)

            curses.start_color()
            bg = curses.COLOR_BLACK  # original uses YELLOW
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