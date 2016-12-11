import random

from .engine import Player


MAX_TRIES = 200


class Bot(Player):

    def __repr__(self):
        return '<Bot %s>' % self.name

    @property
    def is_bot(self):
        return True

    def propose_move(self):
        for try_nr in range(MAX_TRIES):
            x = random.randint(0, self.board.width - 1)
            y = random.randint(0, self.board.height - 1)
            if self.board[x, y].player in [None, self]:
                return x, y
