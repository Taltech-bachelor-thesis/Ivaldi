import tkinter as tk


class ManageBoxes(tk.Toplevel):
    """
    ManageBoxes is a window that allows the user to manage preset Boxes in the application.
    """
    def __init__(self, master, main_diagram):
        """
        ManageBoxes constructor.

        :param master: Tkinter master window.
        :param main_diagram: MainDiagram used for accessing functions and variables.
        """
        super().__init__(master)
        self.main_diagram = main_diagram
        self.title("Manage preset Boxes")

        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        [self.listbox.insert(tk.END, item) for item in self.main_diagram.boxes]

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        remove_button = tk.Button(button_frame, text="Remove preset", command=self.remove_selected_item)
        remove_button.pack(side=tk.LEFT, padx=5)

    def remove_selected_item(self):
        """
        Remove selected item from Listbox.

        :return: None
        """
        selected_item_index = self.listbox.curselection()
        if selected_item_index:
            name = self.listbox.get(selected_item_index)
            self.remove_option(name)
            self.listbox.delete(selected_item_index)

    def remove_option(self, option):
        """
        Removes option from configuration file.

        :param option: Option to remove from box configuration.
        :return: None
        """
        self.main_diagram.project_exporter.del_box_menu_option(option)
        self.main_diagram.update_add_box_dropdown_menu()
