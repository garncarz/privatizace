from privatizace import engine
from privatizace import bot


RUNS = 10


def evaluation(description):
    def decorator(func):
        async def func_wrapper(*args, **kwargs):
            score = 0
            for _ in range(RUNS):
                score += await func(*args, **kwargs)
            rating = score / RUNS
            print('%s... %d %%' % (description, rating * 100))
        return func_wrapper
    return decorator


@evaluation('Wins at 1 move (is supposed to).')
async def eval_win():
    board = smallest_winning_board()

    try:
        await board.play()
    except engine.WinnerException as w:
        assert w.args[0] == board.players[-1]
        return 1
    else:
        return 0


def smallest_winning_board():
    board = engine.Board(2, 2, players=2, bots=1)
    board.load('1101-0-01')
    return board
