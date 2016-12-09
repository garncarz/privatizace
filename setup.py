#!/usr/bin/env python3

from setuptools import setup, find_packages

from privat import __version__


classifiers = """\
Development Status :: 3 - Alpha
Environment :: Console :: Curses
License :: OSI Approved :: MIT License
Operating System :: POSIX
Programming Language :: Python :: 3.5
Topic :: Games/Entertainment :: Board Games
"""

setup(
    name='privatizace',
    version=__version__,
    author='Ondřej Garncarz',
    author_email='ondrej@garncarz.cz',
    url='https://github.com/garncarz/privatizace',
    license='MIT',

    description='Logical game, a homage to the old game Velká privatizace',
    keywords='game logical',

    packages=find_packages(),
    classifiers=classifiers.splitlines(),

    entry_points={
        'console_scripts': [
            'privatizace = privat.app:main',
        ],
    },
)
