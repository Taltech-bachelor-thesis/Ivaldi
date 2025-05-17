import tkinter
import unittest
from unittest.mock import patch

import constants as const
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestMainDiagram(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class BoxTests(TestMainDiagram):
    def test__init__values(self):
        expected_x = 25
        expected_y = 50

        expected_width = 100
        expected_height = 125

        box = Box(self.custom_canvas, expected_x, expected_y, size=(expected_width, expected_height))

        self.assertEqual(expected_x, box.x)
        self.assertEqual(expected_y, box.y)

        self.assertEqual((expected_width, expected_height), box.size)

        self.assertListEqual([], box.connections)

        self.assertEqual(0, box.left_connections)
        self.assertEqual(0, box.right_connections)

        self.assertIsNone(box.label)

        self.assertFalse(box.label_text)
        self.assertListEqual([], box.wires)

        self.assertIsNone(box.context_menu)

        self.assertFalse(False, box.locked)

        self.assertIsNone(box.sub_diagram)

        self.assertFalse(box.is_snapped)

        self.assertEqual(expected_x, box.start_x)
        self.assertEqual(expected_y, box.start_y)
        self.assertEqual(0, box.x_dif)
        self.assertEqual(0, box.y_dif)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_position")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    def test__update_size__changes_size(self, mock, mock2, mock3):
        box = Box(self.custom_canvas, 100, 100)
        expected_size = (100, 100)
        box.update_size(expected_size[0], expected_size[1])
        self.assertEqual(expected_size, box.size)
        self.assertTrue(mock.called)
        self.assertTrue(mock2.called)
        self.assertTrue(mock3.called)

    def test__add_left_connection__adds_connection(self):
        box = Box(self.custom_canvas, 100, 100)
        box.add_left_connection()

        self.assertEqual(1, len(box.connections))
        self.assertEqual(1, box.left_connections)
        self.assertEqual(0, box.right_connections)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.resize_by_connections")
    def test__add_left_connection__calls_other_methods(self,
                                                       resize_by_connections_mock,
                                                       update_wires_mock,
                                                       update_connections_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.add_left_connection()

        self.assertTrue(resize_by_connections_mock.called)
        self.assertTrue(update_wires_mock.called)
        self.assertTrue(update_connections_mock.called)

    def test__add_right_connection__adds_connection(self):
        box = Box(self.custom_canvas, 100, 100)
        box.add_right_connection()

        self.assertEqual(1, len(box.connections))
        self.assertEqual(1, box.right_connections)
        self.assertEqual(0, box.left_connections)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.resize_by_connections")
    def test__add_right_connection__calls_other_methods(self,
                                                        resize_by_connections_mock,
                                                        update_wires_mock,
                                                        update_connections_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.add_right_connection()

        self.assertTrue(resize_by_connections_mock.called)
        self.assertTrue(update_wires_mock.called)
        self.assertTrue(update_connections_mock.called)

    def test__lock_box__turns_locked_to_true(self):
        box = Box(self.custom_canvas, 100, 100)
        self.assertFalse(box.locked)

        box.lock_box()
        self.assertTrue(box.locked)

    def test__unlock_box__turns_locked_to_false(self):
        box = Box(self.custom_canvas, 100, 100)
        box.lock_box()
        self.assertTrue(box.locked)

        box.unlock_box()
        self.assertFalse(box.locked)

    def test__select__turns_rect_outline_select_color(self):
        box = Box(self.custom_canvas, 100, 100)

        expected_start_color = const.BLACK
        actual_start_color = self.custom_canvas.itemconfig(box.shape)["outline"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

        box.select()
        expected_selected_color = const.SELECT_COLOR
        actual_selected_color = self.custom_canvas.itemconfig(box.shape)["outline"][-1]
        self.assertEqual(expected_selected_color, actual_selected_color)

    def test__deselect__turns_rect_outline_black(self):
        box = Box(self.custom_canvas, 100, 100)

        box.select()
        expected_selected_color = const.SELECT_COLOR
        actual_selected_color = self.custom_canvas.itemconfig(box.shape)["outline"][-1]
        self.assertEqual(expected_selected_color, actual_selected_color)

        box.deselect()
        expected_start_color = const.BLACK
        actual_start_color = self.custom_canvas.itemconfig(box.shape)["outline"][-1]
        self.assertEqual(expected_start_color, actual_start_color)

    def test__move__updates_x_y(self):
        box = Box(self.custom_canvas, 100, 100)
        self.assertEqual((100, 100), (box.x, box.y))

        expected_x = 500
        expected_y = 600
        box.move(expected_x, expected_y)
        self.assertEqual((expected_x, expected_y), (box.x, box.y))

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_position")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_connections")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_wires")
    def test__move__calls_out_methods(self, update_wires_mock, update_connections_mock, update_position_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.move(100, 100)

        self.assertTrue(update_wires_mock.called)
        self.assertTrue(update_connections_mock.called)
        self.assertTrue(update_position_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.is_illegal_move")
    def test__move__checks_for_illegal_move_when_connections_with_wire_exist(self, is_illegal_move_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.add_left_connection()
        box.connections[0].has_wire = True

        box.move(100, 100)
        self.assertTrue(is_illegal_move_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.is_illegal_move", return_value=True)
    def test__move__if_illegal_doesnt_change_x(self, is_illegal_move_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.add_left_connection()
        box.connections[0].has_wire = True

        box.move(500, 600)
        self.assertTrue(is_illegal_move_mock.called)
        self.assertEqual(100, box.x)
        self.assertEqual(600, box.y)

    @patch("tkinter.simpledialog.askstring", return_value="1")
    def test__set_inputs_outputs__asks_user_for_input(self, ask_string_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.set_inputs_outputs()

        self.assertTrue(ask_string_mock.called)
        self.assertEqual(2, len(box.connections))

    @patch("tkinter.simpledialog.askstring", return_value="2")
    def test__set_inputs_outputs__removes_outputs_if_needed(self, ask_string_mock):
        box = Box(self.custom_canvas, 100, 100)
        for i in range(3):
            box.add_left_connection()
            box.add_right_connection()

        self.assertEqual(6, len(box.connections))
        self.assertEqual(3, box.left_connections)
        self.assertEqual(3, box.right_connections)

        box.set_inputs_outputs()

        self.assertEqual(2, ask_string_mock.call_count)
        self.assertEqual(4, len(box.connections))
        self.assertEqual(2, box.left_connections)
        self.assertEqual(2, box.right_connections)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.bind_event_label")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_label")
    def test__edit_label__with_param_changes_label(self, update_label_mock, bind_mock):
        box = Box(self.custom_canvas, 100, 100)
        bind_mock.call_count = 0  # resetting tag_bind amount from box creation

        expected_label = "new_label"
        box.edit_label(expected_label)

        self.assertEqual(expected_label, box.label_text)
        self.assertTrue(update_label_mock.called)
        self.assertTrue(bind_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.bind_event_label")
    @patch("tkinter.simpledialog.askstring", return_value="new_label")
    def test__edit_label__without_param_asks_input(self, ask_string_mock, bind_mock):
        box = Box(self.custom_canvas, 100, 100)
        bind_mock.call_count = 0
        box.edit_label()

        expected_label = "new_label"
        self.assertTrue(ask_string_mock.called)
        self.assertEqual(expected_label, box.label_text)
        self.assertTrue(bind_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.bind_event_label")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.update_io")
    @patch("tkinter.messagebox.askokcancel", return_value=True)
    @patch("json.load", return_value={"new_label": ""})
    @patch("tkinter.simpledialog.askstring", return_value="new_label")
    @patch("os.stat")
    def test__edit_label__without_param_checks_existing_and_updates(self,
                                                                    os_stat_mock,
                                                                    ask_string_mock,
                                                                    json_load_mock,
                                                                    ask_ok_cancel_mock,
                                                                    update_io_mock,
                                                                    bind_event_mock):
        box = Box(self.custom_canvas, 100, 100)
        bind_event_mock.call_count = 0
        os_stat_mock.return_value.st_size = 1
        box.edit_label()

        self.assertTrue(ask_string_mock.called)
        expected_label = "new_label"
        self.assertEqual(expected_label, box.label_text)
        self.assertTrue(os_stat_mock.called)
        self.assertTrue(json_load_mock.called)
        self.assertTrue(ask_ok_cancel_mock.called)
        self.assertTrue(update_io_mock.called)
        self.assertTrue(bind_event_mock.called)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    def test__bind_events__calls_tag_bind(self, tag_bind_mock):
        box = Box(self.custom_canvas, 100, 100)
        tag_bind_mock.call_count = 0
        box.bind_events()
        self.assertEqual(11, tag_bind_mock.call_count)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    def test__bind_event_label__calls_out_tag_bind(self, tag_bind_mock):
        box = Box(self.custom_canvas, 100, 100)
        tag_bind_mock.call_count = 0
        box.bind_event_label()

        self.assertEqual(7, tag_bind_mock.call_count)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.bind_events")
    def test__init__calls_bind_event(self, bind_events_mock):
        box = Box(self.custom_canvas, 100, 100)
        self.assertTrue(bind_events_mock.called)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.add_cascade")
    @patch("tkinter.Menu.entryconfig")
    @patch("tkinter.Menu.add_separator")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.close_menu")
    def test__show_context_menu__default_box(self,
                                             close_menu_mock,
                                             tk_popup_mock,
                                             add_separator_mock,
                                             entry_config_mock,
                                             add_cascade_mock,
                                             add_command_mock):
        box = Box(self.custom_canvas, 100, 100)
        event = tkinter.Event()
        event.x_root, event.y_root = 100, 100
        box.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(12, add_command_mock.call_count)
        self.assertEqual(1, entry_config_mock.call_count)
        self.assertEqual(1, add_separator_mock.call_count)
        self.assertEqual(1, add_cascade_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.add_cascade")
    @patch("tkinter.Menu.entryconfig")
    @patch("tkinter.Menu.add_separator")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.close_menu")
    def test__show_context_menu__default_box_with_connections(self,
                                                              close_menu_mock,
                                                              tk_popup_mock,
                                                              add_separator_mock,
                                                              entry_config_mock,
                                                              add_cascade_mock,
                                                              add_command_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.add_left_connection()
        box.add_right_connection()
        event = tkinter.Event()
        event.x_root, event.y_root = 100, 100
        box.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(14, add_command_mock.call_count)
        self.assertEqual(1, entry_config_mock.call_count)
        self.assertEqual(1, add_separator_mock.call_count)
        self.assertEqual(1, add_cascade_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.add_cascade")
    @patch("tkinter.Menu.entryconfig")
    @patch("tkinter.Menu.add_separator")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.close_menu")
    def test__show_context_menu__locked_box(self,
                                            close_menu_mock,
                                            tk_popup_mock,
                                            add_separator_mock,
                                            entry_config_mock,
                                            add_cascade_mock,
                                            add_command_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.lock_box()
        event = tkinter.Event()
        event.x_root, event.y_root = 100, 100
        box.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(5, add_command_mock.call_count)
        self.assertEqual(1, entry_config_mock.call_count)
        self.assertEqual(1, add_separator_mock.call_count)
        self.assertEqual(0, add_cascade_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.add_cascade")
    @patch("tkinter.Menu.entryconfig")
    @patch("tkinter.Menu.add_separator")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.close_menu")
    def test__show_context_menu__sub_diagram_box_not_locked(self,
                                                            close_menu_mock,
                                                            tk_popup_mock,
                                                            add_separator_mock,
                                                            entry_config_mock,
                                                            add_cascade_mock,
                                                            add_command_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.sub_diagram = True
        event = tkinter.Event()
        event.x_root, event.y_root = 100, 100
        box.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(7, add_command_mock.call_count)
        self.assertEqual(0, entry_config_mock.call_count)
        self.assertEqual(1, add_separator_mock.call_count)
        self.assertEqual(0, add_cascade_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.add_cascade")
    @patch("tkinter.Menu.entryconfig")
    @patch("tkinter.Menu.add_separator")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.box.Box.close_menu")
    def test__show_context_menu__locked_sub_diagram(self,
                                                    close_menu_mock,
                                                    tk_popup_mock,
                                                    add_separator_mock,
                                                    entry_config_mock,
                                                    add_cascade_mock,
                                                    add_command_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.sub_diagram = True
        box.lock_box()
        event = tkinter.Event()
        event.x_root, event.y_root = 100, 100
        box.show_context_menu(event)

        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(4, add_command_mock.call_count)
        self.assertEqual(0, entry_config_mock.call_count)
        self.assertEqual(1, add_separator_mock.call_count)
        self.assertEqual(0, add_cascade_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)

    @patch("MVP.refactored.frontend.windows.code_editor.CodeEditor.__init__", return_value=None)
    def test__open_editor__creates_editor(self, init_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.open_editor()

        self.assertTrue(init_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.select")
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.canvasx", return_value=300)
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.canvasy", return_value=300)
    def test__on_press__callouts(self, canvas_y_mock, canvas_x_mock, select_mock):
        box = Box(self.custom_canvas, 100, 100)
        event = tkinter.Event()
        event.x = 300
        event.y = 300
        box.on_press(event)
        self.assertTrue(canvas_x_mock.called)
        self.assertTrue(canvas_y_mock.called)
        self.assertTrue(select_mock.called)

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.canvasx", return_value=300)
    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.canvasy", return_value=400)
    def test__on_press__variable_changes(self, canvas_y_mock, canvas_x_mock):
        box = Box(self.custom_canvas, 100, 100)
        box.x = 100
        box.y = 100
        event = tkinter.Event()
        event.x = 300
        event.y = 400
        box.on_press(event)

        self.assertTrue(canvas_x_mock.called)
        self.assertTrue(canvas_y_mock.called)

        self.assertEqual(300, box.start_x)
        self.assertEqual(400, box.start_y)

        self.assertEqual(300 - 100, box.x_dif)
        self.assertEqual(400 - 100, box.y_dif)

    def test__on_drag__no_other_items_changes_location(self):
        box = Box(self.custom_canvas, 100, 100)
        event = tkinter.Event()
        event.state = False
        event.x = 150
        event.y = 150

        box.on_press(event)
        box.on_drag(event)

        event.x = 200
        event.y = 200

        box.on_drag(event)

        self.assertEqual(150, box.x)
        self.assertEqual(150, box.y)

    def test__on_drag__box_above(self):
        self.custom_canvas.add_box(size=(50, 50))
        self.custom_canvas.add_box(loc=(100, 200), size=(50, 50))

        box_2 = self.custom_canvas.boxes[1]

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 225, 225

        box_2.on_press(event)

        for _ in range(100):
            event.y -= 1
            box_2.on_drag(event)

        self.assertEqual(100, box_2.x)  # Should not have changed
        self.assertEqual(151, box_2.y)  # Box 1 ends at 150 so this should be 151

    def test__on_drag__box_below(self):
        self.custom_canvas.add_box(size=(50, 50))
        self.custom_canvas.add_box(loc=(100, 200), size=(50, 50))

        box_1 = self.custom_canvas.boxes[0]

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 125, 125

        box_1.on_press(event)

        for _ in range(100):
            event.y += 1
            box_1.on_drag(event)

        self.assertEqual(100, box_1.x)  # Should not have changed
        self.assertEqual(149, box_1.y)  # Box 2 starts at 200 so this should be 149

    def test__on_drag__box_right_should_snap_to_same_x(self):
        self.custom_canvas.add_box(size=(50, 50))
        self.custom_canvas.add_box(loc=(200, 100), size=(50, 50))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 125, 125

        box_1 = self.custom_canvas.boxes[0]

        box_1.on_press(event)

        for _ in range(51):
            event.x += 1
            box_1.on_drag(event)

        self.assertEqual(200, box_1.x)  # Should match the 2nd box x coords

    def test__on_drag__spider_snap(self):
        self.custom_canvas.add_box(size=(50, 50))
        self.custom_canvas.add_spider(loc=(200, 125))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 125, 125

        box_1 = self.custom_canvas.boxes[0]

        box_1.on_press(event)

        for _ in range(50):
            event.x += 1
            box_1.on_drag(event)

        expected_x = 200 - box_1.size[0] / 2
        self.assertEqual(expected_x, box_1.x)

    def test__on_drag__spider_below(self):
        self.custom_canvas.add_box(size=(50, 50))
        self.custom_canvas.add_spider(loc=(125, 175))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 125, 125

        box_1 = self.custom_canvas.boxes[0]

        box_1.on_press(event)

        for _ in range(50):
            event.y += 1
            box_1.on_drag(event)

        expected_y = 175 - 10 - 50 - 1  # Spider.y - spider.size - box.size - gap
        self.assertEqual(expected_y, box_1.y)

    def test__on_drag__spider_above(self):
        self.custom_canvas.add_box(loc=(100, 150), size=(50, 50))
        self.custom_canvas.add_spider(loc=(125, 100))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 125, 175

        box_1 = self.custom_canvas.boxes[0]

        box_1.on_press(event)

        for _ in range(50):
            event.y -= 1
            box_1.on_drag(event)

        self.assertEqual(111, box_1.y)

    @patch("MVP.refactored.frontend.canvas_objects.box.Box.move_label")
    def test__on_resize_drag__updates_size_same_coords(self, move_label_mock):
        box = Box(self.custom_canvas, 100, 100)

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 155, 155

        box.on_press(event)

        for _ in range(50):
            event.x += 1
            event.y += 1
            box.on_resize_drag(event)

        self.assertEqual((110, 110), box.size)
        self.assertEqual(50, move_label_mock.call_count)
