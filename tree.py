
####################################
# Lambda internal structure / tree #
####################################

class Node(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.parent = None

    def setLeft(self, node):
        self.left = node
        node.parent = self

    def setRight(self, node):
        self.right = node
        node.parent = self

    def canInvoke(self):
        return False

    def alphaExec(self, alpha):
        self.left.alphaExec(alpha)
        self.left.alphaExec(alpha)


class ApplyNode(Node):
    def __init__(self):
        super().__init__()

    def copy(self, beta):
        newval = ApplyNode()
        left = self.left.copy(beta)
        right = self.right.copy(beta)
        newval.setLeft(left)
        newval.setRight(right)
        return newval

    def __str__(self):
        paren_l = isfunction(self.left)
        paren_r = not isterminal(self.right)

        val = ""
        if paren_l:
            val += "("
        val += str(self.left)
        if paren_l:
            val += ")"
        val += " "
        if paren_r:
            val += "("
        val += str(self.right)
        if paren_r:
            val += ")"
        return val

    def traverse(self, tt):
        l = self.left.traverse(tt)
        r = self.right.traverse(tt)
        return tt.apply(self, l, r)

class FunctionNode(Node):
    def __init__(self, bindings, to_call):
        super().__init__()
        self.setLeft(bindings)
        self.to_call = to_call

    def copy(self, beta):
        new = FunctionNode(self.left.name)
        new.setLeft(self.left.copy(beta))
        new.setRight(self.right.copy(beta))
        return new

    def alphaExec(self, alpha):
        alpha.renameFunc(self)
        self.right.alphaExec(alpha)

    def __str__(self):
        return "L" + self.left.name + ". " + str(self.right)

    def traverse(self, tt):
        l = self.left.traverse(tt)
        r = self.right.traverse(tt)
        return tt.function(self, l, r)

    def canInvoke(self):
        return True

    def beta_call(self, val):
        return self.to_call(self, val)

class LeafNode(Node):
    def setLeft(self, node):
        raise RuntimeError("Error: cannot give children to a leaf node.")

    def setRight(self, node):
        raise RuntimeError("Error: cannot give children to a leaf node.")

    def expand(self, tree):
        left = self.parent.left is self
        if left:
            self.parent.setLeft(tree)
        else:
            self.parent.setRight(tree)


class BindingsNode(LeafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.bindings = []

    def __getitem__(self, index):
        return self.bindings[index]

    def bind(self, node):
        if not isterminal(node):
            raise TypeError("Can only append terminal nodes to a binding list")
        assert node.name == self.name
        self.bindings.append(node)
        node.bound = True
        node.bindingNode = self
        node.bindIndex = len(self.bindings) - 1

    def createBoundNode(self):
        node = BoundNode(self)
        self.bindings.append(node)
        return node

    def bind_replace(self, node, index):
        if not isterminal(node):
            raise TypeError("Can only bind terminal nodes to a binding list")
        assert node.name == self.name
        self.bindings[index] = node
        node.bound = True
        node.bindingNode = self
        node.bindIndex = index

    def rename(self, newname):
        self.name = newname
        for node in self.bindings:
            node.name = newname

    def copy(self, beta):
        return beta.copyBindings(self)

    def traverse(self, tt):
        return tt.bindings(self)

class TerminalNode(LeafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.bound = False
        self.bindingNode = None
        self.bindIndex = -1

    def __str__(self):
        if not self.bound:
            return self.name + "^"
        return self.name

    def copy(self, beta):
        if self.bound:
            return beta.copyTerminal(self)
        else:
            new = TerminalNode(self.name)
            beta.try_bind(new)
            return new

    def alphaExec(self, alpha):
        alpha.renameTerminal(self)


class BoundNode(LeafNode):
    def __init__(self, binding):
        super().__init__()
        self.bindingNode = binding

    def __str__(self):
        return self.bindingNode.name

    def traverse(self, tt):
        return tt.bound(self)

class UnboundNode(LeafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name + "^"

    def traverse(self, tt):
        return tt.unbound(self)

class MacroNode(LeafNode):
    def __init__(self, macro):
        super().__init__()
        self.macro = macro

    def __str__(self):
        return self.macro.name

    def traverse(self, tt):
        return tt.macro(self)



def isterminal(node):
    return isinstance(node, BoundNode) or isinstance(node, UnboundNode) or isinstance(node, MacroNode)

def isleaf(node):
    return isinstance(node, LeafNode)

def isfunction(node):
    return isinstance(node, FunctionNode)

def isapply(node):
    return isinstance(node, ApplyNode)

def ismacro(node):
    return isinstance(node, MacroNode)


