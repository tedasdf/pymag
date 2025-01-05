import argparse
import copy
import os
import sys
import ast
import httpx
import asyncio

from python import Python
from model import Call, File, UserDefinedClass, Variable, UserDefinedFunc
from db.main import CallModel, FileModel, FunctionModel, VariableModel

def find_index(lst, element):
    if element in lst:
        return lst.index(element)
    return None  # If the element is not found



async def run_post_file(payload):
    # Define the URL of the POST endpoint
    url = "http://127.0.0.1:8000/file"
    
    # Payload to match the FastAPI model

    async with httpx.AsyncClient() as client:
        # Pass source_path as a query parameter and file_group as JSON body
        response = await client.post(
            url, 
            params={"source_path": payload["source_path"]}, 
            json=payload["file_group"]
        )
        print("POST Response:", response.json())

language = Python()

def get_sources_and_language(raw_source_paths):
    """
    Given a list of files and directories, return just files.
    If we are not passed a language, determine it.
    Filter out files that are not of that language

    :param list[str] raw_source_paths: file or directory paths
    :param str|None language: Input language
    :rtype: (list, str)
    """

    individual_files = []
    for source in sorted(raw_source_paths):
        if os.path.isfile(source):
            individual_files.append((source, True))
            continue
        for root, _, files in os.walk(source):
            for f in files:
                individual_files.append((os.path.join(root, f), False))


    sources = set()
    for source, explicity_added in individual_files:
        if explicity_added or source.endswith('.py'):
            sources.add(source)

    if not sources:
        raise AssertionError("Could not find any source files given {raw_source_paths} "
                             "and language {language}.")

    sources = sorted(list(sources))
    return sources

def make_file_group(tree, file_path):
    """
    Given an AST for the entire file, generate a file group complete with
    subgroups, nodes, etc.

    :param tree ast:
    :param file_path str:

    :rtype: File
    """

    subgroup_trees, node_trees, body_trees = language.separate_namespaces(tree)

    token = '.'.join(
        part for part in file_path.replace('.py', '').split('/') if part and part != '..'
    )

    file_inst = File(token)

    # NEXT PR implement nested functino
    for node_tree in node_trees:
        file_inst.add_func_list(language.make_function(node_tree, parent=file_inst))
    # ## NEW VERSION NEXT PR MAKE ROOT NODE FOR FILE GROUP
    # file_grouptest.root_node = language.new_make_root_node(new_body_trees, parent=file_grouptest)

    for subgroup_tree in subgroup_trees:
        file_inst.add_classes_list(language.make_class(subgroup_tree, parent=file_inst))
    
    return file_inst


def main(sys_argv=None):
    """
    CLI interface. Sys_argv is a parameter for the sake of unittest coverage.
    :param sys_argv list:
    :rtype: None
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'sources', metavar='sources', nargs='+',
        help='source code file/directory paths.')

    sys_argv = sys_argv or sys.argv[1:]
    args = parser.parse_args(sys_argv)

    raw_source_paths=args.sources

    if not isinstance(raw_source_paths, list):
        raw_source_paths = [raw_source_paths]

    sources = get_sources_and_language(raw_source_paths)


    # get tree 
    file_ast_trees = []
    for source in sources:
        try:
            file_ast_trees.append((source, language.get_tree(source)))
        except Exception as ex:
            raise ex

    # NEXT PR Folder group
    file_group = {}
    for source, file_ast_tree in file_ast_trees:
        file_group[str(source)] = make_file_group(file_ast_tree, source)


    


    # for file_key, file_symbol in file_group.items():
    #     file_symbol = file_symbol.all_symbols()
    #     for func in file_symbol.all_symbols():
    #         in_func_symbol = {}
    #         for process, _ in func.process:
    #             if isinstance(process, Call):
    #                 if process.parent_token 
    #             elif isinstance(process, Variable):
    #                 comparing_token = process.points_to.func
                    


    for file_key, file_symbol in file_group.items():
        # Iterate through all functions in the current file
        for func in file_symbol.all_symbols():
            for single_process in func.process:
                process, ast_tree = single_process

                # Extract the comparing token based on the type of `process`
                parent = None
                if isinstance(process, Call):
                    comparing_token = process.func
                    parent = process.parent_token
                elif isinstance(process, Variable):
                    comparing_token = process.points_to.func
                    parent = process.points_to.parent
                else:
                    continue  # Skip if the process is neither a Call nor a Variable

                # Find the matching symbol for the comparing token
                substitute = None
                for comp in file_symbol.all_symbols():
                    if comp.token == comparing_token and parent == None:# Not yet have class function so this will be good for now
                        substitute = comp
                        break

                # If a match is found, update the process attributes
                if substitute:
                    if isinstance(process, Call):
                        process.func = substitute
                    elif isinstance(process, Variable):
                        process.points_to.func = substitute
                    continue


                    
    for file_key, file_symbol in file_group.items():
        # file_model = FileModel( token=file_symbol.token ,
        #                         path=file_key)
        for func in file_symbol.all_func():
            # function_model = FunctionModel( token=func.token,
            #                                 parent=file_model)
            print(func.token)
            output= []
            for process , ast_tree in func.process:
                if isinstance(process, Call) and isinstance(process.func, UserDefinedFunc):
                        output.append(process)
                elif isinstance(process, Variable) and isinstance(process.points_to.func, (UserDefinedClass, UserDefinedFunc)):
                    output.append(process)
                else:
                    output.append(ast.unparse(ast_tree))

            print()
            print(output)
            print()
            print("==================================================")
            print()
            print()
            func.output = output


    # file_model = None
    # for file_key, file_symbol in file_group.items():
    #     file_model = FileModel( token=file_symbol.token,
    #                             path=file_key)
    #     for func in file_symbol.all_func():
    #         func_model = FunctionModel( token=file_symbol.token , parent=file_model)
    #         file_model.function_dict[func.token] = func_model
        
    # for file_key, file_symbol in file_group.items():
    #     for func in file_symbol.all_func():
    #         output_list = []
    #         for single_output in func.output:
    #             if type(single_output) == 'str':
    #                 output_list.append(single_output)
    #             elif isinstance(single_process, Call):
    #                 output_list.append(CallModel(file_model.function_dict[single_process.func.token]))
    #             elif isinstance(single_process, Variable):
    #                 if isinstance(single_process.points_to , UserDefinedFunc):
    #                     output_list.append(VariableModel(points_to=file_model.function_dict[single_process.points_to.func.token] , token= single_process.token))
    file_model = FileModel(
        token="abc",
        path="/example/path",
        function_list={},  # No circular references here
        class_list={}      # No circular references here
    )




    print(file_model.model_dump())
    # payload = {
    #     "source_path": file_model.token,
    #     "file_group": file_model
    # }
    # asyncio.run(run_post_file(payload))

        # check the process of the func
    # parse into pydantic



    # send to fastapi 



if __name__ == "__main__":
    main()
