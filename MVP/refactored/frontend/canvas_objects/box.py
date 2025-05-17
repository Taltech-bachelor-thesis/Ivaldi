import json
import re
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import simpledialog

import constants as const
from MVP.refactored.backend.box_functions.box_function import BoxFunction, predefined_functions
from MVP.refactored.backend.id_generator import IdGenerator
from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.connection_side import ConnectionSide
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.windows.code_editor import CodeEditor
from constants import *


class Box:
    """
    A box is a rectangle on the CustomCanvas. A box can have Connections on it's left and right side.

    Boxes represent a function, the function itself can be defined by the user.

    Boxes are also used to contain sub-diagrams. The sub-diagram is accessible from the treeview on canvases on the left side of the application.

    Boxes can contain code. The functions are findable in the "Manage methods" window. Applying code to boxes can be done
    by renaming them to match an existing function or by adding code to them yourself through the code editor.
    Code can only be added to a box with an existing label.

    The coordinates of a Box are the top left corner for it.
    """
    def __init__(self, canvas, x, y, size=(60, 60), id_=None, style=const.RECTANGLE):
        """
        Box constructor.

        :param canvas: CustomCanvas object that Box will be created on.
        :param x: X coordinate of the Box.
        :param y: Y coordinate of the Box.
        :param size: (Optional) Tuple with width and height of box.
        :param id_: (Optional) ID of the box.
        :param style: (Optional) Shape of the box.
        """
        self.style = style
        self.canvas = canvas
        x, y = self.canvas.canvasx(x), self.canvas.canvasy(y)
        self.x = x
        self.y = y
        self.rel_x = round(x / self.canvas.main_diagram.custom_canvas.winfo_width(), 4)
        self.rel_y = round(y / self.canvas.main_diagram.custom_canvas.winfo_height(), 4)
        self.start_x = x
        self.start_y = y
        self.size = size
        self.x_dif = 0
        self.y_dif = 0
        self.connections: list[Connection] = []
        self.left_connections = 0
        self.right_connections = 0
        self.label = None
        self.label_text = ""
        self.wires = []
        if not id_:
            self.id = IdGenerator.id(self)
        else:
            self.id = id_
        self.context_menu = None
        self.shape = self.create_shape()

        self.resize_handle = self.canvas.create_rectangle(self.x + self.size[0] - 10, self.y + self.size[1] - 10,
                                                          self.x + self.size[0], self.y + self.size[1],
                                                          outline=const.BLACK, fill=const.BLACK)
        self.locked = False
        self.bind_events()
        self.sub_diagram = None
        self.receiver = canvas.main_diagram.receiver
        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_CREATE, generator_id=self.id, canvas_id=self.canvas.id)
            if self.canvas.diagram_source_box:
                self.receiver.receiver_callback(ActionType.BOX_SUB_BOX, generator_id=self.id,
                                                connection_id=self.canvas.diagram_source_box.id,
                                                canvas_id=self.canvas.id)

        self.is_snapped = False

        self.collision_ids = [self.shape, self.resize_handle]
        self.box_function: BoxFunction = None

    def remove_wire(self, wire: Wire):
        self.wires.remove(wire)

    def set_id(self, id_):
        """
        Set Box ID.

        :param id_: New ID of the box.
        :return: None
        """
        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_SWAP_ID, generator_id=self.id, new_id=id_,
                                            canvas_id=self.canvas.id)
            if self.canvas.diagram_source_box:
                self.receiver.receiver_callback(ActionType.BOX_SUB_BOX, generator_id=self.id,
                                                connection_id=self.canvas.diagram_source_box.id,
                                                canvas_id=self.canvas.id)
        self.id = id_

    def bind_events(self):
        """
        Bind events to Box rectangle and resize handle.

        :return: None
        """
        self.canvas.tag_bind(self.shape, '<Control-ButtonPress-1>', lambda event: self.on_control_press())
        self.canvas.tag_bind(self.shape, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.shape, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.shape, '<ButtonPress-3>', self.show_context_menu)
        self.canvas.tag_bind(self.resize_handle, '<ButtonPress-1>', self.on_resize_press)
        self.canvas.tag_bind(self.resize_handle, '<B1-Motion>', self.on_resize_drag)
        self.canvas.tag_bind(self.resize_handle, '<Enter>', lambda _: self.canvas.on_hover(self))
        self.canvas.tag_bind(self.resize_handle, '<Leave>', lambda _: self.canvas.on_leave_hover())
        self.canvas.tag_bind(self.shape, '<Double-Button-1>', lambda _: self.handle_double_click())
        self.canvas.tag_bind(self.shape, '<Enter>', lambda _: self.canvas.on_hover(self))
        self.canvas.tag_bind(self.shape, '<Leave>', lambda _: self.canvas.on_leave_hover())

    def show_context_menu(self, event):
        """
        Create and display Box context menu.

        :param event: tkinter.Event object that holds location where menu is created.
        :return: None
        """
        self.close_menu()
        self.context_menu = tk.Menu(self.canvas, tearoff=0)

        if not self.sub_diagram:
            self.context_menu.add_command(label="Add code", command=self.open_editor)
            if not self.label_text.strip():
                self.context_menu.entryconfig("Add code", state="disabled", label="Label needed to add code")

        if not self.locked and not self.sub_diagram:
            self.context_menu.add_command(label="Add Left Connection", command=self.add_left_connection)
            self.context_menu.add_command(label="Add Right Connection", command=self.add_right_connection)

            for circle in self.connections:
                self.context_menu.add_command(label=f"Remove {circle.side} connection nr {circle.index}",
                                              command=lambda bound_arg=circle: self.remove_connection(bound_arg))

            sub_menu = tk.Menu(self.context_menu, tearoff=0)
            self.context_menu.add_cascade(menu=sub_menu, label="Shape")

            for shape in const.SHAPES:
                sub_menu.add_command(label=shape, command=lambda style=shape: self.change_shape(style))

        if self.locked:
            self.context_menu.add_command(label="Unlock Box", command=self.unlock_box)
        if not self.locked:
            self.context_menu.add_command(label="Edit label", command=self.edit_label)
            self.context_menu.add_command(label="Edit Sub-Diagram", command=self.edit_sub_diagram)
            self.context_menu.add_command(label="Unfold sub-diagram", command=self.unfold)
            self.context_menu.add_command(label="Lock Box", command=self.lock_box)
        self.context_menu.add_command(label="Save Box to Menu", command=self.save_box_to_menu)
        self.context_menu.add_command(label="Add function", command=lambda: self.add_function(event))
        if self.sub_diagram:
            self.context_menu.add_command(label="Delete Box", command=lambda: self.delete_box(action="sub_diagram"))
        else:
            self.context_menu.add_command(label="Delete Box", command=self.delete_box)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cancel")
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def unfold(self):
        """
        Unfold sub-diagram contained in Box.

        If a Box is a sub-diagram then this is used for bringing the sub-diagram to its parent canvas.

        :return: None
        """
        if not self.sub_diagram:
            return
        event = tk.Event()
        event.x = self.x + self.size[0] / 2
        event.y = self.y + self.size[1] / 2
        self.sub_diagram.select_all()
        self.canvas.selector.copy_selected_items(canvas=self.sub_diagram)
        self.on_press(event)
        self.canvas.paste_copied_items(event)

    def add_function(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        for name in predefined_functions:
            menu.add_command(label=name, command=lambda function=name: self.set_predefined_function(function))
        menu.add_command(label="Add custom function", command=self.show_add_custom_function_menu)
        menu.post(event.x_root, event.y_root)

    def show_add_custom_function_menu(self):
        file = filedialog.askopenfile(title="Send a python script, that contains function \"invoke\"",
                                      filetypes=(("Python script", "*.py"),))
        if file:
            box_function = BoxFunction(predefined_function_file_name=file.name, file_code=file.read())
            self.set_box_function(box_function)

    def set_predefined_function(self, name: str):
        box_function = BoxFunction(predefined_function_file_name=name, is_predefined_function=True)
        self.set_box_function(box_function)

    def set_box_function(self, box_function: BoxFunction):
        self.box_function = box_function
        self.receiver.receiver_callback(ActionType.BOX_SET_FUNCTION, generator_id=self.id, canvas_id=self.canvas.id,
                                        box_function=box_function)

    def get_box_function(self) -> BoxFunction:
        return self.box_function

    def count_inputs(self) -> int:
        count = 0
        for connection in self.connections:
            if connection.side == "left":
                count += 1
        return count

    def open_editor(self):
        """
        Open a CodeEditor for Box.

        :return: None
        """
        CodeEditor(self.canvas.main_diagram, box=self)

    def count_outputs(self) -> int:
        count = 0
        for connection in self.connections:
            if connection.side == "right":
                count += 1
        return count

    def get_inputs(self) -> list[int]:
        inputs = []
        for connection in self.connections:
            if connection.side == "left":
                inputs.append(connection.wire.id)
        return inputs

    def get_outputs(self) -> list[int]:
        outputs = []
        for connection in self.connections:
            if connection.side == "right":
                outputs.append(connection.wire.id)
        return outputs

    def save_box_to_menu(self):
        """
        Save Box to config file.

        Saves the Box and it's attributes to a config file, which allows the Box to be imported from menus.

        :return: None
        """
        if not self.label_text:
            self.edit_label()
        if not self.label_text:
            return
        self.canvas.main_diagram.save_box_to_diagram_menu(self)

    def handle_double_click(self):
        """
        Handle double click action on Box.

        Allows user to select input and output amounts unless the Box has a sub-diagram, in which case the user will
        be moved to the sub-diagram canvas.

        :return: None
        """
        if self.sub_diagram:
            self.canvas.main_diagram.switch_canvas(self.sub_diagram)
        else:
            self.set_inputs_outputs()

    def set_inputs_outputs(self):
        """
        Set input and output amounts for Box.

        Opens 2 dialogs requiring the user to input the wanted amounts of inputs and outputs.
        The entered amounts will be applied to the Box.

        :return: None
        """
        if self.locked or self.sub_diagram:
            return
        # ask for input amount
        inputs = simpledialog.askstring(title="Inputs (left connections)", prompt="Enter amount")
        if inputs and not inputs.isdigit():
            while True:
                inputs = simpledialog.askstring(title="Inputs (left connections)",
                                                prompt="Enter amount, must be integer!")
                if inputs:
                    if inputs.isdigit():
                        break
                else:
                    break

        # ask for output amount
        outputs = simpledialog.askstring(title="Outputs (right connections)", prompt="Enter amount")
        if outputs and not outputs.isdigit():
            while True:
                outputs = simpledialog.askstring(title="Outputs (right connections)",
                                                 prompt="Enter amount, must be integer!")
                if outputs:
                    if outputs.isdigit():
                        break
                else:
                    break
        # select connections to remove

        to_be_removed = []
        for c in self.connections:
            if c.side == const.RIGHT and outputs:
                to_be_removed.append(c)
            if c.side == const.LEFT and inputs:
                to_be_removed.append(c)

        # remove selected connectionsS
        for c in to_be_removed:
            c.delete()
            self.remove_connection(c)
            self.update_connections()
            self.update_wires()

        # add new connections
        if not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_REMOVE_ALL_CONNECTIONS, generator_id=self.id,
                                            canvas_id=self.canvas.id)
        if outputs:
            for _ in range(int(outputs)):
                self.add_right_connection()
        if inputs:
            for _ in range(int(inputs)):
                self.add_left_connection()

    def edit_sub_diagram(self, save_to_canvasses=True, switch=True):
        """
        Edit the Box sub-diagram.

        Will create a sub-diagram in the Box. If a sub-diagram already exists it will open it. Returns sub-diagram
        CustomCanvas object.

        :param save_to_canvasses: boolean to save canvas
        :param switch: boolean for switching canvas to sub-diagram after creation.
        :return: CustomCanvas sub-diagram
        """
        from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
        if not self.sub_diagram:
            self.sub_diagram = CustomCanvas(self.canvas.main_diagram, self.canvas.main_diagram,
                                            id_=self.id, highlightthickness=0,
                                            diagram_source_box=self)
            self.canvas.itemconfig(self.shape, fill="#dfecf2")
            if save_to_canvasses:
                name = self.label_text
                if not name:
                    name = str(self.sub_diagram.id)[-6:]
                    self.set_label(name)
                self.sub_diagram.set_name(name)
                self.canvas.main_diagram.add_canvas(self.sub_diagram)
                self.canvas.main_diagram.update_canvas_name(self.sub_diagram)
                if switch:
                    self.canvas.main_diagram.switch_canvas(self.sub_diagram)

        else:
            if switch:
                self.canvas.main_diagram.switch_canvas(self.sub_diagram)

        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_COMPOUND, generator_id=self.id, canvas_id=self.canvas.id,
                                            new_canvas_id=self.sub_diagram.id)
        return self.sub_diagram

    def close_menu(self):
        """
        Close the Box context menu.

        :return: None
        """
        if self.context_menu:
            self.context_menu.destroy()

    # MOVING, CLICKING ETC.
    def on_press(self, event):
        """
        Handle press action for Box.

        Sets variables to allow dragging of the Box. Clears previous selection and selects the Box.

        :param event: tkinter.Event object holding the location of the action.
        :return: None
        """
        event.x, event.y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        for item in self.canvas.selector.selected_items:
            item.deselect()
        self.canvas.selector.selected_boxes.clear()
        self.canvas.selector.selected_spiders.clear()
        self.canvas.selector.selected_wires.clear()
        self.canvas.selector.selected_items.clear()
        self.select()
        self.canvas.selector.selected_items.append(self)
        self.start_x = event.x
        self.start_y = event.y
        self.x_dif = event.x - self.x
        self.y_dif = event.y - self.y

    def on_control_press(self):
        """
        Handle control press action for Box.

        This method will select or unselect the Box depending on previous select state. It will not clear the previously
        selected items.

        :return: None
        """
        if self in self.canvas.selector.selected_items:
            self.canvas.selector.selected_items.remove(self)
            self.deselect()
        else:
            self.select()
            self.canvas.selector.selected_items.append(self)
        self.canvas.selector.select_wires_between_selected_items()

    def on_drag(self, event, from_configuration=False):
        """
        Handle dragging action for Box.

        :param event: tkinter.Event for dragging locations.
        :param from_configuration: (Optional) Boolean stating if the call to drag is coming due to canvas configuration.
        :return: None
        """
        if event.state & 0x4:
            return
        event.x, event.y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        self.start_x = event.x
        self.start_y = event.y

        go_to_x = event.x - self.x_dif
        go_to_y = event.y - self.y_dif

        # snapping into place
        found = False
        if not from_configuration:
            for box in self.canvas.boxes:
                if box == self:
                    continue

                if abs(box.x + box.size[0] / 2 - (go_to_x + self.size[0] / 2)) < box.size[0] / 2 + self.size[0] / 2:
                    go_to_x = box.x + box.size[0] / 2 - +self.size[0] / 2

                    found = True
            for spider in self.canvas.spiders:

                if abs(spider.location[0] - (go_to_x + self.size[0] / 2)) < self.size[0] / 2 + spider.r:
                    go_to_x = spider.x - +self.size[0] / 2

                    found = True

            if found:
                collision = self.find_collisions(go_to_x, go_to_y)

                if len(collision) != 0:
                    if self.is_snapped:
                        return

                    jump_size = 10
                    counter = 0
                    while collision:
                        if counter % 2 == 0:
                            go_to_y += counter * jump_size
                        else:
                            go_to_y -= counter * jump_size

                        collision = self.find_collisions(go_to_x, go_to_y)

                        counter += 1

        self.is_snapped = found

        self.move(go_to_x, go_to_y, bypass_legality=from_configuration)
        self.move_label()

    def update_self_collision_ids(self):
        """
        Update collision ids that are attached to the Box.

        Will update collision_ids with new label tag or Connections tags.

        :return: None
        """
        self.collision_ids = [self.shape, self.resize_handle]
        if self.label:
            self.collision_ids.append(self.label)
        for connection in self.connections:
            self.collision_ids.append(connection.circle)

    def find_collisions(self, go_to_x, go_to_y):
        """
        Return list of tags that would be colliding with the Box if it was at go_to_x and go_to_y coordinates.

        :param go_to_x: X coordinate where the Box would be.
        :param go_to_y: Y coordinate where the Box would be.
        :return: List of tags that would be colliding with the Box in the given location.
        """
        self.update_self_collision_ids()
        collision = self.canvas.find_overlapping(go_to_x, go_to_y, go_to_x + self.size[0], go_to_y + self.size[1])
        collision = list(collision)
        for index in self.collision_ids:
            if index in collision:
                collision.remove(index)
        for wire_label in self.canvas.wire_label_tags:
            if wire_label in collision:
                collision.remove(wire_label)
        for wire in self.canvas.wires:
            tag = wire.line
            if tag in collision:
                collision.remove(tag)
        return collision

    def on_resize_scroll(self, event):
        """
        Resize the Box based on event.

        Handles the ctrl + scroll event on Box. Will resize it accordingly to delta attribute of tkinter.Event.

        :param event: tkinter.Event object.
        :return: None
        """
        if event.delta == 120:
            multiplier = 1
        else:
            multiplier = -1
        if multiplier == -1:
            if 20 > min(self.size):
                return
        old_size = self.size
        self.size = (self.size[0] + 5 * multiplier, self.size[1] + 5 * multiplier)
        if self.find_collisions(self.x, self.y):
            self.size = old_size
            return
        self.update_size(self.size[0] + 5 * multiplier, self.size[1] + 5 * multiplier)
        self.move_label()

    def on_resize_drag(self, event):
        """
        Resize the Box based on mouse movement.

        Handles dragging on the resize handle.

        :param event: tkinter.Event object.
        :return: None
        """
        event.x, event.y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        resize_x = self.x + self.size[0] - 10
        resize_y = self.y + self.size[1] - 10
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        if dx > 0 and not resize_x <= event.x:
            dx = 0

        if dy > 0 and not resize_y <= event.y:
            dy = 0

        self.start_x = event.x
        self.start_y = event.y
        new_size_x = max(20, self.size[0] + dx)
        new_size_y = max(20, self.size[1] + dy)
        self.update_size(new_size_x, new_size_y)
        self.move_label()

    def resize_by_connections(self):
        """
        Resize the Box based on the amount of Connections.

        Resizes the Box so all Connections could have an appropriate amount of space between them.

        :return: None
        """
        nr_cs = max([c.index for c in self.connections] + [0])
        height = max([50 * nr_cs, 50])
        if self.size[1] < height:
            self.update_size(self.size[0], height)
            self.move_label()

    def move_label(self):
        """
        Move label to the center of the Box.

        :return: None
        """
        if self.label:
            self.canvas.coords(self.label, self.x + self.size[0] / 2, self.y + self.size[1] / 2)

    def bind_event_label(self):
        """
        Bind events to the Box label.

        :return: None
        """
        self.canvas.tag_bind(self.label, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.label, '<ButtonPress-3>', self.show_context_menu)
        self.canvas.tag_bind(self.label, '<Double-Button-1>', lambda _: self.handle_double_click())
        self.canvas.tag_bind(self.label, '<Control-ButtonPress-1>', lambda event: self.on_control_press())
        self.canvas.tag_bind(self.label, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.label, '<Enter>', lambda _: self.canvas.on_hover(self))
        self.canvas.tag_bind(self.label, '<Leave>', lambda _: self.canvas.on_leave_hover())

    def edit_label(self, new_label=None):
        """
        Edit Box label.

        If no parameters are given, the user will be asked to enter a label for the Box.
        With parameters asking the user for input is skipped and the new label will be applied to the box immediately.

        :param new_label: (Optional) New label for the box.
        :return: None
        """
        if new_label is None:
            text = simpledialog.askstring("Input", "Enter label:", initialvalue=self.label_text)
            if text is not None:
                self.label_text = text
            if os.stat(const.FUNCTIONS_CONF).st_size != 0:
                with open(const.FUNCTIONS_CONF, "r") as file:
                    data = json.load(file)
                    for label, code in data.items():
                        if label == self.label_text:
                            if messagebox.askokcancel("Confirmation",
                                                      "A box with this label already exists."
                                                      " Do you want to use the existing box?"):
                                self.update_io()
                            else:
                                return self.edit_label()
        else:
            self.label_text = new_label

        self.update_label()

        if self.label_text:
            if self.sub_diagram:
                self.sub_diagram.set_name(self.label_text)
                self.canvas.main_diagram.update_canvas_name(self.sub_diagram)

        self.bind_event_label()

    def update_label(self):
        """
        Create or update label.

        This will create or update a label based on the label_text variable

        :return: None
        """
        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_ADD_OPERATOR, generator_id=self.id, operator=self.label_text,
                                            canvas_id=self.canvas.id)
            # Add function to box associated with label (if exists).
            label_content = self.canvas.main_diagram.label_content
            if self.label_text in label_content:
                function_code = label_content[self.label_text]
                box_function = BoxFunction(file_code=function_code, main_function_name=self.label_text)
                self.set_box_function(box_function)
        if not self.label:
            self.label = self.canvas.create_text((self.x + self.size[0] / 2, self.y + self.size[1] / 2),
                                                 text=self.label_text, fill=const.BLACK, font=('Helvetica', 14))
            self.collision_ids.append(self.label)
        else:
            self.canvas.itemconfig(self.label, text=self.label_text)

    def set_label(self, new_label):
        """
        Set label for Box.

        :param new_label: New label text.
        :return: None
        """
        self.label_text = new_label
        self.update_label()
        self.bind_event_label()

    def on_resize_press(self, event):
        """
        Handles pressing on the resize handle.

        Sets variables start_(x/y) to allow for dragging.

        :param event: tkinter.Event object.
        :return: None
        """
        self.start_x = event.x
        self.start_y = event.y

    def move(self, new_x, new_y, bypass_legality=False):
        """
        Move the Box to a new location.

        Will move the Box to a new location unless the move is not legal.

        :param new_x: X coordinate Box will be moved to.
        :param new_y: Y coordinate Box will be moved to.
        :param bypass_legality: If movement should bypass legality checks.
        :return:
        """
        new_x = round(new_x, 4)
        new_y = round(new_y, 4)
        is_bad = False
        for connection in self.connections:
            if connection.has_wire and self.is_illegal_move(connection, new_x, bypass=bypass_legality):
                is_bad = True
                break
        if is_bad:
            self.y = new_y
            self.update_position()
            self.update_connections()
            self.update_wires()
        else:
            self.x = new_x
            self.y = new_y
            self.update_position()
            self.update_connections()
            self.update_wires()
        self.rel_x = round(self.x / self.canvas.winfo_width(), 4)
        self.rel_y = round(self.y / self.canvas.winfo_height(), 4)

    def select(self):
        """
        Apply the select style to the Box.

        Turns the Box outline and Connections into green.

        :return: None
        """
        self.canvas.itemconfig(self.shape, outline=const.SELECT_COLOR)
        [c.select() for c in self.connections]

    def search_highlight_secondary(self):
        """
        Apply the secondary search highlight style.

        Applies the secondary search highlight style to the Box. Changes outline color and Connections colors. Will
        add the Box to CustomCanvas list containing search highlighted objects.

        :return: None
        """
        self.canvas.itemconfig(self.shape, outline=const.SECONDARY_SEARCH_COLOR)
        [c.search_highlight_secondary() for c in self.connections]
        self.canvas.search_result_highlights.append(self)

    def search_highlight_primary(self):
        """
        Apply primary search highlight style.

        Applies the primary search highlight style to the Box. Changes outline color and Connections colors. Will
        add the Box to CustomCanvas list containing search highlighted objects.

        :return: None
        """
        self.canvas.itemconfig(self.shape, outline=const.PRIMARY_SEARCH_COLOR)
        [c.search_highlight_primary() for c in self.connections]
        self.canvas.search_result_highlights.append(self)

    def deselect(self):
        """
        Deselect the Box.

        Turns the outline of the Box to black along with its Connections.

        :return: None
        """
        self.canvas.itemconfig(self.shape, outline=const.BLACK)
        [c.deselect() for c in self.connections]

    def lock_box(self):
        """
        Lock the Box.

        Turns locked value to True.

        :return: None
        """
        self.locked = True

    def unlock_box(self):
        """
        Unlock the Box.

        Turns the locked value to False.

        :return: None
        """
        self.locked = False

    # UPDATES
    def update_size(self, new_size_x, new_size_y):
        """
        Update Box size.

        Update the Size and locations of items attached to the Box.

        :param new_size_x: New width
        :param new_size_y: New height
        :return: None
        """
        self.size = (new_size_x, new_size_y)
        self.update_position()
        self.update_connections()
        self.update_wires()

    def update_position(self):
        """
        Update the CustomCanvas position of the Box.

        :return: None
        """
        if self.style == const.RECTANGLE:
            self.canvas.coords(self.shape, self.x, self.y, self.x + self.size[0], self.y + self.size[1])
        if self.style == const.TRIANGLE:
            self.canvas.coords(self.shape,
                               self.x + self.size[0], self.y + self.size[1] / 2,
                               self.x, self.y,
                               self.x, self.y + self.size[1])
        self.canvas.coords(self.resize_handle, self.x + self.size[0] - 10, self.y + self.size[1] - 10,
                           self.x + self.size[0], self.y + self.size[1])

    def update_connections(self):
        """
        Update Connection locations of Box.

        :return: None
        """
        for c in self.connections:
            conn_x, conn_y = self.get_connection_coordinates(c.side, c.index)
            c.move_to((conn_x, conn_y))

    def update_wires(self):
        """
        Update Wires.

        Updates Wires that are connected to the Box.

        :return: None
        """
        [wire.update() for wire in self.wires]

    def update_io(self):
        """
        Update inputs and outputs of Box.

        Updates the inputs and outputs of a Box based on the code that is added to it.

        :return: None
        """
        with open(const.FUNCTIONS_CONF, "r") as file:
            data = json.load(file)
            for label, code in data.items():
                if label == self.label_text:
                    inputs_amount, outputs_amount = self.get_input_output_amount_off_code(code)
                    if inputs_amount > self.left_connections:
                        for i in range(inputs_amount - self.left_connections):
                            self.add_left_connection()
                    elif inputs_amount < self.left_connections:
                        for j in range(self.left_connections - inputs_amount):
                            for con in self.connections[::-1]:
                                if con.side == const.LEFT:
                                    self.remove_connection(con)
                                    break

                    if outputs_amount > self.right_connections:
                        for i in range(outputs_amount - self.right_connections):
                            self.add_right_connection()
                    elif outputs_amount < self.right_connections:
                        for i in range(self.right_connections - outputs_amount):
                            for con in self.connections[::-1]:
                                if con.side == const.RIGHT:
                                    self.remove_connection(con)
                                    break

    # ADD TO/REMOVE FROM CANVAS
    def add_wire(self, wire):
        """
        Add a wire to the Box.

        :param wire: Wire to be added.
        :return: None
        """
        if wire not in self.wires:
            self.wires.append(wire)

    def add_left_connection(self, id_=None, connection_type=ConnectionType.GENERIC):
        """
        Add a Connection to the left side of the Box.

        Creates and adds a Connection to the left side of the Box.

        :param id_: (Optional) ID that will be added to the Connection.
        :param connection_type: (Optional) Type of Connection that will be added.
        :return: Connection object
        """
        i = self.get_new_left_index()
        conn_x, conn_y = self.get_connection_coordinates(const.LEFT, i)
        connection = Connection(self, i, const.LEFT, (conn_x, conn_y), self.canvas, id_=id_,
                                connection_type=connection_type)
        self.left_connections += 1
        self.connections.append(connection)
        self.collision_ids.append(connection.circle)

        self.update_connections()
        self.update_wires()
        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_ADD_LEFT, generator_id=self.id, connection_nr=i,
                                            connection_id=connection.id, canvas_id=self.canvas.id)

        self.resize_by_connections()
        return connection

    def add_right_connection(self, id_=None, connection_type=ConnectionType.GENERIC):
        """
        Add a Connection to the right side of the Box.

        Creates and adds a Connection to the right side of the Box.

        :param id_: (Optional) ID that will be added to the Connection.
        :param connection_type: (Optional) Type of Connection that will be added.
        :return: Connection object
        """
        i = self.get_new_right_index()
        conn_x, conn_y = self.get_connection_coordinates(const.RIGHT, i)
        connection = Connection(self, i, const.RIGHT, (conn_x, conn_y), self.canvas, id_=id_,
                                connection_type=connection_type)
        self.right_connections += 1
        self.connections.append(connection)
        self.collision_ids.append(connection.circle)

        self.update_connections()
        self.update_wires()
        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_ADD_RIGHT, generator_id=self.id, connection_nr=i,
                                            connection_id=connection.id, canvas_id=self.canvas.id)
        self.resize_by_connections()
        return connection

    def remove_connection(self, circle: Connection):
        """
        Remove a Connection from the box.

        Removes the given Connection from the Box.

        :param circle: Connection that will be removed
        :return: None
        """
        for c in self.connections:
            if c.index > circle.index and circle.side == c.side:
                c.lessen_index_by_one()
        if self.receiver.listener and not self.canvas.is_search:
            if circle.side == ConnectionSide.LEFT:
                self.receiver.receiver_callback(ActionType.BOX_REMOVE_LEFT, generator_id=self.id,
                                                connection_nr=circle.index, connection_id=circle.id,
                                                canvas_id=self.canvas.id)
            elif circle.side == ConnectionSide.RIGHT:
                self.receiver.receiver_callback(ActionType.BOX_REMOVE_RIGHT, generator_id=self.id,
                                                connection_nr=circle.index, connection_id=circle.id,
                                                canvas_id=self.canvas.id)
        if circle.side == const.LEFT:
            self.left_connections -= 1
        elif circle.side == const.RIGHT:
            self.right_connections -= 1

        self.connections.remove(circle)
        self.collision_ids.remove(circle.circle)
        circle.delete()
        self.update_connections()
        self.update_wires()
        self.resize_by_connections()

    def delete_box(self, keep_sub_diagram=False, action=None):
        """
        Delete Box.

        Delete the Box, its Connections and sub-diagram if chosen to.

        :param keep_sub_diagram: (Optional) Specify whether the sub-diagram will be kept.
        :param action: (Optional) Specify if the deletion is done for creating a sub-diagram.
        :return: None
        """
        for c in self.connections:
            c.delete()

        self.canvas.delete(self.shape)
        self.canvas.delete(self.resize_handle)

        if self in self.canvas.boxes:
            self.canvas.boxes.remove(self)
        self.canvas.delete(self.label)
        if self.sub_diagram and not keep_sub_diagram:
            self.canvas.main_diagram.del_from_canvasses(self.sub_diagram)
        if self.receiver.listener and not self.canvas.is_search:
            self.receiver.receiver_callback(ActionType.BOX_DELETE, generator_id=self.id, canvas_id=self.canvas.id)

    # BOOLEANS
    def is_illegal_move(self, connection, new_x, bypass=False):
        """
        Check whether move to new_x is illegal.

        Will take a Connection and an x coordinate and check whether moving the connection to the x coordinate is legal.

        :param connection: Connection that the new location
        :param new_x: x coordinate to move to.
        :param bypass: if legality checking will be bypassed.
        :return: boolean if move is illegal
        """
        if bypass:
            return False
        wire = connection.wire
        if connection.side == const.LEFT:
            if connection == wire.start_connection:
                other_connection = wire.end_connection
            else:
                other_connection = wire.start_connection
            other_x = other_connection.location[0]
            if other_x + other_connection.width_between_boxes >= new_x:
                return True

        if connection.side == const.RIGHT:
            if connection == wire.start_connection:
                other_connection = wire.end_connection
            else:
                other_connection = wire.start_connection

            other_x = other_connection.location[0]
            if other_x - other_connection.width_between_boxes <= new_x + self.size[0]:
                return True
        return False

    # HELPERS
    def get_connection_coordinates(self, side, index):
        """
        Return coordinates for a Connection.

        Returns coordinates for a Connection at one side of the Box at index.

        :param side: Side of Box that the Connection would be on.
        :param index: Index at which the Connection would be on the given side.
        :return: Tuple of coordinates for a Connection.
        """
        if side == const.LEFT:
            i = self.get_new_left_index()
            return self.x, self.y + (index + 1) * self.size[1] / (i + 1)

        elif side == const.RIGHT:
            i = self.get_new_right_index()
            return self.x + self.size[0], self.y + (index + 1) * self.size[1] / (i + 1)

    def get_new_left_index(self):
        """
        Return a new index for the left side of the Box.

        :return: int
        """
        if not self.left_connections > 0:
            return 0
        return max([c.index if c.side == const.LEFT else 0 for c in self.connections]) + 1

    def get_new_right_index(self):
        """
        Return a new index for the right side of the Box.

        :return: int
        """
        if not self.right_connections > 0:
            return 0
        return max([c.index if c.side == const.RIGHT else 0 for c in self.connections]) + 1

    def create_shape(self):
        """
        Create a CustomCanvas shape for the Box.

        :return: Tag that represents the Box in CustomCanvas.
        """
        w, h = self.size
        if self.style == const.RECTANGLE:
            return self.canvas.create_rectangle(self.x, self.y, self.x + w, self.y + h,
                                                outline=const.BLACK, fill=const.WHITE)
        if self.style == const.TRIANGLE:
            return self.canvas.create_polygon(self.x + w, self.y + h / 2, self.x, self.y,
                                              self.x, self.y + h, outline=const.BLACK, fill=const.WHITE)

    def change_shape(self, shape):
        """
        Change shape of Box.

        Works by creating a new copied Box with a different shape.

        :param shape: Shape of new Box
        :return: None
        """
        if shape == const.RECTANGLE:
            new_box = self.canvas.add_box((self.x, self.y), self.size, style="rectangle")
        elif shape == const.TRIANGLE:
            new_box = self.canvas.add_box((self.x, self.y), self.size, style="triangle")
        else:
            return
        self.canvas.copier.copy_box(self, new_box)
        self.delete_box()

    @staticmethod
    def get_input_output_amount_off_code(code):
        """
        Return amount of inputs and outputs based off code.

        Returns the amount of inputs and outputs in code.

        :param code: String code
        :return: Tuple of input and output amount
        """
        inputs = re.search(r"\((.*)\)", code).group(1)
        outputs = re.search(r"return (.*)\n*", code).group(1)
        inputs_amount = len(inputs.split(","))
        if outputs[0] == "(":
            outputs = outputs[1:-1]
        outputs_amount = len(outputs.strip().split(","))
        if not inputs:
            inputs_amount = 0
        if not outputs:
            outputs_amount = 0
        return inputs_amount, outputs_amount

    def __eq__(self, other):
        if type(self) is type(other):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
