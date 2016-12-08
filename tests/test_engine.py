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
    board = engine.Board(4, 4, players=2)

    await board[0, 0].increment()
    await board[0, 0].increment()
    await board.process()

    assert board[0, 0].value == 0
    assert board[0, 1].value == 1
    assert board[1, 0].value == 1

    await board[1, 1].increment()
    await board[2, 1].increment()
    await board.process()

    assert board[1, 1].value == 1
    assert board[2, 1].value == 1

    await board[0, 1].increment()
    await board[0, 1].increment()
    await board[0, 1].increment()
    await board.process()

    assert board[1, 1].value == 2
    assert board[0, 1].value == 1
    assert board[2, 1].value == 1
    assert board[1, 0].value == 1
    assert board[1, 2].value == 0

    return board  # used in another test


@pytest.mark.asyncio
async def test_process_bad_player():
    board = engine.Board(4, 4)

    await board[0, 0].increment()
    await board.process()

    with pytest.raises(engine.SquareException) as e:
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

    with pytest.raises(engine.WinnerException) as e:
        await board.process()
        assert e.number == 0

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

    with pytest.raises(engine.WinnerException) as e:
        await board.process()
        assert e.number == 0

    assert board.players[0].amount == 3
    assert board.players[1].amount == 0
    assert not board.players[1].active


@pytest.mark.asyncio
async def test_dump_and_load():
    board1 = await test_process()

    board2 = engine.Board(4, 4, players=2)

    board2.load(board1.dump())

    assert board2[1, 1].value == 2
    assert board2[0, 1].value == 1
    assert board2[2, 1].value == 1
    assert board2[1, 0].value == 1
    assert board2[1, 2].value == 0

    assert board2[1, 1].player.number == 0
    assert board2[2, 1].player.number == 1
    assert not board2[3, 3].player


@pytest.mark.parametrize('max_x, max_y, steps', [
    (5, 5, 40),
    (5, 5, 100),
    (4, 4, 50),
])
@pytest.mark.asyncio
async def test_continuous_addition(max_x, max_y, steps):
    board = engine.Board(max_x, max_y)
    old_value = 0

    for step in range(steps):
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        try:
            await board[x, y].increment()
            await board.process()

            new_value = board.overall_value
            assert new_value == old_value + 1
            old_value = new_value
        except engine.SquareException:
            pass
        except engine.WinnerException:
            pass

        for player in board.players:
            if not player.active:
                for square in board:
                    assert square.player != player


@pytest.mark.asyncio
async def test_multiple_expansions():
    board = engine.Board(4, 4)
    board.load('111110111212123102023230010002311')

    old_value = board.overall_value

    await board[0, 0].increment()
    await board.process()

    assert board.dump() == '111210111113123111133230101102313'
    assert board.overall_value == old_value + 1


def test_multiple_iterators():
    board = engine.Board()

    it1 = iter(board)
    it2 = iter(board)

    assert next(it1) == next(it2)
    assert next(it1) == next(it2)
    assert next(it1) == next(it2)
