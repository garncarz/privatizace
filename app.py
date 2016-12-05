#!/usr/bin/env python3

import asyncio

from privat import curses


if __name__ == '__main__':
    app = curses.App()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.run())
