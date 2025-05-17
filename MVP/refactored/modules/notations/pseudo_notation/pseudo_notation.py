import numpy as np

from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.modules.notations.pseudo_notation.obj_structure import ColumnN, IdentityN, BoxN, DiagramN, \
    SymmetryN, SpiderN
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.wire import curved_line


class PseudoNotation:
    def get_pseudo_notations(self, canvas):
        boxes = sorted(canvas.boxes, key=lambda x_: x_.x + x_.size[0] / 2)
        wires = canvas.wires  # just in case
        spiders = sorted(canvas.spiders, key=lambda x_: x_.location[0])
        intersections = self.get_wires_intersections(canvas)

        # group all items (boxes, spiders and intersections) by their x coordinate value
        stage_d = {}
        for box in boxes:
            x = round(box.x + box.size[0] / 2, 5)
            if x not in stage_d.keys():
                stage_d[x] = [box]
            else:
                stage_d[x].append(box)
        for spider in spiders:
            x = round(spider.location[0], 5)
            if x not in stage_d.keys():
                stage_d[x] = [spider]
            else:
                stage_d[x].append(spider)

        # find intersections and group by their x coordinate
        for intersection in intersections:
            found = False
            x = round(intersection[0][0], 5)
            for k, v in stage_d.items():
                box_sizes = [0]
                for item in v:
                    if type(item) is Box:
                        item: Box
                        box_sizes.append(item.size[0] / 2)
                    if type(item) is Spider:
                        item: Spider
                        box_sizes.append(item.r)
                max_s = max(box_sizes)
                if abs(k - x) <= max_s:
                    stage_d[k].append(intersection)
                    found = True
                    break
            if found:
                continue

            stage_d[round(intersection[0][0], 5)] = [intersection]

        # sort the groups by their x coordinate
        sorted_d = [(k, v) for k, v in stage_d.items()]
        sorted_d.sort(key=lambda x_: x_[0])

        # create actual string representation of the diagram
        diagram = DiagramN()
        for k, v in sorted_d:
            new_lst = []  # (y_value, object)
            # sort current group by y value
            this_group_intersections = []

            for item in v:
                if type(item) is Box:
                    item: Box
                    new_lst.append((item.y + item.size[1] / 2, item))
                elif type(item) is Spider:
                    item: Spider
                    new_lst.append((item.location[1], item))
                else:
                    item: list
                    new_lst.append((item[0][1], item))
                    this_group_intersections.append(item)
            # add Identity(1)-s to the list
            [new_lst.append(x) for x in self.are_wires_here(k, wires, canvas, this_group_intersections)]
            new_lst.sort(key=lambda x_: x_[0])
            column = ColumnN()
            # add all entries to the final string
            for entry in new_lst:
                if len(entry) == 1:
                    column.elements.append(IdentityN())
                elif type(entry[1]) is Box:
                    column.elements.append(
                        BoxN(sum([1 if c.side == "left" else 0 for c in entry[1].connections] + [0]),
                             sum([1 if c.side == "right" else 0 for c in entry[1].connections] + [0]),
                             entry[1].label_text))
                elif type(entry[1]) is Spider:
                    column.elements.append(self.get_spider_n(entry[1]))

                else:
                    column.elements.append(SymmetryN())
            diagram.columns.append(column)
        return diagram

    def are_wires_here(self, loc_x, wires, canvas, intersections):
        # find out if there are wires without boxes/spiders/intersections near this x value
        wires_here = []
        for wire in wires:
            continue_now = False
            for inter in intersections:
                if wire.id in inter[1]:
                    continue_now = True
                    break
            if continue_now:
                continue
            if wire.start_connection.location[0] < loc_x < wire.end_connection.location[0] or \
                    wire.end_connection.location[0] < loc_x < wire.start_connection.location[0]:

                coordinates = self.convert_coords(canvas.coords(wire.line))

                for i in range(1, len(coordinates)):
                    w1 = coordinates[i - 1]
                    w2 = coordinates[i]

                    if w1[0] <= loc_x <= w2[0] or w2[0] <= loc_x <= w1[0]:
                        y_value = (w1[1] + w2[1]) / 2
                        wires_here.append([y_value])
                        break
        return wires_here

    def get_wires_intersections(self, canvas):
        intersections = set()
        for w1 in canvas.wires:
            for w2 in canvas.wires:
                if (w1 == w2 or w1.end_connection == w2.end_connection or w1.end_connection == w2.start_connection or
                        w1.start_connection == w2.end_connection or w1.start_connection == w2.start_connection):
                    continue

                w1_coordinates = self.convert_coords(
                    curved_line(w1.start_connection.location, w1.end_connection.location, det=5))
                w2_coordinates = self.convert_coords(
                    curved_line(w2.start_connection.location, w2.end_connection.location, det=5))

                for i in range(1, len(w1_coordinates)):
                    w1_1 = w1_coordinates[i - 1]
                    w1_2 = w1_coordinates[i]
                    for j in range(1, len(w2_coordinates)):
                        w2_1 = w2_coordinates[j - 1]
                        w2_2 = w2_coordinates[j]

                        x, y = self.get_intersect(w1_1, w1_2, w2_1, w2_2)
                        # if is intersection
                        x = round(x, 5)
                        y = round(y, 5)
                        first_x = sorted([round(w1_1[0], 5), round(w1_2[0], 5)])
                        first_y = sorted([round(w1_1[1], 5), round(w1_2[1], 5)])

                        second_x = sorted([round(w2_1[0], 5), round(w2_2[0], 5)])
                        second_y = sorted([round(w2_1[1], 5), round(w2_2[1], 5)])

                        if first_x[0] <= x <= first_x[1] and first_y[0] <= y <= first_y[1] \
                                and second_x[0] <= x <= second_x[1] and second_y[0] <= y <= second_y[1]:
                            intersections.add(((x, y), tuple(sorted((w1.id, w2.id)))))

        return intersections

    # HELPERS
    @staticmethod
    def get_spider_n(spider):
        all_connections = list(set(filter(lambda x: (x is not None and x != spider), [w.end_connection for w in
                                                                                      spider.wires] + [
                                              w.start_connection for w in spider.wires])))
        lefts = rights = 0
        for c in all_connections:
            lefts += c.location[0] < spider.location[0]
            rights += c.location[0] >= spider.location[0]
        return SpiderN(lefts, rights)

    @staticmethod
    def get_intersect(a1, a2, b1, b2):
        stacked = np.vstack([a1, a2, b1, b2])  # s for stacked
        homogeneous = np.hstack((stacked, np.ones((4, 1))))  # h for homogeneous
        first_line = np.cross(homogeneous[0], homogeneous[1])  # get first line
        second_line = np.cross(homogeneous[2], homogeneous[3])  # get second line

        x, y, z = np.cross(first_line, second_line)  # point of intersection

        if z == 0:  # lines are parallel
            return float('inf'), float('inf')
        return x / z, y / z

    @staticmethod
    def convert_coords(coordinates):
        return [(coordinates[i], coordinates[i + 1]) for i in range(0, len(coordinates), 2)]

    @staticmethod
    def get_boxes_notations(canvas):
        boxes_not = set()
        for box in canvas.boxes:
            if not box.label_text:
                continue
            left_connections = sum([1 if c.side == "left" else 0 for c in box.connections] + [0])
            right_connections = sum([1 if c.side == "right" else 0 for c in box.connections] + [0])
            boxes_not.add(f"{box.label_text}: ({left_connections},{right_connections})")
        end = " |-\n"
        if not boxes_not:
            end = ""
        return ", ".join(boxes_not) + end
