import tkinter as tk
from tkinter import font  # Import the font module
from tkinter import messagebox

import hupper

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class Launcher:
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("String Diagrams")
        self.root.resizable(False, False)
        self.receiver = Receiver()

        # Get the screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = round(screen_width / 5)
        window_height = round(screen_height / 5)

        # Calculate the center coordinates
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # Set the window size and position
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.do_i_exit)
        # Create buttons
        # Define a bold font
        bold_font = font.Font(weight="bold")
        btn_create = tk.Button(self.root, text="Create New Diagram", command=self.create_new_diagram, width=18,
                               font=bold_font)
        btn_import = tk.Button(self.root, text="Import from File", command=self.import_from_file, width=18,
                               font=bold_font)
        btn_exit = tk.Button(self.root, text="Exit", command=self.exit_program, width=18, font=bold_font)

        # Place buttons on the window
        btn_create.pack(padx=10, pady=15)
        btn_import.pack(padx=10, pady=15)
        btn_exit.pack(padx=10, pady=15)

        # Start the main loop
        self.root.mainloop()

    def do_i_exit(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.exit_program()

    def create_new_diagram(self):
        self.root.destroy()
        MainDiagram(self.receiver)

    def import_from_file(self):
        self.root.destroy()
        MainDiagram(self.receiver, True)

    def exit_program(self):
        self.root.destroy()


def start_program():
    Launcher()


if __name__ == '__main__':
    # hupper.start_reloader('launcher.start_program')
    start_program()
