from __future__ import annotations

import json
from abc import ABC, abstractmethod
from tkinter import filedialog
from tkinter import messagebox
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.frontend.components.custom_canvas import CustomCanvas


class Exporter(ABC):

    def __init__(self, canvas: CustomCanvas):
        self.canvas = canvas

    @abstractmethod
    def create_file_content(self, filename: str) -> Any:
        pass

    @staticmethod
    def ask_filename_and_location() -> str:
        # Define the default file type and file extension
        filetypes = [('JSON files', '*.json')]

        # Show the save file dialog
        file_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=filetypes, title="Save JSON file")
        return file_path

    def export(self) -> str:
        filename = self.ask_filename_and_location()
        if filename:
            d = self.create_file_content(filename)
            with open(filename, "w") as outfile:
                json.dump(d, outfile, indent=4)
            messagebox.showinfo("Info", "Project saved successfully")

        return filename
