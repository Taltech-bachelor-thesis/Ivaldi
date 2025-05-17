import ast

from MVP.refactored.backend.box_functions.function_structure.assigned_value.assigned_value import AssignedValue
from MVP.refactored.backend.box_functions.function_structure.code_element import CodeElement, CodeElementType
from MVP.refactored.backend.box_functions.function_structure.assigned_value.code_expression import CodeExpression
from MVP.refactored.backend.box_functions.function_structure.code_line import CodeLine
from MVP.refactored.backend.box_functions.function_structure.assigned_value.function_call import FunctionCall
from MVP.refactored.backend.box_functions.function_structure.function_structure import FunctionStructure
from MVP.refactored.util.string_util import StringUtil


class FunctionParser(ast.NodeVisitor):

    def __init__(self):
        self.arguments: list[str] = []
        self.body_lines: list[CodeLine] = []
        self.return_line: CodeLine|None = None
        self.functions_to_ignore = {"print"}

        self.parsed_nodes = set()
        self.current_expression: str = ""

    @staticmethod
    def parse_function_code(function_code: str) -> FunctionStructure:
        """
        Parse the function code and extract its structure.

        Args:
            function_code (str): The Python code of the function to parse.

        Returns:
            FunctionStructure: An object representing the structure of the function.
        """
        tree = ast.parse(function_code)
        return FunctionParser.parse_function_tree(tree)

    @staticmethod
    def parse_function_tree(function_tree):
        parser = FunctionParser()
        parser.visit(function_tree)

        return FunctionStructure(arguments=parser.arguments, body_lines=parser.body_lines, return_line=parser.return_line)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.arguments = []
        for arg in node.args.args:
            self.arguments.append(arg.arg)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        assigned_variables = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                assigned_variables.append(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        assigned_variables.append(elt.id)

        assigned_value = self._parse_expression(node.value)
        code_line = CodeLine(assigned_variables=assigned_variables, assigned_value=assigned_value)
        self.body_lines.append(code_line)

    def visit_Return(self, node: ast.Return):
        assigned_value = self._parse_expression(node.value)
        self.return_line = CodeLine(assigned_value=assigned_value)

    def _parse_expression(self, node: ast.AST) -> AssignedValue:
        self.current_expression = ast.unparse(node)

        expression_elements: list[CodeElement] = []
        function_call: FunctionCall | None = None

        for n in ast.walk(node):
            parsed_node = self._parse_node(n, node)
            if not parsed_node:
                continue

            if isinstance(parsed_node, CodeElement):
                expression_elements.append(parsed_node)
            elif isinstance(parsed_node, FunctionCall):
                if function_call:
                    raise ValueError("Multiple function calls in a single expression are not supported.")
                function_call = parsed_node

        if function_call:
            return function_call
        else:
            return CodeExpression(self.current_expression, expression_elements)

    def _parse_arguments(self, node: ast.Call) -> list[CodeElement]:
        arguments = []
        for arg in node.args:
            code_element = self._parse_node(arg, node)
            if code_element:
                arguments.append(code_element)

        return arguments

    def _parse_node(self, node: ast.AST, parent_node: ast.AST) -> CodeElement | FunctionCall | None:
        if node in self.parsed_nodes:
            return None

        self.parsed_nodes.add(node)

        if isinstance(node, ast.Name) and not self._is_function_name(node, parent_node):
            return CodeElement(node.id, CodeElementType.VARIABLE)

        elif isinstance(node, ast.Constant):
            return CodeElement(repr(node.value), CodeElementType.CONSTANT) # `repr` to preserve e.g., string quotes

        elif isinstance(node, ast.Call):
            function_name = node.func.id
            if function_name not in self.functions_to_ignore:
                arguments = self._parse_arguments(node)
                function_call = FunctionCall(function_name, arguments)
                variable_name = StringUtil.generate_new_variable_name_from(function_name)

                function_call_str = str(function_call)
                if self.current_expression != function_call_str:
                    code_line = CodeLine(assigned_variables=[variable_name], assigned_value=function_call)
                    self.body_lines.append(code_line)
                    self.current_expression = self.current_expression.replace(function_call_str, variable_name)
                    return CodeElement(variable_name, CodeElementType.VARIABLE)

                return function_call

        return None

    def _is_function_name(self, name_node: ast.Name, context_node: ast.AST) -> bool:
        for parent in ast.walk(context_node):
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name):
                if parent.func is name_node:
                    return True
        return False
