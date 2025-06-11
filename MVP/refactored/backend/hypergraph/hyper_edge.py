from __future__ import annotations

from typing import TYPE_CHECKING

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.id_generator import IdGenerator

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.node import Node
    from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph


class HyperEdge:

    def __init__(self, hyper_edge_id=None, canvas_id: int = -2, box_function: BoxFunction = None, sub_diagram_canvas_id=-1):
        if hyper_edge_id is None:
            hyper_edge_id = IdGenerator.id(self)
        self.canvas_id = canvas_id
        self.id = hyper_edge_id
        self.box_function: BoxFunction | None = box_function

        self.source_nodes: dict[int, Node] = dict()  # key is connection index, it is necessary for keeping the right queue
        self.target_nodes: dict[int, Node] = dict()

        self.sub_diagram_canvas_id = sub_diagram_canvas_id

    def get_hypergraphs_inside(self) -> list[Hypergraph]:
        # why dynamically get hypergraphs?
        # Because in sub diagram hypergraphs can be modified, deleted, added and that handling is tricky,
        # so it is easier to do that in this way.
        from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager

        if self.sub_diagram_canvas_id == -1:
            return []
        return HypergraphManager.get_graphs_by_canvas_id(self.sub_diagram_canvas_id)

    def is_compound(self) -> bool:
        return self.sub_diagram_canvas_id != -1

    def set_sub_diagram_canvas_id(self, canvas_id: int):
        self.sub_diagram_canvas_id = canvas_id

    def swap_id(self, new_id: int):
        self.id = new_id

    def remove_all_source_nodes(self):
        self.source_nodes.clear()

    def remove_all_target_nodes(self):
        self.target_nodes.clear()

    def remove_source_connection_by_index(self, conn_index: int):
        """NB! It deletes connection and all connections with index more that current connection index,
        their connection decreases.
        """
        if conn_index in self.source_nodes:
            del self.source_nodes[conn_index]
        for key in self.source_nodes.keys():
            if key > conn_index:
                self.source_nodes[key - 1] = self.source_nodes[key]
                del self.source_nodes[key]

    def remove_target_connection_by_index(self, conn_index: int):
        """NB! It deletes connection and all connections with index more that current connection index,
        their connection decreases.
        """
        if conn_index in self.source_nodes:
            del self.target_nodes[conn_index]
        for key in self.target_nodes.keys():
            if key > conn_index:
                self.target_nodes[key - 1] = self.target_nodes[key]
                del self.target_nodes[key]

    def get_source_nodes(self) -> list[Node]:
        """
        :return Ordered list of source nodes(vertices):
        """
        return [item[1] for item in sorted(self.source_nodes.items(), key=lambda item: item[0])]

    def get_target_nodes(self) -> list[Node]:
        """
        :return Ordered list of target nodes(vertices):
        """
        return [item[1] for item in sorted(self.target_nodes.items(), key=lambda item: item[0])]

    def get_source_node_connection_index(self, node: Node) -> int | None:
        for conn_index, source_node in self.source_nodes.items():
            if source_node == node:
                return conn_index
        return None

    def get_target_node_connection_index(self, node: Node) -> int | None:
        for conn_index, target_node in self.target_nodes.items():
            if target_node == node:
                return conn_index
        return None

    def get_box_function(self) -> BoxFunction:
        return self.box_function

    def set_source_node(self, conn_index: int, node: Node):
        if conn_index in self.source_nodes:
            self.set_source_node(conn_index + 1, self.source_nodes[conn_index])
        self.source_nodes[conn_index] = node

    def set_target_node(self, conn_index: int, node: Node):
        if conn_index in self.target_nodes:
            self.set_target_node(conn_index + 1, self.target_nodes[conn_index])
        self.target_nodes[conn_index] = node

    def set_box_function(self, function: BoxFunction):
        self.box_function = function

    def append_target_node(self, node: Node):
        self.target_nodes[len(self.target_nodes)] = node

    def append_source_node(self, node: Node):
        self.source_nodes[len(self.source_nodes)] = node

    def append_source_nodes(self, nodes: list[Node]):
        for node in nodes:
            self.append_source_node(node)

    def remove_all_source_nodes(self):
        self.source_nodes.clear()

    def remove_all_target_nodes(self):
        self.target_nodes.clear()

    def remove_source_connection_by_index(self, conn_index: int):
        """NB! It deletes connection and all connections with index more that current connection index,
        their connection decreases.
        """
        if conn_index in self.source_nodes:
            del self.source_nodes[conn_index]
        for key in list(self.source_nodes.keys()):
            if key > conn_index:
                self.source_nodes[key - 1] = self.source_nodes[key]
                del self.source_nodes[key]

    def remove_target_connection_by_index(self, conn_index: int):
        """NB! It deletes connection and all connections with index more that current connection index,
        their connection decreases.
        """
        if conn_index in self.source_nodes:
            del self.target_nodes[conn_index]
        for key in list(self.target_nodes.keys()):
            if key > conn_index:
                self.target_nodes[key - 1] = self.target_nodes[key]
                del self.target_nodes[key]

    def remove_source_node_by_connection_index(self, conn_index: int):
        if conn_index in self.source_nodes:
            del self.source_nodes[conn_index]

    def remove_target_node_by_connection_index(self, conn_index: int):
        if conn_index in self.target_nodes:
            del self.target_nodes[conn_index]

    def remove_source_node_by_reference(self, node: Node):
        connection_index = self.get_source_node_connection_index(node)
        if connection_index is not None:
            del self.source_nodes[connection_index]

    def remove_target_node_by_reference(self, node: Node):
        connection_index = self.get_target_node_connection_index(node)
        if connection_index is not None:
            del self.target_nodes[connection_index]

    def remove_self(self):
        for node in self.source_nodes.values():
            node.remove_output(self)
        for node in self.target_nodes.values():
            node.remove_input(self)
        self.source_nodes.clear()
        self.target_nodes.clear()

    def swap_id(self, new_id: int):
        self.id = new_id

    def to_dict(self) -> dict:
        """Return a dictionary representation of the hyper edge."""
        return {
            "id": self.id,
            "sourceNodes": [node.id for node in self.get_source_nodes()],
            "targetNodes": [node.id for node in self.get_target_nodes()],
        }

    def __str__(self) -> str:
        """Return a string representation of the node."""
        return (f"Hyper edge ID: {self.id}\n"
                f"Inputs: {", ".join([str(node) for node in self.get_source_nodes()])}\n"
                f"Outputs: {", ".join([str(node) for node in self.get_target_nodes()])}")

    def __eq__(self, other):
        if not isinstance(other, HyperEdge):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
