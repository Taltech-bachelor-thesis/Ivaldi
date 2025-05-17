class DiagramN:
    def __init__(self):
        self.columns: [ColumnN] = []

    def __str__(self):
        return self.get_box_definitions() + ";\n".join([str(col) for col in self.columns])

    def get_box_definitions(self):
        definitions = []
        for column in self.columns:
            for column_element in column.elements:
                if type(column_element) is BoxN and column_element.is_defined():
                    definitions.append(column_element.get_definition())
        result = ", ".join(definitions)
        if definitions:
            result += " | - \n"
        return result


class ColumnN:
    def __init__(self):
        self.elements: [SpiderN | BoxN | SymmetryN | IdentityN] = []

    def __str__(self):
        return "⊗".join([str(el) for el in self.elements])


class IdentityN:
    def __init__(self, nr=1):
        self.nr = nr

    def __str__(self):
        return f"Identity({self.nr})"


class SpiderN:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def __str__(self):
        return f"Spider({self.inputs},{self.outputs})"


class BoxN:
    def __init__(self, inputs, outputs, label=None):
        self.inputs = inputs
        self.outputs = outputs
        self.label = label

    def get_definition(self):
        if not self.label:
            return f""
        return f"{self.label}: ({self.inputs},{self.outputs})"

    def is_defined(self):
        if self.label:
            return True
        return False

    def __str__(self):
        if not self.label:
            return f"UndefinedBox({self.inputs},{self.outputs})"
        return f"{self.label}"


class SymmetryN:
    def __init__(self, nr1=1, nr2=1):
        self.nr1 = nr1
        self.nr2 = nr2

    def __str__(self):
        return f"Symmetry({self.nr1},{self.nr2})"
