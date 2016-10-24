
#########################
# Tokens and tokenizing #
#########################

from tree import *
from bindingstack import BindingStack

binder = BindingStack()

def parse(instream):
    reader = WordReader(instream)
    result = do_parse(reader)

    if reader.current() is not None:
        print("Unexpected tokens after end of expression.", reader.current())
        return None

    return result


def do_parse(reader):
    current = None
    while True:
        if reader.current() is None:
            return current

        if reader.current() == ")":
            return current

        if current is None:
            current = parse_nonapply(reader)
            if current is None:
                return None
        else:
            newval = parse_nonapply(reader)
            if newval is None:
                return None

            node = ApplyNode()
            node.setLeft(current)
            node.setRight(newval)
            current = node


def parse_nonapply(reader):
    word = reader.current()
    assert word is not None
    assert len(word) > 0

    if word[0] == 'L':
        return parseFunc(reader)
    elif word == "(":
        return parseParens(reader)
    else:
        return parseIdentifier(reader)


def parseFunc(reader):
    word = reader.current()
    assert len(word) > 0 and word[0] == 'L'

    reader.getNext() # eat word

    if len(word) == 1:
        name = require_name(reader)
        if name is None:
            return None
    else:
        name = word[1:]

    if require_dot(reader) is None:
        return None

    func = FunctionNode(name)

    binder.push(func)
    body = do_parse(reader)
    binder.pop(func)

    if body is None:
        return None

    func.setRight(body)
    return func


def parseIdentifier(reader):
    name = require_name(reader)
    if name is None:
        return None

    node = TerminalNode(name)
    binder.try_bind(node)

    return node

def parseParens(reader):
    word = reader.current()
    assert word == "("

    reader.getNext() # eat the paren
    result = do_parse(reader)

    if require_close_paren(reader) is None:
        return None

    return result


def require_name(reader):
    word = reader.current()
    reader.getNext()

    if word is None:
        print("Unexpected end of file! Expecting a name.")

    if word == 'L':
        print("Expected variable name. Got lambda expression.")
        return None

    if word in _special_chars:
        print("Invalid variable name '{0}'.".format(word))
        return None

    return word

def require_dot(reader):
    word = reader.current()
    reader.getNext()

    if word is None:
        print("Unexpected end of file! Expecting a period after lambda declaration.")
        return None

    if word != ".":
        print("Expecting a period. Got '{0}'.".format(word))
        return None

    return word

def require_close_paren(reader):
    word = reader.current()
    reader.getNext()

    if word is None:
        print("Unexpected end of file! Expecting a closing parenthesis.")
        return None

    if word != ")":
        print("Expecting a closing parenthesis. Got '{0}'.".format(word))
        return None

    return word


_special_chars = set(['^', ':', '=', '(', ')', '.'])

class WordReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.sent = []
        self.word = None
        self.getNext()

    def current(self):
        return self.word

    def getNext(self):
        while len(self.sent) <= 0:
            line = self.stream.readline()
            if line == '': # EOF
                self.word = None
                self.sent = []
                return None

            self.sent = self.doSplit(line)

        self.word = self.sent[0]
        del self.sent[0]
        return self.word

    def doSplit(self, line):
        line = line.strip()
        vals = []

        initial = line.split()
        for word in initial:
            while True:
                flag = False
                for i in range(len(word)):
                    char = word[i]
                    if char in _special_chars:
                        if i != 0:
                            vals.append(word[:i])
                        vals.append(char)
                        word = word[i+1:]
                        flag = True
                        break
                if not flag:
                    if len(word) > 0:
                        vals.append(word)
                    break

        return vals



