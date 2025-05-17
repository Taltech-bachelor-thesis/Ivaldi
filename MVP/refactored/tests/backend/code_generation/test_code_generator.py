from unittest import TestCase

from MVP.refactored.backend.code_generation.code_generator import CodeGenerator
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.wire import Wire
from MVP.refactored.frontend.windows.main_diagram import MainDiagram

class TestCodeGenerator(TestCase):

    def setUp(self):
        self.app = MainDiagram(Receiver())
        self.receiver = self.app.receiver
        self.custom_canvas = self.app.custom_canvas

        # Create boxes
        box_a = self.custom_canvas.add_box(Box(self.custom_canvas, 241, 444, self.receiver))
        box_b = self.custom_canvas.add_box(Box(self.custom_canvas, 241, 166, self.receiver))
        box_c = self.custom_canvas.add_box(Box(self.custom_canvas, 457, 306, self.receiver))
        box_d = self.custom_canvas.add_box(Box(self.custom_canvas, 787, 302, self.receiver))

        # Create inputs and outputs
        in1 = self.custom_canvas.add_diagram_input()
        in2 = self.custom_canvas.add_diagram_input()
        in3 = self.custom_canvas.add_diagram_input()
        in4 = self.custom_canvas.add_diagram_input()
        out1 = self.custom_canvas.add_diagram_output()
        out2 = self.custom_canvas.add_diagram_output()

        # Add connections to boxes
        a_in1 = box_a.add_left_connection()
        a_in2 = box_a.add_left_connection()
        a_out = box_a.add_right_connection()
        b_in1 = box_b.add_left_connection()
        b_in2 = box_b.add_left_connection()
        b_out = box_b.add_right_connection()
        c_in1 = box_c.add_left_connection()
        c_in2 = box_c.add_left_connection()
        c_out = box_c.add_right_connection()
        d_in = box_d.add_left_connection()
        d_out1 = box_d.add_right_connection()
        d_out2 = box_d.add_right_connection()

        # Wire everything up
        self.custom_canvas.add_wire(Wire(self.custom_canvas, in1, self.receiver, a_in1))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, in2, self.receiver, a_in2))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, in3, self.receiver, b_in1))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, in4, self.receiver, b_in2))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, a_out, self.receiver, c_in1))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, b_out, self.receiver, c_in2))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, c_out, self.receiver, d_in))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, d_out1, self.receiver, out1))
        self.custom_canvas.add_wire(Wire(self.custom_canvas, d_out2, self.receiver, out2))

        # Assign predefined functions
        box_a.set_predefined_function("add")
        box_b.set_predefined_function("add")
        box_c.set_predefined_function("subtract")
        box_d.set_predefined_function("copy")

    def tearDown(self):
        self.app.destroy()

    def test_construct_main_function(self):
        code = CodeGenerator.generate_code(self.custom_canvas)
        print(code)
        self.assertIn("def main", code)
