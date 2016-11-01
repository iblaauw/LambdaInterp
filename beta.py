
from tree import *
from bindingstack import BindingStack
from alpha import Renamer

class Bag(object): pass
execute_sentinel = Bag()


class BetaExecuter(object):
    def run(self, tree):
        while True:
            if isapply(tree):
               result = self.runApply(tree)
            elif isfunction(tree):
                result = self.runFunction(tree)
            else:
                return tree

            if result is execute_sentinel:
                tree = execute_sentinel.tree
            else:
                return tree

    def runApply(self, node):
        func = self.run(node.left)
        if func is not node.left:
            node.setLeft(func)

        val = node.right

        if not func.canInvoke(val):
            return node

        result = func.beta_call(val)

        # Now delete the previous tree
        BetaDeleter().run(val)

        execute_sentinel.tree = result
        return execute_sentinel

    def runFunction(self, node):
        result = self.run(node.right)
        if result is not node.right:
            node.setRight(result)
        return node



class BetaCopier(object):
    def __init__(self, tree):
        self.bindings_cache = {}
        self.tree = tree

    def copy(self):
        self.bindings_cache = {}
        return self.tree.traverse(self)

    def apply(self, node, l, r):
        new = ApplyNode()
        new.setLeft(l)
        new.setRight(r)
        return new

    def function(self, node, l, r):
        new = FunctionNode(l, node.to_call)
        new.setRight(r)
        return new

    def bindings(self, node):
        new = BindingsNode(node.name)
        self.bindings_cache[node] = new
        return new

    def bound(self, node):
        old = node.bindingNode
        if old in self.bindings_cache:
            new = self.bindings_cache[old]
        else:
            new = old
        return new.createBoundNode()

    def unbound(self, node):
        return UnboundNode(node.name)

    def macro(self, node):
        return MacroNode(node.macro)

class BetaDeleter(object):
    def run(self, tree):
        self.inner_bindings = set()
        tree.traverse(self)

    def apply(self, node, l, r): pass

    def function(self, node, l, r): pass

    def bindings(self, node): 
        self.inner_bindings.add(node)

    def bound(self, node):
        bind = node.bindingNode
        if bind not in self.inner_bindings:
            bind.delete(node)
            node.bindingNode = None

    def unbound(self, node): pass

    def macro(self, node): pass

def _betaLambdaCaller(func_node, val_node):
    bindings = func_node.left
    copier = BetaCopier(val_node)

    for terminal in bindings.bindings:
        new_copy = copier.copy()
        terminal.expand(new_copy)

    return func_node.right

def createNormalLambda(name):
    bindings = BindingsNode(name)
    func = FunctionNode(bindings, _betaLambdaCaller)
    return func

