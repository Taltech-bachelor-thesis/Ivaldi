import json
import os
import tkinter as tk
from tkinter import messagebox

import pygments.lexers
from chlorophyll import CodeView

from MVP.refactored.util.exporter.code_exporter import CodeExporter
import constants as const


class CodeEditor:
    """
    `CodeEditor` is the class that holds the window for the code editor and its functions.

    The editor itself is imported from `chlorophyll` package.
    """
    def __init__(self, main_diagram, box=None, label=None, code=None, is_generated=False):
        """
        CodeEditor constructor.

        :param main_diagram: MainDiagram object for accessing functions.
        :param box: Box that the CodeEditor was opened from.
        :param label: Label of the function.
        :param code: Code that will be displayed upon opening CodeEditor.
        :param is_generated: Boolean defining if the code inside CodeEditor is generated.
        """
        self.main_diagram = main_diagram
        self.box = box
        if label:
            self.label = label
        elif box:
            self.label = self.box.label_text

        self.window = tk.Toplevel()
        self.window.title('Code Editor')
        self.window.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.window.geometry("1000x750")
        self.code_view = CodeView(self.window, lexer=pygments.lexers.PythonLexer,
                                  tab_width=4,
                                  font="Courier")

        self.code_view.pack(fill=tk.BOTH, expand=True)

        self.save_as_button = tk.Button(
            self.code_view,
            text="Save as",
            command=self.save_as,
        )
        self.save_as_button.pack(
            anchor=tk.E,
            pady=5
        )

        if not is_generated:
            self.save_button = tk.Button(
                self.code_view,
                text="Save",
                command=self.save_handler,
            )
            self.save_button.pack(
                anchor=tk.E
            )

        if box:
            param_list = []
            return_list = []
            input_count = 0
            output_count = 0
            for i in self.box.connections:
                if i.side == const.LEFT:
                    param_list.append(f"x{input_count}")
                    input_count += 1
                else:
                    return_list.append(f"y{output_count}")
                    output_count += 1
            param_str = tuple(param_list).__str__().replace("'", "")
            return_str = tuple(return_list).__str__().replace("'", "")
            if len(param_list) == 1:
                param_str = param_str.replace(",", "")
            if len(return_list) == 1:
                return_str = return_str.replace(",", "")
            function_name = self.generate_function_name_from_label()
            text = f"def {function_name}{param_str}:\n    return {return_str}"
            if self.box.label_text in self.box.canvas.master.label_content.keys():
                text = self.box.canvas.master.label_content[self.box.label_text].strip()
        else:
            text = code

        self.code_view.insert('1.0', text)

        self.code_exporter = CodeExporter(self)

    def generate_function_name_from_label(self):
        """
        Generate a name for the function preset.

        Takes the Box label and generates a usable python function name.

        :return: string of function name.
        """
        base = self.box.label_text.strip()
        result = base
        for char in base:
            if not (char.isalpha() or char == "_"):
                if char.isnumeric():
                    if result.index(char) == 0:
                        result = result.replace(char, "", 1)
                else:
                    result = result.replace(char, "")
        return result.strip()

    def confirm_exit(self):
        """
        Ask user for exiting confirmation.

        :return: None
        """
        if messagebox.askokcancel("Warning", "Unsaved changes will be lost. Are you sure you want to exit?"):
            self.window.destroy()

    def save_handler(self, destroy=True):
        """
        Handle saving.

        :param destroy: Specifies if the editor should be destroyed after saving.
        :return: None
        """
        self.save_to_file()
        self.main_diagram.load_functions()
        if self.box:
            self.update_boxes()
        else:
            self.main_diagram.manage_methods.add_methods()
        if destroy:
            self.window.destroy()

    def save_as(self):
        """
        Export code and save.

        Activates exporting from CodeExporter and uses save.

        :return: None
        """
        self.code_exporter.export()
        self.save_handler(destroy=False)

    def save_to_file(self):
        """
        Save code to json file.

        Saves the code in the editor to the functions_conf.json file.

        :return: None
        """
        if os.stat(const.FUNCTIONS_CONF).st_size != 0:
            with open(const.FUNCTIONS_CONF, "r+") as file:
                existing_json = json.load(file)
                existing_json[self.label] = self.code_view.get('1.0', tk.END).strip()
                json_object = json.dumps(existing_json, indent=4)
                file.seek(0)
                file.truncate(0)
                file.write(json_object)
        else:
            with open(const.FUNCTIONS_CONF, "w") as file:
                json_object = json.dumps(
                    {f"{self.label}": self.code_view.get('1.0', tk.END).strip()},
                    indent=4
                )
                file.write(json_object)

    def update_boxes(self):
        """
        Update boxes in canvas.

        Updates the inputs and outputs of Boxes on the canvas.

        :return: None
        """
        for box in self.main_diagram.custom_canvas.boxes:
            if box.label_text in self.box.label_text:
                box.update_io()
        self.main_diagram.label_content[self.label] = self.code_view.get('1.0', tk.END)
