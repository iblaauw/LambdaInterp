
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

    def canInvoke(self, val):
        return False


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

    def traverse(self, tt):
        l = self.left.traverse(tt)
        r = self.right.traverse(tt)
        return tt.apply(self, l, r)

class FunctionNode(Node):
    def __init__(self, bindings, to_call):
        super().__init__()
        self.setLeft(bindings)
        self.to_call = to_call

    def __str__(self):
        return "L" + self.left.name + ". " + str(self.right)

    def traverse(self, tt):
        l = self.left.traverse(tt)
        r = self.right.traverse(tt)
        return tt.function(self, l, r)

    def canInvoke(self, val):
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

    def createBoundNode(self):
        node = BoundNode(self)
        self.bindings.append(node)
        return node

    def delete(self, node):
        self.bindings.remove(node)


    def rename(self, newname):
        self.name = newname

    def traverse(self, tt):
        return tt.bindings(self)

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


