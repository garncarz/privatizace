#!/usr/bin/env python

import asyncio

from evaluation import bots


def main():
    loop = asyncio.get_event_loop()

    for f in filter(lambda f: f.startswith('eval_'), dir(bots)):
        loop.run_until_complete(getattr(bots, f)())


if __name__ == '__main__':
    main()
