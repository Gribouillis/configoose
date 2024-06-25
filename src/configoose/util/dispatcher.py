#!/usr/bin/env python
# SPDX-FileCopyrightText: 2023 Eric Ringeisen
# SPDX-License-Identifier: MIT
"""An implementation of the dispatcher pattern in Python
that is compatible with class inheritance.
"""

from collections import ChainMap
from functools import partial
from weakref import WeakKeyDictionary

__version__ = "2023.08.07.2"


def _table_decorator(table, key, value):
    table[key] = value
    return value


class Table(ChainMap):
    def setitem(self, key):
        return partial(_table_decorator, self, key)

    __call__ = setitem


class PolymorphicDispatcher:
    def __init__(self):
        self._table_dict = WeakKeyDictionary()

    def __get__(self, obj, cls):
        # ignore obj, this is a class feature
        return self.table(cls)

    def table(self, cls):
        try:
            table = self._table_dict[cls]
        except KeyError:
            m = Table()
            for c in cls.mro()[1:]:
                m.maps.append(self.table(c).maps[0])
            table = self._table_dict[cls] = m
        return table


if __name__ == "__main__":

    class Spam:
        on = PolymorphicDispatcher()

        def react(self, key):
            return self.on[key](self)

    @Spam.on.setitem("foo")
    def somefoo(self):
        print(f"somefoo: {self}")

    class Ham(Spam):
        pass

    @Ham.on.setitem("bar")
    def somebar(self):
        print(f"somebar: {self}")

    spam = Spam()
    spam.react("foo")

    ham = Ham()
    ham.react("foo")
    ham.react("bar")
