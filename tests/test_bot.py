import pytest

from privat import engine


MAX_TRIES = 1000


@pytest.mark.parametrize('width, height, bots', [
    (5, 5, 3),
    (5, 5, 4),
    (4, 4, 2),
    (8, 6, 4),
])
@pytest.mark.asyncio
async def test_two_bots(width, height, bots):
    board = engine.Board(width, height, players=bots, bots=bots)

    for _ in range(MAX_TRIES):
        x, y = board.actual_player.propose_move()
        try:
            await board.play(x, y)
        except engine.WinnerException:
            break


def test_init():
    board = engine.Board(4, 4, players=4, bots=2)

    assert not board.players[0].is_bot
    assert not board.players[1].is_bot
    assert board.players[2].is_bot
    assert board.players[3].is_bot

    first_player = board.actual_player

    next(board.players_wheel)
    next(board.players_wheel)
    next(board.players_wheel)

    assert next(board.players_wheel) == first_player
