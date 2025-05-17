from typing import List

from MVP.refactored.backend.box_functions.function_structure.assigned_value.assigned_value import AssignedValue
from MVP.refactored.backend.box_functions.function_structure.code_element import CodeElement


class CodeExpression(AssignedValue):

    def __init__(self,
                 expression_code: str,
                 elements: List[CodeElement] = None):
        super().__init__(expression_code, elements)

    def __str__(self):
        return self.value

    def __repr__(self):
        return (f"CodeExpression(expression_code={self.value!r}, "
                f"elements={self.elements!r})")

    def __eq__(self, other):
        if not isinstance(other, CodeExpression):
            return False
        return self.value == other.value and self.elements == other.elements
