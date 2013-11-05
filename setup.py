"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['Peanuts.py']
DATA_FILES = ['BoardModel.py',
        'BoardController.py',
 'BoardWidget.py',
 'Constants.py',
 'Problem.py',
 'sgflib.py',
 'typelib.py']
OPTIONS = {'argv_emulation': True,
 'iconfile': './Peanuts.icns'}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
