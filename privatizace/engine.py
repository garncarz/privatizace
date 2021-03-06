import asyncio
import logging


logger = logging.getLogger(__name__)


class GameException(Exception):
    pass


class SquareException(GameException):
    pass


class WinnerException(GameException):
    pass


class HistoryException(GameException):
    pass


class Board:

    def __init__(self, width=8, height=8, players=4, bots=0):
        self.width = width
        self.height = height

        self.tasks = []
        self.listeners = []

        from .bot import Bot
        self.players = \
            [Player(self, i) for i in range(players - bots)] \
            + [Bot(self, i) for i in range(players - bots, players)]
        self.players_wheel = PlayersWheel(self.players)
        self.actual_player = next(self.players_wheel)

        squares = [[Square(self, x, y) for y in range(height)]
                                       for x in range(width)
                  ]
        for x, column in enumerate(squares):
            for y, square in enumerate(column):
                if x > 0:
                    square.neighbours['left'] = squares[x-1][y]
                if x < width - 1:
                    square.neighbours['right'] = squares[x+1][y]
                if y > 0:
                    square.neighbours['up'] = squares[x][y-1]
                if y < height - 1:
                    square.neighbours['down'] = squares[x][y+1]
        self.squares = squares

        self.history = [self.dump()]
        self.history_position = 0

    def __getitem__(self, index):
        if isinstance(index, tuple):
            try:
                column, row = index
                return self.squares[column][row]
            except IndexError:
                raise SquareException('bad coordinate', index)

        if isinstance(index, int):
            column = index // len(self.squares[0])
            if column >= len(self.squares):
                raise SquareException("there's not that many squares")
            row = index % len(self.squares[0])
            return self[column, row]

    def __iter__(self):
        return SquaresIterator(self)

    async def play(self, x=None, y=None):
        if self.is_victory():
            raise WinnerException(self.actual_player)

        if x is None or y is None:
            x, y = self.actual_player.propose_move()

        self.last_move = {'x': x, 'y': y}
        logger.info('%s moving at %d, %d' % (self.actual_player, x, y))

        await self[x, y].increment()
        await self.process()

    async def process(self):
        while self.tasks:
            task = self.tasks.pop(0)
            await asyncio.wait([task])

        self.actual_player = next(self.players_wheel)

        self.history_position += 1
        self.history = self.history[:self.history_position]
        self.history.append(self.dump())

        if self.is_victory():
            raise WinnerException(self.actual_player)

    def is_victory(self):
        actives = sum(int(player.active) for player in self.players)
        if actives == 1:
            return True
        elif actives < 1:
            raise GameException('No active players')
        return False

    def is_expecting_move(self):
        return (not self.history
                 or (self.history_position == len(self.history) - 1
                     and not self.is_victory()))

    def dump(self):
        dump = ''
        for square in self:
            player_number = square.player.number if square.player else '-'
            dump += '%s%d' % (player_number, square.value)
        dump += '%s' % self.actual_player.number
        return dump

    def load(self, dump):
        assert len(dump) == self.width * self.height * 2 + 1

        for sq_nr, square in enumerate(self):
            player_number = dump[2 * sq_nr]
            square.player = self.players[int(player_number)] \
                            if player_number != '-' else None
            square.value = int(dump[2 * sq_nr + 1])

        self.recalculate_players()

        self.players_wheel.set_number(int(dump[-1]))
        self.actual_player = next(self.players_wheel)

    def recalculate_players(self):
        for player in self.players:
            player.amount = 0
            player.active = True
        for square in self:
            if square.player:
                square.player.amount += square.value
        if self.overall_value >= len(self.players):
            for player in self.players:
                if player.amount <= 0:
                    player.active = False

    @property
    def overall_value(self):
        return sum(square.value for square in self)

    def history_jump(self, step):
        if 0 <= self.history_position + step < len(self.history):
            self.history_position += step
            self.load(self.history[self.history_position])
        else:
            raise HistoryException('cannot jump there')


class Square:

    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y

        self.neighbours = {}
        self.value = 0
        self.player = None

    def __repr__(self):
        return '<Square %d,%d>' % (self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.x == other.x and self.y == other.y:
                return True
        return False

    def __hash__(self):
        return self.x * self.board.height + self.y

    def __getattr__(self, name):
        if name in self.neighbours:
            return self.neighbours[name]

    async def increment(self):
        if self.player and self.player != self.board.actual_player:
            raise SquareException('%s does not belong to %s'
                                  % (self, self.board.actual_player))
        if not self.player:
            self.player = self.board.actual_player

        self.value += 1
        self.player.amount += 1

        if self.value >= len(self.neighbours) and not self.board.is_victory():
            self.player.amount -= self.value
            self.value = 0

            for neighbour in self.neighbours.values():
                if neighbour.player and neighbour.player != self.player:
                    neighbour.player.amount -= neighbour.value

                    if neighbour.player.amount == 0:
                        neighbour.player.active = False
                    elif neighbour.player.amount < 0:
                        raise GameException('player.amount < 0',
                                            neighbour.player)

                    self.player.amount += neighbour.value
                    neighbour.player = self.player

                self.board.tasks.insert(
                    0,
                    asyncio.ensure_future(neighbour.increment())
                )

        for listener in self.board.listeners:
            listener.refresh_square(self)

    @property
    def color(self):
        if self.player:
            return self.player.color
        return 0


class Player:

    NAMES = ['Tesla', 'Lacrum', 'Loana', 'Tatra']

    def __init__(self, board, number, name=None):
        self.board = board
        self.number = number
        self.name = name or self.NAMES[self.number]
        self.amount = 0
        self.active = True

    def __repr__(self):
        return '<Player %s>' % self.name

    def __str__(self):
        return self.name

    @property
    def color(self):
        return self.number + 1

    @property
    def is_bot(self):
        return False


class SquaresIterator:
    def __init__(self, board):
        self.board = board
        self._iter_square = 0

    def __next__(self):
        try:
            square = self.board[self._iter_square]
            self._iter_square += 1
            return square
        except SquareException:
            raise StopIteration


class PlayersWheel:

    def __init__(self, players):
        self.players = players
        self._iter_player = 0

    def __next__(self):
        if self._iter_player >= len(self.players):
            self._iter_player = 0

        player = self.players[self._iter_player]
        self._iter_player += 1

        if player.active:
            return player
        else:
            # beware, might end as an infinite loop
            return next(self)

    def set_number(self, number):
        self._iter_player = number
