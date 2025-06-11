from __future__ import annotations

import logging
from queue import Queue
from typing import TYPE_CHECKING

from MVP.refactored.backend.id_generator import IdGenerator

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.node import Node

from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', )
logger = logging.getLogger(__name__)
message_start = "\x1b[33;20m"
message_end = "\x1b[0m"


class Hypergraph:
    """Hypergraph class."""

    def __init__(self, hypergraph_id=None, canvas_id=None):
        self.id = hypergraph_id
        if hypergraph_id is None:
            self.id = IdGenerator.id(self)
        self.canvas_id = canvas_id
        self.hypergraph_source: dict[int, Node] = {}
        self.nodes: dict[int, Node] = {}
        self.edges: dict[int, HyperEdge] = {}

        logger.debug(message_start + f"Creating hypergraph with id {self.id}" + message_end)

    def get_node_by_id(self, node_id: int) -> Node | None:
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> list[Node]:
        return list(self.nodes.values())

    def get_all_nodes_ids(self) -> list[int]:
        return list(self.nodes.keys())

    def get_all_hyper_edges(self) -> list[HyperEdge]:
        return list(self.edges.values())

    def get_hyper_edge_by_id(self, hyper_edge_id: int) -> HyperEdge | None:
        return self.edges.get(hyper_edge_id)

    def get_hypergraph_source(self) -> list[Node]:
        return list(self.hypergraph_source.values())

    def get_hypergraph_source_ids(self) -> list[int]:
        return list(self.hypergraph_source.keys())

    def get_hypergraph_target(self) -> list[Node]:
        queue = Queue()
        target_nodes: dict[int, Node] = dict()
        visited: set[Node] = set()
        for node in self.get_hypergraph_source():
            queue.put(node)

        while not queue.empty():
            node = queue.get()
            visited.add(node)
            output_hyper_edges: list[HyperEdge] = node.get_output_hyper_edges()
            if len(output_hyper_edges) == 0:
                target_nodes[node.id] = node
                for united_with in node.get_united_with_nodes():
                    target_nodes[united_with.id] = united_with

            for output_hyper_edge in output_hyper_edges:
                for target_node in output_hyper_edge.get_target_nodes():
                    if target_node not in visited:
                        queue.put(target_node)
        return list(target_nodes.values())

    def get_canvas_id(self) -> int:
        return self.canvas_id

    def set_hypergraph_sources(self, nodes: list[Node]):
        self.hypergraph_source.clear()
        self.add_hypergraph_sources(nodes)

    def set_canvas_id(self, canvas_id: int) -> None:
        self.canvas_id = canvas_id

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        if len(node.get_parent_nodes()) == 0:
            self.hypergraph_source[node.id] = node
            for directly_connected in node.get_united_with_nodes():
                self.nodes[directly_connected.id] = directly_connected
                self.hypergraph_source[directly_connected.id] = directly_connected
        else:
            for directly_connected in node.get_united_with_nodes():
                self.nodes[directly_connected.id] = directly_connected

    def add_nodes(self, nodes: list[Node]):
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: HyperEdge):
        self.edges[edge.id] = edge

    def add_edges(self, edges: list[HyperEdge]):
        for edge in edges:
            self.add_edge(edge)

    # def get_all_nodes(self) -> list[Node]:
    #     return list(self.nodes.values())
    #
    # def get_hypergraph_source(self) -> list[Node]:
    #     return list(self.hypergraph_source.values())

    def remove_node(self, node_to_remove_id: int):
        removed_node = self.nodes.pop(node_to_remove_id)
        removed_node_united_with_nodes = removed_node.get_united_with_nodes()
        removed_node.remove_self()

        if node_to_remove_id in self.hypergraph_source:
            self.hypergraph_source.pop(node_to_remove_id)

        for directly_connected in removed_node_united_with_nodes:
            for source_node in self.hypergraph_source.values():
                if not source_node.is_connected_to(directly_connected):
                    self.nodes.pop(directly_connected.id)
                    if directly_connected.id in self.hypergraph_source:
                        self.hypergraph_source.pop(directly_connected.id)
                    break

    def remove_hyper_edge(self, edge_to_remove_id: int) -> HyperEdge:
        self.edges[edge_to_remove_id].remove_self()
        return self.edges.pop(edge_to_remove_id)

    def swap_hyper_edge_id(self, prev_id: int, new_id: int) -> bool:
        """
        :param prev_id:
        :param new_id:
        :return: True, if id was changed.
        """
        if prev_id in self.edges and prev_id != new_id:
            self.edges[prev_id].swap_id(new_id)
            self.edges[new_id] = self.edges[prev_id]
            self.edges.pop(prev_id)
            return True
        return False

    def contains_node(self, node: Node) -> bool:
        return node.id in self.get_all_nodes_ids()

    def add_hypergraph_source(self, node: Node):
        self.hypergraph_source[node.id] = node
        self.nodes[node.id] = node
        for directly_connected in node.get_united_with_nodes():
            self.nodes[directly_connected.id] = directly_connected
            self.hypergraph_source[directly_connected.id] = directly_connected

    def add_hypergraph_sources(self, nodes: list[Node]):
        for node in nodes:
            self.add_hypergraph_source(node)

    def update_source_nodes_descendants(self):
        """
        Update all hypergraph nodes.
        Must be called when the source node is added.
        """
        self.nodes.clear()
        queue: Queue[Node] = Queue()
        visited: set[int] = set()
        for source_node in self.get_hypergraph_source():
            queue.put(source_node)
            for connected_node in source_node.get_children_nodes() + source_node.get_united_with_nodes():
                queue.put(connected_node)

        while not queue.empty():
            child_node = queue.get()
            # self.add_node(child_node) TODO maybe use this? (not good because adds complexity, but exclude some possible errors with hypergraph source)
            self.nodes[child_node.id] = child_node
            visited.add(child_node.id)
            for connected_node in child_node.get_children_nodes() + child_node.get_united_with_nodes():
                if connected_node.id not in visited:
                    queue.put(connected_node)

    def update_edges(self):
        """
        Update all hypergraph edges.
        Must be called when the source node is added.
        """
        self.edges.clear()
        queue: Queue[Node] = Queue()
        visited_nodes: set[int] = set()
        for source_node in self.get_hypergraph_source():
            hyper_edges: list[HyperEdge] = source_node.get_output_hyper_edges() + source_node.get_input_hyper_edges()
            for hyper_edge in hyper_edges:
                self.edges[hyper_edge.id] = hyper_edge  # update hyper edges
            for connected_node in source_node.get_children_nodes() + source_node.get_united_with_nodes():
                queue.put(connected_node)  # add next level nodes to queue

        while not queue.empty():
            node = queue.get()  # current level node
            visited_nodes.add(node.id)
            for hyper_edge in node.get_output_hyper_edges() + node.get_input_hyper_edges():
                self.edges[hyper_edge.id] = hyper_edge  # update hyper edges
            for connected_node in node.get_children_nodes() + node.get_united_with_nodes():
                if connected_node.id not in visited_nodes:
                    queue.put(connected_node)  # add next level nodes to queue

    def get_node_groups(self) -> list[list[int]]:
        """
        Return list of node groups.
        Node group is a list of nodes that are directly connected with each other.
        """
        node_groups: list[list[int]] = []
        visited: set[int] = set()

        for node in self.nodes.values():
            if node.id not in visited:
                node_group = [node.id]
                visited.add(node.id)

                united_nodes = node.get_united_with_nodes()
                for united_node in united_nodes:
                    visited.add(united_node.id)
                    node_group.append(united_node.id)

                node_groups.append(node_group)

        return node_groups

    def to_dict(self) -> dict:
        """Return a dictionary representation of the hypergraph."""
        return {
            "id": self.id,
            "hyperEdges": [hyper_edge.to_dict() for hyper_edge in self.get_all_hyper_edges()],
            "nodeGroups": self.get_node_groups(),
            "sourceNodes": [source_node.id for source_node in self.get_hypergraph_source()],
        }

    def is_empty(self):
        return len(self.nodes) == 0 and len(self.edges) == 0 and len(self.hypergraph_source) == 0

    def __str__(self) -> str:
        result = f"Hypergraph: {self.id}\n"

        hyper_edges = self.get_all_hyper_edges()
        result += f"Hyper edges({len(hyper_edges)}): " + ", ".join(
            str(hyper_edge) for hyper_edge in hyper_edges) + "\n"

        vertices = self.get_all_nodes()
        result += f"Vertices({len(vertices)}): " + ", ".join(
            f"{str(vertex)}({len(vertex.get_united_with_nodes())})" for vertex in vertices) + "\n"

        result += "Connections:\n"
        visited = set()
        for vertex in vertices:
            if vertex not in visited:
                visited.add(vertex)
                for node in vertex.get_united_with_nodes():
                    visited.add(node)
                inputs = f"|" + "|".join(f"{hyper_edge}" for hyper_edge in vertex.get_input_hyper_edges())
                outputs = f"|" + "|".join(f"{hyper_edge}" for hyper_edge in vertex.get_output_hyper_edges())
                result += f"{inputs}<-{vertex.id}->{outputs}\n"

        return result

    def __eq__(self, other):
        if not isinstance(other, Hypergraph):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
