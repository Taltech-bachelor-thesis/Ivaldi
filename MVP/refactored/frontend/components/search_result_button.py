import tkinter as tk

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from constants import *


class SearchResultButton(tk.LabelFrame):
    """
    SearchResultButton class.

    SearchResultButton is a button that is shown after a search has been conducted on the CustomCanvas.
    The buttons purpose is to display information about the search and allow moving between results.
    It shows the number of results as well as the currently primarily highlighted parts index.
    It has 2 buttons that allow moving between results.
    It has a button to turn off search results. It will turn off search highlights and toggle off the button.

    """
    def __init__(self, master, main_diagram, **kwargs):
        """
        SearchResultButton constructor.

        :param master: Tk that SearchResultButton will be displayed on.
        :param main_diagram:  MainDiagram object.
        :param kwargs: Keyword arguments for LabelFrame.
        """
        super().__init__(master, **kwargs)
        self.main_diagram = main_diagram

        self.close_button_frame = tk.LabelFrame(self, height=30, width=25)
        self.close_button_frame.pack(side=tk.RIGHT)

        self.close_icon = Image.open(ASSETS_DIR + "/close-circle-outline.png")
        self.close_icon = self.close_icon.resize((20, 20))
        self.close_icon = ImageTk.PhotoImage(self.close_icon)

        close_button = tk.Label(self.close_button_frame, image=self.close_icon, height=30, width=25)
        close_button.bind("<Button-1>", lambda event: self.main_diagram.cancel_search_results())
        close_button.pack()

        up_down_frame = tk.LabelFrame(self, height=30)
        up_down_frame.pack(side=tk.RIGHT, padx=(0, 5))

        self.up_icon = Image.open(ASSETS_DIR + "/chevron-up-circle.png")
        self.up_icon = self.up_icon.resize((20, 20))
        self.up_icon = ImageTk.PhotoImage(self.up_icon)

        up_button = tk.Label(up_down_frame, text="", height=30, width=25, image=self.up_icon)
        up_button.bind("<Button-1>", lambda event: self.main_diagram.move_between_search_results(up=True))
        up_button.pack(side=tk.LEFT)

        ttk.Separator(up_down_frame, orient=tk.VERTICAL).pack(side=tk.LEFT)

        self.down_icon = Image.open(ASSETS_DIR + "chevron-down-circle.png")
        self.down_icon = self.down_icon.resize((20, 20))
        self.down_icon = ImageTk.PhotoImage(self.down_icon)

        down_button = tk.Label(up_down_frame, text="", height=30, width=25, image=self.down_icon)
        down_button.bind("<Button-1>", lambda event: self.main_diagram.move_between_search_results(up=False))
        down_button.pack(side=tk.LEFT)

        self.info_frame = tk.LabelFrame(self, height=30)
        self.info_frame.pack(side=tk.LEFT, padx=(0, 5))

        self.info_text = tk.StringVar()
        self.info_text.set(f"Search: {self.main_diagram.active_search_index + 1}/{len(self.main_diagram.search_results)}")

        self.info_label = tk.Label(self.info_frame,
                                   height=30,
                                   textvariable=self.info_text)
        self.info_label.pack()
