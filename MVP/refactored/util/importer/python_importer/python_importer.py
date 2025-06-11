import ast
import os
from typing import List
from typing import TextIO

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.box_functions.function_structure.assigned_value.assigned_value import AssignedValue
from MVP.refactored.backend.box_functions.function_structure.assigned_value.function_call import FunctionCall
from MVP.refactored.backend.box_functions.function_structure.code_element import CodeElement, CodeElementType
from MVP.refactored.backend.box_functions.function_structure.code_line import CodeLine
from MVP.refactored.backend.box_functions.function_structure.function_parser import FunctionParser
from MVP.refactored.backend.box_functions.function_structure.function_structure import FunctionStructure
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.windows.checkbox_dialog import CheckboxDialog
from MVP.refactored.util.importer.importer import Importer
from MVP.refactored.util.string_util import StringUtil


class PythonImporter(Importer):

    ELEMENTS_Y_POSITION = 300
    BOXES_STARTING_X_POSITION = 200
    BOXES_ENDING_X_POSITION = 1200

    def start_import(self, python_files: List[TextIO]) -> str:
        dialog = CheckboxDialog(self.canvas.main_diagram,
                                title="Importing mode",
                                checkbox_text="Import python code deeply (create sub-diagrams for every function)")

        deep_generation = dialog.result

        all_functions = {}
        all_imports = []
        main_logic: FunctionStructure | None = None
        main_diagram_name = None

        for python_file in python_files:
            file_functions, file_imports, file_main_logic = PythonImporter._extract_data_from_file(python_file)

            all_functions.update(file_functions)
            all_imports.extend(file_imports)

            if file_main_logic:
                if main_logic is None:
                    main_logic = file_main_logic
                    main_diagram_name = os.path.basename(python_file.name)
                else:
                    raise ValueError("Multiple main execution blocks found in the imported files!\n"
                                     "Only one file should contain 'if __name__ == \"__main__\":'.")

        if not main_logic:
            raise ValueError("The Python code in imported files does not contain a main execution block!\n"
                             "One of the selected files must include 'if __name__ == \"__main__\":'.")

        first_function = next(iter(all_functions.values()))
        first_function.imports = all_imports

        data = {"functions": all_functions, "main_logic": main_logic, "deep_generation": deep_generation}
        self.load_everything_to_canvas(data, self.canvas)

        return main_diagram_name

    def load_everything_to_canvas(self, data: dict, canvas: CustomCanvas) -> None:
        functions = data["functions"]
        main_logic: FunctionStructure = data["main_logic"]
        deep_generation = data["deep_generation"]

        main_logic_body_lines: List[CodeLine] = main_logic.body_lines

        boxes_amount = len(main_logic_body_lines)
        boxes_gap = PythonImporter._calculate_boxes_gap(boxes_amount)
        box_x = PythonImporter._calculate_box_initial_x(boxes_amount)

        possible_outputs: set[str] = set()
        boxes_by_assigned_variable: dict[str, Box] = {}
        box_right_connection_spiders = {}

        for code_line in main_logic_body_lines:
            box_x = PythonImporter._add_main_logic_code_line_to_canvas(
                canvas, code_line, functions, boxes_by_assigned_variable,
                box_right_connection_spiders, possible_outputs, box_x, boxes_gap, deep_generation
            )

        PythonImporter._add_outputs_to_canvas(canvas, possible_outputs, boxes_by_assigned_variable)

    @staticmethod
    def _add_main_logic_code_line_to_canvas(canvas: CustomCanvas,
                                            code_line: CodeLine,
                                            functions: dict[str, BoxFunction],
                                            boxes_by_assigned_variable: dict[str, Box],
                                            box_right_connection_spiders: dict[str, Spider],
                                            possible_outputs: set[str],
                                            box_x: int,
                                            boxes_gap: int,
                                            deep_generation: bool) -> int:
        assigned_variables = code_line.assigned_variables
        assigned_value_elements = code_line.assigned_value.elements

        box_position = (box_x, PythonImporter.ELEMENTS_Y_POSITION)
        new_box = PythonImporter._add_box_to_canvas(
            canvas, code_line, box_position, functions, len(assigned_variables), deep_generation
        )

        for assigned_variable in code_line.assigned_variables:
            possible_outputs.add(assigned_variable)
            boxes_by_assigned_variable[assigned_variable] = new_box

        for assigned_value_element in assigned_value_elements:
            if assigned_value_element.type == CodeElementType.VARIABLE:
                variable_name = assigned_value_element.value
                left_connection = new_box.add_left_connection()
                canvas.start_wire_from_connection(left_connection)

                previous_box = boxes_by_assigned_variable.get(variable_name)
                PythonImporter._end_wire_to_box_spider(canvas, previous_box, variable_name,
                                                       box_right_connection_spiders, boxes_gap)

                if variable_name in possible_outputs:
                    possible_outputs.remove(variable_name)
            elif assigned_value_element.type == CodeElementType.CONSTANT:
                left_connection = new_box.add_left_connection()
                canvas.start_wire_from_connection(left_connection)
                diagram_input = canvas.add_diagram_input()
                canvas.end_wire_to_connection(diagram_input, True)

        new_box.lock_box()
        return box_x + boxes_gap

    @staticmethod
    def _add_box_to_canvas(canvas: CustomCanvas,
                           code_line: CodeLine,
                           box_position: tuple,
                           functions: dict[str, BoxFunction],
                           assigned_variables_amount: int,
                           deep_generation: bool) -> Box:
        new_box = canvas.add_box(box_position)
        assigned_value = code_line.assigned_value

        create_sub_diagram = False
        if isinstance(assigned_value, FunctionCall) and assigned_value.value in functions:
            function_name = assigned_value.value
            box_function = functions[function_name]
            create_sub_diagram = deep_generation
        else:
            box_function = PythonImporter._create_mocked_box_function(assigned_value)

        canvas.main_diagram.add_function_to_label_content(box_function.main_function_name, box_function.main_function)
        new_box.set_label(box_function.main_function_name)

        if create_sub_diagram:
            PythonImporter._create_box_sub_diagram(new_box, assigned_variables_amount, functions)

        return new_box

    @staticmethod
    def _create_box_sub_diagram(box: Box, assigned_variables_amount: int, functions: dict[str, BoxFunction]) -> None:
        function_structure: FunctionStructure = box.get_box_function().function_structure
        arguments = function_structure.arguments

        sub_diagram_canvas: CustomCanvas = box.edit_sub_diagram(save_to_canvasses=True, switch=False)

        boxes_amount = len(function_structure.body_lines) + 1
        boxes_gap = PythonImporter._calculate_boxes_gap(boxes_amount)
        box_x = PythonImporter._calculate_box_initial_x(boxes_amount)

        input_spiders: dict[str, Spider] = PythonImporter._add_inputs_with_spiders_to_canvas(sub_diagram_canvas, arguments)

        boxes_by_assigned_variable: dict[str, Box] = {}
        box_right_connection_spiders = {}

        for code_line in function_structure.body_lines:
            box_x = PythonImporter._add_box_function_structure_code_line_to_canvas(
                sub_diagram_canvas, code_line, arguments, boxes_by_assigned_variable,
                input_spiders, box_right_connection_spiders, functions, 0, box_x, boxes_gap
            )

        return_line = function_structure.return_line
        PythonImporter._add_box_function_structure_code_line_to_canvas(
            sub_diagram_canvas, return_line, arguments, boxes_by_assigned_variable,
            input_spiders, box_right_connection_spiders, functions, assigned_variables_amount, box_x, boxes_gap
        )

    @staticmethod
    def _add_inputs_with_spiders_to_canvas(canvas: CustomCanvas, input_names: list[str]) -> dict[str, Spider]:
        input_spiders: dict[str, Spider] = {}

        for input_name in input_names:
            diagram_input = canvas.add_diagram_input()
            canvas.start_wire_from_connection(diagram_input)
            spider_position = (PythonImporter.BOXES_STARTING_X_POSITION  / 2, PythonImporter.ELEMENTS_Y_POSITION)
            new_spider = canvas.add_spider(loc=spider_position)
            canvas.end_wire_to_connection(new_spider, True)
            input_spiders[input_name] = new_spider

        return input_spiders

    @staticmethod
    def _add_box_function_structure_code_line_to_canvas(canvas: CustomCanvas,
                                                        code_line: CodeLine,
                                                        arguments: list[str],
                                                        boxes_by_assigned_variable: dict[str, Box],
                                                        input_spiders: dict[str, Spider],
                                                        box_right_connection_spiders: dict[str, Spider],
                                                        functions: dict[str, BoxFunction],
                                                        outputs_amount: int,
                                                        box_x: int,
                                                        boxes_gap: int) -> int:
        assigned_variables: list[str] = code_line.assigned_variables
        assigned_value_elements = code_line.assigned_value.elements

        box_position = (box_x, PythonImporter.ELEMENTS_Y_POSITION)
        new_box = PythonImporter._add_box_to_canvas(
            canvas, code_line, box_position, functions, len(assigned_variables), True
        )

        for assigned_variable in assigned_variables:
            boxes_by_assigned_variable[assigned_variable] = new_box


        for assigned_value_element in assigned_value_elements:
            if assigned_value_element.type == CodeElementType.VARIABLE:
                variable_name = assigned_value_element.value
                left_connection = new_box.add_left_connection()
                canvas.start_wire_from_connection(left_connection)

                if variable_name in arguments:
                    input_spider = input_spiders.get(variable_name)
                    canvas.end_wire_to_connection(input_spider, True)
                else:
                    previous_box = boxes_by_assigned_variable.get(variable_name)
                    PythonImporter._end_wire_to_box_spider(canvas, previous_box, variable_name,
                                                           box_right_connection_spiders, boxes_gap)

            elif assigned_value_element.type == CodeElementType.CONSTANT:
                left_connection = new_box.add_left_connection()
                canvas.start_wire_from_connection(left_connection)
                spider_position = (box_x - 100, PythonImporter.ELEMENTS_Y_POSITION)
                new_spider = canvas.add_spider(loc=spider_position)
                canvas.end_wire_to_connection(new_spider, True)

        for _ in range(outputs_amount):
            wire_start_connection = new_box.add_right_connection()
            canvas.start_wire_from_connection(wire_start_connection)
            output = canvas.add_diagram_output()
            canvas.end_wire_to_connection(output, True)

        new_box.lock_box()
        return box_x + boxes_gap

    @staticmethod
    def _end_wire_to_box_spider(canvas: CustomCanvas,
                                box: Box,
                                function_argument: str,
                                box_right_connection_spiders: dict[str, Spider],
                                boxes_gap: int) -> None:
        new_spider_added = False
        if function_argument not in box_right_connection_spiders.keys():
            spider_x_position = box.x + boxes_gap / 2
            new_spider = canvas.add_spider(loc=(spider_x_position, PythonImporter.ELEMENTS_Y_POSITION))
            box_right_connection_spiders[function_argument] = new_spider
            new_spider_added = True

        connection_spider = box_right_connection_spiders[function_argument]
        canvas.end_wire_to_connection(connection_spider, True)

        if new_spider_added:
            wire_end_connection = box.add_right_connection()
            canvas.start_wire_from_connection(connection_spider)
            canvas.end_wire_to_connection(wire_end_connection, True)

    @staticmethod
    def _add_outputs_to_canvas(canvas: CustomCanvas, outputs: set[str], boxes_by_assigned_variable: dict[str, Box]) -> None:
        for output_assigned_variable in outputs:
            variable_box = boxes_by_assigned_variable.get(output_assigned_variable)
            wire_start_connection = variable_box.add_right_connection()
            canvas.start_wire_from_connection(wire_start_connection)

            output = canvas.add_diagram_output()
            canvas.end_wire_to_connection(output, True)

    @staticmethod
    def _create_mocked_box_function(assigned_value: AssignedValue) -> BoxFunction:
        value = assigned_value.value
        main_function_name = StringUtil.generate_new_variable_name_from("fun_" + value)
        code = str(assigned_value)
        variables = []

        for element in assigned_value.elements:
            if element.type == CodeElementType.VARIABLE and element.value not in variables:
                variables.append(element.value)
            else:
                new_variable = StringUtil.generate_new_variable_name()
                variables.append(new_variable)
                occurrence = 1 if element.type == CodeElementType.CONSTANT else 2
                code = StringUtil.replace_nth_occurrence(code, element.value, new_variable, occurrence)

        main_function = f"def {main_function_name}({", ".join(variables)}):\n\treturn {code}"
        return BoxFunction(main_function_name=main_function_name, function = main_function)

    @staticmethod
    def _calculate_boxes_gap(boxes_amount: int) -> int:
        if boxes_amount == 0:
            return 0
        elif boxes_amount == 1:
            return PythonImporter.BOXES_ENDING_X_POSITION - PythonImporter.BOXES_STARTING_X_POSITION // 2
        else:
            return (PythonImporter.BOXES_ENDING_X_POSITION - PythonImporter.BOXES_STARTING_X_POSITION) // (boxes_amount - 1)

    @staticmethod
    def _calculate_box_initial_x(boxes_amount: int) -> int:
        if boxes_amount == 0:
            return 0
        elif boxes_amount == 1:
            return PythonImporter.BOXES_ENDING_X_POSITION - PythonImporter.BOXES_STARTING_X_POSITION // 2
        else:
            return PythonImporter.BOXES_STARTING_X_POSITION

    @staticmethod
    def _extract_data_from_file(python_file: TextIO) -> tuple:
        functions = {}
        imports = []
        main_logic: FunctionStructure | None = None

        source_code = python_file.read()
        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                PythonImporter._extract_function(node, source_code, functions)

        for node in tree.body:
            if isinstance(node, ast.Import):
                PythonImporter._extract_imports(node, imports)

            elif isinstance(node, ast.ImportFrom):
                PythonImporter._extract_imports_from(node, imports)

            elif (isinstance(node, ast.If)
                  and isinstance(node.test, ast.Compare)
                  and isinstance(node.test.left, ast.Name)
                  and node.test.left.id == "__name__"
                  and isinstance(node.test.comparators[0], ast.Constant)
                  and node.test.comparators[0].value == "__main__"):
                main_logic = FunctionParser.parse_function_tree(node)
                main_logic.convert_mutable_variables_to_immutable()

        return functions, imports, main_logic

    @staticmethod
    def _extract_function(node, source_code: str, functions: dict) -> None:
        func_name = node.name
        function = ast.get_source_segment(source_code, node)
        num_inputs = len(node.args.args)

        box_function = BoxFunction(
            main_function_name=func_name, function=function, min_args=num_inputs, max_args=num_inputs
        )
        box_function.function_structure.convert_mutable_variables_to_immutable()
        functions[func_name] = box_function

    @staticmethod
    def _extract_imports(node, imports):
        for alias in node.names:
            imports.append(f"import {alias.name}")

    @staticmethod
    def _extract_imports_from(node, imports):
        if node.module:
            module = node.module
        else:
            module = "." * node.level

        for alias in node.names:
            imports.append(f"from {module} import {alias.name}")
