import tkinter
import unittest

from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.windows.main_diagram import MainDiagram


class TestMainDiagram(unittest.TestCase):

    async def _start_app(self):
        self.app.mainloop()

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self._start_app()

    def tearDown(self):
        self.app.destroy()


class Test(TestMainDiagram):

    def test__init_title(self):
        expected = "Dynamic String Diagram Canvas"
        actual = self.app.title()
        self.assertEqual(expected, actual)

    def test__init_tree_hidden(self):
        actual = self.app.is_tree_visible
        self.assertFalse(actual)

    def test__init_creates_1_custom_canvas(self):
        expected_size = 1
        actual_size = len(self.app.canvasses)
        self.assertEqual(expected_size, actual_size)

    def test__init_adds_custom_canvas_to_canvases(self):
        expected_key = self.app.custom_canvas.id
        expected_value = self.app.custom_canvas
        actual_item = list(self.app.canvasses.items())[0]
        actual_key = int(actual_item[0])
        actual_value = actual_item[1]
        self.assertEqual(expected_key, actual_key)
        self.assertEqual(expected_value, actual_value)

    def test__add_input__adds_input(self):
        self.app.add_diagram_input()
        expected = 1
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not added correctly")

    def test__add_input__adds_input_2(self):
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        expected = 2
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not added correctly")

    def test__remove_input__removes_input(self):
        self.app.add_diagram_input()
        self.app.remove_diagram_input()
        expected = 0
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not removed correctly")

    def test__remove_input__removes_input_2(self):
        self.app.add_diagram_input()
        self.app.add_diagram_input()
        self.app.remove_diagram_input()
        expected = 1
        actual = len(self.app.custom_canvas.inputs)
        self.assertEqual(expected, actual, "Inputs are not removed correctly")

    def test__add_output__adds_output(self):
        self.app.add_diagram_output()
        expected = 1
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not added correctly")

    def test__add_output__adds_output_2(self):
        self.app.add_diagram_output()
        self.app.add_diagram_output()
        expected = 2
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not added correctly")

    def test__remove_output__removes_output(self):
        self.app.add_diagram_output()
        self.app.add_diagram_input()
        self.app.remove_diagram_output()
        expected = 0
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not removed correctly")

    def test__remove_output__removes_output_2(self):
        self.app.add_diagram_output()
        self.app.add_diagram_output()
        self.app.remove_diagram_output()
        expected = 1
        actual = len(self.app.custom_canvas.outputs)
        self.assertEqual(expected, actual, "Outputs are not removed correctly")

    def test__toggle_tree_view__changes_boolean(self):
        actual = self.app.is_tree_visible
        self.assertFalse(actual)
        self.app.toggle_treeview()
        actual = self.app.is_tree_visible
        self.assertTrue(actual)

    def test__copy_to_clipboard__copies_text_from_text_box(self):
        text = tkinter.Text()
        expected = "Lorem ipsum"
        text.insert(tkinter.END, expected)
        self.app.copy_to_clipboard(text)
        actual = self.app.clipboard_get().strip()
        self.assertEqual(expected, actual)

    def test__del_from_canvasses__removes_dict_entry(self):
        self.app.del_from_canvasses(self.app.canvasses[str(self.app.custom_canvas.id)])
        expected = 0
        actual = len(self.app.canvasses)
        self.assertEqual(expected, actual)

    def test__add_canvas__adds_new_canvas_to_canvasses_and_tree(self):
        new_canvas = CustomCanvas(self.app, self.app, id_=1)
        self.app.add_canvas(new_canvas)

        expected_size = 2
        actual_size = len(self.app.canvasses)
        self.assertEqual(expected_size, actual_size)

        new_canvas_id = 1
        self.assertTrue(self.app.canvasses[str(new_canvas_id)] == new_canvas)

    def test__switch_canvas__changes_custom_canvas(self):
        new_canvas = CustomCanvas(self.app, self.app, id_=1)
        self.app.add_canvas(new_canvas)
        self.app.switch_canvas(new_canvas)

        self.assertEqual(new_canvas, self.app.custom_canvas)
