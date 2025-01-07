import ast
import logging
import os

from model import (File, UserDefinedFunc , Call, UserDefinedClass,
                    Variable, LogicStatement)

AstControlType = [ast.If , ast.Try]

UNKOWN_VAR = 'unknown'

def djoin(*tup):
    """
    Convenience method to join strings with dots
    :rtype: str
    """
    if len(tup) == 1 and isinstance(tup[0], list):
        return '.'.join(tup[0])
    return '.'.join(tup)

def get_call_from_func_element(func):
    """
    Given a python ast that represents a function call, clear and create our
    generic Call object. Some calls have no chance at resolution (e.g. array[2](param))
    so we return nothing instead.

    :param func ast:
    :rtype: Call|None
    """
    assert type(func) in (ast.Attribute, ast.Name, ast.Subscript, ast.Call , ast.BinOp)
    if type(func) == ast.Attribute:
        owner_token = []
        val = func.value
        while True:
            try:
                owner_token.append(getattr(val, 'attr', val.id))
            except AttributeError:
                pass
            val = getattr(val, 'value', None)
            if not val:
                break
        if owner_token:
            owner_token = djoin(*reversed(owner_token))
        else:
            owner_token = UNKOWN_VAR
        return Call(func=func.attr, line_number=func.lineno, parent_token=owner_token)
    if type(func) == ast.Name:
        return Call(func=func.id, line_number=func.lineno, parent_token = None)
    if type(func) in (ast.Subscript, ast.Call):
        return None

def process_assign(element):
    """
    Process an assignment AST node to extract variables and associated calls.
    Handles nested binary operations like `&`.
    
    :param element: An `Assign` node from the AST.
    :return: A list of Variable instances or an empty list if no valid assignment is found.
    """
    def extract_calls(value):
        """Recursively extract all calls and attributes from a BinOp."""
        calls = []
        if isinstance(value, ast.BinOp):  # Handle nested binary operations
            calls.extend(extract_calls(value.left))
            calls.extend(extract_calls(value.right))
        elif isinstance(value, ast.Call):  # Handle function calls
            calls.append(get_call_from_func_element(value.func))
        elif isinstance(value, ast.Attribute):  # Handle attributes like `dict.keys`
            calls.append(get_call_from_func_element(value))
        elif isinstance(value, ast.Name):  # Handle simple variable names
            calls.append(value.id)  # Add the variable name
        return calls

    def extract_targets(target):
        """Recursively extract all variable names from assignment targets."""
        variables = []
        if isinstance(target, ast.Name):  # Handle simple variable names
            variables.append(target.id)
        elif isinstance(target, ast.Tuple):  # Handle tuple unpacking
            for elt in target.elts:  # Recursively process tuple elements
                variables.extend(extract_targets(elt))
        return variables
    
    if not isinstance(element.value, (ast.BinOp, ast.Call, ast.Attribute)):
        return []  # Ignore non-call or non-operation assignments

    calls = extract_calls(element.value)
    if not calls:  # No valid calls extracted
        return []

    ret = []
    for target in element.targets:
        # Extract all variable names from the target
        variable_names = extract_targets(target)
        for token in variable_names:
            ret.append(Variable(token, calls, element.lineno))
        
    return ret

def make_operations(lines , is_root=False):
    operation = []
    for tree in lines:
        if is_root and check_rootnode(tree):
            return make_operations(tree.body)
        elif type(tree) == ast.Assign:
            operation.append(process_assign(tree))
        elif type(tree) in AstControlType:
            line_no = tree.lineno
            if type(tree) == ast.Try:
                cond_type = 'try'
            else:
                cond_type = 'if'
            subtree = tree.body
            process = make_operations(subtree)
            logic_inst = LogicStatement(cond_type , process, line_no)
            operation.append(logic_inst)
        else:
            if type(tree) == ast.Expr and type(tree.value) == ast.Call:
                call = get_call_from_func_element(tree.value.func)
                if call:
                    operation.append(call)
    return operation # return a list of  List[Tuple( [Call | Variables | Logic Statement ] , corresponding ast tree)]

def get_inherits(tree):
    """
    Get what superclasses this class inherits
    This handles exact names like 'MyClass' but skips things like 'cls' and 'mod.MyClass'
    Resolving those would be difficult
    :param tree ast:
    :rtype: list[str]
    """
    return [base.id for base in tree.bases if type(base) == ast.Name]

def check_rootnode(node):
    if isinstance(node, ast.If):  # Check if it's an `If` node
        # Check if the test is a comparison: __name__ == "__main__"
        if (
            isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.Eq)
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value == "main"
        ):
            return True
    return False

