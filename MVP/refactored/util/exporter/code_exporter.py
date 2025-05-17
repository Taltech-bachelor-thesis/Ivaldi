import tkinter as tk
from tkinter import filedialog, messagebox


class CodeExporter:

    def __init__(self, code_editor, file_extension=".py"):
        self.code_editor = code_editor
        self.file_extension = file_extension
        if file_extension == ".py":
            self.filetype = [("Python files", "*.py")]
            self.title = "Python"

    def ask_filename_and_location(self) -> str:
        # Show the save file dialog
        file_path = filedialog.asksaveasfilename(defaultextension=self.file_extension, filetypes=self.filetype,
                                                 title=f"Save {self.title} file")
        return file_path

    def export(self) -> str:
        filename = self.ask_filename_and_location()
        if filename:
            content = self.code_editor.code_view.get("1.0", tk.END)
            with open(filename, "w") as outfile:
                outfile.write(content)
            messagebox.showinfo("Info", f"{self.title} file saved successfully")

        return filename
