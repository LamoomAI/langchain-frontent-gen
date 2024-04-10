
import re


class TreeNode:
    def __init__(self, name, parent=None):
        self.name: str = name
        self.parent = parent
        self.children = []

    def create_child(self, name: str):
        child = TreeNode(name, parent=self)
        self.children.append(child)
        return child

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

    def __str__(self, level=0):
        ret = "\t"*level + repr(self.name) + "\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return f'{self.name}, parent: {self.parent}'
    
    def pre_order_traverse(self, level=0):
        indent = '  ' * level
        print(f'{indent}{self.name}')
        for child in self.children:
            child.pre_order_traverse(level + 1)

    def find_node_by_name(self, target_name: str):
        if self.name == target_name:
            return self
        for child in self.children:
            found = child.find_node_by_name(target_name)
            if found is not None:
                return found
        return None
    
    def find_node_by_name_regex(self, pattern):
        if re.match(pattern, self.name):
            yield self
        for child in self.children:
            yield from self.find_node_by_name_regex(child, pattern)


# ! DOESN'T WORK PROPERLY
# def build_tree_from_indent(text) -> DomNode:
#     lines = text.strip().split('\n')
#     root = DomNode(name="root")
#     stack = [root]

#     prev_indentation = 0
#     prev_parent = None
#     for line in lines:
#         indentation = len(line) - len(line.lstrip())
#         name = line.strip()
#         while len(stack) > indentation + 1:
#             stack.pop()
#         node = stack[-1].create_child(name)
#         stack.append(node)
#         prev_indentation = indentation

#     return root.children[0]  # Return the root of the tree

def build_tree_from_indented_text(text: str) -> TreeNode:
    lines = text.strip().split('\n')
    stack = []
    root = None
    indentation_step = len(lines[1]) - len(lines[1].lstrip()) or 2

    for line in lines:
        indentation_level = 0
        while line[indentation_level] == ' ':
            indentation_level += 1

        # Calculate the current depth based on the indentation level
        current_depth = indentation_level // indentation_step  # Assuming two spaces per indentation level

        # Remove the indentation from the line
        name = line[indentation_level:].strip()

        # Create a new node
        node = TreeNode(name)

        # If this is the first node, set it as the root
        if not root:
            root = node
        else:
            # Find the parent at the current depth
            while len(stack) > current_depth:
                stack.pop()
            # Add the new node as a child of the parent
            stack[-1].add_child(node)

        # Push the node onto the stack
        stack.append(node)

    return root

# def build_tree_stripped(text) -> DomNode:
#     lines = text.strip().split('\n')
#     root = DomNode(name="root")
#     stack = [root]

#     for line in lines:
#         # Strip leading hyphens or asterisks
#         line = line.lstrip('-* ')
#         indentation = len(line) - len(line.lstrip())
#         name = line.strip()
#         while len(stack) > indentation + 1:
#             stack.pop()
#         node = stack[-1].add_child(name)
#         stack.append(node)

#     return root.children[0]  # Return the root of the tree