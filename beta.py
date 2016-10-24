
from tree import *
from bindingstack import BindingStack

class Bag(object): pass
execute_sentinel = Bag()

class BetaExecuter(object):
    def __init__(self):
        self.binder = BindingStack()

    def run(self, tree):
        while True:
            if isapply(tree):
                val = self.runApply(tree)
            elif isfunction(tree):
                val = self.runFunction(tree)
            else:
                val = self.runTerminal(tree)

            if val is execute_sentinel:
                tree = execute_sentinel.tree
            else:
                return val

    def runApply(self, node):
        self.run(node.left)

        if isfunction(node.left):
            newTree = self.execute(node)
            execute_sentinel.tree = newTree
            return execute_sentinel

        return node

    def runFunction(self, node):
        self.binder.push(node)
        self.run(node.right)
        self.binder.pop(node)

        return node

    def runTerminal(self, node):
        return node

    def execute(self, applyNode):
        func = applyNode.left
        bindingNode = func.left
        bindings = bindingNode.bindings
        arg = applyNode.right

        copier = BetaCopier(self.binder)

        for node in bindings:
            newtree = copier.run(arg)
            self.replace(node, newtree)

        funcBody = func.right
        self.replace(applyNode, funcBody)
        return funcBody

    def replace(self, original, new):
        parent = original.parent

        if parent is None:
            return

        isleft = parent.left is original
        if isleft:
            parent.setLeft(new)
        else:
            parent.setRight(new)


class BetaCopier(object):
    def __init__(self, binder):
        self.bindings_cache = {}
        self.bindings_position = {}
        self.binder = binder

    def run(self, tree):
        return tree.copy(self)

    def copyBindings(self, bindingNode):
        name = bindingNode.name

        new = BindingsNode(name)
        for i in range(len(bindingNode.bindings)):
            node = TerminalNode(name)
            new.bind(node)

        self.bindings_cache[bindingNode] = new
        self.bindings_position[bindingNode] = 0
        return new

    def copyTerminal(self, node):
        assert node.bound == True
        original_bind = node.bindingNode
        new_bind = self.bindings_cache[original_bind]
        new_pos = self.bindings_position[original_bind]

        val = new_bind.bindings[new_pos]

        self.bindings_position[original_bind] += 1

        return val

    def try_bind(self, node):
        self.binder.try_bind(node)
        pass


