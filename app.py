#!/usr/bin/env python3

import logging

from privatizace import app


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.FileHandler('privatizace.log')],
    )
    app.main()
