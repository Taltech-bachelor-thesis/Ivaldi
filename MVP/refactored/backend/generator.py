from __future__ import annotations

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.types.GeneratorType import GeneratorType
from MVP.refactored.backend.types.connection_side import ConnectionSide

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.backend.types.connection_info import ConnectionInfo


class Generator:
    """Backend representation of frontend box."""

    def __init__(self, generator_id):
        self.id = generator_id
        self.type: GeneratorType = GeneratorType.ATOMIC  # 0-atomic 1-compound None-undefined
        self.left: list[ConnectionInfo] = []
        self.right: list[ConnectionInfo] = []
        self.left_inner: list[ConnectionInfo] = []
        self.right_inner: list[ConnectionInfo] = []
        self.sub_diagram_id: int = -1  # -1 if does`t have
        self.subset = []
        self.parent = None
        self.spiders = []
        self.operand = None
        self.box_function: BoxFunction | None = None

    def get_sub_diagram_id(self):
        """Returns -1 if no sub diagram is defined."""
        return self.sub_diagram_id

    def set_sub_diagram_id(self, sub_diagram_id):
        self.sub_diagram_id = sub_diagram_id

    def get_left_by_id(self, left_id: int):
        for left in self.left:
            if left.id == left_id:
                return left

    def get_right_by_id(self, right_id: int):
        for right in self.right:
            if right.id == right_id:
                return right

    def get_left(self) -> list[ConnectionInfo]:
        return self.left

    def get_right(self) -> list[ConnectionInfo]:
        return self.right

    def add_left(self, left: ConnectionInfo):
        if left.side != ConnectionSide.SPIDER:  # because connection info with spider will always have the same id
            if left not in self.left:
                self.left.insert(left.index, left)
        else:
            self.left.insert(left.index, left)

    def add_right(self, right: ConnectionInfo):
        if right.side != ConnectionSide.SPIDER:  # because connection info with spider will always have the same id
            if right not in self.right:
                self.right.insert(right.index, right)
        else:
            self.right.insert(right.index, right)

    def add_left_inner(self, left: ConnectionInfo):
        self.left_inner.insert(left.index, left)

    def add_right_inner(self, right: ConnectionInfo):
        self.right_inner.insert(right.index, right)

    def add_operand(self, operand):
        self.operand = operand

    def remove_operand(self):
        self.operand = None

    def set_box_function(self, box_function: BoxFunction):
        self.box_function = box_function

    def get_box_function(self) -> BoxFunction | None:
        return self.box_function

    def set_id(self, new_id: int):
        self.id = new_id

    def set_type(self, type: GeneratorType):
        self.type = type

    def remove_type(self):
        self.type = None

    def remove_all_left(self):
        for left in self.left:
            left.set_box_id(None)
        self.left.clear()

    def remove_all_right(self):
        for right in self.right:
            right.set_box_id(None)
        self.right.clear()

    def remove_left(self, connection_id: int = None):
        # self.left.pop(connection_id)
        # for i, resource in enumerate(self.left):
        #     resource.index = i
        is_found_connection = False
        to_be_removed: ConnectionInfo | None = None
        for connection in self.left:
            if connection.id == connection_id:
                connection.set_box_id(None)
                to_be_removed = connection
                is_found_connection = True
            elif is_found_connection:  # same as in Resource class
                connection.index -= 1
        if to_be_removed is not None:
            self.left.remove(to_be_removed)

    def remove_right(self, connection_id: int = None):
        # self.right.pop(connection_id)
        # for i, resource in enumerate(self.right):
        #     resource.index = i
        is_found_connection = False
        to_be_removed: ConnectionInfo | None = None
        for connection in self.right:
            if connection.id == connection_id:
                connection.set_box_id(None)
                to_be_removed = connection
                is_found_connection = True
            elif is_found_connection:  # same as in Resource class
                connection.index -= 1
        if to_be_removed is not None:
            self.right.remove(to_be_removed)

    def remove_left_inner(self, connection_id: int = None):
        # self.left_inner.pop(connection_id)
        # for i, resource in enumerate(self.left_inner):
        #     resource.index = i
        is_found_connection = False
        to_be_removed: ConnectionInfo | None = None
        for connection in self.left_inner:
            if connection.id == connection_id:
                connection.set_box_id(None)
                to_be_removed = connection
                is_found_connection = True
            elif is_found_connection:  # same as in Resource class
                connection.index -= 1
        if to_be_removed is not None:
            self.left_inner.remove(to_be_removed)

    def remove_right_inner(self, connection_id: int = None):
        # self.right_inner.pop(connection_id)
        # for i, resource in enumerate(self.right_inner):
        #     resource.index = i
        is_found_connection = False
        to_be_removed: ConnectionInfo | None = None
        for connection in self.right_inner:
            if connection.id == connection_id:
                connection.set_box_id(None)
                to_be_removed = connection
                is_found_connection = True
            elif is_found_connection:  # same as in Resource class
                connection.index -= 1
        if to_be_removed is not None:
            self.right_inner.remove(to_be_removed)

    def remove_left_atomic(self, connection_id: int):
        self.left.pop(connection_id)
        for i, resource in enumerate(self.left):
            resource.index = i

    def remove_right_atomic(self, connection_id: int):
        self.right.pop(connection_id)
        for i, resource in enumerate(self.left):
            resource.index = i

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "left": self.left,
            "right": self.right,
            "left_inner": self.left_inner,
            "right_inner": self.right_inner,
            "operand": self.operand
        }

    @classmethod
    def from_dict(cls, data):
        box = cls(data["id"])
        box.type = data.get("type")
        box.left = data.get("left", [])
        box.right = data.get("right", [])
        box.left_inner = data.get("left_inner", [])
        box.right_inner = data.get("right_inner", [])
        box.operand = data.get("operand")
        return box

    def __eq__(self, __value):
        return isinstance(__value, type(self)) and __value.id == self.id
