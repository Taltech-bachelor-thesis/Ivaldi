from typing import List

from MVP.refactored.backend.box_functions.function_structure.code_element import CodeElement


class AssignedValue:

    def __init__(self,
                 value: str,
                 elements: List[CodeElement] = None):
        self.value = value
        self.elements = elements or []

    def __hash__(self):
        return hash((
            self.value,
            tuple(self.elements),
        ))
