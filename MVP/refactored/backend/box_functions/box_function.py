import os
from typing import Optional, List

from MVP.refactored.backend.box_functions.function_structure.function_structure import FunctionStructure
from MVP.refactored.backend.code_generation.code_inspector import CodeInspector
from MVP.refactored.backend.box_functions.function_structure.function_parser import FunctionParser


def get_predefined_functions() -> dict:
    predefined_functions_dict = {}
    functions_path = os.path.join(os.path.dirname(__file__), "./predefined/")
    dirs_and_files = os.listdir(functions_path)
    for name in dirs_and_files:
        full_path = os.path.join(functions_path, name)
        if os.path.isfile(full_path):
            with open(full_path, "r") as file:
                function_name = name.replace(".py", "").replace("_", " ")
                predefined_functions_dict[function_name] = file.read()
    return predefined_functions_dict


predefined_functions = get_predefined_functions()
INVOKE_METHOD = "invoke"

class BoxFunction:

    def __init__(self,
                 function: Optional[str] = None,
                 min_args: Optional[int] = None,
                 max_args: Optional[int] = None,
                 imports: Optional[List[str]] = None,
                 file_code: Optional[str] = None,
                 is_predefined_function: bool = False,
                 predefined_function_file_name: Optional[str] = None,
                 main_function_name: Optional[str] = None):

        self.main_function_name: str = main_function_name or INVOKE_METHOD
        self.imports: List[str] = imports or []
        self.global_statements: List[str] = []
        self.helper_functions: List[str] = []
        self.main_function: Optional[str] = None
        self.is_predefined_function = is_predefined_function
        self.min_args: Optional[int] = min_args
        self.max_args: Optional[int] = max_args
        self.code: str = file_code or ""

        if is_predefined_function:
            predefined_file_code = predefined_functions[predefined_function_file_name]
            self._set_data_from_file_code(predefined_file_code)
        elif file_code is not None:
            self._set_data_from_file_code(file_code)
        else:
            self.main_function: str = function

        self._create_function_structure()

    def get_file_code(self) -> str:
        return self.code

    def get_main_function_name(self) -> str:
        return self.main_function_name

    def _set_data_from_file_code(self, file_code: str):
        """
        Parse and extract data from the provided file code.

        This method processes the given Python file code to extract the main function,
        helper functions, imports, and global statements. These components are then
        assigned to the respective attributes of the `BoxFunction` instance.
        """
        self.main_function = CodeInspector.get_main_function(file_code, self.main_function_name)
        self.helper_functions = CodeInspector.get_help_methods(file_code, self.main_function_name)
        self.imports = CodeInspector.get_imports(file_code)
        self.global_statements = list(CodeInspector.get_global_statements(file_code))
        self.code = file_code

    def _create_function_structure(self):
        if not self.main_function:
            raise ValueError("Cannot create function structure without a main function.")

        self.function_structure: FunctionStructure = FunctionParser.parse_function_code(self.main_function)

    def __eq__(self, other):
        """
        Compares the current BoxFunction instance with another object for equality.
        """
        if isinstance(other, BoxFunction):
            return (self.main_function == other.main_function
                    and self.helper_functions == other.helper_functions
                    and self.imports == other.imports
                    and self.min_args == other.min_args
                    and self.max_args == other.max_args)
        return False

    def __hash__(self):
        """
        Generates a hash value for an instance based on its attributes to allow its use
        as a key in hash-based collections like sets and dictionaries.
        """
        helper_hash = tuple(func for func in self.helper_functions)
        imports_hash = tuple(self.imports)
        main_function_hash = hash(self.main_function) if self.main_function else 0

        return hash((
            main_function_hash,
            helper_hash,
            imports_hash,
            self.min_args,
            self.max_args
        ))

    def __str__(self) -> str:
        """
        Generates a string representation of a Python file by organizing and assembling
        its components, including imports, global statements, helper functions, and
        the main function. This output is formatted using autopep8 for adherence to
        PEP 8 style guidelines.
        """
        # TODO could be implemented better
        return "BoxFunction: " + self.main_function_name

    def __repr__(self):
        return self.__str__()
