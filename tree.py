
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

class FunctionNode(Node):
    def __init__(self, name):
        super().__init__()
        self.setLeft(BindingsNode(name))

    def copy(self, beta):
        new = FunctionNode(self.left.name)
        new.setLeft(self.left.copy(beta))
        new.setRight(self.right.copy(beta))
        return new

    def __str__(self):
        return "L" + self.left.name + ". " + str(self.right)

class LeafNode(Node):
    def setLeft(self, node):
        raise RuntimeError("Error: cannot give children to a leaf node.")

    def setRight(self, node):
        raise RuntimeError("Error: cannot give children to a leaf node.")

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

    def rename(self, newname):
        self.name = newname
        for node in self.bindings:
            node.name = newname

    def copy(self, beta):
        return beta.copyBindings(self)

class TerminalNode(LeafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.bound = False
        self.bindingNode = None

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

def isterminal(node):
    return isinstance(node, TerminalNode)

def isleaf(node):
    return isinstance(node, LeafNode)

def isfunction(node):
    return isinstance(node, FunctionNode)

def isapply(node):
    return isinstance(node, ApplyNode)



