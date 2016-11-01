
from tree import isfunction

def _setChar(string, index, val):
    if index < 0 or index >= len(string):
        raise ValueError("Index out of range: {0}.".format(index))

    before = string[:index]
    after = string[index+1:]
    return before + val + after

def _nameIncr(name, index=None):
    if index == None:
        index = len(name) - 1

    char = name[index]
    if char == 'z':
        if index == 0:
            return 'a'*(len(name) + 1)
        return _nameIncr(name, index - 1)

    new_char = chr(ord(char) + 1)
    return _setChar(name, index, new_char)

class Renamer(object):
    def __init__(self):
        self.used = set()
        self.name = 'a'

    def push(self, func):
        if not isfunction(func):
            raise TypeError("Can only push a function node onto a renamer.")

        name = func.left.name
        self.used.add(name)
        if name == self.name:
            self.incr_name()

    def renameFunc(self, func):
        if not isfunction(func):
            raise TypeError("Can only push a function node onto a renamer.")

        name = func.left.name
        if name in self.used:
            func.left.rename(self.name)
            self.used.add(self.name)
            self.incr_name()

    def renameTerminal(self, terminal):
        if terminal.bound:
            return

        if terminal.name in self.used:
            terminal.name = self.name
            self.used.add(self.name)
            self.incr_name()

    def incr_name(self):
        self.name = _nameIncr(self.name)
        while self.name in self.used:
            self.name = _nameIncr(self.name)


