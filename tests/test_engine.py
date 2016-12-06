import random

import pytest

from privat import engine


def test_init_board():
    width = random.randint(5, 10)
    height = random.randint(5, 10)

    board = engine.Board(width=width, height=height)

    assert board[3, 3].up == board[3, 2]
    assert board[3, 3].right == board[4, 3]
    assert board[3, 3].down == board[3, 4]
    assert board[3, 3].left == board[2, 3]

    assert not 'up' in board[0, 0].neighbours
    assert not 'left' in board[0, 0].neighbours
    assert not 'right' in board[width-1, 0].neighbours
    assert not 'down' in board[width-1, height-1].neighbours


@pytest.mark.asyncio
async def test_process():
    board = engine.Board(4, 4, players=1)

    await board[0, 0].increment()
    await board[0, 0].increment()
    await board.process()

    assert board[0, 0].value == 0
    assert board[0, 1].value == 1
    assert board[1, 0].value == 1

    await board[0, 1].increment()
    await board[0, 1].increment()
    await board.process()

    assert board[0, 1].value == 0
    assert board[0, 0].value == 1
    assert board[0, 2].value == 1
    assert board[1, 1].value == 1

    await board[1, 1].increment()
    await board[1, 1].increment()
    await board[1, 1].increment()
    await board.process()

    assert board[1, 1].value == 0
    assert board[0, 1].value == 1
    assert board[2, 1].value == 1
    assert board[1, 0].value == 2
    assert board[1, 2].value == 1


@pytest.mark.asyncio
async def test_process_bad_player():
    board = engine.Board(4, 4)

    await board[0, 0].increment()
    await board.process()

    with pytest.raises(engine.GameException) as e:
        await board[0, 0].increment()
    assert 'does not belong to' in str(e)
    assert board.actual_player == board.players[1]


@pytest.mark.asyncio
async def test_process_multiple_players():
    board = engine.Board(2, 2, players=2)

    await board[0, 0].increment()
    await board.process()

    assert board[0, 0].player == board.players[0]

    await board[0, 1].increment()
    await board[0, 1].increment()
    await board.process()

    assert board[0, 0].value == 0
    assert board[0, 0].player == board.players[1]
    assert board[0, 1].value == 1


def test_bad_coordinate():
    board = engine.Board(4, 4)

    with pytest.raises(engine.SquareException) as e:
        board[5, 0]

    with pytest.raises(engine.SquareException) as e:
        board[1, 6]


def test_iterator():
    board = engine.Board(2, 2)
    it = iter(board)

    sq = next(it)
    assert sq.x == 0
    assert sq.y == 0

    sq = next(it)
    assert sq.x == 0
    assert sq.y == 1

    sq = next(it)
    assert sq.x == 1
    assert sq.y == 0

    sq = next(it)
    assert sq.x == 1
    assert sq.y == 1

    with pytest.raises(StopIteration):
        next(it)


@pytest.mark.asyncio
async def test_amounts():
    board = engine.Board(3, 3, players=2)

    await board[0, 0].increment()
    await board.process()

    await board[0, 1].increment()
    await board.process()

    assert board.players[1].amount == 1
    assert board.players[1].active

    await board[0, 0].increment()
    await board.process()

    assert board.players[0].amount == 3
    assert board.players[1].amount == 0
    assert not board.players[1].active
