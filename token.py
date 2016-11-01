
#########################
# Tokens and tokenizing #
#########################

from tree import *
from bindingstack import BindingStack
from beta import createNormalLambda

binder = BindingStack()

def parse(instream):
    #reader = WordReader(instream)

    reader = TokenStream(instream)
    reader.getNext() # advance to the first line

    result = do_parse(reader)

    if reader.current() is not None and result is not None:
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

    func = createNormalLambda(name)

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

    return binder.createTerminal(name)
    # node = TerminalNode(name)
    # binder.try_bind(node)

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

    if word is None:
        print("Unexpected end of file! Expecting a name.")
        return None

    reader.getNext()

    if word == 'L':
        print("Expected variable name. Got lambda expression.")
        return None

    if word in _special_chars:
        print("Invalid variable name '{0}'.".format(word))
        return None

    return word

def require_dot(reader):
    word = reader.current()

    if word is None:
        print("Unexpected end of file! Expecting a period after lambda declaration.")
        return None

    reader.getNext()

    if word != ".":
        print("Expecting a period. Got '{0}'.".format(word))
        return None

    return word

def require_close_paren(reader):
    word = reader.current()

    if word is None:
        print("Unexpected end of file! Expecting a closing parenthesis.")
        return None

    reader.getNext()

    if word != ")":
        print("Expecting a closing parenthesis. Got '{0}'.".format(word))
        return None

    return word


_special_chars = set(['^', ':', '=', '(', ')', '.', '\\'])


class TokenStream(object):
    def __init__(self, stream):
        self.stream = stream
        self.line = None
        self.word = None

    def current(self):
        return self.word

    def getNext(self):
        self.word = self.do_getNext()
        return self.word

    def do_getNext(self):
        while self.line is None or self.line == "\\":
            self.line = self.do_readline()
            if self.line is None:
                return None

        if self.line == '':
            # Signal end of sequence, but prepare a newline for the next call
            self.line = None
            return None 

        if self.line[0] == "\\":
            print("Invalid '\\' character: a backslash must be at the end of a line.")
            self.line = None
            return None

        if self.line[0] == "L":
            return self._consumeFront()

        for i, char in enumerate(self.line):
            if char in _special_chars or char == ' ' or char == '\t':
                if i == 0:
                    assert char != ' '
                    return self._consumeFront()
                return self._consume(i)

        # Return the entire string
        val = self.line
        self.line = ""
        return val

    def do_readline(self):
        line = self.stream.readline()
        if line == '': #EOF
            return None
        return line.strip()

    def _consume(self, i):
        val = self.line[:i]
        self.line = self.line[i:].strip()
        return val

    def _consumeFront(self):
        val = self.line[0]
        self.line = self.line[1:].strip()
        return val


