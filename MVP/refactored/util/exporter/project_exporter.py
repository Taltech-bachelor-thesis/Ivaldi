import json
import re
import time
from tkinter import messagebox
from pathlib import Path

from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.backend.box_functions.box_function import BoxFunction
from constants import *

from MVP.refactored.util.exporter.exporter import Exporter
import constants as const


class ProjectExporter(Exporter):

    def __init__(self, canvas):
        super().__init__(canvas)
        self.box_function_to_filename: dict[BoxFunction, str] = dict()  # value is box function filename
        self.filename_to_box_function: dict[str, BoxFunction] = dict()  # key is box function filename
        # two same dicts for following purpose: if box function already added, we don`t need to add it again, just use it`s name.
        # but if it is new, we need to create filename and check if it is coincided with other filename

    def create_file_content(self, filename):
        return {"file_name": filename,
                "date": time.time(),
                "static_variables": self.get_static_variables(),
                "main_canvas": self.create_canvas_dict(self.canvas)
                }

    @staticmethod
    def get_static_variables():
        variables = {
            "active_types": Connection.active_types,
            "defined_wires": Wire.defined_wires
        }
        return variables

    def create_canvas_dict(self, canvas):
        return {"boxes": self.create_boxes_list(canvas),
                "spiders": self.create_spiders_list(canvas),
                "io": self.create_io_dict(canvas),
                "wires": self.create_wires_list(canvas)}

    def create_wires_list(self, canvas):
        return [{"id": wire.id,
                 "start_c": self.get_connection(wire.start_connection),
                 "end_c": self.get_connection(wire.end_connection)
                 } for wire in canvas.wires]

    def create_spiders_list(self, canvas):
        spiders_list = []
        for spider in canvas.spiders:
            connections_list = self.get_connections(spider.connections)

            spider_d = {
                "id": spider.id,
                "x": spider.x,
                "y": spider.y,
                "connections": connections_list,
                "type": spider.type.name
            }
            spiders_list.append(spider_d)

        return spiders_list

    def create_io_dict(self, canvas):
        return {"inputs": self.get_connections(canvas.inputs),
                "outputs": self.get_connections(canvas.outputs)}

    def create_boxes_list(self, canvas):
        boxes_list = []
        for box in canvas.boxes:
            d = {
                "id": box.id,
                "x": box.x,
                "y": box.y,
                "size": box.size,
                "label": box.label_text,
                "connections": self.get_connections(box.connections),
                "sub_diagram": None,
                "locked": box.locked,
                "shape": box.style
            }
            if box.get_box_function() is not None:
                if box.get_box_function() in self.box_function_to_filename:
                    box_function_filename = self.box_function_to_filename[box.get_box_function()]
                else:
                    # box_function_filename = (f"{box.get_box_function().name}" TODO return back when we return "name" to box function
                    #                          f"{f"_{len(self.filename_to_box_function)}" if box.get_box_function().name in self.filename_to_box_function else ""}.py")
                    box_function_filename = (f"{box.get_box_function().main_function_name}"
                                             f"{f"_{len(self.filename_to_box_function)}" if box.get_box_function().main_function_name + ".py" in self.filename_to_box_function else ""}.py")
                    self.box_function_to_filename[box.get_box_function()] = box_function_filename
                    self.filename_to_box_function[box_function_filename] = box.get_box_function()
                d["box_function"] = {
                    "relative_location": f"./box_functions/{box_function_filename}",
                    "name": box_function_filename,
                    "main_function_name": box.get_box_function().get_main_function_name(),
                }
            else:
                d["box_function_relative_location"] = ""
            if box.sub_diagram:
                d["sub_diagram"] = self.create_canvas_dict(box.sub_diagram)
            boxes_list.append(d)

        return boxes_list

    def get_connections(self, c_list):
        return [self.get_connection(c) for c in c_list]

    @staticmethod
    def get_connection(connection):
        d = {"id": connection.id,
             "side": connection.side,
             "index": connection.index,
             "spider": connection.is_spider(),
             "box_id": None,
             "has_wire": connection.has_wire,
             "wire_id": None,
             "type": connection.type.name
             }
        if connection.box:
            d["box_id"] = connection.box.id
        if connection.wire:
            d["wire_id"] = connection.wire.id
        return d

    # BOX MENU LOGIC
    def export_box_to_menu(self, box):
        current = self.get_current_data()
        if box.label_text in current:
            messagebox.showinfo("Info", "Box with same label already in menu")
            return

        left_connections = 0
        right_connections = 0
        left_con_types = []
        right_con_types = []

        for c in box.connections:
            if c.side == "left":
                left_connections += 1
                left_con_types.append(c.type.name)
            elif c.side == "right":
                right_connections += 1
                right_con_types.append(c.type.name)

        new_entry = {
            "label": box.label_text,
            "left_c": left_connections,
            "right_c": right_connections,
            "left_c_types": left_con_types,
            "right_c_types": right_con_types,
            "shape": box.style,
            "sub_diagram": None,
        }
        if box.sub_diagram:
            new_entry["sub_diagram"] = self.create_canvas_dict(box.sub_diagram)
        current[box.label_text] = new_entry

        with open(const.BOXES_CONF, "w") as outfile:
            json.dump(current, outfile, indent=4)

    def export(self) -> str:
        self.box_function_to_filename.clear()
        self.filename_to_box_function.clear()
        filename = self.ask_filename_and_location()
        if filename:
            d = self.create_file_content(filename)
            with open(filename, "w") as outfile:
                json.dump(d, outfile, indent=4)

            box_functions_folder = re.sub(r'(/[^/]+?\.json)', "", filename) + "/box_functions/"
            for box_function_filename, box_function in self.filename_to_box_function.items():
                file_code = box_function.get_file_code()
                if len(file_code) > 0:
                    box_function_file = Path(box_functions_folder + box_function_filename)
                    box_function_file.parent.mkdir(parents=True, exist_ok=True)
                    box_function_file.write_text(file_code)
            messagebox.showinfo("Info", "Project saved successfully")
        return filename

    @staticmethod
    def get_current_data():
        try:
            with open(const.BOXES_CONF, 'r') as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError or IOError or json.JSONDecodeError:
            return {}

    def del_box_menu_option(self, box):
        current = self.get_current_data()
        current.pop(box)
        with open(const.BOXES_CONF, "w") as outfile:
            json.dump(current, outfile, indent=4)
