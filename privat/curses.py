import curses
import logging
import os

from . import engine
from . import io


SQUARE_SLEEP = 100

SAVE_FILE = os.path.expanduser('~/.privatizace')

logger = logging.getLogger(__name__)


class App:

    def __init__(self, width=8, height=8, players=4):
        self._width = width
        self._height = height
        self._players = players
        self._board = None
        self.in_game = True

    @property
    def board(self):
        if not self._board:
            try:
                self._board = io.load_board(open(SAVE_FILE))
                self._board.listeners.append(self)
            except Exception:
                self.create_new_board()
        return self._board

    def create_new_board(self):
        self._board = engine.Board(self._width, self._height, self._players)
        self._board.listeners.append(self)

    async def _run(self):
        self.refresh()

        while True:
            ev = self.screen.getch()

            if ev in [ord('q'), ord('Q')]:
                break

            elif ev == ord('r'):
                self.refresh()

            elif ev == curses.KEY_RESIZE:
                self.refresh()

            elif ev == curses.KEY_MOUSE:
                try:
                    _, x, y, _, m_ev = curses.getmouse()
                except curses.error:
                    continue

                if self.in_game and m_ev & curses.BUTTON1_RELEASED:
                    try:
                        await self.board.play(x, y)
                    except engine.WinnerException as w:
                        self.in_game = False
                    except engine.SquareException:
                        pass

                    self.refresh_info()

                    try:
                        io.save_board(self.board, open(SAVE_FILE, 'w'))
                    except Exception:
                        pass

            elif ev == curses.KEY_F2:
                self.create_new_board()
                self.refresh()

            elif ev == curses.KEY_LEFT:
                try:
                    self.board.history_jump(-1)
                    self.in_game = True
                    self.refresh()
                except engine.HistoryException:
                    pass

            elif ev == curses.KEY_RIGHT:
                try:
                    self.board.history_jump(+1)
                    self.in_game = True
                    self.refresh()
                except engine.HistoryException:
                    pass

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
            self.refresh_square(square, in_game=False)

    def refresh_square(self, square, in_game=True):
        self.board_window.addnstr(square.y, square.x, str(square.value), 1,
                                  curses.color_pair(square.color))
        self.board_window.refresh()

        if in_game:
            self.refresh_info()
            curses.beep()
            curses.napms(SQUARE_SLEEP)

    def refresh_info(self):
        win = self.info_window

        for player in self.board.players:
            name = player.name
            color = curses.color_pair(player.color)

            if player == self.board.actual_player:
                name = name.upper()
                color = color | curses.A_BOLD

            win.addstr(player.number * 3, 0, name, color)
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
