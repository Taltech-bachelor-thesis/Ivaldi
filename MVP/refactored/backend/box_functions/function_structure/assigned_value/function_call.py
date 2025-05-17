from typing import List

from MVP.refactored.backend.box_functions.function_structure.assigned_value.assigned_value import AssignedValue
from MVP.refactored.backend.box_functions.function_structure.code_element import CodeElement


class FunctionCall(AssignedValue):

    def __init__(self,
                 function_name: str,
                 arguments: List[CodeElement] = None):
        super().__init__(function_name, arguments)

    def __str__(self):
        return f"{self.value}({', '.join(str(argument) for argument in self.elements)})"

    def __repr__(self):
        return (f"FunctionCall(function_name={self.value!r}, "
                f"arguments={self.elements!r})")

    def __eq__(self, other):
        if not isinstance(other, FunctionCall):
            return False
        return self.value == other.value and self.elements == other.elements
