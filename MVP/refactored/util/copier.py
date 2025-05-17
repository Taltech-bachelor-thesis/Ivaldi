class Copier:

    def copy_canvas_contents(self, canvas, wires, boxes, spiders, selected_coordinates, box):
        self.copy_over_boxes(boxes, canvas)
        self.copy_over_spiders(spiders, canvas)
        self.copy_over_wires(wires, selected_coordinates, box, canvas)

    @staticmethod
    def copy_over_spiders(spiders, canvas):
        for spider in spiders:
            new_spider = canvas.add_spider(spider.location, connection_type=spider.type, id_=spider.id)

    @staticmethod
    def copy_over_boxes(boxes, canvas):
        for old_box in boxes:
            sub_diagram_box = canvas.add_box(loc=(old_box.x, old_box.y), size=old_box.size, style=old_box.style)
            sub_diagram_box.set_id(old_box.id)
            Copier.copy_box(old_box, sub_diagram_box)
            sub_diagram_box.sub_diagram = old_box.sub_diagram
            if sub_diagram_box.sub_diagram:
                canvas.itemconfig(sub_diagram_box.shape, fill="#dfecf2")

            sub_diagram_box.locked = old_box.locked

    @staticmethod
    def add_diagram_io_based_on_spider(selected_coordinates, box, other_c):
        if other_c.location[0] < selected_coordinates[0]:
            box.sub_diagram.add_diagram_input_for_sub_d_wire()
            return True
        if other_c.location[0] > selected_coordinates[2]:
            box.sub_diagram.add_diagram_output_for_sub_d_wire()
            return False

    def sort_wires_by_y(self, wires, selected_coordinates):
        # Find if wire is fully in the selected area or if only start/end is in
        half_in = []
        full_in = []
        for wire in wires:
            status = self.get_wire_select_status(wire, selected_coordinates)
            if status == "FULL_IN":
                full_in.append(wire)
            if status == "START_IN":
                half_in.append((wire.start_connection, wire))
            if status == "END_IN":
                half_in.append((wire.end_connection, wire))
        half_in = sorted(half_in, key=lambda x: x[0].location[1], reverse=False)
        return half_in, full_in

    def copy_over_wires(self, wires, selected_coordinates, box, canvas):
        add_diagram_io_based_on_side = {
            "left": box.sub_diagram.add_diagram_input_for_sub_d_wire,
            "right": box.sub_diagram.add_diagram_output_for_sub_d_wire,
        }
        half_in, full_in = self.sort_wires_by_y(wires, selected_coordinates)
        for wire in full_in:
            start_c = wire.start_connection
            end_c = wire.end_connection
            # wire start is a box
            # Find wire start box with filter and loop through connections to find the correct one
            self.copy_wire_within_selection(start_c, end_c, canvas)

            # Add wires with start connection in the selected are and end connection outside
        for wire in half_in:
            wire = wire[1]
            start_c = wire.start_connection
            end_c = wire.end_connection
            status = self.get_wire_select_status(wire, selected_coordinates)
            if status == "START_IN":
                if start_c.side == "spider":
                    side_bool = self.add_diagram_io_based_on_spider(selected_coordinates, box, end_c)
                    for spider in canvas.spiders:
                        if start_c.is_spider() and spider.id == start_c.id:
                            self.create_inner_and_outer_wire(spider, box, end_c, canvas, side_bool)
                            break
                else:
                    add_diagram_io_based_on_side.get(start_c.side)()
                    for con in (list(filter(lambda x: (start_c.box and x.id == start_c.box.id),
                                            canvas.boxes))[0].connections):
                        if con.side == start_c.side and con.index == start_c.index:
                            if con.side == "left":
                                self.create_inner_and_outer_wire(con, box, end_c, canvas, True)
                            else:
                                self.create_inner_and_outer_wire(con, box, end_c, canvas)
            if status == "END_IN":
                # Add wires with end connection in the selected are and start connection outside
                start_c = wire.start_connection
                end_c = wire.end_connection
                if end_c.side == "spider":
                    side_bool = self.add_diagram_io_based_on_spider(selected_coordinates, box, start_c)
                    for spider in canvas.spiders:
                        if end_c.is_spider() and spider.id == end_c.id:
                            self.create_inner_and_outer_wire(spider, box, start_c, canvas, side_bool)

                else:
                    add_diagram_io_based_on_side.get(end_c.side)()
                    for con in list(filter(lambda x: (end_c.box and x.id == end_c.box.id),
                                           canvas.boxes))[0].connections:
                        if con.side == end_c.side and con.index == end_c.index:
                            if con.side == "left":
                                self.create_inner_and_outer_wire(con, box, start_c, canvas, True)
                            else:
                                self.create_inner_and_outer_wire(con, box, start_c, canvas)

    @staticmethod
    def get_wire_select_status(wire, selected_coordinates):
        start_coordinates = wire.start_connection.location
        end_coordinates = wire.end_connection.location
        x1, y1 = start_coordinates
        x2, y2 = end_coordinates
        if selected_coordinates[0] <= x1 <= selected_coordinates[2] and selected_coordinates[1] <= y1 <= \
                selected_coordinates[3] and selected_coordinates[0] <= x2 <= selected_coordinates[2] and \
                selected_coordinates[1] <= y2 <= selected_coordinates[3]:
            return "FULL_IN"

        # Add wires with start connection in the selected are and end connection outside
        if selected_coordinates[0] <= x1 <= selected_coordinates[2] and selected_coordinates[1] <= y1 <= \
                selected_coordinates[3] and not (selected_coordinates[0] <= x2 <= selected_coordinates[2] and
                                                 selected_coordinates[1] <= y2 <= selected_coordinates[3]):
            return "START_IN"

        # Add wires with end connection in the selected are and start connection outside
        if not (selected_coordinates[0] <= x1 <= selected_coordinates[2] and selected_coordinates[1] <= y1 <=
                selected_coordinates[3]) and selected_coordinates[0] <= x2 <= selected_coordinates[2] and \
                selected_coordinates[1] <= y2 <= selected_coordinates[3]:
            return "END_IN"

    @staticmethod
    def create_inner_and_outer_wire(con, box, pre_c, canvas, inputs=False):
        if inputs:
            lst = canvas.inputs
        else:
            lst = canvas.outputs
        i = list(filter(lambda x: (not x.has_wire), lst))[0]

        # add wire that goes to sub-diagram edge (IO)
        canvas.start_wire_from_connection(i)
        canvas.end_wire_to_connection(con, True)

        # add outer wire to box with sub-diagram
        for c in box.connections:
            if ((pre_c.side == "left" and c.side == "right" or
                 pre_c.side == "right" and c.side == "left" or pre_c.side == "spider") and not c.has_wire
                    and c.index == i.index):
                pre_c.remove_wire()

                box.canvas.start_wire_from_connection(c)
                box.canvas.end_wire_to_connection(pre_c, True)
                break

    @staticmethod
    def copy_box(old_box, new_box, remember_connections=True):
        for connection in old_box.connections:
            if connection.side == "right":
                new_connection = new_box.add_right_connection(connection_type=connection.type, id_=connection.id if remember_connections else None)
            if connection.side == "left":
                new_connection = new_box.add_left_connection(connection_type=connection.type, id_=connection.id if remember_connections else None)
        new_box.set_label(old_box.label_text)
        new_box.set_box_function(old_box.get_box_function())

    @staticmethod
    def copy_wire_within_selection(start_c, end_c, canvas):
        if list(filter(lambda x: (start_c.box and x.id == start_c.box.id), canvas.boxes)):
            for c in (list(filter(lambda x: (start_c.box and x.id == start_c.box.id),
                                  canvas.boxes))[0].connections):
                if c.side == start_c.side and c.index == start_c.index:
                    canvas.start_wire_from_connection(c)
                    break
        # wire start is a spider
        else:
            for spider in canvas.spiders:
                if start_c.is_spider() and start_c.id == spider.id:
                    canvas.start_wire_from_connection(spider)
                    break

        # the wire end is a box
        if list(filter(lambda x: (end_c.box and x.id == end_c.box.id), canvas.boxes)):
            for c in list(filter(lambda x: (end_c.box and x.id == end_c.box.id), canvas.boxes))[0].connections:
                if c.side == end_c.side and c.index == end_c.index:
                    canvas.end_wire_to_connection(c)
                    break
        # wire end is a spider
        else:
            for spider in canvas.spiders:
                if end_c.is_spider() and end_c.id == spider.id:
                    canvas.end_wire_to_connection(spider)
                    break
