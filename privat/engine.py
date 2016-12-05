import asyncio


class Board:

    def __init__(self, width=8, height=8):
        self.tasks = []
        self.listeners = []

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
        if isinstance(index, int):
            return self.squares[index]

    def __len__(self):
        return len(self.squares)

    async def process(self):
        if self.tasks:
            await asyncio.wait(self.tasks)


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
        self.value += 1
        if self.value >= len(self.neighbours):
            self.value = 0
            for neighbour in self.neighbours.values():
                self.board.tasks.append(
                    asyncio.ensure_future(neighbour.increment())
                )

        for listener in self.board.listeners:
            listener.refresh_square(self)
