from MVP.refactored.backend.box_functions.function_structure.code_element import CodeElementType, CodeElement
from MVP.refactored.backend.box_functions.function_structure.code_line import CodeLine
from MVP.refactored.util.string_util import StringUtil


class FunctionStructure:

    def __init__(self, arguments: list[str] = None, body_lines: list[CodeLine] = None, return_line: CodeLine = None):
        self.arguments = arguments or []
        self.body_lines = body_lines or []
        self.return_line = return_line

    def __str__(self):
        body_str = "\n".join(str(line) for line in self.body_lines)
        if not self.return_line:
            return body_str

        return f"{body_str}\nreturn {str(self.return_line.assigned_value)}"

    def __repr__(self):
        return (f"FunctionStructure(body_lines={self.body_lines!r}, "
                f"return_line={self.return_line!r})")

    def __eq__(self, other):
        return (self.body_lines == other.body_lines
                and self.return_line == other.return_line)

    def __hash__(self):
        return hash((tuple(self.body_lines), self.return_line))

    def convert_mutable_variables_to_immutable(self) -> None:
        used_variable_names = set(self.arguments)
        for code_line in self.body_lines:
            for assigned_variable in code_line.assigned_variables:
                used_variable_names.add(assigned_variable)

        declared_variable_names = set(self.arguments)
        variables_new_names = {}

        for code_line in self.body_lines:
            self._convert_code_line_mutable_variables_to_immutable(
                code_line, used_variable_names, declared_variable_names, variables_new_names
            )

        if self.return_line:
            self._convert_code_line_mutable_variables_to_immutable(
                self.return_line, used_variable_names, declared_variable_names, variables_new_names
            )

    def _convert_code_line_mutable_variables_to_immutable(self,
                                                          code_line: CodeLine,
                                                          used_variable_names: set[str],
                                                          declared_variable_names: set[str],
                                                          variables_new_names: dict[str, str]) -> None:
        assigned_value_elements: list[CodeElement] = code_line.assigned_value.elements
        for index in range(len(assigned_value_elements)):
            element = assigned_value_elements[index]

            if element.type == CodeElementType.VARIABLE and element.value in variables_new_names.keys():
                variable_name = variables_new_names[element.value]
                assigned_value_elements[index] = CodeElement(variable_name, CodeElementType.VARIABLE)

        assigned_variables = code_line.assigned_variables
        for index in range(len(assigned_variables)):
            assigned_variable = assigned_variables[index]

            if assigned_variable in declared_variable_names:
                new_variable_name = assigned_variable
                while new_variable_name in used_variable_names:
                    new_variable_name = StringUtil.generate_new_variable_name_from(assigned_variable)

                assigned_variables[index] = new_variable_name
                variables_new_names[assigned_variable] = new_variable_name
            else:
                declared_variable_names.add(assigned_variable)
