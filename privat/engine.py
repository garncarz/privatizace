import asyncio


class GameException(Exception):
    pass


class SquareException(GameException):
    pass


class WinnerException(GameException):
    pass


class Board:

    def __init__(self, width=8, height=8, players=4):
        self.width = width
        self.height = height

        self.tasks = []
        self.listeners = []
        self.history = []

        self.players = [Player(i) for i in range(players)]
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

    async def process(self):
        while self.tasks:
            task = self.tasks.pop(0)
            await asyncio.wait([task])

        self.history.append(self.dump())
        self.actual_player = next(self.players_wheel)

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

        self.players_wheel.set_number(int(dump[-1]))
        self.actual_player = next(self.players_wheel)
        self.recalculate_players()

    def recalculate_players(self):
        for player in self.players:
            player.amount = 0
        for square in self:
            if square.player:
                square.player.amount += square.value
        for player in self.players:
            player.active = True if player.amount > 0 else False

    @property
    def overall_value(self):
        return sum(square.value for square in self)


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

        if self.value >= len(self.neighbours):
            self.player.amount -= self.value
            self.value = 0

            for neighbour in self.neighbours.values():
                if neighbour.player and neighbour.player != self.player:
                    neighbour.player.amount -= neighbour.value
                    if neighbour.player.amount == 0:
                        neighbour.player.active = False
                    self.player.amount += neighbour.value

                neighbour.player = self.player

                self.board.tasks.append(
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

    def __init__(self, number, name=None):
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
        self.players = players[:]
        self._iter_player = 0

    def __next__(self):
        if self._iter_player >= len(self.players):
            self._iter_player = 0

        player = self.players[self._iter_player]
        if not player.active:
            self.players.pop(self._iter_player)
            player = next(self)
        else:
            self._iter_player += 1

        if len(self.players) == 1:
            raise WinnerException(player)

        return player

    def set_number(self, number):
        self._iter_player = number
