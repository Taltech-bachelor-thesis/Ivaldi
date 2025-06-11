import json
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

import ttkbootstrap as ttk

import constants as const
from MVP.refactored.frontend.windows.code_editor import CodeEditor


class ManageMethods(tk.Toplevel):
    """
    `ManageMethods` is a window that allows overview and management of functions in the application. These are functions
    that can be added to Boxes.

    The window displays a table containing the label of the function and the function content.
    These can be added, removed or edited from this window.
    """
    def __init__(self, main_diagram, *args, **kwargs):
        """
        ManageMethods constructor.

        :param main_diagram: MainDiagram.
        :param args: args for tkinter.Toplevel
        :param kwargs: keyword args for tkinter.Toplevel
        """
        super().__init__(*args, **kwargs)
        self.main_diagram = main_diagram

        self.minsize(400, 100)

        self.title('Manage Methods')

        self.table = ttk.Treeview(self, columns="Function", bootstyle=ttk.PRIMARY)
        self.table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.table.bind("<Motion>", "break")
        self.table.bind("<ButtonRelease-1>", lambda event: self.check_selection())

        self.table.column("#0", width=100, minwidth=100, anchor=tk.W)
        self.table.heading("#0", text="Label", anchor=tk.W)
        self.table.column("Function", width=400, minwidth=400, anchor=tk.W)
        self.table.heading('Function', text='Function', anchor=tk.W)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT, fill=tk.X)

        self.add_new_button = ttk.Button(self.button_frame, text="Add new", command=self.new_function_handler)
        self.add_new_button.pack(padx=5, side=tk.RIGHT, fill=tk.X)

        self.edit_button = ttk.Button(self.button_frame, text="Edit code", command=self.open_code_editor)

        self.edit_label_button = ttk.Button(self.button_frame, text="Edit label", command=self.open_label_editor)

        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_method, bootstyle=ttk.DANGER)

        self.add_methods()

        self.buttons_hidden = True

    def check_selection(self):
        """
        Check if something is selected on the table.

        If nothing is selected then it will hide buttons to edit
        selected function.

        :return: None
        """
        if self.table.selection() and self.buttons_hidden:
            self.buttons_hidden = False
            self.edit_button.pack(padx=5, side=tk.LEFT, fill=tk.X)
            self.edit_label_button.pack(padx=5, side=tk.LEFT, fill=tk.X)
            self.delete_button.pack(padx=5, side=tk.LEFT, fill=tk.X)
        elif not self.table.selection() and not self.buttons_hidden:
            self.buttons_hidden = True
            self.edit_button.pack_forget()
            self.edit_label_button.pack_forget()
            self.delete_button.pack_forget()

    def new_function_handler(self):
        """
        Handle adding new function.

        Asks the user if they want to create a function theirself or import a function.

        :return: None
        """
        on_import = messagebox.askyesnocancel("Add new function", "Would you like to import a new function?")
        if on_import is None:
            return
        elif on_import:
            file = filedialog.askopenfilename(filetypes=[("python files", "*.py")], title="Add new function")
            if not file:
                return
            with open(file, "r") as f:
                code = f.read()
            editor = CodeEditor(self.main_diagram, label=file.split("/")[-1][:-3], code=code)
            editor.save_handler(destroy=False)
        else:
            self.add_new_function()

    def add_new_function(self):
        """
        Add a new function.

        Asks the user for a label and opens a CodeEditor for the user to enter a new function.

        :return:
        """
        label = simpledialog.askstring("Add label", "Please enter new label")
        if label:
            label = label.strip()
        if label is None:
            return
        if not label or label in self.main_diagram.label_content.keys():
            messagebox.showerror(title="Error", message="Label is empty or already exists")
            self.add_new_function()
            return
        CodeEditor(self.main_diagram, label=label, code="")

    def add_methods(self):
        """
        Add methods to the table.

        Clears the table and adds methods to it from MainDiagram.label_content.

        :return: None
        """
        self.table.delete(*self.table.get_children())
        for label, method in self.main_diagram.label_content.items():
            self.table.insert('', tk.END, text=label, values=(method.replace('\n', ''),))
            # The tuple with a comma in values is necessary to prevent tkinter splitting string.

    def delete_method(self):
        """
        Delete selected function.

        :return: None
        """
        label = self.table.item(self.table.focus())["text"]
        item = self.table.selection()[0]
        del self.main_diagram.label_content[label]
        self.table.delete(item)
        self.write_to_json(self.main_diagram.label_content)
        for canvas in self.main_diagram.canvasses.values():
            for box in canvas.boxes:
                if box.label_text == label:
                    box.edit_label(new_label="")
        self.check_selection()

    def open_code_editor(self):
        """
        Open CodeEditor for the selected function.

        :return: None
        """
        label = self.table.item(self.table.focus())["text"]
        code = self.main_diagram.label_content[label]
        CodeEditor(self.main_diagram, label=label, code=code)

    def open_label_editor(self):
        """
        Open a simple string dialog to edit the label of the selected function.

        :return: None
        """
        label = self.table.item(self.table.focus())["text"]
        if label:
            new_label = simpledialog.askstring("Input", "Enter new label", initialvalue=label)
            if new_label:
                self.main_diagram.change_function_label(label, new_label)
                self.add_methods()
                self.write_to_json(self.main_diagram.label_content)

    @staticmethod
    def write_to_json(content):
        """
        Writes content into the functions_conf file.

        :param content: Dictionary that will be written to the functions conf file.
        :return:
        """
        with open(const.FUNCTIONS_CONF, "r+") as file:
            json_object = json.dumps(content, indent=4)
            file.seek(0)
            file.truncate(0)
            file.write(json_object)
