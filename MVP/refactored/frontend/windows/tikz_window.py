import tkinter as tk

from PIL import Image, ImageTk

import constants as const


class TikzWindow(tk.Toplevel):
    """
    `TikzWindow` is
    """
    def __init__(self, main_diagram):
        super().__init__(None)

        self.main_diagram = main_diagram

        self.copy_logo = Image.open(const.ASSETS_DIR + "/content-copy.png")
        self.copy_logo = self.copy_logo.resize((20, 20))
        self.copy_logo = ImageTk.PhotoImage(self.copy_logo)

        self.title("TikZ Generator")
        self.resizable(False, True)
        self.minsize(0, 500)

        tk.Label(self,
                 text="PGF/TikZ plots can be used with the following packages.\n"
                      "Use pgfplotsset to change the size of plots.",
                 justify="left").pack()

        pgfplotsset_text = tk.Text(self, width=30, height=5)
        pgfplotsset_text.insert(tk.END,
                                "\\usepackage{tikz}\n\\usepackage{pgfplots}\n"
                                "\\pgfplotsset{\ncompat=newest, \nwidth=15cm, \nheight=10cm\n}")
        pgfplotsset_text.config(state=tk.DISABLED)
        pgfplotsset_text.pack()

        tikz_text = tk.Text(self)
        tikz_text.insert(tk.END, self.main_diagram.generate_tikz(self.main_diagram.custom_canvas))
        tikz_text.config(state="disabled")
        tikz_text.pack(pady=10, fill=tk.BOTH, expand=True)
        tikz_text.update()

        tikz_copy_button = tk.Label(tikz_text, image=self.copy_logo, relief="flat")
        tikz_copy_button.bind("<Button-1>", lambda event: self.main_diagram.copy_to_clipboard(tikz_text))

        tikz_copy_button.place(x=tikz_text.winfo_width() - 30, y=20, anchor=tk.CENTER)



