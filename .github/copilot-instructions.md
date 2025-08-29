# The Great Privatization

The Great Privatization is a Python-based ncurses logical game, a homage to the old game "Velká privatizace". The game uses an asyncio engine, ncurses interface, and supports bots.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Install Dependencies
DO NOT use the pip-sync approach mentioned in README.md as it fails with permission issues in most environments.

Use this working approach instead:
- `pip install --user pytest pytest-asyncio pytest-cov` - Install test dependencies. Takes ~1 second. NEVER CANCEL: Set timeout to 60+ seconds.
- `pip install --user -e .` - Install package in development mode for testing. Takes ~1 second.

### Build and Test
- `PYTHONPATH=. python -m pytest tests/ -v` - Run all tests. Takes ~0.4 seconds. NEVER CANCEL: Set timeout to 30+ seconds for safety.
- `PYTHONPATH=. python -m pytest --cov-report html --cov=privatizace tests/` - Run tests with coverage. Takes ~0.7 seconds. NEVER CANCEL: Set timeout to 30+ seconds.
- `./test.sh` - Also works and runs the same pytest with coverage (legacy script that still functions).

### Run the Application
- ALWAYS install dependencies and package first using the bootstrap steps above.
- `privatizace` - Run the installed game (after `pip install -e .`).
- `privatizace --help` - Show command line help.
- `python ./app.py` - Run game directly from source.
- `python ./app.py --help` - Show command line options.

## Validation

### Testing Changes
- ALWAYS run the test suite after making changes: `PYTHONPATH=. python -m pytest tests/ -v`
- Tests run very quickly (~0.4 seconds) so run them frequently during development.
- One test (`test_continuous_addition[5-5-100]`) may occasionally fail due to randomness - this is expected.
- Coverage report is generated in `htmlcov/` directory.
- Alternative: `./test.sh` also works and includes coverage reporting.

### Manual Application Testing
After making changes to the game engine or UI:
- ALWAYS test that the application starts: `privatizace --help` should display usage information.
- Test basic game creation: `privatizace --width 4 --height 4 --players 2` attempts to start the game.
- **IMPORTANT**: The game uses ncurses and requires a real terminal. In headless environments, it will fail with `_curses.error: curs_set() returned ERR` - this is expected behavior and indicates the application code is working correctly.
- If testing in a proper terminal environment, you can interact with the game using mouse and keyboard (see README.md for controls).

## Common Tasks

### Repository Structure
```
/home/runner/work/privatizace/privatizace/
├── privatizace/           # Main package
│   ├── __init__.py       # Version info
│   ├── app.py           # Main application entry point
│   ├── engine.py        # Core game engine with asyncio
│   ├── bot.py           # Bot AI implementation
│   ├── curses.py        # Ncurses user interface
│   └── io.py            # Save/load functionality
├── tests/               # Test suite
│   ├── test_engine.py   # Core engine tests
│   ├── test_bot.py      # Bot functionality tests
│   └── test_io.py       # Save/load tests
├── app.py              # Development runner script
├── test.sh             # Legacy test script (broken)
├── setup.py            # Package configuration
└── README.md           # Basic project documentation
```

### Key Files Content Summary

#### setup.py
- Package name: `privatizace`
- Version: from `privatizace.__version__`
- Entry point: `privatizace = privatizace.app:main`
- Requires Python 3.5+

#### privatizace/engine.py
- Core game classes: `Board`, `Square`, `Player`
- Exceptions: `GameException`, `SquareException`, `WinnerException`
- Asyncio-based game processing

#### privatizace/app.py
- Command line argument parsing
- Game board configuration options
- Integration with curses UI

### Development Workflow
1. Make code changes
2. Run tests: `PYTHONPATH=. python -m pytest tests/ -v`
3. Test application startup: `privatizace --help`
4. For engine changes, also run: `python -c "from privatizace import engine; print('Import successful')"`

### Dependencies and Versions
- **CRITICAL**: Do not use the pinned versions in `requirements-test.txt` - they are too old for modern Python
- Working versions: pytest>=8.0, pytest-asyncio>=1.0, pytest-cov>=6.0
- The game saves state to `~/.privatizace` automatically

### Common Issues and Solutions
- "pip-sync fails": Use direct pip install instead of pip-sync from README.md
- "py.test not found": Use `python -m pytest` instead of the legacy `py.test` command
- "Old pytest version errors": Install modern pytest versions with `pip install --user pytest pytest-asyncio pytest-cov`
- "Permission denied during pip-sync": Skip pip-sync entirely, use direct pip install approach

### CI Integration
The project uses Travis CI (`.travis.yml`), but the configuration may need updating for modern Python versions. The working test command for CI is:
```bash
pip install --user pytest pytest-asyncio pytest-cov
pip install --user -e .
PYTHONPATH=. python -m pytest tests/ -v
```