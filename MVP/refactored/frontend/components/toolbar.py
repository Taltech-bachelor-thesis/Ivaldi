import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from PIL import Image, ImageTk

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.frontend.windows.help_window import HelpWindow
from constants import *


class Toolbar(ttk.Frame):
    """
    Toolbar is the file menu bar of our application. It holds different save, generation, importing functions along
    with settings.
    """
    def __init__(self, main_diagram):
        """
        Toolbar constructor.

        :param main_diagram: MainDiagram object used to access functions.
        """
        super().__init__(main_diagram)
        self.main_diagram = main_diagram
        self.config(bootstyle=ttk.LIGHT)

        # File button
        self.file_button = tk.Menubutton(self, text="File",
                                         width=5, indicatoron=False)
        self.file_menu = tk.Menu(self.file_button, tearoff=False)
        self.file_button.config(menu=self.file_menu)

        # File -> Save as
        self.save_submenu = tk.Menu(self.file_menu, tearoff=False)
        self.save_submenu.add_command(label="png file", command=lambda: self.main_diagram.custom_canvas.save_as_png())
        self.save_submenu.add_command(label="project", command=lambda: self.main_diagram.save_to_file())
        self.save_submenu.add_command(label="hypergraph",
                                      command=lambda: self.main_diagram.custom_canvas.export_hypergraph())

        # File -> Generate
        self.generate_submenu = tk.Menu(self.file_menu, tearoff=False)
        self.generate_submenu.add_command(label="TikZ", command=lambda: self.main_diagram.custom_canvas.open_tikz_generator())
        self.generate_submenu.add_command(label="code", command=lambda: self.main_diagram.generate_code())

        # File menu buttons
        self.file_menu.add_cascade(menu=self.save_submenu, label="Save as")
        self.file_menu.add_cascade(menu=self.generate_submenu, label="Generate")
        self.file_menu.add_command(label="New", command=self.handle_new_graph)
        self.file_menu.add_command(label="Import new diagram", command=lambda: self.handle_new_graph(import_=True))
        self.file_menu.add_command(label="Import as sub-diagram", command=self.import_sub_diagram)
        self.file_button.pack(side=ttk.LEFT)

        # Edit button
        self.edit_button = tk.Menubutton(self, text="Edit", width=5, indicatoron=False)
        self.edit_menu = tk.Menu(self.edit_button, tearoff=False)
        self.edit_button.config(menu=self.edit_menu)

        # Edit menu buttons
        self.edit_menu.add_command(label="Search in Project",
                                   command=lambda: self.main_diagram.open_search_window())
        self.edit_button.pack(side=ttk.LEFT)

        # View button
        self.view_button = tk.Menubutton(self, text="View",
                                         width=5, indicatoron=False)
        self.view_menu = tk.Menu(self.view_button, tearoff=False)
        self.view_button.config(menu=self.view_menu)

        # # View menu buttons
        self.view_menu.add_command(label="Visualize hypergraph",
                                   command=lambda: self.main_diagram.visualize_as_graph())
        self.view_menu.add_command(label="DEBUG",
                                   command=lambda: self.debug())

        self.view_button.pack(side=ttk.LEFT)

        self.help_logo = (Image.open(ASSETS_DIR + "/help-circle-outline.png"))
        self.help_logo = self.help_logo.resize((21, 21))
        self.help_logo = ImageTk.PhotoImage(self.help_logo)

        help_button = ttk.Label(self, image=self.help_logo, bootstyle="inverse-light")
        help_button.pack(side=ttk.RIGHT, anchor=tk.CENTER, padx=(0, 5))

        help_button.bind("<Button-1>", lambda event: self.open_help_window())

        # Current canvas name
        self.canvas_name_text = tk.StringVar()
        self.canvas_name_label = ttk.Label(self, textvariable=self.canvas_name_text,
                                           bootstyle="inverse-light", font="Helvetica 15 bold")

    def debug(self):
        receiver = self.main_diagram.receiver
        manager = HypergraphManager
        print()

    def open_help_window(self):
        """
        Create and display the help window.

        Creates a HelpWindow object.

        :return: None
        """
        HelpWindow(self.main_diagram)

    def import_sub_diagram(self):
        """
        Import a diagram as a sub-diagram.

        Imports a saved diagram as a sub-diagram to the currently open diagram.

        :return: None
        """
        box = self.main_diagram.custom_canvas.add_box(loc=(200, 100))
        sub_diagram = box.edit_sub_diagram(switch=False)

        main_canvas = self.main_diagram.importer.canvas
        self.main_diagram.importer.canvas = sub_diagram
        is_importing = self.main_diagram.importer.import_diagram()
        for _ in range(len(sub_diagram.inputs)):
            box.add_left_connection()
        for _ in range(len(sub_diagram.outputs)):
            box.add_right_connection()
        self.main_diagram.importer.canvas = main_canvas
        if not is_importing:
            box.delete_box()

    def update_canvas_label(self):
        """
        Update canvas name label.

        Updates the name label in the Toolbar that displays the currently opened CustomCanvas name.

        :return: None
        """
        self.canvas_name_text.set(self.main_diagram.custom_canvas.name_text)
        self.canvas_name_label.place_forget()
        tree_width = self.main_diagram.tree.winfo_width() if self.main_diagram.is_tree_visible else 0
        width = self.main_diagram.custom_canvas.winfo_width()
        self.canvas_name_label.place(x=tree_width + width / 2, anchor=tk.N)

    def confirm_deletion(self):
        """
        Ask user for deletion confirmation.

        Asks user whether they wish to save progress.
        If the user wishes to save then a save function is called in MainDiagram.

        :return: Dialog result, tk.NO |tk.YES |tk.NONE
        """
        dialog = messagebox.askyesnocancel(title="Warning",
                                           message="All unsaved progress will be deleted. Do you wish to save?")
        match dialog:
            case tk.NO:
                return tk.NO
            case tk.YES:
                self.main_diagram.save_to_file()
                return tk.YES
            case _:
                return tk.NONE

    def handle_new_graph(self, import_=False):
        """
        Handle creating a new graph.

        Will delete the current diagram, and if specified with a function parameter, will also import a new diagram.

        :param import_: (Optional) Boolean that specifies whether a new diagram should be importer after deletion of
        previous diagram.
        :return: None
        """
        root_canvas = list(self.main_diagram.canvasses.items())[0][1]
        if root_canvas.boxes or root_canvas.spiders or root_canvas.wires or root_canvas.outputs or root_canvas.inputs:
            dialog_result = self.confirm_deletion()
            if dialog_result == tk.NONE:
                return
            self.main_diagram.switch_canvas(root_canvas)
            root_canvas.delete_everything()
        if import_:
            self.main_diagram.load_from_file()
