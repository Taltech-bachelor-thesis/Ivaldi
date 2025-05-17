import tkinter as tk
import ttkbootstrap as ttk
import ctypes

from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.util.search_algorithm import SearchAlgorithm


class SearchWindow(tk.Toplevel):
    """
    `SearchWindow` is the window that holds settings and a canvas to conduct searches in the diagram.
    """
    def __init__(self, main_diagram):
        """
        SearchWindow constructor.

        :param main_diagram: MainDiagram object to use for functions and variables.
        """
        super().__init__()
        self.main_diagram = main_diagram

        try:
            mult = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        except Exception:
            mult = 1
        height = round(self.winfo_screenheight() * 0.55 * mult)
        width = round(self.winfo_screenwidth() * 0.2635 * mult)
        self.geometry(f'{width}x{height}')

        self.resizable(False, False)
        self.title("Search in Project")

        self.options_frame = tk.Frame(self)
        self.options_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.options_frame.rowconfigure(0, weight=1)
        self.options_frame.rowconfigure(1, weight=1)
        self.options_frame.columnconfigure(0, weight=1)
        self.options_frame.columnconfigure(1, weight=1)

        self.settings_label = tk.Label(self.options_frame, text="Settings", font=("Arial", 14, "bold"))
        self.settings_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=(30, 0), pady=10)

        self.search_all_canvases = tk.IntVar()
        self.search_all_canvases.set(1)
        self.search_all_option_button = ttk.Checkbutton(self.options_frame, text="Search all canvases",
                                                        variable=self.search_all_canvases)
        self.search_all_option_button.grid(row=1, column=0, sticky=tk.NSEW, padx=(50, 0))

        self.match_labels = tk.IntVar()
        self.match_labels.set(0)
        self.match_labels_button = ttk.Checkbutton(self.options_frame, text="Match labels",
                                                   variable=self.match_labels)
        self.match_labels_button.grid(row=1, column=1, sticky=tk.NSEW, padx=(0, 0))

        self.canvas_label_frame = tk.Frame(self)
        self.canvas_label_frame.rowconfigure(0, weight=1)
        self.canvas_label_frame.columnconfigure(0, weight=1)
        self.canvas_label_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=(20, 0))

        self.canvas_label = tk.Label(self.canvas_label_frame, text="Canvas", font=("Arial", 14, "bold"))
        self.canvas_label.grid(row=1, column=0, sticky=tk.W, padx=(30, 0))
        self.canvas_frame = ttk.Frame(self, bootstyle=ttk.PRIMARY)
        self.canvas_frame.pack(padx=2, pady=9, fill=tk.BOTH, expand=True)

        self.search_canvas = CustomCanvas(self.canvas_frame, self.main_diagram, is_search=True)
        self.search_canvas.set_name("")
        self.search_canvas.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        self.result_frame = tk.Frame(self)
        self.result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        self.search_button = ttk.Button(self.result_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.RIGHT)

    def search(self):
        """
        Activate the search.

        Activates search and turns on SearchResultButton.

        :return: None
        """
        if self.main_diagram.is_search_active:
            self.main_diagram.cancel_search_results()
        algorithm = SearchAlgorithm(self.search_canvas, self.main_diagram.custom_canvas, self)
        found = algorithm.contains_searchable()
        self.main_diagram.search_results = algorithm.results
        self.main_diagram.search_objects = algorithm.result_objects
        self.main_diagram.wire_objects = algorithm.wire_objects
        self.main_diagram.update_search_result_button_texts()
        self.main_diagram.is_search_active = found
        if found:
            self.main_diagram.highlight_search_result_by_index(0)
            for canvas in self.main_diagram.canvasses.values():
                canvas.toggle_search_results_button()

