import json

from . import engine


def save_board(board, out_file):
    data = {
        'width': board.width,
        'height': board.height,
        'players': len(board.players),
        'history': board.history,
    }

    out_file.write(json.dumps(data))


def load_board(in_file):
    data = json.loads(in_file.read())

    board = engine.Board(
        width=int(data['width']),
        height=int(data['height']),
        players=int(data['players']),
    )

    board.history = data['history']
    board.history_jump(len(board.history) - 1)

    return board
