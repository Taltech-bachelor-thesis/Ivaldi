import tkinter
import unittest
from unittest.mock import patch

import constants as const
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestApplication(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        Connection.active_types = 1
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class ConnectionTests(TestApplication):

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.bind_events')
    def test__init__values(self, bind_events_mock):
        connection = Connection(None, 1010, "left", (111, 222), self.custom_canvas)

        self.assertIsNone(connection.box)
        self.assertEqual(1010, connection.index)
        self.assertEqual(const.LEFT, connection.side)
        self.assertEqual((111, 222), connection.location)
        self.assertIsNone(connection.wire)
        self.assertFalse(connection.has_wire)
        self.assertEqual(5, connection.r)
        self.assertEqual(1, connection.width_between_boxes)
        self.assertEqual(ConnectionType.GENERIC, connection.type)
        self.assertTrue(bind_events_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.bind_events')
    def test__init__type_set(self, bind_events_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas,
                                connection_type=ConnectionType.FIFTH)

        self.assertEqual(ConnectionType.FIFTH, connection.type)
        self.assertTrue(bind_events_mock.called)

    @patch('tkinter.Canvas.itemconfig')
    @patch('tkinter.Canvas.update')
    def test__update__callouts(self, update_mock, itemconfig_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.update()

        self.assertEqual(2, itemconfig_mock.call_count)
        self.assertEqual(1, update_mock.call_count)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind')
    def test__bind_events__number_of_tag_binds(self, tag_bind_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        tag_bind_mock.call_count = 0
        connection.bind_events()
        self.assertEqual(2, tag_bind_mock.call_count)

    def test__increment_type__changes_type(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas,
                                connection_type=ConnectionType.FIRST)
        connection.increment_type()

        self.assertEqual(ConnectionType.SECOND, connection.type)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.change_type')
    @patch('MVP.refactored.frontend.canvas_objects.types.connection_type.ConnectionType.next')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.increment_active_types')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.update')
    def test__increment_type__callouts(self, update_mock, increment_type_mock, next_mock, change_type_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.increment_type()

        self.assertEqual(1, change_type_mock.call_count)
        self.assertEqual(1, next_mock.call_count)
        self.assertEqual(1, update_mock.call_count)
        self.assertEqual(1, increment_type_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.update')
    def test__change_type__changes_type(self, update_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)

        self.assertEqual(ConnectionType.GENERIC, connection.type)
        connection.change_type(2)
        self.assertEqual(ConnectionType.SECOND, connection.type)
        self.assertTrue(update_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.update')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.get_tied_connection', return_value=None)
    def test__change_type__does_not_change_if_tied_con_is_none(self, get_tied_connection_mock, update_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)

        self.assertEqual(ConnectionType.GENERIC, connection.type)
        connection.change_type(2)
        self.assertTrue(get_tied_connection_mock.called)
        self.assertNotEqual(ConnectionType.SECOND, connection.type)
        self.assertFalse(update_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.update')
    def test__change_type__updates_tied_con_if_found(self, update_mock):
        box = Box(self.custom_canvas, 10, 10)
        sub_diagram = CustomCanvas(self.app, self.app, diagram_source_box=box)
        connection = Connection(box, 0, const.RIGHT, (111, 222), self.custom_canvas)

        box.sub_diagram = sub_diagram
        box.connections.append(connection)

        sub_diagram.add_diagram_output()

        self.assertEqual(ConnectionType.GENERIC, connection.type)
        self.assertEqual(ConnectionType.GENERIC, sub_diagram.outputs[0].type)
        connection.change_type(2)
        self.assertEqual(ConnectionType.SECOND, connection.type)
        self.assertEqual(ConnectionType.SECOND, sub_diagram.outputs[0].type)
        self.assertEqual(2, update_mock.call_count)

    def test__get_tied_connection__returns_self_if_no_box(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)

        self.assertEqual(connection, connection.get_tied_connection())

    def test__get_tied_connection__returns_self_if_input_and_output_differ(self):
        box = Box(self.custom_canvas, 10, 10)
        sub_diagram = CustomCanvas(self.app, self.app, diagram_source_box=box)
        connection = Connection(box, 0, const.LEFT, (111, 222), self.custom_canvas)

        box.sub_diagram = sub_diagram
        box.connections.append(connection)

        sub_diagram.add_diagram_output()

        self.assertEqual(connection, connection.get_tied_connection())

    def test__get_tied_connection__return_none_if_inner_connection_has_wire(self):
        box = Box(self.custom_canvas, 10, 10)
        sub_diagram = CustomCanvas(self.app, self.app, diagram_source_box=box)
        connection = Connection(box, 0, const.RIGHT, (111, 222), self.custom_canvas)

        box.sub_diagram = sub_diagram
        box.connections.append(connection)

        sub_diagram.add_diagram_output()
        sub_diagram.outputs[0].has_wire = True

        self.assertIsNone(connection.get_tied_connection())

    def test__get_tied_connection__return_io_if_outer_connection_has_no_wire(self):
        box = Box(self.custom_canvas, 10, 10)
        sub_diagram = CustomCanvas(self.app, self.app, diagram_source_box=box)
        connection = Connection(box, 0, const.RIGHT, (111, 222), self.custom_canvas)

        box.sub_diagram = sub_diagram
        box.connections.append(connection)

        sub_diagram.add_diagram_output()

        self.assertEqual(sub_diagram.outputs[0], connection.get_tied_connection())

    def test__get_tied_connection__return_self_if_index_differ(self):
        box = Box(self.custom_canvas, 10, 10)
        sub_diagram = CustomCanvas(self.app, self.app, diagram_source_box=box)
        connection = Connection(box, 2, const.RIGHT, (111, 222), self.custom_canvas)

        box.sub_diagram = sub_diagram
        box.connections.append(connection)

        sub_diagram.add_diagram_output()
        sub_diagram.add_diagram_output()

        self.assertEqual(connection, connection.get_tied_connection())

    def test__get_tied_connection__return_io_with_correct_index(self):
        box = Box(self.custom_canvas, 10, 10)
        sub_diagram = CustomCanvas(self.app, self.app, diagram_source_box=box)
        connection = Connection(box, 1, const.RIGHT, (111, 222), self.custom_canvas)

        box.sub_diagram = sub_diagram
        box.connections.append(connection)

        sub_diagram.add_diagram_output()
        sub_diagram.add_diagram_output()
        sub_diagram.add_diagram_output()

        self.assertEqual(sub_diagram.outputs[1], connection.get_tied_connection())

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.add_type_choice')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.tk_popup')
    def test__show_context_menu__shows_if_no_box(self, tk_popup_mock, add_command_mock,
                                                 close_menu_mock, add_type_choice_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.wire = Wire(self.custom_canvas, connection, connection, is_temporary=False)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertFalse(close_menu_mock.called)
        self.assertFalse(add_type_choice_mock.called)
        self.assertEqual(0, add_command_mock.call_count)
        self.assertEqual(0, tk_popup_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.add_type_choice')
    @patch('MVP.refactored.frontend.canvas_objects.wire.Wire.handle_wire_addition_callback')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.tk_popup')
    def test__show_context_menu__shows_if_no_box(self, tk_popup_mock, add_command_mock,
                                                 close_menu_mock, handle_wire_addition_mock,
                                                 type_choice_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.wire = Wire(self.custom_canvas, connection, connection)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertTrue(type_choice_mock.called)
        self.assertTrue(handle_wire_addition_mock.called)
        self.assertEqual(2, add_command_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.wire.Wire.handle_wire_addition_callback')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.tk_popup')
    def test__show_context_menu__closes_if_locked_box(self, tk_popup_mock, add_command_mock,
                                                      close_menu_mock, handle_wire_addition_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10)
        connection.wire = Wire(self.custom_canvas, connection, connection)
        connection.box.locked = True
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertTrue(handle_wire_addition_mock.called)
        self.assertFalse(add_command_mock.called)
        self.assertFalse(tk_popup_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.add_type_choice')
    @patch('MVP.refactored.frontend.canvas_objects.wire.Wire.handle_wire_addition_callback')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.close_menu')
    @patch('tkinter.Menu.add_command')
    @patch('tkinter.Menu.tk_popup')
    def test__show_context_menu__calls_all_if_has_box(self, tk_popup, add_command_mock,
                                                      close_menu_mock, handle_wire_addition_mock,
                                                      type_choice_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10)
        connection.wire = Wire(self.custom_canvas, connection, connection)
        event = tkinter.Event()
        event.x_root, event.y_root = 10, 10
        connection.show_context_menu(event)

        self.assertTrue(close_menu_mock.called)
        self.assertTrue(type_choice_mock.called)
        self.assertTrue(handle_wire_addition_mock.called)
        self.assertEqual(2, add_command_mock.call_count)
        self.assertEqual(1, tk_popup.call_count)

    @patch('tkinter.Menu.add_cascade')
    @patch('tkinter.Menu.add_command')
    def test__add_type_choice__no_callouts_with_wire(self, add_command_mock, add_cascade_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.has_wire = True
        connection.add_type_choice()

        self.assertFalse(add_command_mock.called)
        self.assertFalse(add_cascade_mock.called)

    @patch('tkinter.Menu.add_cascade')
    @patch('tkinter.Menu.add_command')
    def test__add_type_choice__no_active_types(self, add_command_mock, add_cascade_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.context_menu = tkinter.Menu()
        connection.add_type_choice()

        self.assertEqual(1, add_cascade_mock.call_count)
        self.assertEqual(2, add_command_mock.call_count)

    @patch('tkinter.Menu.add_cascade')
    @patch('tkinter.Menu.add_command')
    def test__add_type_choice__some_active_types(self, add_command_mock, add_cascade_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        Connection.active_types = 4
        connection.context_menu = tkinter.Menu()
        connection.add_type_choice()

        self.assertEqual(1, add_cascade_mock.call_count)
        self.assertEqual(5, add_command_mock.call_count)

    @patch('tkinter.Menu.add_cascade')
    @patch('tkinter.Menu.add_command')
    def test__add_type_choice__all_active_types_no_add_new_button(self, add_command_mock, add_cascade_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        Connection.active_types = 10
        connection.context_menu = tkinter.Menu()
        connection.add_type_choice()

        self.assertEqual(1, add_cascade_mock.call_count)
        self.assertEqual(10, add_command_mock.call_count)

    @patch('tkinter.Menu.destroy')
    def test__close_menu__destroys_menu(self, destroy_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.context_menu = tkinter.Menu()

        connection.close_menu()
        self.assertTrue(destroy_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.change_type')
    @patch('MVP.refactored.frontend.canvas_objects.connection.Connection.increment_active_types')
    def test__add_active_type__callouts(self, increment_mock, change_type_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)

        connection.add_active_type()

        self.assertTrue(increment_mock.called)
        self.assertTrue(change_type_mock.called)

    def test__increment_active_types__adds_1_to_active_type(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.type = ConnectionType.FIRST

        connection.increment_active_types()
        self.assertEqual(2, Connection.active_types)

        connection.type = ConnectionType.SECOND
        connection.increment_active_types()
        self.assertEqual(3, Connection.active_types)

    @patch('MVP.refactored.frontend.canvas_objects.box.Box.remove_connection')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__has_box_is_input(self, input_mock, output_mock, remove_connection_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10)
        connection.box.sub_diagram = self.custom_canvas
        self.custom_canvas.diagram_source_box = connection.box
        connection.box.connections.append(connection)
        self.custom_canvas.inputs.append(connection)

        connection.delete_from_parent()

        self.assertTrue(input_mock.called)
        self.assertFalse(remove_connection_mock.called)
        self.assertFalse(output_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.box.Box.remove_connection')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__no_call_if_not_in_canvas_inputs(self, input_mock, remove_connection_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10)
        connection.box.sub_diagram = self.custom_canvas
        connection.box.connections.append(connection)

        connection.delete_from_parent()

        self.assertFalse(input_mock.called)
        self.assertTrue(remove_connection_mock.called)

    @patch('MVP.refactored.frontend.canvas_objects.box.Box.remove_connection')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__wrong_side_is_not_called_in_diagram_removal(self, input_mock, output_mock,
                                                                              remove_connection_mock):
        connection = Connection(None, 1010, const.RIGHT, (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10)
        connection.box.sub_diagram = self.custom_canvas
        connection.box.connections.append(connection)
        self.custom_canvas.inputs.append(connection)

        connection.delete_from_parent()

        self.assertFalse(input_mock.called)
        self.assertFalse(output_mock.called)
        self.assertTrue(remove_connection_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__right_calls_output(self, input_mock, output_mock):
        connection = Connection(None, 1010, const.RIGHT, (111, 222), self.custom_canvas)
        connection.box = Box(self.custom_canvas, 10, 10)
        connection.box.sub_diagram = self.custom_canvas
        connection.box.connections.append(connection)
        self.custom_canvas.outputs.append(connection)

        connection.delete_from_parent()

        self.assertFalse(input_mock.called)
        self.assertTrue(output_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_input')
    def test__delete_from_parent__without_box_is_input(self, input_mock):
        connection = Connection(None, 1010, const.RIGHT, (111, 222), self.custom_canvas)
        self.custom_canvas.inputs.append(connection)

        connection.delete_from_parent()

        self.assertTrue(input_mock.called)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.remove_specific_diagram_output')
    def test__delete_from_parent__without_box_is_output(self, output_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        self.custom_canvas.outputs.append(connection)

        connection.delete_from_parent()

        self.assertTrue(output_mock.called)

    def test__change_color__no_param_changes_config_fill_to_black(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.change_color('red')

        config = self.custom_canvas.itemconfig(connection.circle)["fill"]
        self.assertTrue('red' in config)

        connection.change_color()
        config = self.custom_canvas.itemconfig(connection.circle)["fill"]
        self.assertTrue('black' in config)

    def test__change_color__changes_config_fill_to_green(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.change_color(color='green')
        config = self.custom_canvas.itemconfig(connection.circle)["fill"]
        self.assertTrue('green' in config)

    def test__move_to__changes_location(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.move_to((1010, 2020))
        self.assertEqual(1010, connection.location[0])
        self.assertEqual(2020, connection.location[1])

    def test__lessen_index_by_one__lowers_index(self):
        connection = Connection(None, 2, const.LEFT, (111, 222), self.custom_canvas)

        connection.lessen_index_by_one()

        self.assertEqual(1, connection.index)

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete')
    def test__delete__no_wire_calls_delete_once(self, delete_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.delete()

        self.assertEqual(1, delete_mock.call_count)

    @patch('MVP.refactored.frontend.canvas_objects.wire.Wire.delete')
    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.delete')
    def test__delete__has_wire_calls_delete_twice(self, delete_mock, delete_wire_mock):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, None, is_temporary=True)
        connection.wire = wire
        connection.has_wire = True
        connection.delete()

        self.assertEqual(2, delete_mock.call_count)
        self.assertEqual(1, delete_wire_mock.call_count)

    def test__add_wire__adds_wire(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection2 = Connection(None, 1011, const.RIGHT, (222, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, connection2, is_temporary=True)
        self.assertIsNone(connection.wire)
        self.assertFalse(connection.has_wire)

        connection.add_wire(wire)
        self.assertEqual(wire, connection.wire)
        self.assertTrue(connection.has_wire)

    def test__add_wire__does_not_change_wire_if_connection_has_wire(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection2 = Connection(None, 1011, const.RIGHT, (222, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, connection2, is_temporary=True)
        wire2 = Wire(self.custom_canvas, connection2, connection, is_temporary=True)

        connection.add_wire(wire)

        connection.add_wire(wire2)

        self.assertEqual(wire, connection.wire)
        self.assertTrue(connection.has_wire)

    def test__is_spider__returns_false(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        self.assertFalse(connection.is_spider())

    def test__remove_wire__removes_wire(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection2 = Connection(None, 1011, const.RIGHT, (222, 222), self.custom_canvas)
        wire = Wire(self.custom_canvas, connection, connection2, is_temporary=True)

        connection.add_wire(wire)
        self.assertEqual(wire, connection.wire)
        self.assertTrue(connection.has_wire)

        connection.remove_wire(wire)
        self.assertIsNone(connection.wire)
        self.assertFalse(connection.has_wire)

    def test__select__turns_item_select_color(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        self.assertTrue(const.BLACK in self.custom_canvas.itemconfig(connection.circle)["fill"])

        connection.select()
        self.assertTrue(const.SELECT_COLOR in self.custom_canvas.itemconfig(connection.circle)["fill"])

    def test__search_highlight_secondary__turns_item_secondary_color_and_adds_to_search_highlights(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        self.assertTrue(const.BLACK in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([], self.custom_canvas.search_result_highlights)

        connection.search_highlight_secondary()
        self.assertTrue(const.SECONDARY_SEARCH_COLOR in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([connection], self.custom_canvas.search_result_highlights)

    def test__search_highlight_primary__turns_item_primary_color_and_adds_to_search_highlights(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        self.assertTrue(const.BLACK in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([], self.custom_canvas.search_result_highlights)

        connection.search_highlight_primary()
        self.assertTrue(const.PRIMARY_SEARCH_COLOR in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertListEqual([connection], self.custom_canvas.search_result_highlights)

    def test__deselect__turns_item_black(self):
        connection = Connection(None, 1010, const.LEFT, (111, 222), self.custom_canvas)
        connection.select()
        self.assertTrue(const.SELECT_COLOR in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertFalse(const.BLACK in self.custom_canvas.itemconfig(connection.circle)["fill"])

        connection.deselect()
        self.assertFalse(const.SELECT_COLOR in self.custom_canvas.itemconfig(connection.circle)["fill"])
        self.assertTrue(const.BLACK in self.custom_canvas.itemconfig(connection.circle)["fill"])
