import tkinter.messagebox

from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.frontend.canvas_objects.spider import Spider
import constants as const


class SearchAlgorithm:
    def __init__(self, searchable: CustomCanvas, canvas: CustomCanvas, search_window):
        self.searchable = searchable
        self.canvas = canvas
        self.search_window = search_window
        self.search_all_canvases = search_window.search_all_canvases.get()
        self.results = []
        self.result_objects = {}
        self.wire_objects = {}

    def get_potential_results(self, searchable_objects, canvas_objects):
        potential_results = []

        searchable_connections = self.create_connection_dictionary(searchable_objects)
        canvas_connections = self.create_connection_dictionary(canvas_objects)

        counter = 0
        for searchable_connection in searchable_connections.items():
            curr_search_left, curr_search_right = searchable_connection[1]
            for canvas_connection in canvas_connections.items():
                curr_canvas_id = canvas_connection[0]
                curr_canvas_left, curr_canvas_right = canvas_connection[1]
                if searchable_objects[counter].__class__ == canvas_objects[curr_canvas_id].__class__:

                    if len(curr_canvas_left) == len(curr_search_left) or len(curr_search_left) == 0 or isinstance(
                            canvas_objects[curr_canvas_id], Spider):
                        if len(curr_canvas_right) == len(curr_search_right) or len(
                                curr_search_right) == 0 or isinstance(canvas_objects[curr_canvas_id], Spider):
                            if counter == 0:
                                res_start = {curr_canvas_id: [curr_canvas_left, curr_canvas_right]}
                                potential_results.append(res_start)
                            else:
                                for potential in potential_results.copy():
                                    if len(potential) == counter:
                                        for key in potential.keys():
                                            if key in curr_canvas_left or not curr_search_left:
                                                new_part = {curr_canvas_id: [curr_canvas_left, curr_canvas_right]}
                                                if not new_part.items() <= potential.items():
                                                    new_res = potential | new_part
                                                    potential_results.append(new_res)
                                                break
            counter += 1

        potential_results = list(filter(lambda x: len(x) == len(searchable_connections), potential_results))
        return potential_results

    @staticmethod
    def filter_connectivity(connection_dicts):
        connected_dicts = []
        for connection_dict in connection_dicts:
            connection_ids = []
            connected_ids = []
            connected = True
            connection_dict_items = list(connection_dict.items())
            for connection in connection_dict_items:
                connection_ids.append(connection[0])
                left_con, right_con = connection[1]
                connected_ids = connected_ids + left_con + right_con
            for connection_id in connection_ids:
                if connection_id not in connected_ids:
                    connected = False
            if connected:
                connected_dicts.append(connection_dict)

        return connected_dicts

    def contains_searchable(self):
        found = False
        result_ids = []
        if self.search_all_canvases:
            canvases = list(self.canvas.main_diagram.canvasses.values())
            canvases.remove(self.canvas)
            canvases.insert(0, self.canvas)
            items = []
            for canvas in canvases:
                items = items + canvas.spiders + canvas.boxes
            canvas_objects = sorted(items, key=lambda item: [canvases.index(item.canvas), item.x, item.y])
        else:
            canvas_objects = sorted(self.canvas.spiders + self.canvas.boxes,
                                    key=lambda item: [item.x, item.y])

        searchable_objects = sorted(self.searchable.spiders + self.searchable.boxes, key=lambda item: [item.x, item.y])

        if len(searchable_objects) <= 1:
            tkinter.messagebox.showwarning("Warning", "Please add more items into search.")
            self.search_window.focus()
            return False

        searchable_connections_dict = self.create_connection_dictionary(searchable_objects)
        if not self.filter_connectivity([searchable_connections_dict]):
            tkinter.messagebox.showwarning("Warning", "All items need to be connected to search.")
            self.search_window.focus()
            return False

        potential_results = self.get_potential_results(searchable_objects, canvas_objects)
        potential_results = self.filter_connectivity(potential_results)

        for potential_result in potential_results:

            temp_result_ids = []
            normalized = self.normalize_dictionary(potential_result)
            not_correct = False
            for normalized_key in normalized.keys():
                if normalized_key not in searchable_connections_dict.keys():
                    not_correct = True
                    break
                normalized_item = normalized[normalized_key]
                normalized_left, normalized_right = normalized_item

                searchable = searchable_connections_dict[normalized_key]
                searchable_left, searchable_right = searchable

                for key in searchable_left:
                    if key not in normalized_left and key is not None:
                        not_correct = True
                for key in searchable_right:
                    if key not in normalized_right and key is not None:
                        not_correct = True

            if not_correct:
                continue
            for i in range(len(searchable_objects)):
                potential = list(potential_result.items())[i]
                potential_id = potential[0]
                potential_left, potential_right = potential[1]
                potential_item = canvas_objects[potential_id]

                searchable = list(searchable_connections_dict.items())[i]
                searchable_id = searchable[0]
                searchable_left, searchable_right = searchable[1]
                searchable_item = searchable_objects[searchable_id]

                left_side_check = False
                right_side_check = False
                if searchable_item.__class__ == potential_item.__class__:
                    if isinstance(searchable_item, Box):

                        left_side_check = self.check_side_connections(canvas_objects, left_side_check, potential_left,
                                                                      searchable_item.left_connections, searchable_left,
                                                                      searchable_objects)

                        right_side_check = self.check_side_connections(canvas_objects, right_side_check,
                                                                       potential_right,
                                                                       searchable_item.right_connections,
                                                                       searchable_right,
                                                                       searchable_objects)

                    elif isinstance(searchable_item, Spider):
                        left_side_check = True
                        right_side_check = True

                if left_side_check and right_side_check:
                    temp_result_ids.append(potential_id)
                else:
                    temp_result_ids = []
                    break

            if temp_result_ids == list(potential_result.keys()):
                duplicate = False
                for res in result_ids:
                    if set(res) == set(temp_result_ids):
                        duplicate = True
                if not duplicate:
                    found = True
                    result_ids.append(temp_result_ids)

        for results in result_ids:
            self.highlight_results(results, canvas_objects)
            self.highlight_wires(results, canvas_objects, searchable_connections_dict)

        self.results = result_ids
        objects = {}
        for result in self.results:
            for index in result:
                objects[index] = canvas_objects[index]
        self.result_objects = objects

        return found

    def highlight_wires(self, result_ids, canvas_objects, searchable_connections_dict):
        canvases = self.canvas.main_diagram.canvasses.values() if self.search_all_canvases else [self.canvas]
        for canvas in canvases:
            for wire in canvas.wires:
                if wire.start_connection in canvas_objects:
                    start_index = canvas_objects.index(wire.start_connection)
                elif wire.start_connection.box in canvas_objects:
                    start_index = canvas_objects.index(wire.start_connection.box)
                else:
                    continue

                if wire.end_connection in canvas_objects:
                    end_index = canvas_objects.index(wire.end_connection)
                elif wire.end_connection.box in canvas_objects:
                    end_index = canvas_objects.index(wire.end_connection.box)
                else:
                    continue

                if start_index in result_ids and end_index in result_ids:
                    bad_wire = True
                    search_start_index = result_ids.index(start_index)
                    search_end_index = result_ids.index(end_index)
                    if search_end_index in searchable_connections_dict[search_start_index][1]:
                        bad_wire = False
                    if not bad_wire:
                        wire.search_highlight_secondary()
                        if tuple(result_ids) not in self.wire_objects:
                            self.wire_objects[tuple(result_ids)] = [wire]
                        else:
                            self.wire_objects[tuple(result_ids)].append(wire)

    @staticmethod
    def check_side_connections(canvas_objects, side_check, potential, connection_amount, searchable,
                               searchable_objects):
        if connection_amount:
            matching_connection_count = 0
            for j in range(connection_amount):
                if (searchable[j] is None
                        or potential[j] is None
                        or searchable_objects[searchable[j]].__class__ == canvas_objects[potential[j]].__class__):
                    matching_connection_count += 1
            if matching_connection_count == connection_amount:
                side_check = True
        else:
            side_check = True
        return side_check

    @staticmethod
    def highlight_results(result_indexes, canvas_objects):
        for result_index in result_indexes:
            canvas_objects[result_index].search_highlight_secondary()

    @staticmethod
    def normalize_dictionary(dictionary):
        """{6: [[4], [9]], 9: [[7, 6], [11]]} -> {0: [[], [1]], 1: [[0], []]}"""
        number_correspondence_dict = {}
        result = {}

        number_count = 0
        for key in sorted(dictionary.keys()):
            number_correspondence_dict[key] = number_count
            number_count += 1

        for item in dictionary.items():
            corresponding_num = number_correspondence_dict[item[0]]
            left, right = item[1]
            new_left, new_right = [], []
            for num in left:
                if num in number_correspondence_dict:
                    new_left.append(number_correspondence_dict[num])
            for numb in right:
                if numb in number_correspondence_dict:
                    new_right.append(number_correspondence_dict[numb])
            result[corresponding_num] = [new_left, new_right]
        return result

    @staticmethod
    def create_connection_dictionary(canvas_objects):
        canvas_connection_dict = {}
        for i in range(len(canvas_objects)):
            curr_item = canvas_objects[i]
            left_wires = []
            right_wires = []
            if isinstance(curr_item, Box):
                for connection in curr_item.connections:
                    if connection.side == const.LEFT:
                        index = SearchAlgorithm.get_item_index_from_connection(canvas_objects, connection,
                                                                               "start_connection")
                        left_wires.append(index)
                    elif connection.side == const.RIGHT:
                        index = SearchAlgorithm.get_item_index_from_connection(canvas_objects, connection,
                                                                               "end_connection")
                        right_wires.append(index)
            elif isinstance(curr_item, Spider):
                for wire in curr_item.wires:
                    if wire.start_connection == curr_item:
                        if wire.end_connection in canvas_objects:
                            index_of_end = canvas_objects.index(wire.end_connection)
                        elif wire.end_connection.box in canvas_objects:
                            index_of_end = canvas_objects.index(wire.end_connection.box)
                        else:
                            index_of_end = None
                        right_wires.append(index_of_end)
                    if wire.end_connection == curr_item:
                        if wire.start_connection in canvas_objects:
                            index_of_start = canvas_objects.index(wire.start_connection)
                        elif wire.start_connection.box in canvas_objects:
                            index_of_start = canvas_objects.index(wire.start_connection.box)
                        else:
                            index_of_start = None
                        left_wires.append(index_of_start)
            canvas_connection_dict[i] = [left_wires, right_wires]
        return canvas_connection_dict

    @staticmethod
    def get_item_index_from_connection(canvas_objects, connection, start_end_variable):
        if connection.wire:
            start_end_connection = getattr(connection.wire, start_end_variable)
            if start_end_connection in canvas_objects:
                index = canvas_objects.index(start_end_connection)
            elif start_end_connection.box in canvas_objects:
                index = canvas_objects.index(start_end_connection.box)
            else:
                index = None
        else:
            index = None
        return index

