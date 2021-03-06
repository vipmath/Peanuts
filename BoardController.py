# Copyright (C) 2013 Alexey Vyskubov (alexey@ocaml.nl)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# The license is currently available on the Internet at:
#     http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
"""
Controller to connect BoardModel with BoardWidget
"""
from Constants import Color, Rotation
from Problem import Problem
from os import listdir
from os.path import isfile, join
from BoardModel import BoardModel
from random import randint

def _compose(outer, inner):
    """
    Given an inner function, which takes two arguments and produces 2-tuple,
    and an outer function, which takes two arguments, construct the
    composition of inner function, unpacking, and outer function.
    """
    def comp(arg1, arg2):
        return outer(*inner(arg1, arg2))
    return comp

class Transform(object):
    """
    The class to do different transformations of the board:
    mirroring, rotation and color swap
    """
    def __init__(self):
        mirror = {0: lambda nx, ny: (nx, ny),
                1: lambda nx, ny: (18 - nx, ny)}[randint(0, 1)]
        rotation = {
                0: Rotation.NONE,
                1: Rotation.RIGHT,
                2: Rotation.LEFT,
                3: Rotation.BOTH}[randint(0, 3)]
        swap = {0: False, 1: True}[randint(0, 1)]
        rotate = Rotation.rotate(rotation)
        unrotate = Rotation.unrotate(rotation)
        self.to_board = _compose(rotate, mirror)
        self.from_board = _compose(mirror, unrotate)
        self.fix_color = Color.change_color(swap)

class BoardController(object):
    def __init__(self):
        self._v_message = None
        self._model = None
        self._to_board = lambda x, y: (x, y)
        self._from_board = lambda x, y: (x, y)
        self._fix_color = lambda c: c
        self._board_widget = None
        self._directory = None
        self._collection = None
        self._problem = None

    def register_message_var(self, v):
        self._v_message = v

    def register_board_widget(self, widget):
        self._board_widget = widget

    def get_stones(self):
        stones = self._model.get_stones()
        def stone_to_board((nx, ny, s)):
            nxb, nyb = self._to_board(nx, ny)
            c = self._fix_color(s)
            return (nxb, nyb, c)
        return map(stone_to_board, stones)

    def get_ko(self):
        ko = self._model.get_ko()
        if ko:
            return self._to_board(*ko)
        else:
            return None

    def allowed(self, nxb, nyb):
        nx, ny = self._from_board(nxb, nyb)
        return self._model.allowed(nx, ny)

    def add(self, nxb, nyb):
        assert(self._v_message)
        nx, ny = self._from_board(nxb, nyb)
        self._model.do_move(nx, ny)
        self._board_widget.update_board()
        if not self._problem.is_over():
            reply = self._problem.get_reply(nx, ny)
            # TODO
            if self._problem.is_over():
                if self._problem.is_wrong():
                    self._v_message.set("Wrong")
                else:
                    self._v_message.set("Right")
            else:
                self._v_message.set('')
            if reply is None:
                return
            self._model.do_move(*reply)
            self._board_widget.update_board()

    def to_move(self):
        return self._fix_color(self._model.to_move())

    def last_move(self):
        lm = self._model.last_move()
        if lm:
            lmx, lmy = lm
            return self._to_board(lmx, lmy)
        else:
            return None

    def open_collection(self, directory):
        # FIXME
        self._directory = directory
        self._collection = [f for f in listdir(directory)
                if isfile(join(directory, f))]

    def next_problem(self):
        assert(self._v_message)
        # FIXME
        l = len(self._collection)
        r = randint(0, l - 1)
        f = open(join(self._directory, self._collection[r]))
        self._problem = Problem(f.read())
        transform = Transform()
        self._to_board = transform.to_board
        self._from_board = transform.from_board
        self._fix_color = transform.fix_color
        self._model = BoardModel()
        if self.to_move() == Color.B:
            self._v_message.set('Black to move')
        else:
            self._v_message.set('White to move')
        self._model.setup_position(self._problem.get_setup())
        self._board_widget.update_board()
