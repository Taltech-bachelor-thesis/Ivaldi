import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Toplevel, Frame, Label

from PIL import Image, ImageTk

import constants as const


class HelpWindow(Toplevel):
    """
    `HelpWindow` class.

    `HelpWindow` is a `tkinter.Toplevel` that displays helpful information to the user, such as key-binds.
    """
    def __init__(self, master=None):
        """
        HelpWindow constructor.

        :param master: (Optional) tk application the Toplevel is tied to.
        """
        super().__init__(master)
        self.title("Help")
        self.focus_set()
        self.resizable(False, False)
        self.geometry("400x450")
        self.bind("<FocusOut>", lambda event: self.destroy())

        self.keybind_frame = Frame(self)
        self.keybind_frame.pack(fill=tk.BOTH, expand=True)

        self.font = ("Arial", 11)

        self.key_binds_descriptions = [
            ("CTRL + N", "Create a sub-diagram from selected items"),
            ("CTRL + C", "Copy the selected items"),
            ("CTRL + V", "Paste the copied items"),
            ("CTRL + X", "Cut the selected items"),
            ("CTRL + A", "Select all items"),
            ("CTRL + F", "Open search window")
        ]
        self.items_per_page = 5
        self.current_page = 0

        self.display_key_binds()

        ttk.Separator(self.keybind_frame, orient=tk.VERTICAL).grid(column=0, row=0, rowspan=6, sticky="nse")
        ttk.Separator(self.keybind_frame, orient=tk.HORIZONTAL).grid(column=0, row=5, columnspan=2, sticky="ews")

        self.pagination_frame = Frame(self, pady=10)
        self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)

        self.backward_logo = Image.open(const.ASSETS_DIR + "/chevron-left-circle-outline.png")
        self.backward_logo = self.backward_logo.resize((35, 35))
        self.backward_logo = ImageTk.PhotoImage(self.backward_logo)

        self.backward = tk.Button(self.pagination_frame, image=self.backward_logo, command=self.previous_page)
        self.backward.config(bg=const.WHITE, activebackground=const.WHITE)

        self.forward_logo = (Image.open(const.ASSETS_DIR + "/chevron-right-circle-outline.png"))
        self.forward_logo = self.forward_logo.resize((35, 35))
        self.forward_logo = ImageTk.PhotoImage(self.forward_logo)

        self.forward = tk.Button(self.pagination_frame, image=self.forward_logo, command=self.next_page)
        self.forward.config(bg=const.WHITE, activebackground=const.WHITE)

        self.page_label = Label(self.pagination_frame, text="", font=self.font)
        self.update_page_label()

        self.pagination_frame.columnconfigure(0, minsize=100, weight=1)
        self.pagination_frame.columnconfigure(1, minsize=100, weight=1)
        self.pagination_frame.columnconfigure(2, minsize=100, weight=1)
        self.pagination_frame.columnconfigure(3, minsize=100, weight=1)

        self.pagination_frame.rowconfigure(0, weight=1)

        self.backward.grid(column=1, row=0, sticky=tk.E, padx=(0, 15))
        self.forward.grid(column=2, row=0, sticky=tk.W, padx=(15, 0))
        self.page_label.grid(column=3, row=0, sticky=tk.E, padx=(0, 15))

    def display_key_binds(self):
        """
        Add key-binds to HelpWindow.

        Adds key-binds specified in key_bind_descriptions to the window.

        :return: None
        """
        for widget in self.keybind_frame.winfo_children():
            if isinstance(widget, Label):
                widget.destroy()

        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        visible_key_binds = self.key_binds_descriptions[start_idx:end_idx]

        for i, (keybind_text, description_text) in enumerate(visible_key_binds):
            keybind_label = Label(self.keybind_frame, text=keybind_text, font=self.font)
            description_label = Label(self.keybind_frame, text=description_text, wraplength=200, justify=tk.CENTER,
                                      font=self.font)

            keybind_label.grid(column=0, row=i)
            description_label.grid(column=1, row=i)
            self.keybind_frame.rowconfigure(i, minsize=80)
            self.keybind_frame.columnconfigure(0, minsize=100, weight=1)
            self.keybind_frame.columnconfigure(1, minsize=260, weight=1)

    def next_page(self):
        """
        Display next page information.

        Update information being displayed in the window to match with the next page.

        :return: None
        """
        if (self.current_page + 1) * self.items_per_page < len(self.key_binds_descriptions):
            self.current_page += 1
            self.display_key_binds()
            self.update_page_label()

    def previous_page(self):
        """
        Display previous page information.

        Update information being displayed in the window to match with the previous page.

        :return: None
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.display_key_binds()
            self.update_page_label()

    def update_page_label(self):
        """
        Update page number label.

        :return: None
        """
        total_pages = (len(self.key_binds_descriptions) - 1) // self.items_per_page + 1
        self.page_label.config(text=f"{self.current_page + 1}/{total_pages}")
