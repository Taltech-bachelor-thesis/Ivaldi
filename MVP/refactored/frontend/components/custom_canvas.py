import tkinter as tk
from threading import Timer
from tkinter import filedialog

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *

import constants as const
from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.id_generator import IdGenerator
from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.connection_side import ConnectionSide
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.corner import Corner
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
from MVP.refactored.frontend.canvas_objects.types.wire_types import WireType
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.components.search_result_button import SearchResultButton
from MVP.refactored.frontend.util.selector import Selector
from MVP.refactored.frontend.windows.tikz_window import TikzWindow
from MVP.refactored.util.copier import Copier
from MVP.refactored.util.exporter.hypergraph_exporter import HypergraphExporter


class CustomCanvas(tk.Canvas):
    """
    `CustomCanvas` is a wrapper for `tkinter.Canvas` that all `canvas_objects` are drawn on.
    """
    def __init__(self, master, main_diagram, id_=None, is_search=False, diagram_source_box=None, **kwargs):
        """
        CustomCanvas constructor.

        :param master: Tk object that CustomCanvas will be displayed in.
        :param main_diagram: MainDiagram object.
        :param id_: (Optional) Unique ID for CustomCanvas.
        :param is_search: (Optional) Boolean for stating if CustomCanvas is used for searching.
        :param diagram_source_box: (Optional) Box object that CustomCanvas belongs to. Existing if CustomCanvas is a
        sub-diagram.
        :param parent_diagram: (Optional) Parent diagram. CustomCanvas object.
        :param kwargs: Other keyword arguments that are used for tkinter.Canvas.
        """
        super().__init__(master, **kwargs)

        screen_width_min = round(main_diagram.winfo_screenwidth() / 1.5)
        screen_height_min = round(main_diagram.winfo_screenheight() / 1.5)
        if not is_search:
            self.configure(bg=const.WHITE, width=screen_width_min, height=screen_height_min)
            self.selector = main_diagram.selector
        else:
            self.selector = Selector(main_diagram, canvas=self)
        self.update()

        self.parent_diagram = diagram_source_box.canvas if diagram_source_box else None
        self.main_diagram = main_diagram
        self.master = master
        self.is_search = is_search
        self.boxes: list[Box] = []
        self.outputs: list[Connection] = []
        self.inputs: list[Connection] = []
        self.spiders: list[Spider] = []
        self.wires: list[Wire] = []
        self.corners: list[Corner] = []
        self.temp_wire = None
        self.temp_end_connection = None
        self.pulling_wire = False
        self.quick_pull = False
        self.receiver = main_diagram.receiver
        self.current_wire_start = None
        self.draw_wire_mode = False
        self.bind('<Button-1>', self.on_canvas_click)
        self.bind("<Configure>", self.on_canvas_resize)
        self.diagram_source_box = diagram_source_box  # Only here if canvas is sub-diagram

        if not id_:
            self.id = IdGenerator.id(self)
        else:
            self.id = id_

        self.receiver.add_new_canvas(self.id)

        self.name_text = str(self.id)[-6:]
        self.select_box = None
        self.bind("<ButtonPress-1>", self.__select_start__)
        self.bind('<Motion>', self.start_pulling_wire)
        self.bind('<Double-Button-1>', self.pull_wire)
        self.bind("<B1-Motion>", self.__select_motion__)
        self.bind("<ButtonRelease-1>", lambda event: self.__select_release__())
        self.bind("<Button-3>", self.handle_right_click)
        self.bind("<Delete>", lambda event: self.selector.delete_selected_items())
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Right>", self.pan_horizontal)
        self.bind("<Left>", self.pan_horizontal)
        self.bind("<Down>", self.pan_vertical)
        self.bind("<Up>", self.pan_vertical)
        self.bind("<Control-MouseWheel>", self.scale_item)
        self.bind("<Control-a>", lambda _: self.select_all())
        self.bind("<Control-c>", lambda event: self.selector.copy_selected_items())
        self.bind("<Control-v>", self.paste_copied_items)
        self.bind("<Control-x>", lambda event: self.cut_selected_items())
        self.bind("<Control-n>", lambda event: self.create_sub_diagram())
        self.selecting = False
        self.copier = Copier()
        self.hypergraph_exporter = HypergraphExporter(self)

        self.context_menu = None

        if not is_search:
            self.tree_logo = Image.open(const.ASSETS_DIR + "/file-tree-outline.png")
            self.tree_logo = self.tree_logo.resize((20, 15))
            self.tree_logo = ImageTk.PhotoImage(self.tree_logo)

            tree_button = ttk.Button(self, image=self.tree_logo,
                                     command=lambda: self.main_diagram.toggle_treeview(), bootstyle=(PRIMARY, OUTLINE))
            tree_button.place(x=28, y=20, anchor=tk.CENTER)

        self.search_result_button = SearchResultButton(self, self.main_diagram)

        self.box_shape = const.RECTANGLE

        self.total_scale = 1.0
        self.delta = 0.75

        self.prev_width_max = self.canvasx(self.winfo_width())
        self.prev_height_max = self.canvasy(self.winfo_height())
        self.prev_width_min = self.canvasx(0)
        self.prev_height_min = self.canvasy(0)

        c1 = Corner([0, 0], self, 0)
        c2 = Corner([0, self.winfo_height()], self, 0)
        c3 = Corner([self.winfo_width(), 0], self, 0)
        c4 = Corner([self.winfo_width(), self.winfo_height()], self, 0)
        self.corners.append(c1)
        self.corners.append(c2)
        self.corners.append(c3)
        self.corners.append(c4)
        self.init_corners()

        self.prev_scale = 1.0
        self.pan_speed = 20

        self.hover_item = None
        self.search_result_highlights = []

        self.wire_label_tags = []

    def on_hover(self, item):
        """
        Updates hover_item variable.

        :param item: canvas_object item that hover_item will be changed to.
        :return: None
        """
        self.hover_item = item

    def on_leave_hover(self):
        """
        Reset hover_item variable.

        :return: None
        """
        self.hover_item = None

    def scale_item(self, event):
        """
        Activates `.on_resize_scroll(event)` on the item that is being hovered over.

        :param event: tkinter.Event
        :return: None
        """
        if self.hover_item:
            self.hover_item.on_resize_scroll(event)

    def toggle_search_results_button(self):
        """
        Toggle visibility of search result button based on active search status.

        Search result button is the button used for moving between search results and cancelling search results.

        :return: None
        """
        if self.main_diagram.is_search_active:
            self.search_result_button.place(x=self.winfo_width() - 90, y=20, anchor=tk.CENTER, width=175, height=30)
        else:
            self.search_result_button.place_forget()

    def update_search_results_button(self):
        """
        Update the search result button location.

        :return: None
        """
        if self.main_diagram.is_search_active:
            self.search_result_button.place_forget()
            self.search_result_button.place(x=self.winfo_width() - 90, y=20, anchor=tk.CENTER, width=175, height=30)

    def remove_search_highlights(self):
        """
        Remove search highlights from CustomCanvas.

        Removes highlights from highlighted search objects and toggles search results button.

        :return: None
        """
        for item in self.search_result_highlights:
            item.deselect()
        self.search_result_highlights = []
        self.toggle_search_results_button()

    def select_all(self):
        """
        Selects all objects in the CustomCanvas.

        :return: None
        """
        if self.main_diagram.custom_canvas == self:
            event = tk.Event()
            event.x, event.y = -100, -100
            self.__select_start__(event)

            event.x, event.y = self.corners[3].location[0] + 100, self.corners[3].location[1] + 100
            self.__select_motion__(event)

            self.__select_release__()
        else:
            self.selector.selected_items = self.boxes + self.spiders + self.wires
            self.selector.selected_boxes = self.boxes
            self.selector.selected_wires = self.wires
            self.selector.selected_spiders = self.spiders

    def update_prev_winfo_size(self):
        """
        Update previous height/width variables with current CustomCanvas size.

        :return: None
        """
        self.prev_width_max = self.canvasx(self.winfo_width())
        self.prev_height_max = self.canvasy(self.winfo_height())
        self.prev_width_min = self.canvasx(0)
        self.prev_height_min = self.canvasy(0)

    def pan_horizontal(self, event):
        """
        Move objects on the CustomCanvas horizontally.

        Based on Event object will move objects horizontally left or right.

        :param event: tkinter.Event
        :return: None
        """
        if event.keysym == "Right":
            multiplier = -1
        else:
            multiplier = 1

        for corner in self.corners:
            next_location = [
                corner.location[0] + multiplier * self.pan_speed,
                corner.location[1]
            ]
            if 0 < round(next_location[0]) < self.winfo_width() or 0 < round(next_location[1]) < self.winfo_height():
                self.pan_speed = min(abs(1 - corner.location[0]), abs(self.winfo_width() - corner.location[0] - 1))
                return

        for connection in self.corners + self.inputs + self.outputs:
            connection.location[0] = connection.location[0] + multiplier * self.pan_speed
            self.coords(connection.circle,
                        connection.location[0] - connection.r, connection.location[1] - connection.r,
                        connection.location[0] + connection.r, connection.location[1] + connection.r)
        self.move_boxes_spiders('x', multiplier)
        self.pan_speed = 20

    def pan_vertical(self, event):
        """
        Move objects on the CustomCanvas vertically.

        Based on Event object will move objects vertically up or down.

        :param event: tkinter.Event
        :return: None
        """
        if event.keysym == "Down":
            multiplier = -1
        else:
            multiplier = 1

        for corner in self.corners:
            next_location = [
                corner.location[0], corner.location[1] + multiplier * self.pan_speed
            ]
            if 0 < round(next_location[0]) < self.winfo_width() or 0 < round(next_location[1]) < self.winfo_height():
                self.pan_speed = min(abs(1 - corner.location[1]), abs(self.winfo_height() - corner.location[1] - 1))
                return

        for connection in self.corners + self.inputs + self.outputs:
            connection.location[1] = connection.location[1] + multiplier * self.pan_speed
            self.coords(connection.circle,
                        connection.location[0] - connection.r, connection.location[1] - connection.r,
                        connection.location[0] + connection.r, connection.location[1] + connection.r)
        self.move_boxes_spiders('y', multiplier)
        self.pan_speed = 20

    def move_boxes_spiders(self, attr, multiplier):
        """
        Move boxes and spiders on the CustomCanvas along the x or y-axis.

        :param attr: attribute to move items on.
        :param multiplier: move towards positive or negative coordinates.
        :return: None
        """
        for spider in self.spiders:
            setattr(spider, attr, getattr(spider, attr) + multiplier * self.pan_speed)
            spider.move_to((spider.x, spider.y))
        for box in self.boxes:
            setattr(box, attr, getattr(box, attr) + multiplier * self.pan_speed)
            box.update_size(box.size[0], box.size[1])
            box.move_label()
        for wire in self.wires:
            wire.update()
        if self.pulling_wire:
            self.temp_wire.update()

    def delete(self, *args):
        """
        Delete items identified by all tag or ids contained in ARGS.

        :return: None
        """
        super().delete(*args)

    def handle_right_click(self, event):
        """
        Handle right click event on CustomCanvas.

        Possible actions are finishing selection, cancelling wire pulling and showing context menu.

        :param event: tkinter.Event
        :return: None
        """
        if self.selector.selecting:
            self.selector.finish_selection()
        if self.draw_wire_mode:
            self.cancel_wire_pulling(event)
        else:
            self.show_context_menu(event)

    def set_name(self, name):
        """
        Set name of CustomCanvas.

        Will change the label and name of the CustomCanvas.

        :param name: new name
        :return: None
        """
        self.name_text = name
        self.main_diagram.toolbar.update_canvas_label()

    def reset_zoom(self):
        """
        Reset the scale of the CustomCanvas.

        :return: None
        """
        while self.total_scale - 1 > 0.01:
            event = tk.Event()
            event.x, event.y = self.winfo_width() / 2, self.winfo_height() / 2
            event.num = 5
            event.delta = -120
            event.state = False
            self.zoom(event)

    def zoom(self, event):
        """
        Zooming main function.

        Activated on scrolling on CustomCanvas. Cannot zoom out from starting point.

        :param event: tkinter.Event
        :return: None
        """
        if event.state & 0x4:
            return
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        scale = 1

        self.prev_scale = self.total_scale
        self.scan_dragto(0, 0, gain=1)
        if event.num == 5 or event.delta == -120:
            scale *= self.delta
            self.total_scale *= self.delta
        if event.num == 4 or event.delta == 120:
            if self.total_scale > 10000:
                return
            scale /= self.delta
            self.total_scale /= self.delta

        if self.prev_scale < self.total_scale:
            denominator = self.delta
        else:
            denominator = 1 / self.delta
            is_allowed, x_offset, y_offset, end = self.check_max_zoom(event.x, event.y, denominator)
            if end:
                self.total_scale = self.prev_scale
                return
            if not is_allowed:
                event.x += x_offset
                event.y += y_offset

        self.update_coordinates(denominator, event, scale)
        self.update_inputs_outputs()
        if self.total_scale - 1 < 0.1:
            self.init_corners()
        self.configure(scrollregion=self.bbox('all'))

    def update_coordinates(self, denominator, event, scale):
        """
        Update/move all objects to new location after zooming.

        :param denominator: Denominator used for calculating object movement.
        :param event: tkinter.Event
        :param scale: stating how much was scaled.
        :return: None
        """
        for corner in self.corners:
            next_location = [
                self.calculate_zoom_dif(event.x, corner.location[0], denominator),
                self.calculate_zoom_dif(event.y, corner.location[1], denominator)
            ]
            corner.location = next_location
            self.coords(corner.circle, next_location[0] - corner.r, corner.location[1] - corner.r,
                        corner.location[0] + corner.r, corner.location[1] + corner.r)

        for i_o in self.inputs + self.outputs:
            i_o_location = [
                self.calculate_zoom_dif(event.x, i_o.location[0], denominator),
                self.calculate_zoom_dif(event.y, i_o.location[1], denominator)
            ]
            i_o.r *= scale
            i_o.location = i_o_location
            self.coords(i_o.circle, i_o.location[0] - i_o.r, i_o.location[1] - i_o.r,
                        i_o.location[0] + i_o.r, i_o.location[1] + i_o.r)
            self.itemconfig(i_o.circle, width=i_o.r * 2 / 10)

        for box in self.boxes:
            box.x = self.calculate_zoom_dif(event.x, box.x, denominator)
            box.y = self.calculate_zoom_dif(event.y, box.y, denominator)
            box.update_size(box.size[0] * scale, box.size[1] * scale)
            box.move_label()

        for spider in self.spiders:
            spider.x = self.calculate_zoom_dif(event.x, spider.x, denominator)
            spider.y = self.calculate_zoom_dif(event.y, spider.y, denominator)
            spider.location = spider.x, spider.y
            spider.r *= scale
            self.coords(spider.circle, spider.x - spider.r, spider.y - spider.r, spider.x + spider.r,
                        spider.y + spider.r)
            self.itemconfig(spider.circle, width=round(min(spider.r / 5, 5)))

        for wire in self.wires:
            wire.wire_width *= scale
            wire.update()
        if self.temp_wire:
            self.temp_wire.update()

    def check_max_zoom(self, x, y, denominator):
        """
        Check whether zooming is allowed.

        :param x: x coordinate of where zooming out is done.
        :param y: y coordinate of where zooming in is done.
        :param denominator: denominator used for calculating object movement.
        :return: Tuple of 4 variables. If movement is allowed, needed x and y offset, and if corners are in visual
        corners.
        """
        x_offset = 0
        y_offset = 0
        for corner in self.corners:
            next_location = [
                self.calculate_zoom_dif(x, corner.location[0], denominator),
                self.calculate_zoom_dif(y, corner.location[1], denominator)
            ]
            multiplier = 1 / (1 - self.delta)
            if self.canvasx(0) < round(next_location[0]) < self.canvasx(self.winfo_width()):
                x_offset = -next_location[0] * multiplier
                if round(next_location[0]) > self.canvasx(self.winfo_width()) / 2:
                    x_offset = (self.canvasx(self.winfo_width()) - next_location[0]) * multiplier
            if self.canvasy(0) < round(next_location[1]) < self.canvasy(self.winfo_height()):
                y_offset = -next_location[1] * multiplier
                if round(next_location[1]) > self.canvasy(self.winfo_height()) / 2:
                    y_offset = (self.canvasy(self.winfo_height()) - next_location[1]) * multiplier

        is_allowed = x_offset == 0 == y_offset
        return is_allowed, x_offset, y_offset, self.check_corner_start_locations()

    def check_corner_start_locations(self):
        """
        Checks if all Corner objects are at the visual corners of the CustomCanvas.

        :return: boolean
        """
        min_x = self.canvasx(0)
        min_y = self.canvasy(0)
        max_x = self.canvasx(self.winfo_width())
        max_y = self.canvasy(self.winfo_height())
        count = 0
        locations = [
            [min_x, min_y],
            [min_x, max_y],
            [max_x, min_y],
            [max_x, max_y]
        ]
        for corner in self.corners:
            for location in locations:
                if ((abs(round(self.canvasx(corner.location[0])) - location[0]) < 2
                     and abs(round(self.canvasy(corner.location[1])) - location[1]) < 2)
                        or
                        (abs(round(corner.location[0]) - location[0]) < 2
                         and abs(round(corner.location[1]) - location[1]) < 2)):
                    count += 1
        return count >= 4

    def close_menu(self):
        """
        Close context menu of CustomCanvas.

        :return: None
        """
        if self.context_menu:
            self.context_menu.destroy()

    def show_context_menu(self, event):
        """
        Create and display CustomCanvas context menu.

        Menu will be created at event location.

        :param event: tkinter.Event
        :return: None
        """
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        if not self.is_mouse_on_object(event):
            self.close_menu()
            self.context_menu = tk.Menu(self, tearoff=0)

            self.context_menu.add_command(label="Add undefined box",
                                          command=lambda loc=(event.x, event.y): self.add_box(loc))

            if len(self.main_diagram.quick_create_boxes) > 0:
                sub_menu = tk.Menu(self.context_menu, tearoff=0)
                self.context_menu.add_cascade(menu=sub_menu, label="Add custom box")
                for box in self.main_diagram.quick_create_boxes:
                    sub_menu.add_command(label=box,
                                         command=lambda loc=(event.x, event.y), name=box:
                                         self.main_diagram.importer.add_box_from_menu(self, name, loc))

            self.context_menu.add_command(label="Add spider",
                                          command=lambda loc=(event.x, event.y): self.add_spider(loc))

            self.context_menu.add_command(label="Cancel")
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def is_mouse_on_object(self, event):
        """
        Return boolean of if event location is overlapping with a canvas object.

        :param event: tkinter.Event
        :return: Boolean
        """
        return bool(self.find_overlapping(event.x, event.y - 1, event.x, event.y + 1))

    # binding for drag select
    def __select_start__(self, event):
        """
        Start a selection box from event location.

        :param event: tkinter.Event.
        :return: None
        """
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        [box.close_menu() for box in self.boxes]
        [wire.close_menu() for wire in self.wires]
        [(spider.close_menu(), self.tag_raise(spider.circle)) for spider in self.spiders]

        [i.close_menu() for i in self.inputs]
        [o.close_menu() for o in self.outputs]
        [[c.close_menu() for c in box.connections] for box in self.boxes]

        if self.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1):
            self.on_canvas_click(event)
            return
        self.selector.finish_selection()
        self.selector.start_selection(event)

    def __select_motion__(self, event):
        """
        Update selection area.

        :param event: tkinter.Event
        :return: None
        """
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        self.selector.update_selection(event)

    def __select_release__(self):
        """
        End the active selection.

        :return:
        """
        self.selector.finalize_selection(self.boxes, self.spiders, self.wires)
        self.selector.select_action()

    def pull_wire(self, event):
        """
        Start quick pulling wire from event, if event is overlapping with a Connection.

        :param event: tkinter.Event
        :return: None
        """
        if not self.quick_pull and not self.draw_wire_mode:
            self.quick_pull = True
            connection = self.get_connection_from_location(event)
            if connection is not None and (not connection.has_wire or connection.is_spider()):
                self.toggle_draw_wire_mode()
                self.on_canvas_click(event, connection)
            else:
                self.quick_pull = False

    def get_connection_from_location(self, event):
        """
        Return Connection or None that is at event location.

        :param event: tkinter.Event
        :return: Connection or None
        """
        if self.draw_wire_mode or self.quick_pull:
            x, y = event.x, event.y
            for circle in [c for box in self.boxes for c in
                           box.connections] + self.outputs + self.inputs + self.spiders:

                conn_x, conn_y, conn_x2, conn_y2 = self.coords(circle.circle)
                if conn_x <= x <= conn_x2 and conn_y <= y <= conn_y2:
                    return circle
        return None

    def _fix_new_sub_diagram_box_wires(self, sub_diagram_box: Box) -> None:
        """
        This is workaround to fix the wires that are not connected to the sub-diagram box
        """
        if not sub_diagram_box:
            return

        for connection in sub_diagram_box.connections:
            correct_wire = connection.wire
            correct_wire.end_connection.wire = correct_wire

    # HANDLE CLICK ON CANVAS
    def on_canvas_click(self, event, connection=None):
        """
        Handle click on canvas.

        :param event: tkinter.Event
        :param connection: (Optional) Connection that is clicked on.
        :return: None
        """
        if self.selector.selecting:
            self.selector.finish_selection()
        if connection is None:
            connection = self.get_connection_from_location(event)
        if connection is not None:
            self.handle_connection_click(connection, event)

    def start_pulling_wire(self, event):
        """
        Start creating a temporary Wire to the mouse location from a chosen start Connection, during draw wire mode.

        :param event: tkinter.Event
        :return: None
        """
        if self.draw_wire_mode and self.pulling_wire:
            if self.temp_wire is not None:
                self.temp_wire.delete()
            if self.temp_end_connection.location != (self.canvasx(event.x), self.canvasy(event.y)):
                self.temp_end_connection.delete()
                self.temp_end_connection = Connection(None, 0, None,
                                                      (self.canvasx(event.x), self.canvasy(event.y)),
                                                      self, connection_type=self.current_wire_start.type)
            self.temp_wire = Wire(self, self.current_wire_start, self.temp_end_connection, None, True,
                                  wire_type=WireType[self.current_wire_start.type.name])
            self.temp_end_connection.wire = self.temp_wire

    def handle_connection_click(self, c, event):
        """
        Handle click on Connection object.

        Redirects to other functions based on application state.

        :param c: Connection that was clicked on.
        :param event: tkinter.Event
        :return: None
        """
        if c.has_wire and not c.is_spider() or not self.draw_wire_mode:
            return
        if not self.current_wire_start:
            self.start_wire_from_connection(c, event)
            self.start_pulling_wire(event)
        else:
            self.end_wire_to_connection(c)

    def start_wire_from_connection(self, connection, event=None):
        """
        Start creating a wire from given Connection.

        Sets current_wire_Start variable to given Connection object. If event is given, draws a temporary Connection on
        event location.

        :param connection: Connection object that wire is started from.
        :param event: (Optional) tkinter.Event
        :return: None
        """
        if connection.side == const.SPIDER or not connection.has_wire:
            self.current_wire_start = connection

            connection.select()

            if event is not None:
                x, y = self.canvasx(event.x), self.canvasy(event.y)
                self.pulling_wire = True
                self.temp_end_connection = Connection(None, None, None, (x, y), self)

    def end_wire_to_connection(self, connection, bypass_legality_check=False):
        """
        End Wire creation to given Connection.

        Deletes temporary Wire and Connection to create a non-temporary Wire from current_wire_start to given connection
        in params. If given connection is same as current_wire_start then wire pulling is cancelled and no Wire is
        created.
        Before creating a non-temporary Wire legality checking is done, if this does not pass a Wire is not created.

        :param connection: Connection that is the End of a new Wire.
        :param bypass_legality_check: boolean stating if legality of Wire creation should be checked.
        :return: None
        """
        if connection == self.current_wire_start:
            self.nullify_wire_start()
            self.cancel_wire_pulling()

        if (self.current_wire_start
                and self.is_wire_between_connections_legal(self.current_wire_start, connection)
                or bypass_legality_check):
            start_end: list[Connection] = sorted([self.current_wire_start, connection], key=lambda x: x.location[0])

            if start_end[0].type == ConnectionType.GENERIC:
                start_end[0].change_type(start_end[1].type.value)
            if start_end[1].type == ConnectionType.GENERIC:
                start_end[1].change_type(start_end[0].type.value)

            if start_end[0].type != start_end[1].type:
                return

            self.cancel_wire_pulling()

            current_wire = Wire(self, start_end[0], start_end[1],
                                wire_type=WireType[start_end[0].type.name])
            self.wires.append(current_wire)

            if self.current_wire_start.box is not None:
                self.current_wire_start.box.add_wire(current_wire)
            if connection.box is not None:
                connection.box.add_wire(current_wire)

            self.current_wire_start.add_wire(current_wire)
            connection.add_wire(current_wire)

            current_wire.update()
            self.nullify_wire_start()

    def cancel_wire_pulling(self, event=None):
        """
        Cancel Wire pulling.

        Resets all variables related to wire pulling.

        :param event: tkinter.Event
        :return: None
        """
        if event:
            self.nullify_wire_start()
        if self.temp_wire is not None:
            self.temp_end_connection.delete()
            self.temp_wire.delete()
            self.temp_wire = None
            self.temp_end_connection = None
            self.pulling_wire = False
            if self.quick_pull:
                self.quick_pull = False
                self.draw_wire_mode = False
                self.main_diagram.draw_wire_button.config(bootstyle=(PRIMARY, OUTLINE))

    def nullify_wire_start(self):
        """
        Nullify wire start.

        Changes current_wire_start color to black and resets it to None.

        :return: None
        """
        if self.current_wire_start:
            self.current_wire_start.deselect()
        self.current_wire_start = None

    def add_box(self, loc=(100, 100), size=(60, 60), id_=None, style=None):
        """
        Add a box to the CustomCanvas.

        Creates a Box on the CustomCanvas, the location, size, id and shape can be specified with additional parameters.

        :param loc: tuple of location that box will be created at.
        :param size: tuple of box size.
        :param id_: custom ID for the Box that's created.
        :param style: Define the style of the Box.
        :return: Box tag.
        """
        if style is None:
            style = self.box_shape
        box = Box(self, *loc, size=size, id_=id_, style=style)
        self.boxes.append(box)
        return box

    def get_box_by_id(self, box_id: int) -> Box | None:
        """
        Get Box object by ID.

        :param box_id: id of the box.
        :return: Box or None
        """
        for box in self.boxes:
            if box.id == box_id:
                return box
        return None

    def get_box_function(self, box_id) -> BoxFunction | None:
        """
        Get BoxFunction object based on specified Box code.

        :param box_id: ID of the Box that BoxFunction is created for.
        :return: BoxFunction or None
        """
        box = self.get_box_by_id(box_id)
        if box:
            return box.get_box_function()
        return None

    def add_spider(self, loc=(100, 100), id_=None, connection_type=ConnectionType.GENERIC):
        """
        Add a spider to the CustomCanvas.

        Creates a Spider on the CustomCanvas. Location, ID, and connection type can be specified with additional
        parameters.

        :param loc: (Optional) location of the spider.
        :param id_: (Optional) id of the spider.
        :param connection_type: (Optional) Type of Connection.
        :return: Spider tag
        """
        spider = Spider(loc, self, id_=id_, connection_type=connection_type)
        self.spiders.append(spider)
        return spider

    def add_spider_with_wires(self, start, end, x, y):
        """
        Add a Spider with wires attached.

        Creates a Spider at (x, y) location and connects the newly created Spider to start and end Connections given
        in params.

        :param start: Connection that created Spider will have a Wire connected to.
        :param end: Connection that the created Spider will have a Wire connected to.
        :param x:  X coordinate that Spider is created on.
        :param y: Y coordinate that Spider is created on.
        :return: None
        """
        spider = self.add_spider((x, y))
        self.start_wire_from_connection(start)
        self.end_wire_to_connection(spider)

        self.start_wire_from_connection(end)
        self.end_wire_to_connection(spider)

    # OTHER BUTTON FUNCTIONALITY
    def save_as_png(self):
        """
        Save current CustomCanvas as PNG file.

        Resets the zoom of the CustomCanvas and asks the user where they would like to save the png file.
        Then MainDiagram is asked for a png file.

        :return: None
        """
        self.reset_zoom()
        filetypes = [('png files', '*.png')]
        file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=filetypes,
                                                 title="Save png file")
        if file_path:
            self.main_diagram.generate_png(self, file_path)

    def open_tikz_generator(self):
        """
        Create TikZ window.

        Resets the zoom of the CustomCanvas and opens a small window that will have the generated TikZ code.

        :return: None
        """
        self.reset_zoom()
        TikzWindow(self.main_diagram)

    def toggle_draw_wire_mode(self):
        """
        Toggle draw wire mode.

        :return: None
        """
        self.draw_wire_mode = not self.draw_wire_mode
        if self.draw_wire_mode:
            for item in self.selector.selected_items:
                item.deselect()
            self.selector.selected_items.clear()
            self.main_diagram.draw_wire_button.config(bootstyle=SUCCESS)
        else:
            self.nullify_wire_start()
            self.cancel_wire_pulling()
            self.main_diagram.draw_wire_button.config(bootstyle=(PRIMARY, OUTLINE))

    # RESIZE/UPDATE
    def on_canvas_resize(self, _):
        """
        Handle canvas resizing.

        Updates the locations on Corner objects and diagram inputs and outputs along with previous winfo sizes and canvas
        label location. This is activated when the application is configured.

        :param _: tkinter.Event
        :return: None
        """
        if self.total_scale - 1 > 0.1:
            self.update_corners()
        else:
            self.init_corners()

        self.update_inputs_outputs()
        self.update_prev_winfo_size()

        self.main_diagram.toolbar.update_canvas_label()

        self.__on_configure_move__()

    def __on_configure_move__(self):
        """
        Move items to their relative location.

        Activated upon canvas configuration, it will move all spiders and boxes
        to their relative location.

        :return: None
        """
        for item in self.spiders + self.boxes:
            event = tk.Event()
            event.state = False
            event.x = self.winfo_width() * item.rel_x
            event.y = self.winfo_height() * item.rel_y
            if isinstance(item, Box):
                item.x_dif = 0
                item.y_dif = 0
            item.on_drag(event, from_configuration=True)

    @staticmethod
    def debounce(wait_time):
        """
        Decorator that will debounce a function so that it is called after wait_time seconds
        If it is called multiple times, will wait for the last call to be debounced and run only this one.
        """

        def decorator(function):
            def debounced(*args, **kwargs):
                def call_function():
                    debounced._timer = None
                    return function(*args, **kwargs)

                # if we already have a call to the function currently waiting to be executed, reset the timer
                if debounced._timer is not None:
                    debounced._timer.cancel()

                # after wait_time, call the function provided to the decorator with its arguments
                debounced._timer = Timer(wait_time, call_function)
                debounced._timer.start()

            debounced._timer = None
            return debounced

        return decorator

    def init_corners(self):
        """
        Set all Corner objects to CustomCanvas visual corners.

        :return: None
        """
        min_x = self.canvasx(0)
        min_y = self.canvasy(0)
        max_x = self.canvasx(self.winfo_width())
        max_y = self.canvasy(self.winfo_height())
        self.corners[0].move_to([min_x, min_y])
        self.corners[1].move_to([min_x, max_y])
        self.corners[2].move_to([max_x, min_y])
        self.corners[3].move_to([max_x, max_y])
        self.update_inputs_outputs()

    @debounce(1)
    def update_corners(self):
        """
        Update Corner object locations during active zooming.

        :return: None
        """
        min_x = self.canvasx(0)
        min_y = self.canvasy(0)
        max_x = self.canvasx(self.winfo_width())
        max_y = self.canvasy(self.winfo_height())
        self.corners[0].move_to([(self.corners[0].location[0] + (min_x - self.prev_width_min) / self.delta),
                                 (self.corners[0].location[1] + (min_y - self.prev_height_min) / self.delta)])

        self.corners[1].move_to([(self.corners[1].location[0] + (min_x - self.prev_width_min) / self.delta),
                                 (self.corners[1].location[1] + (max_y - self.prev_height_max) / self.delta)])

        self.corners[2].move_to([(self.corners[2].location[0] + (max_x - self.prev_width_max) / self.delta),
                                 (self.corners[2].location[1] + (min_y - self.prev_height_min) / self.delta)])

        self.corners[3].move_to([(self.corners[3].location[0] + (max_x - self.prev_width_max) / self.delta),
                                 (self.corners[3].location[1] + (max_y - self.prev_height_max) / self.delta)])

    def update_inputs_outputs(self):
        """
        Update input and output locations of diagram.

        :return: None
        """
        x = self.corners[3].location[0]
        y = self.corners[3].location[1]
        min_y = self.corners[0].location[1]
        output_index = max([o.index for o in self.outputs] + [0])
        for o in self.outputs:
            i = o.index
            step = (y - min_y) / (output_index + 2)
            o.move_to([x - 7, min_y + step * (i + 1)])

        input_index = max([o.index for o in self.inputs] + [0])
        for o in self.inputs:
            i = o.index
            step = (y - min_y) / (input_index + 2)
            o.move_to([6 + self.corners[0].location[0], min_y + step * (i + 1)])
        [w.update() for w in self.wires]

    def delete_everything(self):
        """
        Delete all canvas_objects on CustomCanvas.

        :return: None
        """
        while len(self.wires) > 0:
            self.wires[0].delete()
        while len(self.boxes) > 0:
            if self.boxes[0].sub_diagram:
                sub_diagram = 'sub_diagram'
            else:
                sub_diagram = None
            self.boxes[0].delete_box(action=sub_diagram)
        while len(self.spiders) > 0:
            self.spiders[0].delete()
        while len(self.outputs) > 0:
            self.remove_diagram_output()
        while len(self.inputs) > 0:
            self.remove_diagram_input()

        Connection.active_types = 1
        Wire.defined_wires.clear()

    # STATIC HELPERS
    @staticmethod
    def is_wire_between_connections_legal(start, end):
        """
        Check if a Wire between two Connections is legal.

        :param start: Connection.
        :param end: Connection.
        :return: Boolean.
        """
        if start.type != end.type:
            if ConnectionType.GENERIC not in (start.type, end.type):
                return False
            else:
                if start.type == ConnectionType.GENERIC and start.has_wire:
                    return False
                if end.type == ConnectionType.GENERIC and end.has_wire:
                    return False

        if start.is_spider() and end.is_spider():

            if abs(start.location[0] - end.location[0]) < 2 * start.r:
                return False

            for w in start.wires:
                if w.start_connection == end or w.end_connection == end:
                    return False

        if start == end:
            return False
        if (start.is_spider() and (
                end.side == const.RIGHT and end.location[0] > start.location[0] or
                end.side == const.LEFT and end.location[0] < start.location[0]) or
                end.is_spider() and (
                        start.side == const.RIGHT and start.location[0] > end.location[0]
                        or start.side == const.LEFT and start.location[0] < end.location[0])):
            return False

        if start.side == end.side == const.SPIDER:
            return True

        return not (start.side == end.side or start.side == const.LEFT and start.location[0] - start.width_between_boxes <=
                    end.location[0] or start.side == const.RIGHT and start.location[0] + start.width_between_boxes >=
                    end.location[0])

    def random(self):
        """
        Create Wires between Connections at random.

        :return: None
        """
        if not self.draw_wire_mode:
            self.toggle_draw_wire_mode()

        for circle in [c for box in self.boxes for c in
                       box.connections] + self.outputs + self.inputs + self.spiders:
            if circle.has_wire:
                continue
            self.start_wire_from_connection(circle)

            for circle2 in [c for box in self.boxes for c in
                            box.connections] + self.outputs + self.inputs + self.spiders:

                if circle2.has_wire:
                    continue
                self.end_wire_to_connection(circle2)
                if not self.current_wire_start:
                    break
            self.nullify_wire_start()
        self.toggle_draw_wire_mode()

    def add_diagram_output(self, id_=None, connection_type=ConnectionType.GENERIC):
        """
        Add an output to the diagram.

        ID and type of Connection can be specified with additional parameters.
        Returns created Connection tag.

        :param id_: (Optional) ID for output that will be created.
        :param connection_type: (Optional) ConnectionType.
        :return: Created Connection tag
        """
        output_index = max([o.index for o in self.outputs] + [0])
        if len(self.outputs) != 0:
            output_index += 1
        connection_output_new = Connection(self.diagram_source_box, output_index,
                                           ConnectionSide.LEFT, [0, 0], self,
                                           r=5 * self.total_scale, id_=id_, connection_type=connection_type)

        if self.receiver.listener:
            self.receiver.receiver_callback(ActionType.DIAGRAM_ADD_OUTPUT, connection_nr=connection_output_new.index,
                                            connection_id=connection_output_new.id,
                                            connection_side=connection_output_new.side, canvas_id=self.id)

        self.outputs.append(connection_output_new)
        self.update_inputs_outputs()

        return connection_output_new

    def add_diagram_input_for_sub_d_wire(self, id_=None):
        """
        Add input if CustomCanvas is sub-diagram.

        If the CustomCanvas is a sub-diagram then this will add a left Connection to the source box of the diagram as
        well as to the diagram itself. Returns a tuple of source box Connection tag and diagram Connection tag.

        :param id_: (Optional) ID that will be give to the input created on the diagram.
        :return: Tuple of box connection tag and canvas input tag
        """
        box_c = self.diagram_source_box.add_left_connection()
        canvas_i = self.add_diagram_input(id_=id_)
        return box_c, canvas_i

    def add_diagram_output_for_sub_d_wire(self, id_=None):
        """
        Add output if CustomCanvas is sub-diagram.

        If the CustomCanvas is a sub-diagram then this will add a right Connection to the source box of the diagram as
        well as to the diagram itself. Returns a tuple of source box Connection tag and diagram Connection tag.

        :param id_: (Optional) ID that will be give to the output created on the diagram.
        :return: Tuple of box connection tag and canvas input tag
        """
        box_c = self.diagram_source_box.add_right_connection()
        canvas_o = self.add_diagram_output(id_=id_)
        return box_c, canvas_o

    def remove_diagram_output(self):
        """
        Remove output from diagram.

        :return: None
        """
        if not self.outputs:
            return
        to_be_removed = self.outputs.pop()
        to_be_removed.delete()
        self.update_inputs_outputs()
        if self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.DIAGRAM_REMOVE_OUTPUT, canvas_id=self.id,
                                            connection_id=to_be_removed.id)

    def add_diagram_input(self, id_=None, connection_type=ConnectionType.GENERIC):
        """
        Add an input to the diagram.

        ID and type of Connection can be specified with additional parameters.
        Returns created Connection tag.

        :param id_: (Optional) ID for input that will be created.
        :param connection_type: (Optional) ConnectionType.
        :return: Created Connection tag.
        """
        input_index = max([o.index for o in self.inputs] + [0])
        if len(self.inputs) != 0:
            input_index += 1
        new_input = Connection(self.diagram_source_box, input_index, ConnectionSide.RIGHT, [0, 0], self,
                               r=5 * self.total_scale, id_=id_, connection_type=connection_type)
        if self.receiver.listener:
            self.receiver.receiver_callback(ActionType.DIAGRAM_ADD_INPUT,
                                            connection_id=new_input.id, connection_nr=new_input.index,
                                            connection_side=new_input.side, canvas_id=self.id)

        self.inputs.append(new_input)
        self.update_inputs_outputs()

        return new_input

    def remove_diagram_input(self):
        """
        Remove input from diagram.

        :return: None
        """
        if not self.inputs:
            return
        to_be_removed = self.inputs.pop()
        to_be_removed.delete()
        self.update_inputs_outputs()
        if self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.DIAGRAM_REMOVE_INPUT, canvas_id=self.id,
                                            connection_id=to_be_removed.id)

    def remove_specific_diagram_input(self, con):
        """
        Remove a specified Connection from diagram inputs.

        :param con: Connection that will be removed.
        :return: None
        """
        if not self.inputs:
            return
        if self.diagram_source_box:
            index_ = con.index
            for c in self.diagram_source_box.connections:
                if c.side == const.LEFT and index_ == c.index:
                    self.diagram_source_box.remove_connection(c)

        for c in self.inputs:
            if c.index > con.index and con.side == c.side:
                c.lessen_index_by_one()

        self.inputs.remove(con)
        con.delete()
        self.update_inputs_outputs()

    def remove_specific_diagram_output(self, con):
        """
        Remove a specified Connection from diagram outputs.

        :param con: Connection that will be removed.
        :return: None
        """
        if not self.outputs:
            return
        if self.diagram_source_box:
            index_ = con.index
            for c in self.diagram_source_box.connections:
                if c.side == const.RIGHT and index_ == c.index:
                    self.diagram_source_box.remove_connection(c)

        for c in self.outputs:
            if c.index > con.index and con.side == c.side:
                c.lessen_index_by_one()

        self.outputs.remove(con)

        con.delete()
        self.update_inputs_outputs()

    def find_connection_to_remove(self, side):
        c_max = 0
        c = None
        for connection in self.diagram_source_box.connections:
            if connection.side == side and connection.index >= c_max:
                c_max = connection.index
                c = connection
        return c

    def export_hypergraph(self):
        """
        Export hypergraph.

        Resets zoom and exports hypergraph.

        :return: None
        """
        self.reset_zoom()
        self.hypergraph_exporter.export()

    @staticmethod
    def calculate_zoom_dif(zoom_coord, object_coord, denominator):
        """
        Calculate zoom location difference.

        Calculates how much an object will be moved when zooming.

        :param zoom_coord: coordinate of where zooming is done from.
        :param object_coord: coordinate of where object is.
        :param denominator: denominator used to calculate zoom movement distance.
        :return: float of distance needed to move.
        """
        return round(zoom_coord - (zoom_coord - object_coord) / denominator, 4)

    def set_box_shape(self, shape):
        """
        Set box_shape variable.

        :param shape: Shape that default Box creation will be set to
        :return: None
        """
        self.box_shape = shape

    def paste_copied_items(self, event):
        """
        Paste copied items.

        Pastes copied items. If other items are selected at the moment of pasting then they will be replaced.

        :param event: tkinter.Event
        :return: None
        """
        if len(self.selector.selected_items) > 0:
            copied_x1, copied_x2, copied_y1, copied_y2 = self.selector.find_corners_copied_items()
            selected_x1, selected_y1, selected_x2, selected_y2 = self.selector.find_corners_selected_items()
            selected_middle_x = (selected_x1 + selected_x2) / 2
            selected_middle_y = (selected_y1 + selected_y2) / 2
            copied_x_length = copied_x2 - copied_x1
            copied_y_length = copied_y2 - copied_y1
            multi, x, y = self.find_paste_multipliers(selected_middle_x, selected_middle_y, copied_x_length,
                                                      copied_y_length)

            self.selector.paste_copied_items(x, y, True, multi)
        else:
            self.selector.paste_copied_items(event.x, event.y)

    def cut_selected_items(self):
        """
        Cut selection.

        Copies and deletes selected items.

        :return: None
        """
        self.selector.copy_selected_items()
        self.selector.delete_selected_items()

    def create_sub_diagram(self):
        """
        Create sub-diagram with selected items.

        :return: None
        """
        if len(list(filter(lambda x: isinstance(x, Spider) or isinstance(x, Box), self.selector.selected_items))) > 1:
            self.selector.create_sub_diagram()
            self.selector.selected_items = []

    def find_paste_multipliers(self, x, y, x_length, y_length):
        """
        Find paste multipliers.

        Finds multipliers that would change the size of the pasted items to match the location they're being replaced
        in.

        :param x: x coordinate of the middle of the replacing area.
        :param y: y coordinate of the middle of the replacing area.
        :param x_length: width of the copied area.
        :param y_length: height of the copied area.
        :return: Tuple that contains the smaller multiplier of the X and Y scaling factors
         and the center coordinates of the area
        """
        area_x1 = x - x_length / 2
        area_x2 = x + x_length / 2
        area_y1 = y - y_length / 2
        area_y2 = y + y_length / 2
        left, right = self.selector.find_side_connections()
        if len(left) != 0 or len(right) != 0:
            for connection in left:
                if connection.side == const.SPIDER:
                    if x > connection.location[0] + connection.r > area_x1:
                        area_x1 = connection.location[0] + connection.r
                else:
                    if connection.location[0] > area_x1:
                        area_x1 = connection.location[0]
            for connection in right:
                if connection.side == const.SPIDER:
                    if x < connection.location[0] - connection.r < area_x2:
                        area_x2 = connection.location[0] - connection.r
                else:
                    if connection.location[0] < area_x2:
                        area_x2 = connection.location[0]
        for item in self.boxes + self.spiders:
            if item not in self.selector.selected_items:
                if isinstance(item, Box):
                    if not (item.y + item.size[1] < area_y1 or item.y > area_y2):
                        if x > item.x + item.size[0] > area_x1:
                            area_x1 = item.x + item.size[0]
                        if x < item.x < area_x2:
                            area_x2 = item.x
                    if not (item.x > area_x2 or item.x + item.size[0] < area_x1):
                        if y > item.y + item.size[1] > area_y1:
                            area_y1 = item.y + item.size[1]
                        if y < item.y < area_y2:
                            area_y2 = item.y
                if isinstance(item, Spider):
                    if not (item.y + item.r < area_y1 or item.y - item.r > area_y2):
                        if x > item.x + item.r > area_x1:
                            area_x1 = item.x + item.r
                        if x < item.x - item.r < area_x2:
                            area_x2 = item.x - item.r
                    if not (item.x - item.r > area_x2 or item.x + item.r < area_x1):
                        if y > item.y + item.r > area_y1:
                            area_y1 = item.y + item.r
                        if y < item.y - item.r < area_y2:
                            area_y2 = item.y - item.r
        if area_x1 != x - x_length / 2:
            area_x1 = area_x1 + 10
        if area_x2 != x + x_length / 2:
            area_x2 = area_x2 - 10
        x_multiplier = round((area_x2 - area_x1) / x_length, 3)
        y_multiplier = round((area_y2 - area_y1) / y_length, 3)
        return min(x_multiplier, y_multiplier), (area_x1 + area_x2) / 2, (area_y1 + area_y2) / 2
