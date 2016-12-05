import random

import pytest

from privat import engine


def test_init_board():
    width = random.randint(5, 10)
    height = random.randint(5, 10)

    board = engine.Board(width=width, height=height)

    assert len(board) == width
    assert len(board[0]) == height

    assert board[3][3].up == board[3][2]
    assert board[3][3].right == board[4][3]
    assert board[3][3].down == board[3][4]
    assert board[3][3].left == board[2][3]

    assert not 'up' in board[0][0].neighbours
    assert not 'left' in board[0][0].neighbours
    assert not 'right' in board[width-1][0].neighbours
    assert not 'down' in board[width-1][height-1].neighbours


@pytest.mark.asyncio
async def test_process():
    board = engine.Board(4, 4)

    await board[0][0].increment()
    await board[0][0].increment()
    await board.process()

    assert board[0][0].value == 0
    assert board[0][1].value == 1
    assert board[1][0].value == 1

    await board[0][1].increment()
    await board[0][1].increment()
    await board.process()

    assert board[0][1].value == 0
    assert board[0][0].value == 1
    assert board[0][2].value == 1
    assert board[1][1].value == 1

    await board[1][1].increment()
    await board[1][1].increment()
    await board[1][1].increment()
    await board.process()

    assert board[1][1].value == 0
    assert board[0][1].value == 1
    assert board[2][1].value == 1
    assert board[1][0].value == 2
    assert board[1][2].value == 1
