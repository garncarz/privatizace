# The Great Privatization

[![Build Status](https://travis-ci.org/garncarz/privatizace.svg?branch=master)](https://travis-ci.org/garncarz/privatizace)
[![Coverage Status](https://coveralls.io/repos/github/garncarz/privatizace/badge.svg?branch=master)](https://coveralls.io/github/garncarz/privatizace?branch=master)

This is a homage to the old game
[Velká privatizace](http://www.bestoldgames.net/velka-privatizace).


## Installation

Needed: Python 3.5

`pip install [--user] privatizace`


## Usage

`privatizace` is an ncurses-based game.
See `privatizace --help` for command line arguments.

The board is interacted with with a mouse,
and the game can be controlled by several keys:

- `←` to go backward in history;
- `→` to go forward in history;
- `F2` to start a new game;
- `r` to refresh the screen (shouldn't be needed);
- `q` to quit.

The game automatically saves/loads `~/.privatizace`.


## Development

Preferably under `virtualenv`:

`pip install pip-tools` (once)

`pip-sync requirements*.txt` (keeping the PyPI dependencies up-to-date)

`./test.sh` (runs tests and also generates a coverage)

`./app.py` (runs the game)
