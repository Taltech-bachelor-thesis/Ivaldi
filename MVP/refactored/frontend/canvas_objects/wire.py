import tkinter as tk
from tkinter import simpledialog

from MVP.refactored.backend.id_generator import IdGenerator
from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
from MVP.refactored.frontend.canvas_objects.types.wire_types import WireType
import constants as const
from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.connection_info import ConnectionInfo
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.spider import Spider


def curved_line(start, end, det=15):
    """
    Calculate the coordinates for a curved line.

    :param start: x, y coordinates where the line is starting from.
    :param end: x,y coordinates where the line ends.
    :param det: (Optional) parameter used for calculating wire curvature.
    :return: List of coordinates for a curved line from start to end.
    """
    sx = start[0]
    sy = start[1]
    dx = end[0] - sx
    dy = end[1] - sy

    coordinates = [0] * (det * 2 + 2)
    for i in range(det + 1):
        t = i / det
        coordinates[i * 2] = sx + dx * t
        coordinates[i * 2 + 1] = sy + dy * (3 * t ** 2 - 2 * t ** 3)
    return coordinates


class Wire:
    """
    Wire.

    A Wire is used to create a connection between 2 Connections. On the CustomCanvas it is represented as a line.

    Wire has multiple types. They are differentiated by dash style and color. The Wire type is defined by the
    Connections it is connected to.
    """

    defined_wires = {}

    def __init__(self, canvas, start_connection, end_connection, id_=None, is_temporary=False,
                 wire_type=WireType.GENERIC):
        """
        Wire constructor.

        :param canvas: CustomCanvas object that Wire will be created on.
        :param start_connection: Connection object that will mark the start of the Wire.
        :param end_connection: Connection object that will mark the end of the Wire.
        :param id_: (Optional) Integer ID of the Wire.
        :param is_temporary: (Optional) Boolean value that determines whether the Wire is temporary. Default is False.
        :param wire_type: (Optional) WireType object that will state the wire type and style.
            Default is WireType.GENERIC.
        """
        self.canvas = canvas
        self.context_menu = None
        self.start_connection = start_connection
        self.end_connection = end_connection
        self.line = None
        self.wire_width = 3
        if not id_:
            self.id = IdGenerator.id(self)
        else:
            self.id = id_
        self.receiver = canvas.main_diagram.receiver
        self.is_temporary = is_temporary
        if not is_temporary and not self.canvas.is_search:
            self.handle_wire_addition_callback()
        self.type = wire_type
        self.color = wire_type.value[0]
        self.dash_style = wire_type.value[1]
        self.end_label = None
        self.start_label = None
        self.update()

    def delete(self, action=None):
        """
        Delete the Wire.

        Will remove itself from its start and end Connections. Delete itself from the CustomCanvas. Will delete any
        labels attached to the Wire. Removes itself from Box wires if necessary.

        :param action: (Optional) String stating whether deletion is done with sub-diagram.
        :return: None
        """
        self.start_connection.remove_wire(self)
        self.end_connection.remove_wire(self)
        self.canvas.delete(self.line)
        self.delete_labels()
        if not self.is_temporary:
            if self.start_connection.box:
                self.start_connection.box.wires.remove(self)
            if self.end_connection.box:
                self.end_connection.box.wires.remove(self)
            if self in self.canvas.wires:
                self.canvas.wires.remove(self)
        if not self.is_temporary and not self.canvas.is_search:
            self.handle_wire_deletion_callback(action)

    def delete_from_canvas(self):
        if self.start_connection and self.start_connection.is_spider():
            self.start_connection.remove_wire(self)
        if self.end_connection and self.end_connection.is_spider():
            self.end_connection.remove_wire(self)

        self.canvas.delete(self.line)
        if self.receiver.listener:
            self.receiver.receiver_callback(ActionType.WIRE_DELETE, resource_id=self.id, canvas_id=self.canvas.id)

    def select(self):
        """
        Turn the Wire to the color chosen for selection.

        :return: None
        """
        self.canvas.itemconfig(self.line, fill=const.SELECT_COLOR)

    def search_highlight_secondary(self):
        """
        Apply the secondary highlight to the Wire.

        Turns the color of Wire to the secondary highlight color and adds the Wire to CustomCanvas search highlighted
        objects list.

        :return: None
        """
        self.canvas.itemconfig(self.line, fill=const.SECONDARY_SEARCH_COLOR)
        self.canvas.search_result_highlights.append(self)

    def search_highlight_primary(self):
        """
        Apply the primary highlight to the Wire.

        Turns the color of Wire to the primary highlight color and adds the Wire to CustomCanvas search highlighted
        objects list.

        :return: None
        """
        self.canvas.itemconfig(self.line, fill=const.PRIMARY_SEARCH_COLOR)
        self.canvas.search_result_highlights.append(self)

    def deselect(self):
        """
        Deselect Wire.

        Adds the Wire to its end and start Connections. Turns color back to original color.

        :return: None
        """
        # make sure connections have wires attached after select and deselect as copying between canvasses can remove
        self.start_connection.add_wire(self)
        self.end_connection.add_wire(self)
        self.canvas.itemconfig(self.line, fill=self.type.value[0])

    def update(self):
        """
        Update Wire.

        If no line exists then a line will be created on the CustomCanvas along with labels if needed. If a line already
        exists then its location and labels are updated. Wire lines are moved to the lowest layer of CustomCanvas.

        :return: None
        """
        if self.end_connection:
            if self.line:
                self.canvas.coords(self.line,
                                   *curved_line(self.start_connection.location, self.end_connection.location))
            else:
                self.line = self.canvas.create_line(
                    *curved_line(self.start_connection.location, self.end_connection.location),
                    fill=self.color, width=self.wire_width, dash=self.dash_style)
                self.canvas.tag_bind(self.line, '<ButtonPress-3>', self.show_context_menu)
            self.update_wire_label()
            self.canvas.tag_lower(self.line)

    def update_wire_label(self):
        """
        Update Wire labels.

        Creates and moves labels at wire ends.

        :return: None
        """
        if self.type.name in Wire.defined_wires and not self.is_temporary:
            size = len(Wire.defined_wires[self.type.name]) * 5
            if self.start_label or self.end_label:
                if self.start_label:
                    self.canvas.coords(self.start_label,
                                       self.start_connection.location[0] + self.start_connection.r + size,
                                       self.start_connection.location[1] - 10)
                    self.canvas.itemconfig(self.start_label, text=Wire.defined_wires[self.type.name])
                if self.end_label:
                    self.canvas.coords(self.end_label,
                                       self.end_connection.location[0] - self.end_connection.r - size,
                                       self.end_connection.location[1] - 10)
                    self.canvas.itemconfig(self.end_label, text=Wire.defined_wires[self.type.name])
            else:
                if not self.start_connection.is_spider():
                    self.start_label = self.canvas.create_text(self.start_connection.location[0] + size,
                                                               self.start_connection.location[1] - 10,
                                                               text=Wire.defined_wires[self.type.name],
                                                               font="Courier 10")
                    self.canvas.wire_label_tags.append(self.start_label)
                if not self.end_connection.is_spider():
                    self.end_label = self.canvas.create_text(self.end_connection.location[0] - size,
                                                             self.end_connection.location[1] - 10,
                                                             text=Wire.defined_wires[self.type.name],
                                                             font="Courier 10")
                    self.canvas.wire_label_tags.append(self.end_label)

    def show_context_menu(self, event):
        """
        Create context menu for Wire.

        :param event: tkinter.Event object that holds location for context menu.
        :return: None
        """
        if not self.is_temporary:
            self.close_menu()
            self.context_menu = tk.Menu(self.canvas, tearoff=0)
            self.context_menu.add_command(label="Create Spider",
                                          command=lambda bound_arg=event: self.create_spider(event))
            self.context_menu.add_command(label="Define wire type", command=self.define_type)
            self.context_menu.add_command(label="Delete wire", command=self.delete)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Cancel")
            self.context_menu.post(event.x_root, event.y_root)

    def define_type(self):
        """
        Define Wire type.

        Will ask user for string input for Wire name. If entered labels will be created for all Wires of this type
        and displayed at the ends of wires.

        :return: None
        """
        name = simpledialog.askstring("Wire type", "Enter a name for this type of wire:")
        if name and name.strip():  # When name is inputted
            name = name.strip()
            Wire.defined_wires[self.type.name] = name
            ConnectionType.LABEL_NAMES.value[ConnectionType[self.type.name].value] = name
            for canvas in self.canvas.main_diagram.canvasses.values():
                for wire in canvas.wires:
                    wire.update_wire_label()
        elif name is None:  # When askstring is cancelled
            return
        elif not name and not name.strip():  # When input is empty or only contains whitespace
            del Wire.defined_wires[self.type.name]
            for wire in self.canvas.wires:
                if wire.type == self.type:
                    wire.delete_labels()

    def delete_labels(self):
        """
        Delete Wire labels.

        Removes labels from CustomCanvas.

        :return: None
        """
        if self.start_label:
            self.canvas.delete(self.start_label)
            self.start_label = None
        if self.end_label:
            self.canvas.delete(self.end_label)
            self.end_label = None

    def create_spider(self, event):
        """
        Create Spider in Wire.

        Will take the current Wire and cut it into two, connecting the new Wires with a Spider.

        :param event: tkinter.Event object where the Spider will be created.
        :return: None
        """
        x, y = event.x, event.y
        self.delete()
        self.canvas.add_spider_with_wires(self.start_connection, self.end_connection, x, y)

    def close_menu(self):
        """
        Closes Wire context menu.

        :return: None
        """
        if self.context_menu:
            self.context_menu.destroy()

    # BE callback methods
    def connection_data_optimizer(self) -> tuple[ConnectionInfo, ConnectionInfo]:
        """
        Return 2 lists containing information about the Connections the Wire is attached to.

        :return: List of information about Wire start and end Connections.
        """
        start_conn_data: ConnectionInfo = ConnectionInfo(self.start_connection.index, self.start_connection.side,
                                                         self.start_connection.id)
        end_conn_data: ConnectionInfo = ConnectionInfo(self.end_connection.index, self.end_connection.side,
                                                       self.end_connection.id)

        if self.start_connection.box:
            start_conn_data.box_id = self.start_connection.box.id
        elif isinstance(self.start_connection, Spider):
            start_conn_data.resource_id = self.start_connection.id
        if self.end_connection.box:
            end_conn_data.box_id = self.end_connection.box.id
        elif isinstance(self.end_connection, Spider):
            end_conn_data.resource_id = self.end_connection.id
        return start_conn_data, end_conn_data

    # BE callback methods
    def handle_wire_addition_callback(self):
        """
        Send Wire creation information to the backend.

        :return: None
        """
        if not self.receiver.listener or self.canvas.is_search:
            return

        start_conn_data, end_conn_data = self.connection_data_optimizer()

        if self.start_connection.side == const.SPIDER:
            self.receiver.receiver_callback(ActionType.WIRE_CREATE, resource_id=self.id,
                                            start_connection=start_conn_data,
                                            end_connection=end_conn_data,
                                            canvas_id=self.canvas.id)
        elif self.end_connection.side == const.SPIDER:
            self.receiver.receiver_callback(ActionType.WIRE_CREATE, resource_id=self.id,
                                            start_connection=start_conn_data,
                                            end_connection=end_conn_data,
                                            canvas_id=self.canvas.id)
        else:
            self.receiver.receiver_callback(ActionType.WIRE_CREATE, resource_id=self.id,
                                            start_connection=start_conn_data,
                                            end_connection=end_conn_data,
                                            canvas_id=self.canvas.id)

    # BE callback methods
    def handle_wire_deletion_callback(self, action):
        """
        Send Wire deletion information to the backend.

        :param action: string detailing whether action is done for a sub-diagram or not.
        :return: None
        """
        if not self.receiver.listener:
            return
        if self.start_connection.side == const.SPIDER:
            if self.end_connection.box is None:
                self.receiver.receiver_callback(ActionType.WIRE_DELETE, resource_id=self.id, canvas_id=self.canvas.id)
            else:
                self.receiver.receiver_callback(ActionType.WIRE_DELETE, resource_id=self.id, canvas_id=self.canvas.id)
        elif self.end_connection.side == const.SPIDER:
            if self.start_connection.box is None:
                self.receiver.receiver_callback(ActionType.WIRE_DELETE, resource_id=self.id, canvas_id=self.canvas.id)
            else:
                self.receiver.receiver_callback(ActionType.WIRE_DELETE, resource_id=self.id, canvas_id=self.canvas.id)
        else:
            self.receiver.receiver_callback(ActionType.WIRE_DELETE, resource_id=self.id, canvas_id=self.canvas.id)

    # BE callback methods
    def add_end_connection(self, connection):
        """
        Send end Connection information to the backend.

        :param connection: Connection object that is the end connection of the Wire
        :return: None
        """
        self.end_connection = connection
        if connection.box and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.WIRE_CREATE, resource_id=self.id,
                                            start_connection=ConnectionInfo(connection.index, connection.side,
                                                                            connection.id, connection.box.id),
                                            connection_id=connection.id, canvas_id=self.canvas.id)
        elif connection.box is None and self.receiver.listener and self.start_connection.box is not None:
            self.receiver.receiver_callback(ActionType.WIRE_CREATE, resource_id=self.id,
                                            start_connection=ConnectionInfo(connection.index,
                                                                            connection.side,
                                                                            connection.id,
                                                                            related_resource_id=connection.id if isinstance(
                                                                                connection, Spider) else None),
                                            connection_id=connection.id, canvas_id=self.canvas.id)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
