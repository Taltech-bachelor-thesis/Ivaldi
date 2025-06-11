from __future__ import annotations
import tkinter as tk

from MVP.refactored.backend.id_generator import IdGenerator
from MVP.refactored.backend.types.connection_side import ConnectionSide

from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
import constants as const


class Connection:
    """
    Connection.

    A CustomCanvas widget that allows a Wire to be connected to it. This object is represented as a circle on
    CustomCanvas. It is used as diagram inputs and outputs, as well as Box inputs and outputs.
    """

    active_types = 1

    def __init__(self, box, index, side: ConnectionSide, location, canvas, r=5, id_=None, connection_type=ConnectionType.GENERIC):
        """
        Connection constructor.

        :param box: Box that the connection is attached to.
        :param index: Index of the Connection, shows index of Connection in the same place
        :param side: String that states what side the Connection is created on.
        :param location: Tuple of coordinates that the Connection will be created at.
        :param canvas: CustomCanvas that the Connection is created on.
        :param r: (Optional) Radius of the circle that represents the Connection.
        :param id_: (Optional) ID of Connection
        :param connection_type: (Optional) Type of Connection.
        """
        self.canvas = canvas
        self.box = box  # None if connection is diagram input/output/spider
        self.index = index
        self.side: ConnectionSide = side  # 'spider' if connection is a spider
        self.location = location
        self.type = connection_type
        self.wire = None
        self.has_wire = False
        self.r = r
        if not id_:
            self.id = IdGenerator.id(self)
        else:
            self.id = id_
            IdGenerator.use_id(self.id)

        self.context_menu = None
        self.circle = self.canvas.create_oval(location[0] - self.r, location[1] - self.r, location[0] + self.r,
                                              location[1] + self.r, fill=const.BLACK,
                                              outline=ConnectionType.COLORS.value[self.type.value],
                                              width=round(min(self.r / 5, 5)))
        self.width_between_boxes = 1  # px
        self.bind_events()

    def update(self):
        """
        Update the style of the Connection circle using its type.

        :return: None
        """
        self.canvas.itemconfig(self.circle, outline=ConnectionType.COLORS.value[self.type.value])
        self.canvas.itemconfig(self.circle, width=round(min(self.r / 5, 5)))
        self.canvas.update()

    def bind_events(self):
        """
        Bind events to circle created on CustomCanvas.

        :return: None
        """
        self.canvas.tag_bind(self.circle, '<ButtonPress-3>', self.show_context_menu)
        self.canvas.tag_bind(self.circle, '<Button-2>', lambda x: self.increment_type())

    def increment_type(self):
        """
        Change the Connection type to the next possible type.

        Will not change it if a Wire is connected to it.

        :return: None
        """
        if not self.has_wire:
            self.change_type(self.type.next().value)
            self.increment_active_types()
            self.update()

    def change_type(self, type_id):
        """
        Change type of the Connection to selected type and update style.

        :param type_id: Integer value of the ConnectionType to change to.
        :return: None
        """
        tied_con = self.get_tied_connection()
        if tied_con is None:
            return
        if tied_con and tied_con != self:
            tied_con.type = ConnectionType(type_id)
            tied_con.update()
        if not self.has_wire:
            self.type = ConnectionType(type_id)
            self.update()

    def get_tied_connection(self):
        """
        Return the Connection that is its sub-diagram or sub-diagram box counterpart.

        If a Connection is an input/output for a box that is a sub-diagram. Then this function will return the
        corresponding Connection inside the sub-diagram or on the sub-diagram box.

        :return: Connection
        """
        tied_con = self
        if self.box and self.box.sub_diagram:
            if self.box.sub_diagram == self.canvas:
                connections = self.box.connections
            else:
                connections = self.box.sub_diagram.outputs + self.box.sub_diagram.inputs

            matching_side = ""
            if self.side == const.RIGHT:
                matching_side = const.LEFT
            elif self.side == const.LEFT:
                matching_side = const.RIGHT
            for io in connections:
                if io.side == matching_side and io.index == self.index:
                    if io.has_wire:
                        tied_con = None
                    else:
                        tied_con = io
        return tied_con

    def show_context_menu(self, event):
        """
        Create and display a context menu for the selected Connection.

        :param event: Event sent from keybind. Location used for context menu to be created at.
        :return: None
        """
        if not self.wire or not self.wire.is_temporary:
            self.close_menu()
            if (self.box and not self.box.locked) or self.box is None:
                self.context_menu = tk.Menu(self.canvas, tearoff=0)

                self.add_type_choice()

                self.context_menu.add_command(label="Delete Connection", command=self.delete_from_parent)
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Cancel")

                self.context_menu.tk_popup(event.x_root, event.y_root)

    def add_type_choice(self):
        """
        Add a type choosing sub-menu into the context menu.

        This method will not add type picking if the Connection has a wire.

        :return: None
        """
        if not self.has_wire:
            sub_menu = tk.Menu(self.context_menu, tearoff=0)
            self.context_menu.add_cascade(menu=sub_menu, label="Connection type")
            sub_menu.add_command(label="Generic", command=lambda: self.change_type(0))

            for i in range(1, Connection.active_types):
                sub_menu.add_command(label=ConnectionType.LABEL_NAMES.value[i],
                                     command=lambda c_type=i: self.change_type(c_type))

            if Connection.active_types < len(ConnectionType.COLORS.value):
                sub_menu.add_separator()
                sub_menu.add_command(label="Add new type", command=lambda: self.add_active_type())

    def add_active_type(self):
        """
        Add a new active type for Connections.

        Increases the amount of ConnectionTypes available to be chosen in the context sub-menu.

        :return: None
        """
        self.change_type(Connection.active_types)
        self.increment_active_types()

    def increment_active_types(self):
        """
        Increments active_types variable.

        Will not increment if value would go above the amount of different types.

        :return: None
        """
        if Connection.active_types < len(ConnectionType.COLORS.value) and self.type.value >= Connection.active_types:
            Connection.active_types += 1

    def close_menu(self):
        """
        Close context menu if exists.

        :return: None
        """
        if self.context_menu:
            self.context_menu.destroy()

    def delete_from_parent(self):
        """
        Delete the selected Connection from their parent.

        This deletes the specific Connection from its diagram input or outputs, or it deletes it from the Box.
        :return: None
        """
        if self.box:
            if self.box.sub_diagram and self.side == const.LEFT:
                for i in self.box.sub_diagram.inputs:
                    if i.index == self.index:
                        self.box.sub_diagram.remove_specific_diagram_input(i)
                        return
            if self.box.sub_diagram and self.side == const.RIGHT:
                for i in self.box.sub_diagram.outputs:
                    if i.index == self.index:
                        self.box.sub_diagram.remove_specific_diagram_output(i)
                        return
            self.box.remove_connection(self)
            self.delete()
            return

        if self in self.canvas.inputs:
            self.canvas.remove_specific_diagram_input(self)
            return
        if self in self.canvas.outputs:
            self.canvas.remove_specific_diagram_output(self)
            return

    def change_color(self, color=const.BLACK):
        """
        Change the color of the connection.

        Without a parameter it will turn the Connection to black.
        The function allows usage of all Tkinter built in colors as well as hex code.
        It will change the 'fill' color of the item.

        :param color: string of color name.
        """
        self.canvas.itemconfig(self.circle, fill=color)

    def move_to(self, location):
        """
        Move the Connection to the given location.

        Takes a coordinate location and moves it to the given location on the canvas.

        :param location: tuple of coordinates. (x, y)
        :return: None
        """
        self.canvas.coords(self.circle, location[0] - self.r, location[1] - self.r, location[0] + self.r,
                           location[1] + self.r)
        self.location = location

    def lessen_index_by_one(self):
        """
        Lowers the index of Connection by one.

        :return: None
        """
        self.index -= 1

    def delete(self):
        """
        Delete Connection and Wires connected to it.

        Deletes and removes the Connection from the Canvas. It will also delete the Wire connected to it.

        :return: None
        """
        self.canvas.delete(self.circle)
        if self.has_wire:
            self.canvas.delete(self.wire)
            self.wire.delete()

            if self.box and self.wire in self.box.wires:
                self.box.wires.remove(self.wire)

            if self.wire in self.canvas.wires:
                self.canvas.wires.remove(self.wire)

    def add_wire(self, wire):
        """
        Add Wire to the Connection.

        A Wire will be attached to the Connection, accessible through the wire class variable.

        :param wire: Wire that will be added to the Connection.
        :return: None
        """
        if not self.has_wire and self.wire is None:
            self.wire = wire
            self.has_wire = True

    def is_spider(self):
        """
        Used to check if the Connection is a Spider Connection or a regular Connection.

        :return: boolean
        """
        return False

    def remove_wire(self, wire=None):
        """
        Remove attached wire from Connection.

        This function has an optional parameter to specify the wire to be removed, but this is used
        only in the Spider version of this function.

        :param wire: Optional parameter that specifies what wire will be removed from the Connection
        :return: None
        """
        if self.wire:
            self.wire = None
            self.has_wire = False

    def select(self):
        """
        Turns the Connection green.

        :return: None
        """
        self.change_color(color=const.SELECT_COLOR)

    def search_highlight_secondary(self):
        """
        Apply the secondary highlight to the Connection as a result of a search.

        This method will change the Connection to the secondary search highlight color. Additionally,
        it will the Connection to the search_result_highlights list in CustomCanvas.

        :return: None
        """
        self.change_color(color=const.SECONDARY_SEARCH_COLOR)
        self.canvas.search_result_highlights.append(self)

    def search_highlight_primary(self):
        """
        Apply the primary highlight to the Connection as a result of a search.

        This method will change the Connection to the primary search highlight color. Additionally,
        it will the Connection to the search_result_highlights list in CustomCanvas.

        :return: None
        """
        self.change_color(color=const.PRIMARY_SEARCH_COLOR)
        self.canvas.search_result_highlights.append(self)

    def deselect(self):
        """
        Turns the Connection color to black.

        This is used as turning back to the original color before item selection.

        :return: None
        """
        self.change_color(color=const.BLACK)

    def __eq__(self, __value):
        if isinstance(__value, Connection):
            return self.id == __value.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Connection(id={self.id}, box={self.box}, index={self.index}, side={self.side}, location={self.location})"
