import bisect
import itertools
import random

from .engine import Player


MAX_TRIES = 200
MAX_RATINGS = 10


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
        ratings = {}

        for square in self.board:
            rating = (square.value / len(square.neighbours)
                      if square.value
                      else random.random() * 0.1)
            ratings[square] = [rating] + [0] * (MAX_RATINGS - 1)

        for rating_nr in range(1, MAX_RATINGS):
            for square in ratings.keys():
                my_rating = ratings[square][rating_nr] \
                          = ratings[square][rating_nr - 1]

                for neighbour in square.neighbours.values():
                    neigh_rating = ratings[neighbour][rating_nr - 1]

                    if neighbour.player == square.player:
                        sign = 1
                    elif neigh_rating > my_rating:
                        sign = -1
                    else:
                        sign = 1

                    ratings[square][rating_nr] += sign \
                        * neigh_rating / len(neighbour.neighbours)

        choices = list(filter(lambda r: r[0].player in [None, self],
                              ratings.items()))

        cumdist = list(itertools.accumulate(
            map(lambda ch: ch[1][-1], choices))
        )
        x = random.random() * cumdist[-1]
        try:
            choice = choices[bisect.bisect(cumdist, x)]
        except IndexError:
            choice = random.choice(choices)
        square = choice[0]

        return square.x, square.y
