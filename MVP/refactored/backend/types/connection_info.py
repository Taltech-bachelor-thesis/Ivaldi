from __future__ import annotations
from MVP.refactored.backend.generator import Generator

from typing import Self, TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.backend.resource import Resource
    from MVP.refactored.backend.types.connection_side import ConnectionSide


class ConnectionInfo:
    def __init__(self, connection_index: int, connection_side: ConnectionSide, connection_id: int,
                 related_generator_id: int = None,
                 related_resource_id: int | None = None, related_object: Resource | Generator | None = None):
        self.index = connection_index
        self.box_id = related_generator_id
        self.resource_id = related_resource_id
        self.side = connection_side
        self.id = connection_id
        self.related_object: Resource | Generator | None = None  # spider or box
        self.set_related_object(related_object)

    def is_resource_connection(self) -> bool:
        return self.resource_id is not None and self.box_id is None

    def is_generator_connection(self) -> bool:
        return self.box_id is not None and self.resource_id is None

    def is_input_output_connection(self) -> bool:
        return self.box_id is None and self.resource_id is None

    def get_id(self) -> int:
        return self.id

    def has_box(self) -> bool:
        return self.box_id is not None

    def get_box_id(self) -> int:
        return self.box_id

    def set_box_id(self, box_id: int | None):
        self.box_id = box_id

    def set_related_object(self, related_object: Resource | Generator | None):
        self.related_object = related_object
        if related_object is None: return
        if isinstance(related_object, Generator):
            self.box_id = related_object.id
        else:
            self.resource_id = related_object.id

    def get_related_object(self) -> Resource | Generator:
        return self.related_object

    def to_list(self) -> list:
        return [self.index, self.box_id, self.side, self.id]

    def is_all_fields_exists(self) -> bool:
        return self.index is not None and self.box_id is not None and self.side is not None and self.id is not None

    @classmethod
    def from_list(cls, data) -> Self:
        return ConnectionInfo(data[0], data[2], data[3], data[1])

    def __eq__(self, __value):
        return isinstance(__value, ConnectionInfo) and self.id == __value.id

    def __str__(self):
        return f"index: {self.index}, box_id: {self.box_id}, resource_id: {self.resource_id}, side: {self.side}, id: {self.id}"

    def __repr__(self):
        return str(self)
