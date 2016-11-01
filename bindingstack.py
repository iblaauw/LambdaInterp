
from tree import *

class BindingStack(object):
    def __init__(self):
        self.bindings = {}

    def push(self, node):
        if not isfunction(node):
            raise TypeError("Can only push a lambda onto a bindings stack.")

        binding = node.left
        name = binding.name

        stack = self.bindings.get(name, None)
        if stack is None:
            stack = []
            self.bindings[name] = stack

        stack.append(binding)

    def pop(self, node):
        if not isfunction(node):
            raise TypeError("Can only push a lambda onto a bindings stack.")

        binding = node.left
        name = binding.name

        stack = self.bindings[name]
        if len(stack) == 0:
            raise ValueError("Cannot pop node, it was never pushed.")

        val = stack[-1]

        if val is not binding:
            raise ValueError("Cannot pop node, it was never pushed.")

        stack.pop()

    def createTerminal(self, name):
        bindings = self._getBindings(name)
        if bindings is None:
            return UnboundNode(name)
        else:
            return bindings.createBoundNode()

        # TODO: add macros here

    def _getBindings(self, name):
        stack = self.bindings.get(name, None)
        if stack is None or len(stack) == 0:
            return None
        return stack[-1]


    # def try_bind(self, node):
    #     if not isterminal(node):
    #         raise TypeError("Can only bind a variable with the bindings stack.")

    #     name = node.name
    #     stack = self.bindings.get(name, None)
    #     if stack is None or len(stack) == 0:
    #         return

    #     stack[-1].bind(node)