def make_constant(tree):
    result_list = []

    for el in tree:
        # Check for assignment of constants, dicts, lists, or tuples
        if isinstance(el, ast.Assign):
            # Iterate through all targets in the assignment
            for target in el.targets:
                # Ensure the target is a variable (ast.Name)
                if isinstance(target, ast.Name):
                    result_list.append(target.id)  # Append the variable name

    return result_list
        
def make_attribute(tree):
    attr = []
    def extract_self_attributes(node):
        """Recursively extract self attributes from any node."""
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                    attr.append(target.attr)
        # Recursively handle child nodes
        for child in ast.iter_child_nodes(node):
            extract_self_attributes(child)

    for statement in tree.body:
        extract_self_attributes(statement)
    return attr

def make_function_io(tree):
    """
    Extract input arguments and output values from all functions in the given Python code.

    Args:
        code (str): The source code as a string.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
              - "inputs": List of input argument names
              - "outputs": List of output variable names or expressions
    """
    input_list = [arg.arg for arg in tree.args.args]
    # Extract output values
    output_list = []
    for stmt in tree.body:
        if isinstance(stmt, ast.Return):
            if isinstance(stmt.value, ast.Tuple):  # Multiple return values
                output_list = [el.id for el in stmt.value.elts]
            elif isinstance(stmt.value, ast.Call):
                output_list =  [get_call_from_func_element(stmt.value)]
            elif stmt.value:  # Single return value
                output_list = [stmt.value.id]

    return input_list , output_list

class Python():
    @staticmethod
    def get_tree(filename):
        """
        Get the entire AST for this file

        :param filename str:
        :rtype: ast
        """
        try:
            with open(filename) as f:
                raw = f.read()
        except ValueError:
            with open(filename, encoding='UTF-8') as f:
                raw = f.read()
        return ast.parse(raw)

    @staticmethod
    def separate_namespaces(tree):
        """
        Given an AST, recursively separate that AST into lists of ASTs for the
        subgroups, nodes, and body. This is an intermediate step to allow for
        cleaner processing downstream

        :param tree ast:
        :returns: tuple of group, node, and body trees. These are processed
                  downstream into real Groups and Nodes.
        :rtype: (list[ast], list[ast], list[ast])
        """
        groups = []
        nodes = []
        body = []
        import_list = [] # this is import from same file 
        for el in tree.body:
            if type(el) in (ast.FunctionDef, ast.AsyncFunctionDef):
                nodes.append(el)
            elif type(el) == ast.ClassDef:
                groups.append(el)
            elif getattr(el, 'body', None):
                body.append(el)
            elif type(el) in (ast.Import , ast.ImportFrom):
                import_list.append(el)
            else:
                body.append(el)
        return groups, nodes, body , import_list
    
    @staticmethod
    def make_function(tree, parent):
        """
        Given an ast of all the lines in a function, create the node along with the
        calls and variables internal to it.

        :param tree ast:
        :param parent Group:
        :rtype: list[Node]
        """

        token = tree.name
        print(token)
        line_number = tree.lineno
        input_list , output_list = make_function_io(tree)
        processes = make_operations(tree.body)
        docstring = ast.get_docstring(tree)
        
        print("PROCESS START ")
        for pro in processes:
            if isinstance(pro, LogicStatement):
                print(pro)
                for i in pro.process:
                    print(i)
            else:
                print(pro)
        print("PROCESS END")

        return UserDefinedFunc(
            token, 
            processes , 
            line_number, 
            docstring, 
            input_list , 
            output_list
        )
    
    @staticmethod
    def make_class(tree,parent):
        assert type(tree) == ast.ClassDef
        _, node_trees, _ , _ = Python.separate_namespaces(tree)

        token = tree.name
        print("Class name",token)
        line_number = tree.lineno
        inherits = get_inherits(tree) 

        class_group = UserDefinedClass(token,line_number, inherits)
        for node_tree in node_trees:
            if isinstance(class_group, UserDefinedClass) and node_tree.name in ['__init__', '__new__']:
                class_group.assign_attribute(make_attribute(node_tree))
            else:
                class_group.add_function(Python.make_function(node_tree , parent=class_group))

        # NEXT PR NESTED CLASS
        return class_group

    @staticmethod
    def make_root_node(tree):
        return make_operations(tree, True), make_constant(tree)

    @staticmethod
    def make_import(trees):
        import_list = []
    
        for import_tree in trees:
            if isinstance(import_tree, ast.ImportFrom):
                # only importing from the same repo matters so no need to have import 
                # first filter
                for alias in import_tree.names:
                    import_list.append({
                        'from': import_tree.module, 
                        'function': alias.name, 
                        'as': alias.asname
                    })
        
        return import_list