from MVP.refactored.backend.box_functions.function_structure.assigned_value.assigned_value import AssignedValue


class CodeLine:

    def __init__(self,
                 assigned_variables: list[str] = None,
                 assigned_value: AssignedValue = None):
        self.assigned_variables: list[str] = assigned_variables or []
        self.assigned_value: AssignedValue = assigned_value

    def __str__(self):
        result = ""
        if self.assigned_variables:
            result = ", ".join(self.assigned_variables)
            result += " = "

        result += str(self.assigned_value)

        return result

    def __repr__(self):
        return (f"CodeLine(assigned_variables={self.assigned_variables!r}, "
                f"assigned_value={self.assigned_value!r})")

    def __eq__(self, other):
        if not isinstance(other, CodeLine):
            return False
        return (self.assigned_variables == other.assigned_variables and
                self.assigned_value == other.assigned_value)

    def __hash__(self):
        return hash((
            tuple(self.assigned_variables),
            self.assigned_value
        ))
