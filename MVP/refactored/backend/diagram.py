import json
from typing import Self

from MVP.refactored.backend.generator import Generator
from MVP.refactored.backend.resource import Resource
from MVP.refactored.backend.types.connection_info import ConnectionInfo


class Diagram:
    def __init__(self):
        self.input: list[ConnectionInfo] = []
        self.output: list[ConnectionInfo] = []
        self.boxes: list[Generator] = []
        self.resources: list[Resource] = []
        self.spiders: list[Resource] = []
        self.sub_diagrams: list[
            Diagram] = []  # There is sub diagram of diagram. If sub diagram contains one more sub diagram.
        # It won't be added here. Only to sub diagram's sub diagram

    def get_generator_by_id(self, box_id: int) -> Generator:
        return next((b for b in self.boxes if b.id == box_id), None)

    def get_resource_by_id(self, resource_id: int) -> Resource:
        return next((r for r in self.resources if r.id == resource_id), None)

    def get_spider_by_id(self, spider_id: int) -> Resource | None:
        return next((s for s in self.spiders if s.id == spider_id), None)

    def get_input_by_id(self, input_id):
        return next((i for i in self.input if i.id == input_id), None)

    def get_input_by_index(self, index):
        return next((i for i in self.input if i.index == index), None)

    def get_output_by_id(self, output_id):
        return next((o for o in self.output if o.id == output_id), None)

    def get_output_by_index(self, index):
        return next((o for o in self.output if o.index == index), None)

    def add_resource(self, resource: Resource):
        if resource not in self.resources:
            self.resources.append(resource)

    def add_box(self, box: Generator):
        if box not in self.boxes:
            self.boxes.append(box)

    def add_spider(self, spider: Resource):
        if spider not in self.spiders:
            self.spiders.append(spider)

    def add_resources(self, resources: list[Resource]):
        for resource in resources:
            self.add_resource(resource)

    def add_boxes(self, boxes: list[Generator]):
        for box in boxes:
            self.add_box(box)

    def add_spiders(self, spiders: list[Resource]):
        for spider in spiders:
            self.add_spider(spider)

    def add_input(self, connection_info: ConnectionInfo):
        self.input.insert(connection_info.index, connection_info)

    def add_output(self, connection_info: ConnectionInfo):
        self.output.insert(connection_info.index, connection_info)

    def add_sub_diagram(self, diagram: Self):
        if diagram not in self.sub_diagrams:
            self.sub_diagrams.append(diagram)

    def remove_input(self, connection_id: int):
        for i in self.input:
            if i.id == connection_id:
                self.input.remove(i)
                return

    def remove_output(self, connection_id: int):
        for i in self.output:
            if i.id == connection_id:
                self.output.remove(i)
                return

    def remove_box_by_id(self, box_id: int):
        for box in self.boxes:
            if box.id == box_id:
                self.boxes.remove(box)
                return

    def remove_resource_by_id(self, resource_id: int):
        for resource in self.resources:
            if resource.id == resource_id:
                self.resources.remove(resource)
                if not resource.spider:  # if it is wire, we need to remove connections from spiders, because spider connections live as long as they connected to smt
                    for connection in resource.get_spider_connections():
                        spider = self.get_spider_by_id(connection.id)
                        spider.remove_spider_connection_by_index(connection.index)
                return

    def remove_spider_by_id(self, spider_id: int):
        for spider in self.spiders:
            if spider.id == spider_id:
                self.spiders.remove(spider)
                return

    def remove_box(self, box: Generator):
        if box in self.boxes:
            self.boxes.remove(box)

    def remove_resource(self, resource: Resource):
        if resource in self.resources:
            self.resources.remove(resource)

    def remove_spider(self, spider: Resource):
        if spider in self.spiders:
            self.resources.remove(spider)

    def remove_boxes(self, boxes: list[Generator]):
        for box in boxes:
            self.remove_box(box)

    def remove_resources(self, resources: list[Resource]):
        for resource in resources:
            self.remove_resource(resource)

    def remove_spiders(self, spiders: list[Resource]):
        for spider in spiders:
            self.remove_spider(spider)

    def diagram_import(self, file_path: str):
        with open(file_path, 'r') as file:
            data = json.load(file)
            self._from_dict(data)

    def diagram_export(self, file_path: str):
        data = self._to_dict()
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _to_dict(self):
        return {
            "input": self.input,
            "output": self.output,
            "boxes": [box.to_dict() for box in self.boxes],
            "resources": [resource.to_dict() for resource in self.resources]
        }

    def _from_dict(self, data):
        self.input = data.get("input", [])
        self.output = data.get("output", [])
        self.boxes = [Generator.from_dict(box_data) for box_data in data.get("boxes", [])]
        self.resources = [Resource.from_dict(resource_data) for resource_data in data.get("resources", [])]
