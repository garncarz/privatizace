# The Great Privatization

[![Build Status](https://travis-ci.org/garncarz/privatizace.svg?branch=master)](https://travis-ci.org/garncarz/privatizace)
[![Coverage Status](https://coveralls.io/repos/github/garncarz/privatizace/badge.svg?branch=master)](https://coveralls.io/github/garncarz/privatizace?branch=master)
[![PyPI version](https://badge.fury.io/py/privatizace.svg)](https://badge.fury.io/py/privatizace)

This is a homage to the old game
[Velká privatizace](http://www.bestoldgames.net/velka-privatizace).


## Installation

Needed: Python 3.5

### From PyPI

`pip install [--user] privatizace`

### From cloned repository

```bash
# Basic installation
pip install [--user] -e .

# With web interface support
pip install [--user] -e .[web]
```


## Usage

`privatizace` can be run in two modes:

### ncurses interface (default)

`privatizace` runs an ncurses-based game.
See `privatizace --help` for command line arguments.

The board is interacted with with a mouse,
and the game can be controlled by several keys:

- `←` to go backward in history;
- `→` to go forward in history;
- `F2` to start a new game;
- `r` to refresh the screen (shouldn't be needed);
- `q` to quit.

The game automatically saves/loads `~/.privatizace`.

### Web interface

For a modern web-based interface with HTML5 Canvas:

```bash
privatizace --web --host 0.0.0.0 --port 8000
```

This provides:
- Interactive HTML5 Canvas game board
- Real-time WebSocket communication
- REST API endpoints
- History navigation controls
- Responsive web design

**Note:** Web interface requires additional dependencies. Install with `pip install -e .[web]`.


## Development

Preferably under `virtualenv`:

`pip install pip-tools` (once)

`pip-sync requirements*.txt` (keeping the PyPI dependencies up-to-date)

`./test.sh` (runs tests and also generates a coverage)

`./app.py` (runs the game)


<!-- ❄️ Hello to the GitHub Archive! ❄️ -->
