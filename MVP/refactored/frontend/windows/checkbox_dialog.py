import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class CheckboxDialog(simpledialog.Dialog):

    def __init__(self, parent, title=None, checkbox_text=""):
        self.checkbox_text = checkbox_text
        super().__init__(parent, title)

    def body(self, master):
        self.var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(master, text=self.checkbox_text, variable=self.var)
        self.checkbox.grid(row=0, column=0, padx=10, pady=10)
        return self.checkbox

    def apply(self):
        self.result = self.var.get()
