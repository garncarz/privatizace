import io

import pytest

from privat import engine
import privat.io


@pytest.mark.asyncio
async def test_save_and_load():
    width = 4
    height = 5
    players = 3

    board1 = engine.Board(width, height, players)

    await board1.play(1, 1)
    await board1.play(2, 2)
    await board1.play(1, 2)
    await board1.play(1, 1)

    save_file = io.StringIO()
    privat.io.save_board(board1, save_file)

    save_file.seek(0)
    board2 = privat.io.load_board(save_file)

    assert board1.width == board2.width
    assert board1.height == board2.height
    assert board1.overall_value == board2.overall_value
    assert board1.actual_player.number == board2.actual_player.number

    for square1, square2 in zip(board1, board2):
        assert square1.value == square2.value
        if not square1.player:
            assert not square2.player
        else:
            assert square1.player.number == square2.player.number

    for player1, player2 in zip(board1.players, board2.players):
        assert player1.amount == player2.amount
        assert player1.active == player2.active
