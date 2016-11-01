
from tree import isfunction, TraverseBase


def get_top_cache(tree):
    traverser = MacroTraverse()
    tree.traverse(traverser)
    return NameCache(traverser.names)

def alphaReduce(node1, node2, top_cache):
    # Get all names in the left subtree
    leftNames = NameCache(top_cache)
    node1.traverse(NameFinder(leftNames))

    # Rename the right subtree based on those names
    node2.traverse(Renamer(leftNames))


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



class NameCache(object):
    def __init__(self, parent):
        self.parent = parent
        self.stack = []

    def push(self, name):
        self.stack.append(name)

    def pop(self):
        val = self.stack.pop()
        return val

    def __contains__(self, val):
        if val in self.stack:
            return True
        return val in self.parent

class MacroTraverse(TraverseBase):
    def __init__(self):
        super().__init__()
        self.names = set()

    def macro(self, node):
        self.names.add(node.name)

class NameFinder(TraverseBase):
    def __init__(self, cache):
        super().__init__()
        self.cache = cache

    def bindings(self, node):
        self.cache.push(node.name)

    def unbound(self, node):
        self.cache.push(node.name)

    def macro(self, node):
        self.cache.push(node.name)

class Renamer(TraverseBase):
    def __init__(self, cache):
        super().__init__()
        self.cache = NameCache(cache)
        self.name = "a"
        self.getNextName()

    def bindings(self, node):
        if node.name in self.cache:
            node.rename(self.name)
            self.cache.push(self.name)
            self.getNextName()

    def getNextName(self):
        while self.name in self.cache:
            self.name = _nameIncr(self.name)

#class Renamer(object):
#    def __init__(self):
#        self.used = set()
#        self.name = 'a'
#
#    def push(self, func):
#        if not isfunction(func):
#            raise TypeError("Can only push a function node onto a renamer.")
#
#        name = func.left.name
#        self.used.add(name)
#        if name == self.name:
#            self.incr_name()
#
#    def renameFunc(self, func):
#        if not isfunction(func):
#            raise TypeError("Can only push a function node onto a renamer.")
#
#        name = func.left.name
#        if name in self.used:
#            func.left.rename(self.name)
#            self.used.add(self.name)
#            self.incr_name()
#
#    def renameTerminal(self, terminal):
#        if terminal.bound:
#            return
#
#        if terminal.name in self.used:
#            terminal.name = self.name
#            self.used.add(self.name)
#            self.incr_name()
#
#    def incr_name(self):
#        self.name = _nameIncr(self.name)
#        while self.name in self.used:
#            self.name = _nameIncr(self.name)


