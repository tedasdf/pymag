import os 



class File():
    """
    Files
    """
    def __init__(self, token, file_path):
        self.token = token
        self.file_path = file_path
        self.func_list = [] #  list of func instantiated 
        self.classes_list = [] # List of class instantiated
        self.constant_list = []
        self.root_node = None
        self.imported_list = []
    
    def add_func_list(self, new_func):
        self.func_list.append(new_func)
    
    def add_classes_list(self , new_class):
        self.classes_list.append(new_class)
    
    def all_func(self):
        return self.func_list
    
    def all_classes(self):
        return self.classes_list
    
    def all_symbols(self):
        symbol_list = self.func_list + self.classes_list
        return symbol_list

class UserDefinedClass():
    """
        User Define Classes
    """
    def __init__(self, token, line_number , inherits):
        self.token = token
        self.line_number = line_number
        self.functions = []
        self.attribute = []
        self.inherits = inherits
    
    def __repr__(self):
        return f"<UserDefineClass attribute={self.attribute} token={self.token} line_no={self.line_number} self.function={self.functions} inherit={self.inherits}>"
   
    def add_function(self, new_func):
        self.functions.append(new_func)
    
    def assign_attribute(self, attr):
        self.attribute = attr
    
    def all_symbols(self):
        #provide useable symbol within the class
        raise NotImplementedError

class UserDefinedFunc():
    """
        User Define Functions
    """
    def __init__(self, token, process , line_number, docstring ,input_list, output_list):
        self.token = token
        self.process = process #  List[Tuple( [Call | Variables | Logic Statement ] , corresponding ast tree)]
        self.line_number = line_number
        self.docstring = docstring
        # self.return = 
        self.input_list =  input_list
        self.output_list = output_list
    
    def __repr__(self):
        return (
            f"UserDefinedFunc("
            f"token={self.token!r}, "
            f"line_number={self.line_number}"
            f")"
        )


class LogicStatement():
    def __init__(self, condition_type , process, line_no):
        self.condition_type = condition_type
        # NEXT PR self.condition = condition # { left : Op : Right } for example if __name__ == "__main__" {__name__ : == : "__main__"}
        self.process = process #  List[Tuple( [Call | Variables | Logic Statement ] , corresponding ast tree)]
        self.line_no = line_no
        # self.init_cond = init_cond NEXT PR 
    
    def __iter__(self):
        return iter(self.process)
    
    def has_call(self):
        return any(type(i.has_call() for i, _ in self.process))
    
    def extract_process(self):
        process = []    
        string_inst = ""
        for pro in self.process:
            if isinstance(pro, str):
                string_inst += pro
            elif isinstance(pro, LogicStatement):
                process.append(pro.process)
            else:
                if string_inst != "":
                    process.append(string_inst)
                    string_inst = ""
                else:
                    process.append(pro)
        self.process = process

class Call():
    """
    Calls represent function call expressions.
    They can be an attribute call like
        object.do_something()
    Or a "naked" call like
        do_something()
    """
    def __init__(self, parent_token , func, line_number=None):
        self.func = func
        self.line_number = line_number
        self.parent_token = parent_token
    
    def __repr__(self):
        return f"<Call func={self.func} line_no={self.line_number} parent_token={self.parent_token}>"

    def has_call(self):
        return True
    
class Variable():
    """
    Variables represent named tokens that are accessible to their scope.
    They may either point to a string or, once resolved, a Group/Node.
    Not all variables can be resolved
    """
    def __init__(self, token, points_to, line_number=None):
        """
        :param str token:
        :param str|Call|Node|Group points_to: (str/Call is eventually resolved to Nodes|Groups)
        :param int|None line_number:
        """
        assert token
        self.token = token
        self.points_to = points_to
        self.line_number = line_number

    def __repr__(self):
        return f"Variable token={self.token} point_to={self.points_to} line_no={self.line_number}"

    def has_call(self):
        raise isinstance(self.points_to, Call)