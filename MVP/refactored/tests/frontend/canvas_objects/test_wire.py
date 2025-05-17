import tkinter
import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
from MVP.refactored.frontend.canvas_objects.types.wire_types import WireType
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestApplication(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class WireTest(TestApplication):

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.update")
    def test__init__values(self, update_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        self.assertEqual(connection_start, wire.start_connection)
        self.assertEqual(connection_end, wire.end_connection)
        self.assertEqual(3, wire.wire_width)
        self.assertIsNone(wire.line)
        self.assertFalse(wire.is_temporary)
        self.assertEqual(WireType.GENERIC, wire.type)
        self.assertEqual(1, update_mock.call_count)

    def test__delete_self__removes_self_spider_wires(self):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        connection_start.add_wire(wire)
        connection_end.add_wire(wire)

        self.assertIn(wire, connection_start.wires)
        self.assertIn(wire, connection_end.wires)

        wire.delete()

        self.assertFalse(connection_start.has_wire)
        self.assertFalse(connection_end.has_wire)
        self.assertNotIn(wire, connection_start.wires)
        self.assertNotIn(wire, connection_end.wires)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.handle_wire_addition_callback")
    def test__delete_self__removes_self_connection_wire(self, handle_wire_addition_callback_mock):
        connection_start = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        connection_end = Connection(None, 1010, "left", (111, 222), self.custom_canvas)

        wire = Wire(self.custom_canvas, connection_start, connection_end)

        connection_start.add_wire(wire)
        connection_end.add_wire(wire)

        self.assertTrue(connection_start.has_wire)
        self.assertTrue(connection_end.has_wire)
        self.assertEqual(wire, connection_start.wire)
        self.assertEqual(wire, connection_end.wire)

        wire.delete()

        self.assertFalse(connection_start.has_wire)
        self.assertFalse(connection_end.has_wire)
        self.assertIsNone(connection_start.wire)
        self.assertIsNone(connection_end.wire)

    def test__select__turn_line_green(self):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.select()

        expected_end_color = "green"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)['fill'][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__deselect__turn_line_original(self):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        wire.select()

        expected_start_color = "green"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)['fill'][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.deselect()

        expected_end_color = "black"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__search_highlight_secondary__turns_line_orange(self):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.search_highlight_secondary()

        expected_end_color = "orange"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    def test__search_highlight_primary__turns_line_cyan(self):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        expected_start_color = "black"
        actual_start_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        wire.search_highlight_primary()

        expected_end_color = "cyan"
        actual_end_color = self.custom_canvas.itemconfig(wire.line)["fill"][-1]
        self.assertEqual(expected_end_color, actual_end_color)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.post")
    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.close_menu")
    def test__show_context_menu__callouts(self, post_mock, close_menu_mock, add_command_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        event = tkinter.Event()
        event.x_root, event.y_root = 150, 300

        wire.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(4, add_command_mock.call_count)
        self.assertEqual(1, post_mock.call_count)

    @patch("tkinter.Menu.post")
    def test__show_context_menu__no_callouts_if_is_temporary(self, post_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        wire.is_temporary = True

        event = tkinter.Event()
        event.x_root, event.y_root = 150, 300

        wire.show_context_menu(event)

        self.assertEqual(0, post_mock.call_count)

    @patch("tkinter.Menu.destroy")
    def test__close_context_menu__closes(self, destroy_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        wire.context_menu = tkinter.Menu()

        wire.close_menu()

        self.assertTrue(destroy_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.delete")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.add_spider_with_wires")
    def test__create_spider__calls_out_methods(self, add_spider_with_wires_mock, delete_self_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        self.assertFalse(add_spider_with_wires_mock.called)
        self.assertFalse(delete_self_mock.called)

        event = tkinter.Event()
        event.x, event.y = 150, 300

        wire.create_spider(event)

        self.assertTrue(add_spider_with_wires_mock.called)
        self.assertTrue(delete_self_mock.called)

    def test__create_spider__creates_spider(self):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        self.assertEqual(0, len(self.custom_canvas.spiders))

        event = tkinter.Event()
        event.x, event.y = 150, 300

        wire.create_spider(event)

        spider = self.custom_canvas.spiders[0]

        self.assertEqual(1, len(self.custom_canvas.spiders))
        self.assertEqual(150, spider.x)
        self.assertEqual(300, spider.y)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_lower")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.update_wire_label")
    def test__update__calls_methods(self, update_wire_label_mock, tag_bind_mock, tag_lower_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)

        wire = Wire(self.custom_canvas, connection_start, connection_end)
        wire.line = None

        tag_bind_mock.call_count = 0
        tag_lower_mock.call_count = 0
        update_wire_label_mock.call_count = 0

        wire.update()

        self.assertEqual(tag_bind_mock.call_count, 1)
        self.assertEqual(tag_lower_mock.call_count, 1)
        self.assertEqual(update_wire_label_mock.call_count, 1)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.create_line")
    def test__update__calls_create_line(self, create_line_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        wire.line = None

        create_line_mock.call_count = 0

        wire.update()

        self.assertEqual(create_line_mock.call_count, 1)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.coords")
    def test__update__calls_coords_if_line(self, coords_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        self.assertIsNotNone(wire.line)

        wire.update()

        self.assertTrue(coords_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.update_wire_label")
    @patch("tkinter.simpledialog.askstring", return_value="String")
    def test__define_type__defines_type(self, ask_string_mock, update_wire_label_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        wire.define_type()

        self.assertEqual(Wire.defined_wires[wire.type.name], "String")
        self.assertEqual(ConnectionType.LABEL_NAMES.value[ConnectionType[wire.type.name].value], "String")
        self.assertEqual(update_wire_label_mock.call_count, 1)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.delete_labels")
    @patch("tkinter.simpledialog.askstring", side_effect=["Int", ""])
    def test__define_type__empty_string_deletes_name(self, ask_string_mock, delete_labels_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        self.custom_canvas.wires.append(wire)

        wire.define_type()

        self.assertFalse(delete_labels_mock.called)
        self.assertEqual(Wire.defined_wires[wire.type.name], "Int")

        wire.define_type()

        self.assertTrue(delete_labels_mock.called)
        self.assertEqual(len(Wire.defined_wires), 0)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.delete_labels")
    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.update_wire_label")
    @patch("tkinter.simpledialog.askstring",  return_value=None)
    def test__define_type__canceled(self, ask_string_mock, update_wire_label_mock, delete_labels_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)

        update_wire_label_mock.call_count = 0

        wire.define_type()

        self.assertEqual(update_wire_label_mock.call_count, 0)
        self.assertFalse(delete_labels_mock.called)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    def test__delete_labels__deletes_end_label(self, ask_string_mock, delete_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Connection(None, 1011, "left", (222, 333), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        self.custom_canvas.wires.append(wire)

        wire.define_type()

        self.assertIsNotNone(wire.end_label)
        self.assertIsNone(wire.start_label)

        wire.delete_labels()
        self.assertIsNone(wire.end_label)
        self.assertIsNone(wire.start_label)
        self.assertEqual(delete_mock.call_count, 1)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    def test__delete_labels__deletes_start_label(self, ask_string_mock, delete_mock):
        connection_start = Connection(None, 1011, "right", (222, 333), self.custom_canvas)
        connection_end = Spider((111, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        self.custom_canvas.wires.append(wire)

        wire.define_type()

        self.assertIsNotNone(wire.start_label)
        self.assertIsNone(wire.end_label)

        wire.delete_labels()

        self.assertIsNone(wire.start_label)
        self.assertIsNone(wire.end_label)
        self.assertEqual(delete_mock.call_count, 1)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.handle_wire_addition_callback")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.coords")
    @patch("tkinter.simpledialog.askstring", return_value="Int")
    def test__update_wire_label__updates_existing_labels(self, ask_string_mock, coords_mock,
                                                         handle_wire_addition_callback_mock):
        connection_start = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        connection_end = Connection(None, 1011, "left", (333, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        self.custom_canvas.wires.append(wire)

        wire.define_type()

        self.assertEqual(Wire.defined_wires[wire.type.name], "Int")

        coords_mock.call_count = 0
        Wire.defined_wires[wire.type.name] = "String"
        wire.update_wire_label()

        self.assertEqual(Wire.defined_wires[wire.type.name], "String")
        self.assertEqual(coords_mock.call_count, 2)

    @patch("MVP.refactored.frontend.canvas_objects.wire.Wire.handle_wire_addition_callback")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.create_text")
    def test__update_wire_label__adds_new_labels(self, create_text_mock, handle_wire_addition_callback_mock):
        connection_start = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        connection_end = Connection(None, 1011, "left", (333, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        self.custom_canvas.wires.append(wire)

        Wire.defined_wires[wire.type.name] = "String"
        wire.update_wire_label()

        self.assertEqual(len(self.custom_canvas.wire_label_tags), 2)
        self.assertEqual(create_text_mock.call_count, 2)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.itemconfig")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.create_text")
    def test__update_wire_label__does_not_create_label_for_spiders(self, itemconfig_mock,
                                                                   create_text_mock):
        connection_start = Spider((111, 222), self.custom_canvas)
        connection_end = Spider((222, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end)
        self.custom_canvas.wires.append(wire)

        itemconfig_mock.call_count = 0
        create_text_mock.call_count = 0

        Wire.defined_wires[wire.type.name] = "String"
        wire.update_wire_label()

        self.assertEqual(itemconfig_mock.call_count, 0)
        self.assertEqual(create_text_mock.call_count, 0)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.itemconfig")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.create_text")
    def test__update_wire_label__does_not_create_label_if_temp(self, itemconfig_mock,
                                                               create_text_mock):
        connection_start = Connection(None, 1010, "right", (111, 222), self.custom_canvas)
        connection_end = Connection(None, 1011, "left", (333, 444), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection_start, connection_end, is_temporary=True)
        self.custom_canvas.wires.append(wire)

        itemconfig_mock.call_count = 0
        create_text_mock.call_count = 0

        Wire.defined_wires[wire.type.name] = "String"
        wire.update_wire_label()

        self.assertEqual(itemconfig_mock.call_count, 0)
        self.assertEqual(create_text_mock.call_count, 0)
