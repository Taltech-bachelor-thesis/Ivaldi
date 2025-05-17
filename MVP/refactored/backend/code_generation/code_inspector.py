from __future__ import annotations
import ast
from typing import Optional, TYPE_CHECKING
import astor  # Requires pip install astor
import autopep8

if TYPE_CHECKING:
    from MVP.refactored.backend.box_functions.box_function import BoxFunction


class CodeInspector(ast.NodeTransformer):
    def __init__(self, target_name: str = None, new_name: str = None):
        self.target_name = target_name
        self.new_name = new_name
        self.current_function_globals = set()
        self.current_function_params = set()
        self.main_function_body = None
        self.global_vars = set()
        self.global_statements = set()
        self.function_names = set()

    def visit_Assign(self, node):
        if hasattr(node, "parent") and isinstance(node.parent, ast.Module):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.global_vars.add(target.id)
        self.generic_visit(node)

        return node

    def visit_FunctionDef(self, node):
        self.function_names.add(node.name)
        if node.name == self.target_name:
            node.name = self.new_name

        self.current_function_params = {arg.arg for arg in node.args.args}

        for stmt in node.body:
            if isinstance(stmt, ast.Global):
                stmt.names = [
                    self.new_name if name == self.target_name else name
                    for name in stmt.names
                ]
                self.global_statements.update(stmt.names)
                self.current_function_globals.update(stmt.names)

        self.generic_visit(node)

        self.current_function_globals.clear()
        self.current_function_params.clear()

        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == self.target_name:
            node.func.id = self.new_name
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if (
                node.id == self.target_name
                and (
                node.id in self.current_function_globals
                or not self.current_function_params)
        ):
            node.id = self.new_name

        return node

    def refactor_code(self, code_str: str, target_name: str, new_name: str):
        if target_name:
            self.target_name = target_name
        if new_name:
            self.new_name = new_name
        tree = ast.parse(code_str)
        self.visit(tree)
        return astor.to_source(tree)

    def _attach_parents(self, node, parent=None):
        node.parent = parent
        for child in ast.iter_child_nodes(node):
            self._attach_parents(child, node)

    def find_globals(self, code_str):
        tree = ast.parse(code_str)
        self._attach_parents(tree)
        self.visit(tree)

        all_globals = self.global_vars.union(self.global_statements)
        self.cleanup()
        return all_globals

    def find_function_names(self, code_str):
        tree = ast.parse(code_str)
        self.visit(tree)

        functions = set(self.function_names)
        self.cleanup()
        return functions

    def cleanup(self):
        self.global_vars.clear()
        self.global_statements.clear()
        self.function_names.clear()

    @classmethod
    def rename(cls, box_functions_items_names: dict[BoxFunction, set[str]]) \
            -> tuple[set[str], set[str], set[str], dict[BoxFunction, str]]:
        """
            Renames box function item names for a given dictionary of box functions and their associated
            item names. Each item name will be appended with an index to make it unique.

            Parameters:
                cls: The class on which this class method is invoked.
                box_functions_items_names: A dictionary where keys are BoxFunction instances and values
                    are sets of strings representing item names associated with each BoxFunction.

            Returns:
                A tuple containing:
                - A set of strings representing all renamed global statements.
                - A set of strings representing all renamed helper functions.
                - A set of strings representing all renamed main functions.
                - A dictionary mapping each BoxFunction to its new name if the function name was 'invoke'.
        """
        renamed_global_statements: set[str] = set()
        renamed_helper_functions: set[str] = set()
        renamed_main_functions: set[str] = set()
        main_functions_new_names: dict[BoxFunction, str] = dict()

        for i, (box_function, names) in enumerate(box_functions_items_names.items()):
            renamer = CodeInspector()

            global_statements: set[str] = box_function.global_statements
            helper_functions: set[str] = box_function.helper_functions
            main_function: str = box_function.main_function

            for name in names:
                new_name = f'{name}_{i}'
                # rename name to new_name in all global_statements, helper_functions or main_function if it contains it
                global_statements = [renamer.refactor_code(global_statement, name, new_name)
                                     for global_statement in global_statements]
                helper_functions = [renamer.refactor_code(helper_function, name, new_name)
                                    for helper_function in helper_functions]
                main_function = renamer.refactor_code(main_function, name, new_name)

                if name == box_function.main_function_name:
                    main_functions_new_names[box_function] = new_name

            renamed_global_statements.update(global_statements)
            renamed_helper_functions.update(helper_functions)
            renamed_main_functions.add(main_function)

        return renamed_global_statements, renamed_helper_functions, renamed_main_functions, main_functions_new_names

    @classmethod
    def get_main_function(cls, code_str: str, main_method_name: str) -> Optional[str]:
        """
        Extracts the source code for a function matching `main_method_name` from the given code string.
        """
        tree = ast.parse(code_str)
        main_method = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == main_method_name:
                main_method = node
                break

        if main_method is None:
            return None

        return autopep8.fix_code(astor.to_source(main_method))

    @classmethod
    def get_help_methods(cls, code_str: str, main_method_name: str) -> list[str]:
        """
        Extracts all method definitions from the given code string, excluding the main method.
        """
        tree = ast.parse(code_str)
        methods = set()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name != main_method_name:
                methods.add(node)

        if not methods:
            return []

        return [astor.to_source(method) for method in methods]

    @classmethod
    def get_imports(cls, code_str) -> list[str]:
        """
        Parse the provided Python code string and extract import statements.
        """
        tree = ast.parse(code_str)
        imports = set()

        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.add(node)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node)

        if not imports:
            return []

        return [astor.to_source(ast_import) for ast_import in imports]

    @classmethod
    def get_global_statements(cls, code_str: str) -> list[str]:
        """
        Extract the global variable declarations from the given Python code string.
        """
        tree = ast.parse(code_str)
        global_vars = set()
        assignments = []
        assigned_vars = set()  # Keep track of assigned global variables

        # First pass: check top-level assignments (global variables)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id not in global_vars:
                            global_vars.add(target.id)
                            assignments.append(node)
                            assigned_vars.add(target.id)

        assignments_code = [astor.to_source(assign) for assign in assignments]
        global_var_names = [f"global {var}" for var in global_vars if var not in assigned_vars]

        return assignments_code + global_var_names

    @classmethod
    def get_names(cls, elements: list[str]) -> list[str]:
        """
        Extracts unique names from a list of string representations of Python code.
        """
        names = set()
        for element in elements:
            tree = ast.parse(element)

            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    names.add(node.name)
                elif isinstance(node, ast.Global):
                    names.update(node.names)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            names.add(target.id)

        return list(names) if names else []
