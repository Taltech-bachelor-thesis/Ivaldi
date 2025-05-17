from enum import StrEnum


class CodeElementType(StrEnum):
    VARIABLE = "variable",
    CONSTANT = "constant",

class CodeElement:

    def __init__(self, value: str, element_type: CodeElementType):
        self.value: str = value
        self.type: CodeElementType = element_type

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"CodeElement(name={self.value!r}, type={self.type!r})"

    def __eq__(self, other):
        if not isinstance(other, CodeElement):
            return False
        return self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((self.value, self.type))
