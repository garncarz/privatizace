import random

from .engine import Player


MAX_TRIES = 200


class Bot(Player):

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.propose_move = random.choice([
            self.propose_random,
            self.propose_rated,
        ])

    def __repr__(self):
        return '<Bot %s>' % self.name

    @property
    def is_bot(self):
        return True

    def propose_random(self):
        for try_nr in range(MAX_TRIES):
            x = random.randint(0, self.board.width - 1)
            y = random.randint(0, self.board.height - 1)
            if self.board[x, y].player in [None, self]:
                return x, y

    def propose_rated(self):
        choices = []

        for square in self.board:
            rating = square.value / len(square.neighbours)
            choices.append((rating, square))

        choices = sorted(choices, key=lambda ch: ch[0], reverse=True)
        choices = filter(lambda ch: ch[1].player in [None, self], choices)

        square = random.choice(list(choices)[:10])[1]

        return square.x, square.y
