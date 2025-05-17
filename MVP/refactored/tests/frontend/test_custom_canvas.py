import unittest
from unittest.mock import patch

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.windows.main_diagram import MainDiagram
import constants as const


class TestCustomCanvas(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.custom_canvas = self.app.custom_canvas
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class Tests(TestCustomCanvas):
    def test__init__no_objects_at_start(self):
        self.assertListEqual([], self.custom_canvas.boxes)
        self.assertListEqual([], self.custom_canvas.outputs)
        self.assertListEqual([], self.custom_canvas.inputs)
        self.assertListEqual([], self.custom_canvas.spiders)
        self.assertListEqual([], self.custom_canvas.wires)

    def test__init__other_values(self):
        self.assertIsNone(self.custom_canvas.temp_wire)
        self.assertIsNone(self.custom_canvas.temp_end_connection)
        self.assertFalse(self.custom_canvas.pulling_wire)
        self.assertFalse(self.custom_canvas.quick_pull)
        self.assertIsNone(self.custom_canvas.current_wire_start)
        self.assertFalse(self.custom_canvas.draw_wire_mode)
        self.assertIsNone(self.custom_canvas.select_box)
        self.assertFalse(self.custom_canvas.selecting)

    def test__init__default_box_shape(self):
        expected = const.RECTANGLE
        actual = self.custom_canvas.box_shape
        self.assertEqual(expected, actual)

    def test__init__zoom_values(self):
        expected_total_scale = 1.0
        expected_delta = 0.75
        expected_prev_scale = 1.0

        actual_total_scale = self.custom_canvas.total_scale
        actual_delta = self.custom_canvas.delta
        actual_prev_scale = self.custom_canvas.prev_scale

        self.assertEqual(expected_total_scale, actual_total_scale)
        self.assertEqual(expected_delta, actual_delta)
        self.assertEqual(expected_prev_scale, actual_prev_scale)

    def test__init__pan_value(self):
        expected_speed = 20

        actual_speed = self.custom_canvas.pan_speed
        self.assertEqual(expected_speed, actual_speed)

    def test__init__corners_at_canvas_edges(self):
        self.assertEqual(4, len(self.custom_canvas.corners))

        top_left = self.custom_canvas.corners[0]
        self.assertEqual(top_left.location,
                         [
                             0,
                             0
                         ])

        bottom_left = self.custom_canvas.corners[1]
        self.assertEqual(bottom_left.location,
                         [
                             0,
                             self.custom_canvas.canvasy(self.custom_canvas.winfo_height())
                         ])

        top_right = self.custom_canvas.corners[2]
        self.assertEqual(top_right.location,
                         [
                             self.custom_canvas.canvasx(self.custom_canvas.winfo_width()),
                             0
                         ])

        bottom_right = self.custom_canvas.corners[3]
        self.assertEqual(bottom_right.location,
                         [
                             self.custom_canvas.canvasx(self.custom_canvas.winfo_width()),
                             self.custom_canvas.canvasy(self.custom_canvas.winfo_height())
                         ])

    @patch('MVP.refactored.frontend.components.custom_canvas.CustomCanvas.on_canvas_click')
    def test__init__button_1_callout(self, mock):
        # Tried making other tests like this but for some reason they did not work
        self.custom_canvas.event_generate("<Button-1>")
        self.assertTrue(mock.called)

