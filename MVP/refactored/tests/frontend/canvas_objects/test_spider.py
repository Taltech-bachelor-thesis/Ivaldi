import tkinter
import unittest
from unittest.mock import patch

import constants as const
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.types.connection_type import ConnectionType
from MVP.refactored.frontend.canvas_objects.wire import Wire
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


class SpiderTests(TestMainDiagram):

    def test__init__values(self):
        spider = Spider((100, 150), self.custom_canvas)

        self.assertEqual(self.custom_canvas, spider.canvas)
        self.assertEqual(100, spider.x)
        self.assertEqual(150, spider.y)
        self.assertEqual(10, spider.r)
        self.assertEqual((100, 150), spider.location)

        self.assertTrue(isinstance(spider.connections, list))
        self.assertListEqual([], spider.wires)
        self.assertEqual(ConnectionType.GENERIC, spider.type)
        self.assertFalse(spider.is_snapped)

    def test__is_spider__returns_true(self):
        spider = Spider((100, 150), self.custom_canvas)

        self.assertTrue(spider.is_spider())

    @patch("MVP.refactored.frontend.components.custom_canvas.CustomCanvas.tag_bind")
    def test__bind_events__callouts(self, tag_bind_mock):
        spider = Spider((100, 150), self.custom_canvas)
        tag_bind_mock.call_count = 0

        spider.bind_events()

        self.assertEqual(7, tag_bind_mock.call_count)

    @patch("MVP.refactored.frontend.canvas_objects.spider.Spider.add_type_choice")
    @patch("tkinter.Menu.add_command")
    @patch("tkinter.Menu.tk_popup")
    @patch("MVP.refactored.frontend.canvas_objects.spider.Spider.close_menu")
    def test__show_context_menu__callouts(self, close_menu_mock, tk_popup_mock, add_command_mock, type_choice_mock):
        spider = Spider((100, 150), self.custom_canvas)
        event = tkinter.Event()
        event.x_root = 100
        event.y_root = 150

        spider.show_context_menu(event)

        self.assertTrue(type_choice_mock.called)
        self.assertEqual(1, close_menu_mock.call_count)
        self.assertEqual(1, tk_popup_mock.call_count)
        self.assertEqual(2, add_command_mock.call_count)

    @patch("MVP.refactored.backend.diagram_callback.Receiver.receiver_callback")
    def test__delete__calls_receiver_if_sub_diagram(self, receiver_mock):
        spider = Spider((100, 150), self.custom_canvas)
        self.custom_canvas.spiders.append(spider)

        spider.delete(action="sub_diagram")

        self.assertTrue(receiver_mock.called)

    @patch("MVP.refactored.frontend.canvas_objects.spider.Spider.delete")
    def test__delete__calls_delete_function(self, delete_mock):
        spider = Spider((100, 150), self.custom_canvas)
        self.custom_canvas.spiders.append(spider)

        spider.delete()
        self.assertTrue(delete_mock.called)

    def test__delete__removes_spider_from_canvas_list(self):
        spider = Spider((100, 150), self.custom_canvas)
        self.custom_canvas.spiders.append(spider)

        spider.delete()

        self.assertFalse(self.custom_canvas.spiders)

    @patch("tkinter.Menu.destroy")
    def test__close_menu__doesnt_close_if_no_menu(self, destroy_mock):
        spider = Spider((100, 150), self.custom_canvas)
        spider.context_menu = None
        spider.close_menu()
        self.assertFalse(destroy_mock.called)

    @patch("tkinter.Menu.destroy")
    def test__close_menu__closes_if_menu(self, destroy_mock):
        spider = Spider((100, 150), self.custom_canvas)
        spider.context_menu = tkinter.Menu()
        spider.close_menu()
        self.assertTrue(destroy_mock.called)

    def test__add_wire__adds_wire(self):
        spider = Spider((100, 150), self.custom_canvas)
        wire1 = Wire(self.custom_canvas, None, None, is_temporary=True)
        wire2 = Wire(self.custom_canvas, None, None, is_temporary=True)
        wire3 = Wire(self.custom_canvas, None, None, is_temporary=True)

        spider.add_wire(wire1)
        spider.add_wire(wire2)
        spider.add_wire(wire3)

        self.assertEqual([wire1, wire2, wire3], spider.wires)

    def test__add_wire__doesnt_add_wire_if_wire_in_spider_already(self):
        spider = Spider((100, 150), self.custom_canvas)
        wire1 = Wire(self.custom_canvas, None, None, is_temporary=True)

        spider.add_wire(wire1)
        spider.add_wire(wire1)

        self.assertEqual([wire1], spider.wires)

    def test__on_press__clears_all_selections(self):
        spider = Spider((100, 150), self.custom_canvas)
        random_item = Box(self.custom_canvas, 100, 100)
        self.custom_canvas.selector.selected_items.append(random_item)
        self.custom_canvas.selector.selected_boxes.append(random_item)
        self.custom_canvas.selector.selected_wires.append(random_item)
        self.custom_canvas.selector.selected_spiders.append(random_item)

        spider.on_press()

        self.assertTrue(spider in self.custom_canvas.selector.selected_items)
        self.assertFalse(self.custom_canvas.selector.selected_spiders)
        self.assertFalse(self.custom_canvas.selector.selected_boxes)
        self.assertFalse(self.custom_canvas.selector.selected_wires)

    def test__on_press__does_not_select_self_if_drawing_wire(self):
        spider = Spider((100, 150), self.custom_canvas)

        random_item = Box(self.custom_canvas, 100, 100)
        self.custom_canvas.selector.selected_items.append(random_item)
        self.custom_canvas.selector.selected_boxes.append(random_item)
        self.custom_canvas.selector.selected_wires.append(random_item)
        self.custom_canvas.selector.selected_spiders.append(random_item)
        self.custom_canvas.draw_wire_mode = True

        spider.on_press()

        self.assertFalse(self.custom_canvas.selector.selected_items)

    @patch("MVP.refactored.frontend.canvas_objects.spider.Spider.select")
    def test__on_control_press__selects_self(self, select_mock):
        spider = Spider((100, 150), self.custom_canvas)

        spider.on_control_press()

        self.assertTrue(spider in self.custom_canvas.selector.selected_items)
        self.assertTrue(select_mock.called)

    def test__on_control_press__deselects_self_if_selected(self):
        spider = Spider((100, 150), self.custom_canvas)

        self.custom_canvas.selector.selected_items.append(spider)

        spider.on_control_press()

        self.assertFalse(self.custom_canvas.selector.selected_items)

    def test__on_control_press__selects_wires_between(self):
        spider1 = Spider((100, 150), self.custom_canvas)
        spider2 = Spider((200, 150), self.custom_canvas)

        self.custom_canvas.start_wire_from_connection(spider1)
        self.custom_canvas.end_wire_to_connection(spider2)

        spider1.on_control_press()
        spider2.on_control_press()

        self.assertEqual(3, len(self.custom_canvas.selector.selected_items))

    def test__on_drag__no_other_items_changes_location(self):
        spider = Spider((100, 150), self.custom_canvas)
        event = tkinter.Event()
        event.state = False
        event.x = 100
        event.y = 150

        spider.on_drag(event)

        event.x = 200
        event.y = 250

        spider.on_drag(event)

        self.assertEqual(200, spider.x)
        self.assertEqual(250, spider.y)

    def test__on_drag__box_above(self):
        self.custom_canvas.add_box()
        self.custom_canvas.add_spider(loc=(130, 200))

        spider = self.custom_canvas.spiders[0]

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 130, 200

        for _ in range(100):
            event.y -= 1
            spider.on_drag(event)

        self.assertEqual(130, spider.x)  # Should not have changed
        self.assertEqual(171, spider.y)  # Box 1 ends at 160 so this should be 171 (radius 10 and gap 1)

    def test__on_drag__box_below(self):
        self.custom_canvas.add_spider(loc=(130, 100))
        self.custom_canvas.add_box(loc=(100, 200))

        spider = self.custom_canvas.spiders[0]

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 100, 100

        for _ in range(100):
            event.y += 1
            spider.on_drag(event)

        self.assertEqual(130, spider.x)  # Should not have changed
        self.assertEqual(189, spider.y)  # Box 2 starts at 200 so this should be 189 (radius 10 and gap 1)

    def test__on_drag__box_right_should_snap_to_box_middle(self):
        self.custom_canvas.add_spider()
        self.custom_canvas.add_box(loc=(200, 100), size=(50, 50))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 100, 100

        spider = self.custom_canvas.spiders[0]

        for _ in range(100):
            event.x += 1
            spider.on_drag(event)

        box = self.custom_canvas.boxes[0]
        expected = box.x + box.size[0] / 2
        self.assertEqual(expected, spider.x)

    def test__on_drag__spider_snap_to_same_x(self):
        self.custom_canvas.add_spider()
        self.custom_canvas.add_spider(loc=(200, 100))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 100, 100

        spider = self.custom_canvas.spiders[0]

        for _ in range(90):
            event.x += 1
            spider.on_drag(event)

        self.assertEqual(200, spider.x)

    def test__on_drag__spider_below(self):
        self.custom_canvas.add_spider()
        self.custom_canvas.add_spider(loc=(100, 175))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 100, 100

        spider = self.custom_canvas.spiders[0]

        for _ in range(70):
            event.y += 1
            spider.on_drag(event)

        expected_y = 175 - 10 - 10 - 1  # spider2.y - spider2.r - spider1.r - gap
        self.assertEqual(expected_y, spider.y)

    def test__on_drag__spider_above(self):
        self.custom_canvas.add_spider(loc=(100, 150))
        self.custom_canvas.add_spider(loc=(100, 100))

        event = tkinter.Event()
        event.state = False
        event.x, event.y = 100, 150

        spider = self.custom_canvas.spiders[0]

        for _ in range(40):
            event.y -= 1
            spider.on_drag(event)

        expected = 100 + 10 + 10 + 1  # other spider location + spider.r + spider.r + gap
        self.assertEqual(expected, spider.y)

    def test__on_drag__doesnt_change_loc_if_pulling_wire(self):
        spider = Spider((100, 150), self.custom_canvas)
        self.custom_canvas.pulling_wire = True
        event = tkinter.Event()
        event.state = False
        event.x = 100
        event.y = 150

        spider.on_drag(event)

        event.x = 200
        event.y = 250

        spider.on_drag(event)

        self.assertEqual(100, spider.x)
        self.assertEqual(150, spider.y)

    def test__remove_wire__removes_wire(self):
        spider = Spider((100, 150), self.custom_canvas)
        wire = Wire(self.custom_canvas, None, None, is_temporary=True)

        spider.add_wire(wire)

        self.assertTrue(wire in spider.wires)

        spider.remove_wire(wire)

        self.assertTrue(wire not in spider.wires)

    def test__is_illegal_move__can_be_next_to_connected_connection(self):
        spider = Spider((100, 100), self.custom_canvas)
        spider2 = Spider((150, 100), self.custom_canvas)
        wire = Wire(self.custom_canvas, spider, spider2, is_temporary=True)

        spider.add_wire(wire)
        spider2.add_wire(wire)

        self.assertFalse(spider.is_illegal_move(125))

    def test__is_illegal_move__cant_be_same_x_with_connected_spider(self):
        spider = Spider((100, 100), self.custom_canvas)
        spider2 = Spider((150, 100), self.custom_canvas)
        wire = Wire(self.custom_canvas, spider, spider2, is_temporary=True)

        spider.add_wire(wire)
        spider2.add_wire(wire)

        self.assertTrue(spider.is_illegal_move(145))
        self.assertTrue(spider.is_illegal_move(150))
        self.assertTrue(spider.is_illegal_move(155))

    def test__is_illegal_move__cant_go_from_left_to_right_with_connected_connection(self):
        spider = Spider((100, 100), self.custom_canvas)
        connection = Connection(None, 1, "left", (150, 150), self.custom_canvas)
        wire = Wire(self.custom_canvas, spider, connection, is_temporary=True)

        spider.add_wire(wire)

        x = 140
        for _ in range(20):
            x += 10
            self.assertTrue(spider.is_illegal_move(x))

    def test__is_illegal_move__cant_go_from_right_to_left_with_connected_connection(self):
        spider = Spider((150, 150), self.custom_canvas)
        connection = Connection(None, 1, "right", (100, 100), self.custom_canvas)
        wire = Wire(self.custom_canvas, spider, connection, is_temporary=True)

        spider.add_wire(wire)

        x = 110
        for _ in range(20):
            x -= 10
            self.assertTrue(spider.is_illegal_move(x))


