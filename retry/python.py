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
    assert type(func) in (ast.Attribute, ast.Name, ast.Subscript, ast.Call)
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
    Given an element from the ast which is an assignment statement, return a
    Variable that points_to the type of object being assigned. For now, the
    points_to is a string but that is resolved later.

    :param element ast:
    :rtype: Variable
    """

    if type(element.value) != ast.Call and type(element.value) != ast.Constant:
        return []
    
    call = None
    if type(element.value) == ast.Constant:
        call = element.value.value
    else:
        call = get_call_from_func_element(element.value.func)
    
    if call == None:
        return []

    ret = []
    for target in element.targets:
        if type(target) != ast.Name:
            continue
        token = target.id
        ret.append(Variable(token, call, element.lineno))
    return ret

def make_operations(lines):
    operation = []
    for tree in lines:
        if type(tree) == ast.Assign:
            operation.append((process_assign(tree), tree))
        elif type(tree) in AstControlType:
            line_no = tree.lineno
            if type(tree) == ast.Try:
                cond_type = 'try'
            else:
                cond_type = 'if'
            subtree = tree.body
            process = make_operations(subtree)
            logic_inst = LogicStatement(cond_type , process, line_no)
            operation.append((logic_inst, tree))
        else:
            if type(tree) == ast.Expr and type(tree.value) == ast.Call:
                call = get_call_from_func_element(tree.value.func)
                if call:
                    operation.append((call , tree))
            else:
                print(ast.unparse(tree))
                operation.append((ast.unparse(tree), tree))
    return operation
    raise NotImplementedError # return a list of  List[Tuple( [Call | Variables | Logic Statement ] , corresponding ast tree)]

def get_inherits(tree):
    """
    Get what superclasses this class inherits
    This handles exact names like 'MyClass' but skips things like 'cls' and 'mod.MyClass'
    Resolving those would be difficult
    :param tree ast:
    :rtype: list[str]
    """
    return [base.id for base in tree.bases if type(base) == ast.Name]

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
        for el in tree.body:
            if type(el) in (ast.FunctionDef, ast.AsyncFunctionDef):
                nodes.append(el)
            elif type(el) == ast.ClassDef:
                groups.append(el)
            elif getattr(el, 'body', None):
                body.append(el)
            elif type(el) in (ast.Import , ast.ImportFrom):
                continue
                # Current target is single File NEXT PR import_list.append(el)
            else:
                body.append(el)
        return groups, nodes, body
    
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
        line_number = tree.lineno
        processes = make_operations(tree.body)

        if isinstance(parent, UserDefinedClass) and token in ['__init__', '__new__']:
            return UserDefinedFunc(token, processes , line_number=line_number), True
        
        return UserDefinedFunc(token, processes , line_number=line_number), False
    
    @staticmethod
    def make_class(tree, parent):
        assert type(tree) == ast.ClassDef
        _, node_trees, _ = Python.separate_namespaces(tree)

        token = tree.name
        line_number = tree.lineno
        inherits = get_inherits(tree) 

        class_group = UserDefinedClass(token,line_number, inherits)
        for node_tree in node_trees:
            class_group.add_function(Python.make_function(node_tree , parent=class_group))

        # NEXT PR NESTED CLASS
        return class_group
