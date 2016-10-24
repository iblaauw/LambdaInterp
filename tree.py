
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

    def rename(self, newname):
        self.name = newname
        for node in self.bindings:
            node.name = newname

class TerminalNode(LeafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.bound = False

    def __str__(self):
        if not self.bound:
            return self.name + "^"
        return self.name


def isterminal(node):
    return isinstance(node, TerminalNode)

def isleaf(node):
    return isinstance(node, LeafNode)

def isfunction(node):
    return isinstance(node, FunctionNode)

def isapply(node):
    return isinstance(node, ApplyNode)



