import hashlib
import json
import os
import tkinter as tk
from contextlib import ExitStack
from tkinter import messagebox, filedialog
from tkinter import simpledialog

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import make_interp_spline
from ttkbootstrap.constants import *

import constants as const
import tikzplotlib
from MVP.refactored.backend.code_generation.code_generator import CodeGenerator
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.visualization.visualization import Visualization
from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.types.wire_types import WireType
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.components.toolbar import Toolbar
from MVP.refactored.frontend.util.selector import Selector
from MVP.refactored.frontend.windows.code_editor import CodeEditor
from MVP.refactored.frontend.windows.manage_boxes import ManageBoxes
from MVP.refactored.frontend.windows.manage_methods import ManageMethods
from MVP.refactored.frontend.windows.search_window import SearchWindow
from MVP.refactored.modules.notations.notation_tool import get_notations, is_canvas_complete
from MVP.refactored.util.exporter.project_exporter import ProjectExporter
from MVP.refactored.util.importer.json_importer.json_importer import JsonImporter
from MVP.refactored.util.importer.python_importer.python_importer import PythonImporter
from constants import *


class MainDiagram(tk.Tk):
    """
    `MainDiagram` is the main class of the application. All objects are accessible through this. It is the main window that
    you see when using the application.
    """
    def __init__(self, receiver, load=False):
        """
        MainDiagram constructor.

        :param receiver: Receiver object for sending information to backend.
        :param load: Boolean if a diagram should be loaded upon opening.
        """
        super().__init__()
        self.title("Dynamic String Diagram Canvas")
        self.receiver = receiver

        self.toolbar = Toolbar(self)
        self.toolbar.pack(side='top', fill='both')

        screen_width_min = round(self.winfo_screenwidth() / 1.5)
        screen_height_min = round(self.winfo_screenheight() / 1.5)
        self.wm_minsize(screen_width_min, screen_height_min)

        self.is_search_active = False

        self.selector = None

        self.search_results = []
        self.active_search_index = 0
        self.search_objects = {}
        self.wire_objects = {}

        self.custom_canvas = CustomCanvas(self, self)
        self.custom_canvas.focus_set()
        self.custom_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.selector = Selector(self, self.receiver)
        self.custom_canvas.selector = self.selector

        self.bind("<Button-1>", lambda event: self.custom_canvas.focus_set())
        self.bind("<Control-f>", lambda event: self.open_search_window())
        self.search_window = None

        self.is_tree_visible = True
        self.tree = ttk.Treeview(self, bootstyle=SECONDARY)
        self.tree.bind("<Motion>", "break")
        self.tree.pack(side=tk.LEFT, before=self.custom_canvas, fill=tk.Y)
        self.tree.update()
        self.tree.config(height=20)  # Number of visible rows

        # Add some items to the tree
        self.tree.insert("", "end", str(self.custom_canvas.id), text="Root")
        self.canvasses = {str(self.custom_canvas.id): self.custom_canvas}
        self.custom_canvas.set_name("root")
        self.tree_root_id = str(self.custom_canvas.id)
        # Bind the treeview to the click event
        self.tree.bind("<ButtonRelease-1>", lambda event: self.on_tree_select())
        self.tree.update()

        self.toggle_treeview()

        self.control_frame = ttk.Frame(self, bootstyle=LIGHT)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.project_exporter = ProjectExporter(self.custom_canvas)
        self.json_importer = JsonImporter(self.custom_canvas)
        self.python_importer = PythonImporter(self.custom_canvas)
        # Add undefined box
        self.undefined_box_button = ttk.Button(self.control_frame, text="Add Undefined Box",
                                               command=self.custom_canvas.add_box, width=20,
                                               bootstyle=(PRIMARY, OUTLINE))
        self.undefined_box_button.pack(side=tk.TOP, padx=5, pady=5)
        self.undefined_box_button.update()

        self.shape_dropdown_button = ttk.Menubutton(self.control_frame, text="Select Box Shape", width=16,
                                                    bootstyle=(PRIMARY, OUTLINE))
        self.shape_dropdown_menu = ttk.Menu(self.shape_dropdown_button, tearoff=0)
        self.shape_dropdown_button.config(menu=self.shape_dropdown_menu)
        self.shape_dropdown_button.pack(side=tk.TOP, padx=5, pady=5)
        self.update_shape_dropdown_menu()

        self.boxes = {}
        self.quick_create_boxes = []

        # Create Menubutton and Menu for dropdown
        self.add_box_dropdown_button = ttk.Menubutton(self.control_frame, text="Select Box to Add", width=16,
                                                      bootstyle=(PRIMARY, OUTLINE))
        self.add_box_dropdown_menu = ttk.Menu(self.add_box_dropdown_button, tearoff=0)
        self.add_box_dropdown_button.config(menu=self.add_box_dropdown_menu)
        self.add_box_dropdown_button.pack(side=tk.TOP, padx=5, pady=5)
        self.update_add_box_dropdown_menu()

        self.manage_boxes = ttk.Button(self.control_frame, text="Manage Boxes",
                                       command=self.manage_boxes_method, width=20, bootstyle=(PRIMARY, OUTLINE))
        self.manage_boxes.pack(side=tk.TOP, padx=5, pady=5)

        self.quick_create_booleans = []
        self.get_boxes_from_file()
        self.manage_quick_create = ttk.Button(self.control_frame, text="Manage Quick Create",
                                              command=self.manage_quick_create, width=20, bootstyle=(PRIMARY, OUTLINE))
        self.manage_quick_create.pack(side=tk.TOP, padx=5, pady=5)

        self.manage_methods_button = ttk.Button(self.control_frame, text="Manage Methods",
                                                command=self.open_manage_methods_window, width=20,
                                                bootstyle=(PRIMARY, OUTLINE))
        self.manage_methods_button.pack(side=tk.TOP, padx=5, pady=5)

        # Add Spider
        self.spider_button = ttk.Button(self.control_frame, text="Add Spider",
                                        command=self.custom_canvas.add_spider, width=20, bootstyle=(PRIMARY, OUTLINE))
        self.spider_button.pack(side=tk.TOP, padx=5, pady=5)

        self.rename = ttk.Button(self.control_frame, text="Rename Diagram",
                                 command=self.rename, width=20, bootstyle=(PRIMARY, OUTLINE))
        self.rename.pack(side=tk.TOP, padx=5, pady=5)

        self.random = ttk.Button(self.control_frame, text="Connect At Random",
                                 command=self.custom_canvas.random, width=20, bootstyle=(PRIMARY, OUTLINE))
        self.random.pack(side=tk.TOP, padx=5, pady=5)

        self.alg_not = ttk.Button(self.control_frame, text="Get Algebraic Notation",
                                  command=self.create_algebraic_notation, width=20, bootstyle=(PRIMARY, OUTLINE))
        self.alg_not.pack(side=tk.TOP, padx=5, pady=5)

        # Button for Draw Wire Mode
        self.draw_wire_button = ttk.Button(self.control_frame, text="Draw Wire Mode",
                                           command=self.custom_canvas.toggle_draw_wire_mode, width=20,
                                           bootstyle=(PRIMARY, OUTLINE))
        self.draw_wire_button.pack(side=tk.TOP, padx=5, pady=25)

        # Bottom buttons
        buttons = {
            "Remove input": self.custom_canvas.remove_diagram_input,
            "Remove output": self.custom_canvas.remove_diagram_output,
            "Add input": self.custom_canvas.add_diagram_input,
            "Add output": self.custom_canvas.add_diagram_output
        }
        self.saved_buttons = {}
        for name, method in buttons.items():
            button = ttk.Button(self.control_frame, text=name, command=method, width=20, bootstyle=(PRIMARY, OUTLINE))
            button.pack(side=tk.BOTTOM, padx=5, pady=5)
            self.saved_buttons[name] = button

        self.json_file_hash = self.calculate_boxes_json_file_hash()
        self.label_content = {}
        self.load_functions()
        self.manage_methods = None
        self.import_counter = 0

        if load:
            self.load_from_file()

        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

    @staticmethod
    def calculate_boxes_json_file_hash():
        """
        Return the hash of boxes_conf file.

        :return: String hash of boxes configuration file.
        """
        with open(const.BOXES_CONF, "r") as file:
            file_hash = hashlib.sha256(file.read().encode()).hexdigest()
        return file_hash

    def load_functions(self):
        """
        Load functions configuration.

        If function configuration exists, it will load them into label_content.

        :return: None
        """
        if os.stat(const.FUNCTIONS_CONF).st_size != 0:
            with open(const.FUNCTIONS_CONF, "r") as file:
                self.label_content = json.load(file)

    def add_function_to_label_content(self, function_name: str, function_code: str) -> None:
        """
        Add function to label content dictionary.

        :param function_name: Name of the function.
        :param function_code: Code of the function.
        :return: None
        """
        self.label_content[function_name] = function_code

    def generate_code(self):
        """
        Generate code based on diagram.

        Use CodeGenerator to generate code from diagram. This will also open a CodeEditor to display the code that
        was generated.

        :return: None
        """
        code = CodeGenerator.generate_code(self.custom_canvas)
        CodeEditor(self, code=code, is_generated=True)

    def open_manage_methods_window(self):
        """
        Open ManageMethods window.

        :return: None
        """
        self.manage_methods = ManageMethods(self)

    def open_search_window(self):
        """
        Open SearchWindow.

        Opens a new SearchWindow or brings an existing one into focus.

        :return: None
        """
        try:
            self.search_window.focus()
        except (tk.TclError, AttributeError):
            self.search_window = SearchWindow(self)

    def cancel_search_results(self):
        """
        Cancel search results in diagram.

        Clears search result variables and disables search highlighting on canvases.

        :return: None
        """
        self.is_search_active = False
        self.search_results = []
        self.active_search_index = 0
        self.search_objects = {}
        self.wire_objects = {}
        for canvas in self.canvasses.values():
            canvas.remove_search_highlights()

    def move_between_search_results(self, up: bool):
        """
        Move primary highlight between results.

        Will make the next result primarily highlighted, and potentially change canvas if necessary.

        :param up: Define if moving is done up or down.
        :return: None
        """
        current_search = self.search_results[self.active_search_index]
        for index in current_search:
            self.search_objects[index].search_highlight_secondary()
        for wire in self.wire_objects[tuple(current_search)]:
            wire.search_highlight_secondary()

        if up:
            self.active_search_index += 1
        else:
            self.active_search_index -= 1

        self.active_search_index %= len(self.search_results)

        self.highlight_search_result_by_index(self.active_search_index)
        self.check_search_result_canvas(self.active_search_index)
        self.update_search_result_button_texts()

    def update_search_result_button_texts(self):
        """
        Update text on SearchResultButton.

        :return: None
        """
        for canvas in self.canvasses.values():
            canvas.search_result_button.info_text.set(f"Search: {self.active_search_index + 1}/{len(self.search_results)}")

    def check_search_result_canvas(self, index):
        """
        Check CustomCanvas of search result items at index.

        Checks if the items at index of search results are on the same CustomCanvas.
        If they are on a different CustomCanvas then the active canvas will be changed to the new one.

        :param index: index of search result to check canvas of.
        :return: None
        """
        new_canvas = self.search_objects[self.search_results[index][0]].canvas
        if new_canvas != self.custom_canvas:
            self.switch_canvas(new_canvas)

    def highlight_search_result_by_index(self, index):
        """
        Highlight search results at index.

        Given an index, it will highlight the search result objects that are in the results with that index.

        :param index: Index of search results.
        :return: None
        """
        new_search = self.search_results[index]
        for index in new_search:
            self.search_objects[index].search_highlight_primary()
        for wire in self.wire_objects[tuple(new_search)]:
            wire.search_highlight_primary()

    def change_function_label(self, old_label, new_label):
        """
        Change label of function.

        Update the label for a function, searches by `old_label` and changes it to `new_label`

        :param old_label: Old label that will be changed
        :param new_label: String that old label will be changed to
        :return: None
        """
        if old_label in self.label_content.keys():
            code = self.label_content[old_label]
            self.label_content[new_label] = code
            del self.label_content[old_label]
            for canvas in self.canvasses.values():
                for box in canvas.boxes:
                    if box.label_text == old_label:
                        box.edit_label(new_label)

    def create_algebraic_notation(self):
        """
        Opens the algebraic notation window.

        :return: None
        """
        if not is_canvas_complete(self.custom_canvas):
            text = "Diagram is incomplete!"
            text_window = tk.Toplevel(self)
            text_window.title("Algebraic Notation")

            text_box = tk.Text(text_window, wrap='word', width=40,
                               height=10)
            text_box.pack(padx=10, pady=10)

            text_box.insert(tk.END, text)

            text_box.config(state=tk.DISABLED)

        else:
            texts = get_notations(self.custom_canvas)

            text_window = tk.Toplevel(self)
            text_window.title("Algebraic Notation")
            notebook = ttk.Notebook(text_window)
            notebook.pack(fill='both', expand=True)

            for name, text in texts.items():
                frame = ttk.Frame(notebook)
                notebook.add(frame, text=name)

                text_box = tk.Text(frame, wrap='word', font=('Times New Roman', 15))
                text_box.pack(padx=10, pady=10, fill='both', expand=True)
                text_box.insert(tk.END, text)
                text_box.config(state=tk.DISABLED)
                # Create a button to copy text to clipboard
                copy_button = tk.Button(frame, text="Copy", command=lambda tb=text_box: self.copy_to_clipboard(tb))
                copy_button.pack(pady=5)

    def visualize_as_graph(self):
        """
        Open graph visualization window.

        :return: None
        """
        hypergraphs: list[Hypergraph] = HypergraphManager.get_graphs_by_canvas_id(self.custom_canvas.id)
        if len(hypergraphs) == 0:
            messagebox.showerror("Error", f"No hypergraph found with ID: {self.custom_canvas.id}")
            return

        plot_window = tk.Toplevel(self)
        plot_window.title("Graph Visualization")

        try:
            figure = Visualization.create_visualization_of_hypergraphs(self.custom_canvas.id)
        except Exception as e:
            messagebox.showerror("Error", "Failed to generate the visualization." +
                                 f"Error during visualization: {e}")
            plot_window.destroy()
            return

        figure_canvas = FigureCanvasTkAgg(figure, master=plot_window)
        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plot_window.update_idletasks()
        plot_window.deiconify()

    def copy_to_clipboard(self, text_box):
        """
        Copy text from Tkinter.Text to clipboard.

        :param text_box: tkinter.Text containing text that will be copied.
        :return: None
        """
        self.clipboard_clear()  # Clear the clipboard
        text = text_box.get("1.0", tk.END)  # Get the content of the text box
        self.clipboard_append(text)  # Append the text to the clipboard
        self.update()  # Now it stays on the clipboard even after the window is closed

    def open_children(self, parent):
        """
        Open children of parent in treeview.

        :param parent: Treeview item
        :return: None
        """
        self.tree.item(parent, open=True)  # open parent
        for child in self.tree.get_children(parent):
            self.open_children(child)  # recursively open children

    def bind_buttons(self):
        """
        Bind button functions to input/output add/remove buttons.

        :return: None
        """
        self.undefined_box_button.configure(command=self.custom_canvas.add_box)
        self.manage_boxes.configure(command=self.manage_boxes_method)
        self.spider_button.configure(command=self.custom_canvas.add_spider)

        self.draw_wire_button.configure(command=self.custom_canvas.toggle_draw_wire_mode)

        self.random.configure(command=self.custom_canvas.random)
        if not self.custom_canvas.diagram_source_box:
            buttons = {
                "Remove input": self.custom_canvas.remove_diagram_input,
                "Remove output": self.custom_canvas.remove_diagram_output,
                "Add input": self.custom_canvas.add_diagram_input,
                "Add output": self.custom_canvas.add_diagram_output
            }
        else:
            buttons = {
                "Remove input": self.remove_diagram_input,
                "Remove output": self.remove_diagram_output,
                "Add input": self.add_diagram_input,
                "Add output": self.add_diagram_output
            }
        for name, button in self.saved_buttons.items():
            button.configure(command=buttons[name])

    def add_canvas(self, canvas):
        """
        Add new CustomCanvas to diagram.

        Adds a new diagram to the treeview containing canvases.

        :param canvas: CustomCanvas to be added to diagram tree.
        :return: None
        """
        # Add some items to the tree
        try:
            parent_id = 1
            if canvas.parent_diagram is not None:
                parent_id = canvas.parent_diagram.id
            self.tree.insert(str(parent_id), "end", str(canvas.id), text=canvas.name_text)
        except (tk.TclError, AttributeError) as e:
            if "already exists" in str(e):
                self.import_counter += 1
                canvas.id += self.import_counter
            try:
                self.tree.insert(str(canvas.parent_diagram.id), "end", str(canvas.id), text=canvas.name_text)
            except (tk.TclError, AttributeError):
                self.tree.insert(str(self.custom_canvas.id), "end", str(canvas.id), text=canvas.name_text)
        self.canvasses[str(canvas.id)] = canvas
        for box in canvas.boxes:
            if box.sub_diagram:
                self.tree.move(str(box.sub_diagram.id), str(canvas.id), "end")

        # Expand all items in the tree
        self.open_children(self.tree_root_id)

    def get_canvas_by_id(self, canvas_id):
        """
        Return CustomCanvas object by ID.

        :param canvas_id: ID for CustomCanvas.
        :return: CustomCanvas object
        """
        return self.canvasses[canvas_id]

    def update_canvas_name(self, canvas):
        """
        Update canvas name in treeview.

        :param canvas: CustomCanvas that will have its name updated.
        :return: None
        """
        self.tree.item(str(canvas.id), text=canvas.name_text)

    def rename(self):
        """
        Rename the currently open canvas.

        Opens a dialog for the user to change the name for the canvas.

        :return: None
        """
        if self.custom_canvas.diagram_source_box:
            txt = "Enter label for sub-diagram:"
        else:
            txt = "Enter label for root diagram:"
        new_name = simpledialog.askstring("Input", txt, initialvalue=self.custom_canvas.name_text)

        if new_name:
            self.custom_canvas.set_name(new_name)
            self.update_canvas_name(self.custom_canvas)
            if self.custom_canvas.diagram_source_box:
                self.custom_canvas.diagram_source_box.set_label(new_name)

    def switch_canvas(self, canvas):
        """
        Switch the currently displayed CustomCanvas.

        :param canvas: CustomCanvas that will be displayed after switch.
        :return: None
        """
        for item in self.custom_canvas.selector.selected_items:
            item.deselect()
        width = self.custom_canvas.winfo_width()
        self.custom_canvas.selector.selected_items.clear()
        self.custom_canvas.reset_zoom()
        self.custom_canvas.pack_forget()
        self.custom_canvas = canvas
        self.selector.canvas = self.custom_canvas
        # Show the selected canvas
        self.custom_canvas.pack(fill='both', expand=True)
        self.custom_canvas.configure(width=width)
        self.custom_canvas.update()
        self.custom_canvas.update_search_results_button()
        self.bind_buttons()

        self.toolbar.update_canvas_label()

        self.tree.selection_remove(self.tree.selection())

        self.tree.selection_set(str(canvas.id))
        self.tree.see(str(canvas.id))

    def del_from_canvasses(self, canvas):
        """
        Delete `CustomCanvas` from `self.canvasses`.

        :param canvas: CustomCanvas that will be deleted.
        :return: None
        """
        self.tree.delete(str(canvas.id))
        del self.canvasses[str(canvas.id)]

    def on_tree_select(self):
        """
        Handle tree select.

        Will take the currently selected item in treeview and switch to that canvas.

        :return: None
        """
        # Get the selected item
        selected_item = self.tree.focus()
        if selected_item:
            new_canvas = self.canvasses[selected_item]
            self.switch_canvas(new_canvas)
            new_canvas.focus_set()

    def add_diagram_input(self, id_=None):
        """
        Add input to currently opened diagram.

        :param id_: ID that will be added to input.
        :return: Box connection and diagram input tags.
        """
        box_c = None
        if self.custom_canvas.diagram_source_box:
            box_c = self.custom_canvas.diagram_source_box.add_left_connection()
        canvas_i = self.custom_canvas.add_diagram_input(id_=id_)
        return box_c, canvas_i

    def add_diagram_output(self, id_=None):
        """
        Add output to currently opened diagram.

        :param id_: ID that will be added to output.
        :return: Box connection and diagram output tags.
        """
        box_c = None
        if self.custom_canvas.diagram_source_box:
            box_c = self.custom_canvas.diagram_source_box.add_right_connection()
        canvas_o = self.custom_canvas.add_diagram_output(id_=id_)
        return box_c, canvas_o

    def remove_diagram_input(self):
        """
        Remove input from currently opened diagram.

        :return: None
        """
        if self.custom_canvas.diagram_source_box:
            c: Connection = self.find_connection_to_remove(const.LEFT)
            if c:
                self.custom_canvas.diagram_source_box.remove_connection(c)
            self.custom_canvas.remove_diagram_input()
            if self.receiver.listener:
                self.receiver.receiver_callback(ActionType.BOX_REMOVE_INNER_LEFT,
                                                generator_id=self.custom_canvas.diagram_source_box.id,
                                                canvas_id=self.custom_canvas.id, connection_id=c.id)
        else:
            self.custom_canvas.remove_diagram_input()

    def remove_diagram_output(self):
        """
        Remove output from currently opened diagram.

        :return: None
        """
        if self.custom_canvas.diagram_source_box:

            c = self.find_connection_to_remove(const.RIGHT)
            if c:
                self.custom_canvas.diagram_source_box.remove_connection(c)
            self.custom_canvas.remove_diagram_output()
            if self.receiver.listener:
                self.receiver.receiver_callback(ActionType.BOX_REMOVE_INNER_RIGHT,
                                                generator_id=self.custom_canvas.diagram_source_box.id, canvas_id=self.custom_canvas.id,
                                                connection_id=c.id)
        else:
            self.custom_canvas.remove_diagram_output()

    def find_connection_to_remove(self, side):
        """
        Return `Connection` with the highest index on given side.

        :param side: side to find Connection on.
        :return: Connection object.
        """
        c_max = 0
        c = None
        for connection in self.custom_canvas.diagram_source_box.connections:
            if connection.side == side and connection.index >= c_max:
                c_max = connection.index
                c = connection
        return c

    def manage_boxes_method(self):
        """
        Open manage boxes window.

        :return: None
        """
        ManageBoxes(self, self)

    def manage_quick_create(self):
        """
        Open manage quick create window.

        :return: None
        """
        list_window = tk.Toplevel(self, width=100)
        list_window.minsize(100, 150)
        list_window.title("List of Boxes")

        if self.calculate_boxes_json_file_hash() != self.json_file_hash:
            self.get_boxes_from_file()

        checkbox_frame = tk.Frame(list_window)
        for i, box in enumerate(self.boxes):
            checkbox = tk.Checkbutton(checkbox_frame, text=box, variable=self.quick_create_booleans[i])
            checkbox.pack(padx=5, anchor=tk.W)

        checkbox_frame.pack(pady=10)

        button_frame = tk.Frame(list_window)
        button_frame.pack(pady=10)

        def save():
            self.quick_create_boxes = []
            for j, name in enumerate(self.boxes):
                if self.quick_create_booleans[j].get():
                    self.quick_create_boxes.append(name)
                else:
                    try:
                        self.quick_create_boxes.remove(name)
                    except ValueError:
                        pass
            list_window.destroy()

        remove_button = tk.Button(button_frame, text="Save", command=save)
        remove_button.pack(padx=5)

    def update_add_box_dropdown_menu(self):
        """
        Update add_box_dropdown menu.

        :return: None
        """
        self.boxes = {}

        self.get_boxes_from_file()
        # Clear existing menu items

        # add undefined box button as well to make width greater
        self.add_box_dropdown_menu.delete(0, tk.END)
        self.add_box_dropdown_menu.add_command(label="Add Undefined Box",
                                               command=self.custom_canvas.add_box)
        self.add_box_dropdown_menu.add_separator()

        # Add options to the dropdown menu
        for i, name in enumerate(self.boxes):
            self.add_box_dropdown_menu.add_command(label=name, command=lambda n=name: self.boxes[n](n, self.custom_canvas))

    def remove_option(self, option):
        """
        Remove preset Box from configuration files.

        :param option: Preset that will be removed.
        :return: None
        """
        self.project_exporter.del_box_menu_option(option)
        self.update_add_box_dropdown_menu()

    def get_boxes_from_file(self):
        """
        Load preset Boxes from file.

        :return: None
        """
        d = self.json_importer.load_boxes_to_menu()
        self.quick_create_booleans = []
        for k in d:
            self.boxes[k] = self.add_custom_box
            self.quick_create_booleans.append(tk.BooleanVar())

    def add_custom_box(self, name, canvas):
        """
        Add custom preset Box to currently open CustomCanvas.

        :param name: name of box to add.
        :param canvas: canvas to add box to.
        :return: None
        """
        self.json_importer.add_box_from_menu(canvas, name)

    def save_box_to_diagram_menu(self, box):
        """
        Save new `Box` to presets.

        :param box: `Box` that will be saved
        :return: None
        """
        self.project_exporter.export_box_to_menu(box)
        self.update_add_box_dropdown_menu()

    def set_title(self, filename):
        """
        Set title of MainDiagram.

        :param filename: New title of MainDiagram
        :return: None
        """
        self.title(filename.replace(".json", ""))

    def confirm_exit(self):
        """
        Ask confirmation for exiting the application.

        :return: None
        """
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.destroy()

    def save_to_file(self):
        """
        Save current diagram as a json file.

        :return: None
        """
        self.custom_canvas.reset_zoom()
        filename = self.project_exporter.export()
        self.set_title(filename)

    def load_from_file(self):
        """
        Load a diagram into the application.

        :return: None
        """
        filetypes = (("JSON files", "*.json"), ("Python files", "*.py"), ("All files", "*.*"))
        allowed_multiple_files_filetypes = {".py"}
        importers = {".json": self.json_importer, ".py": self.python_importer}

        while True:
            file_paths = filedialog.askopenfilenames(title="Select JSON / Python file", filetypes=filetypes)
            if not file_paths:
                return

            with ExitStack() as stack:
                try:
                    files = []
                    imported_files_extension = None
                    files_names = set()

                    for file_path in file_paths:
                        file_name, file_extension = os.path.splitext(file_path)
                        if file_name in files_names:
                            raise ValueError( f"Duplicate file name: {file_name}. Please select unique files.")

                        if not imported_files_extension:
                            imported_files_extension = file_extension

                        if file_extension != imported_files_extension:
                            raise ValueError( "Please select files with the same extension.")

                        files.append(stack.enter_context(open(file_path, 'r')))

                    if imported_files_extension not in allowed_multiple_files_filetypes and len(files) > 1:
                        raise ValueError("Selected extension does not support multiple files. Please select a single file.")

                    importer = importers.get(imported_files_extension)
                    if not importer:
                        raise ValueError("Unsupported file format!")

                    title = importer.start_import(files)

                    messagebox.showinfo("Info", "Imported successfully")
                    self.set_title(title)
                    break

                except ValueError as error:
                    messagebox.showerror("Import failed", str(error))

                except (FileNotFoundError, IOError, json.JSONDecodeError):
                    messagebox.showerror("Error", "File import failed, loading new empty canvas.")
                    break

    def update_shape_dropdown_menu(self):
        """
        Update the shape dropdown menu.

        Clears and adds commands with all shapes into the menu.

        :return: None
        """
        self.shape_dropdown_menu.delete(0, tk.END)

        for shape in const.SHAPES:
            self.shape_dropdown_menu.add_command(label=shape,
                                                 command=lambda s=shape: self.custom_canvas.set_box_shape(s))

    def toggle_treeview(self):
        """
        Toggle open the treeview.

        Opens or closes the treeview on the left side of the canvas.

        :return: None
        """
        if not self.is_tree_visible:
            self.is_tree_visible = True
            self.tree.pack(side=tk.LEFT, before=self.custom_canvas, fill=tk.Y)
            self.tree.config(height=20)  # Number of visible rows
            self.custom_canvas.configure(width=self.custom_canvas.winfo_width() - self.tree.winfo_width())
            self.tree.update()
        else:
            self.is_tree_visible = False
            self.custom_canvas.configure(width=self.custom_canvas.winfo_width() + self.tree.winfo_width())
            self.tree.pack_forget()
            self.tree.update()
        self.custom_canvas.update()
        self.custom_canvas.update_search_results_button()

    @staticmethod
    def pairwise(iterable):
        """
        s -> (s0, s1), (s2, s3), (s4, s5), ...

        :param iterable: iterable that will be turned into pairs.
        :return: Tuple of pairs of elements from iterable.
        """
        a = iter(iterable)
        return zip(a, a)

    def generate_tikz(self, canvas):
        """
        Return TikZ code for given CustomCanvas.

        :param canvas: CustomCanvas that TikZ is generated for.
        :return: String of TikZ code.
        """
        fig, ax = self.generate_matplot(canvas)

        tikzplotlib.clean_figure(fig=fig)
        tikz = tikzplotlib.get_tikz_code(figure=fig)
        plt.close()
        return tikz

    def generate_png(self, canvas, file_path):
        """
        Generate a .png file from canvas.

        :param canvas: CustomCanvas that png will be created for.
        :param file_path: file_path of png
        :return: None
        """
        fig, ax = self.generate_matplot(canvas, True)
        fig.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()

    def generate_matplot(self, canvas, show_connections=False):
        """
        Generates a matplot figure of a given canvas.

        :param canvas: CustomCanvas that matplot will be generated for.
        :param show_connections: Boolean to show Connections or not.
        :return: Generated Matplotlib figure and axes containing the drawn canvas elements.
        """
        x_max, y_max = canvas.winfo_width() / 100, canvas.winfo_height() / 100
        fig, ax = plt.subplots(1, figsize=(x_max, y_max))
        ax.set_aspect('equal', adjustable='box')

        for box in canvas.boxes:
            if box.style == const.TRIANGLE:
                polygon = patches.Polygon(((box.x / 100, y_max - box.y / 100 - box.size[1] / 100),
                                           (box.x / 100, y_max - box.y / 100),
                                           (box.x / 100 + box.size[0] / 100, y_max - box.y / 100 - box.size[1] / 200)),
                                          edgecolor=const.BLACK, facecolor="none")
            else:
                polygon = patches.Rectangle((box.x / 100, y_max - box.y / 100 - box.size[1] / 100), box.size[0] / 100,
                                            box.size[1] / 100, label="_nolegend_", edgecolor=const.BLACK,
                                            facecolor="none")
            if show_connections:
                for connection in box.connections:
                    circle = patches.Circle((connection.location[0] / 100, y_max - connection.location[1] / 100),
                                            connection.r / 100, color=const.BLACK, zorder=2)
                    ax.add_patch(circle)

            plt.text(box.x / 100 + box.size[0] / 2 / 100, y_max - box.y / 100 - box.size[1] / 2 / 100, box.label_text,
                     horizontalalignment="center", verticalalignment="center", zorder=2)
            ax.add_patch(polygon)

        for spider in canvas.spiders:
            circle = patches.Circle((spider.x / 100, y_max - spider.y / 100), spider.r / 100,
                                    color=const.BLACK, zorder=2)
            ax.add_patch(circle)

        for i_o in canvas.inputs + canvas.outputs:
            con = patches.Circle((i_o.location[0] / 100, y_max - i_o.location[1] / 100), i_o.r / 100,
                                 color=const.BLACK, zorder=2)
            ax.add_patch(con)

        for wire in canvas.wires:
            x = []
            y = []
            x_y = {}
            for x_coord, y_coord in self.pairwise(canvas.coords(wire.line)):
                x_y[x_coord / 100] = y_max - y_coord / 100

            x_y = dict(sorted(x_y.items()))
            for x_coord in x_y.keys():
                x.append(x_coord)
                y.append(x_y[x_coord])

            x = np.array(x)
            y = np.array(y)

            x_linspace = np.linspace(x.min(), x.max(), 200)
            spl = make_interp_spline(x, y, k=3)
            y_line = spl(x_linspace)

            color, style = self.get_wire_style(wire)

            plt.plot(x_linspace, y_line, style, color=color, linewidth=2, zorder=1)

        for label_tag in canvas.wire_label_tags:
            coords = canvas.coords(label_tag)
            plt.text(coords[0] / 100, y_max - coords[1] / 100, canvas.itemconfig(label_tag)['text'][-1],
                     horizontalalignment='center', verticalalignment='center', zorder=2,
                     family="cmtt10", fontsize=10)

        ax.set_xlim(0, x_max)
        ax.set_ylim(0, y_max)
        plt.axis('off')

        return fig, ax

    @staticmethod
    def get_wire_style(wire):
        """
        Return style for wire for matplot.

        Takes a Wire and returns the corresponding style for matplot usage.

        :param wire: Wire style is created for.
        :return: Tuple of color and dash style.
        """
        match wire.type:
            case WireType.FIRST:
                style = "black", ":"
            case WireType.SECOND:
                style = "black", "--"
            case WireType.THIRD:
                style = "black", "-."
            case WireType.FOURTH:
                style = "hotpink", ""
            case WireType.FIFTH:
                style = "slateblue", ""
            case WireType.SIXTH:
                style = "seagreen", ""
            case WireType.SEVENTH:
                style = "darkolivegreen", ""
            case WireType.EIGHTH:
                style = "goldenrod", ""
            case WireType.NINTH:
                style = "red", ""
            case _:
                style = "black", ""
        return style
