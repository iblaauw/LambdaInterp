
from tree import *
from bindingstack import BindingStack
from alpha import Renamer

class Bag(object): pass
execute_sentinel = Bag()

#class BetaExecuter(object):
#    def __init__(self):
#        self.binder = BindingStack()
#        self.renamer = Renamer()
#
#    def run(self, tree):
#        while True:
#            if isapply(tree):
#                val = self.runApply(tree)
#            elif isfunction(tree):
#                val = self.runFunction(tree)
#            else:
#                val = self.runTerminal(tree)
#
#            if val is execute_sentinel:
#                tree = execute_sentinel.tree
#            else:
#                return val
#
#    def runApply(self, node):
#        self.run(node.left)
#
#        if isfunction(node.left):
#            newTree = self.execute(node)
#            execute_sentinel.tree = newTree
#            return execute_sentinel
#
#        return node
#
#    def runFunction(self, node):
#        self.renamer.push(node)
#        self.binder.push(node)
#        self.run(node.right)
#        self.binder.pop(node)
#
#        return node
#
#    def runTerminal(self, node):
#        return node
#
#    def execute(self, applyNode):
#        print("APPLY: ", applyNode)
#        func = applyNode.left
#        bindingNode = func.left
#        bindings = bindingNode.bindings
#        arg = applyNode.right
#
#        copier = BetaCopier(self.binder)
#
#        arg.alphaExec(self.renamer) # Do alpha reduction
#
#        for node in bindings:
#            newtree = copier.run(arg)
#            self.replace(node, newtree)
#
#        funcBody = func.right
#        self.replace(applyNode, funcBody)
#        return funcBody
#
#    def replace(self, original, new):
#        parent = original.parent
#
#        if parent is None:
#            return
#
#        isleft = parent.left is original
#        if isleft:
#            parent.setLeft(new)
#        else:
#            parent.setRight(new)
#
#
#class BetaCopier(object):
#    def __init__(self, binder):
#        self.bindings_cache = {}
#        self.bindings_position = {}
#        self.binder = binder
#
#    def run(self, tree):
#        return tree.copy(self)
#
#    def copyBindings(self, bindingNode):
#        name = bindingNode.name
#
#        new = BindingsNode(name)
#        for i in range(len(bindingNode.bindings)):
#            node = TerminalNode(name)
#            new.bind(node)
#
#        self.bindings_cache[bindingNode] = new
#        self.bindings_position[bindingNode] = 0
#        return new
#
#    def copyTerminal(self, node):
#        assert node.bound == True
#
#        original_bind = node.bindingNode
#        if original_bind not in self.bindings_cache:
#            # This terminal is bound to a function outside the current copied body
#            new_node = TerminalNode(node.name)
#            if node.bindIndex == -1:
#                original_bind.bind(new_node)
#            else:
#                original_bind.bind_replace(new_node, node.bindIndex)
#                node.bindIndex = -1
#
#            return new_node
#        else:
#            new_bind = self.bindings_cache[original_bind]
#            new_pos = self.bindings_position[original_bind]
#
#            val = new_bind.bindings[new_pos]
#
#            self.bindings_position[original_bind] += 1
#
#            return val
#
#    def try_bind(self, node):
#        self.binder.try_bind(node)


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

        if not func.canInvoke():
            return node

        val = node.right
        result = func.beta_call(val)
        execute_sentinel.tree = result
        return execute_sentinel

    def runFunction(self, node):
        result = self.run(node.right)
        if result is not node.right:
            node.setRight(result)
        return node



class BetaCopier(object):
    def run(self, tree):
        self.bindings_cache = {}
        return tree.traverse(self)

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
        new = self.bindings_cache[old]
        return new.createBoundNode()

    def unbound(self, node):
        return UnboundNode(node.name)

    def macro(self, node):
        return MacroNode(node.macro)

def _betaLambdaCaller(func_node, val_node):
    bindings = func_node.left
    copier = BetaCopier()

    for terminal in bindings.bindings:
        new_copy = copier.run(val_node)
        terminal.expand(new_copy)

    return func_node.right

def createNormalLambda(name):
    bindings = BindingsNode(name)
    func = FunctionNode(bindings, _betaLambdaCaller)
    return func

