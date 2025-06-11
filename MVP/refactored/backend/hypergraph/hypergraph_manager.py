from __future__ import annotations

import logging
from queue import Queue
from typing import TYPE_CHECKING

from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.node import Node

if TYPE_CHECKING:
    pass

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', )
logger = logging.getLogger(__name__)

message_start = "\x1b[33;20m"
message_end = "\x1b[0m"

def debug(x):
    logger.debug(message_start + x + message_end)


class HypergraphManager:
    # hypergraphs: set[Hypergraph] = set()
    nodes: dict[int, Node] = dict()
    edges: dict[int, HyperEdge] = dict()

    source_nodes_group: dict[int, set[Node]] = dict()

    @staticmethod
    def remove_node(node_id: int):
        """
        Removes a node from the hypergraph and handles the case where deleting the node causes the hypergraph to
        split into multiple disconnected hypergraphs.

        This function performs the following steps:
        1. Removes the specified node from its hypergraph.
        2. Checks if removing the node causes the hypergraph to split into multiple disconnected hypergraphs.
        3. If the hypergraph splits, removes the original hypergraph and creates new hypergraphs for each disconnected component.

        :param node_id: The unique identifier of the node to be removed.
        """
        logger.debug(message_start + f"Removing node with id {node_id}" + message_end)

        node = HypergraphManager.get_node_by_node_id(node_id)
        if node:
            node.remove_self()
            HypergraphManager.nodes.pop(node_id)

    @staticmethod
    def remove_hyper_edge(hyper_edge_id: int):
        """
        Removes a hyper edge from the hypergraph and handles the case where deleting the edge causes the hypergraph to
        split into multiple disconnected hypergraphs.

        This function performs the following steps:
        1. Removes the specified hyper edge from its hypergraph.
        2. Checks if removing the hyper edge causes the hypergraph to split into multiple disconnected hypergraphs.
        3. If the hypergraph splits, removes the original hypergraph and creates new hypergraphs for each disconnected component.

        :param hyper_edge_id: The unique identifier of the node to be removed.
        """
        logger.debug(
            message_start + f"Removing hyper edge with id {hyper_edge_id}" + message_end)

        hyper_edge = HypergraphManager.get_hyper_edge_by_id(hyper_edge_id)
        if hyper_edge:
            hyper_edge.remove_self()
            HypergraphManager.edges.pop(hyper_edge_id)

    @staticmethod
    def swap_hyper_edge_id(prev_id: int, new_id: int):
        """
        Replaces a hyper-edge ID in the corresponding hypergraph.

        :param prev_id: The current hyper-edge ID.
        :param new_id: The new hyper-edge ID.
        """
        logger.debug(message_start + f"Swapping hyper edge id from {prev_id} to {new_id}" + message_end)

        hyper_edge = HypergraphManager.get_hyper_edge_by_id(prev_id)
        if hyper_edge:
            HypergraphManager.edges.pop(hyper_edge.id)
            hyper_edge.swap_id(new_id)
            HypergraphManager.edges[new_id] = hyper_edge

    @staticmethod
    def create_new_node(node_id: int, canvas_id: int) -> Node:
        """
        Create new hypergraph when spider/diagram input/diagram output/wire is created.

        :return: Created node
        """
        logger.debug(message_start + f"Creating new node with id {node_id}" + message_end)

        new_node = Node(node_id, canvas_id=canvas_id)
        HypergraphManager.nodes[new_node.id] = new_node
        return new_node

    @staticmethod
    def union_nodes(node: Node, unite_with_id: int):
        logger.debug(
            message_start + f"Union node with id {node.id} with other node with id {unite_with_id}" + message_end)

        unite_with = HypergraphManager.get_node_by_node_id(unite_with_id)

        node.union(unite_with)

    @staticmethod
    def connect_node_with_input_hyper_edge(node: Node, hyper_edge_id: int) -> HyperEdge:
        """
        After hypergraph creation is done, make connectivity of node, with node/hyper edge and
        theirs hyper graphs.
        In this case, to given node (first arg) input should be added node|hyper edge.

        :return: HyperEdge that was added to the node
        """
        logger.debug(
            message_start + f"Connecting to node with id {node.id} input a hyper edge with id {hyper_edge_id}" + message_end)

        hyper_edge: HyperEdge | None = HypergraphManager.get_hyper_edge_by_id(hyper_edge_id)
        if hyper_edge is None:
            hyper_edge = HyperEdge(hyper_edge_id, canvas_id=node.canvas_id)
            HypergraphManager.edges[hyper_edge.id] = hyper_edge
        hyper_edge.append_target_node(node)
        node.append_input(hyper_edge)
        return hyper_edge

    @staticmethod
    def connect_node_with_output_hyper_edge(node: Node, hyper_edge_id: int) -> HyperEdge:
        """
        After hypergraph creation is done, make connectivity of node, with node/hyper edge and
        theirs hyper graphs.
        In this case, to given node (first arg) output should be added node|hyper edge.

        :return: HyperEdge that was added to the node
        """
        logger.debug(
            message_start + f"Connecting to node with id {node.id} output a hyper edge with id {hyper_edge_id}" + message_end)

        hyper_edge: HyperEdge | None = HypergraphManager.get_hyper_edge_by_id(hyper_edge_id)
        if hyper_edge is None:
            hyper_edge = HyperEdge(hyper_edge_id, canvas_id=node.canvas_id)
            HypergraphManager.edges[hyper_edge.id] = hyper_edge
        hyper_edge.append_source_node(node)
        node.append_output(hyper_edge)
        return hyper_edge

    @staticmethod
    def combine_hypergraphs(hypergraphs: list[Hypergraph]):
        """Combine two or more hypergraphs.

        NB!!!
        When combining hypergraphs from different canvases, new hypergraph will have canvas id from the first element!!!
        """

        logger.debug(message_start + f"Combining hypergraphs with following ids: " + ", ".join(
            map(lambda x: str(x.id), hypergraphs)) + message_end)
        pass

    @staticmethod
    def get_node_by_node_id(node_id: int):
        return HypergraphManager.nodes.get(node_id)

    @staticmethod
    def get_hyper_edge_by_id(hyper_edge_id: int) -> HyperEdge | None:
        return HypergraphManager.edges.get(hyper_edge_id)

    @staticmethod
    def get_graph_by_node_id(node_id: int) -> Hypergraph | None:
        node = HypergraphManager.nodes.get(node_id)
        hypergraph = Hypergraph(canvas_id=node.canvas_id)
        hypergraph.nodes[node.id] = node

        visited: set[int] = set()
        queue: Queue[Node | HyperEdge] = Queue()
        visited.add(node.id)
        for hyper_edge in node.get_output_hyper_edges() + node.get_input_hyper_edges():
            if hyper_edge.id not in visited:
                queue.put(hyper_edge)

        while not queue.empty():
            element = queue.get()
            visited.add(element.id)
            if isinstance(element, HyperEdge):
                hypergraph.edges[element.id] = element
                for node in element.get_target_nodes() + element.get_source_nodes():
                    if node.id not in visited:
                        queue.put(node)
            else:
                hypergraph.nodes[element.id] = element
                for hyper_edge in element.get_output_hyper_edges() + element.get_input_hyper_edges():
                    if hyper_edge.id not in visited:
                        queue.put(hyper_edge)

        return hypergraph

    @staticmethod
    def get_graph_by_hyper_edge_id(hyper_edge_id: int) -> Hypergraph | None:
        hyper_edge = HypergraphManager.edges.get(hyper_edge_id)
        hypergraph = Hypergraph(canvas_id=-1)
        hypergraph.edges[hyper_edge.id] = hyper_edge

        visited: set[int] = set()
        queue: Queue[Node|HyperEdge] = Queue()
        visited.add(hyper_edge.id)
        for node in hyper_edge.get_target_nodes() + hyper_edge.get_source_nodes():
            if node.id not in visited:
                queue.put(node)

        while not queue.empty():
            element = queue.get()
            visited.add(element.id)
            if isinstance(element, HyperEdge):
                hypergraph.edges[element.id] = element
                for node in element.get_target_nodes() + element.get_source_nodes():
                    if node.id not in visited:
                        queue.put(node)
            else:
                hypergraph.nodes[element.id] = element
                for hyper_edge in element.get_output_hyper_edges() + element.get_input_hyper_edges():
                    if hyper_edge.id not in visited:
                        queue.put(hyper_edge)

        return hypergraph


    @staticmethod
    def get_graph_by_source_node_id(source_node_id: int) -> Hypergraph | None:
        return HypergraphManager.get_graph_by_node_id(source_node_id)

    @staticmethod
    def get_graphs_by_canvas_id(canvas_id: int) -> list[Hypergraph]:
        element_in_graph: dict[int, Hypergraph] = {}
        hypergraphs: list[Hypergraph] = []

        visited: set[int] = set()
        queue: Queue[Node | HyperEdge] = Queue()

        for node in HypergraphManager.nodes.values():
            if node.id not in visited and node.canvas_id == canvas_id:
                hypergraph = Hypergraph(canvas_id=canvas_id)
                element_in_graph[node.id] = hypergraph
                hypergraph.nodes[node.id] = node
                if len(node.get_parent_nodes()) == 0:
                    hypergraph.hypergraph_source[node.id] = node

                visited.add(node.id)
                for hyper_edge in node.get_output_hyper_edges() + node.get_input_hyper_edges():
                    if hyper_edge.id not in visited:
                        queue.put(hyper_edge)

                for directly_connected_node in node.get_directly_connected_to():
                    if directly_connected_node.id not in visited:
                        queue.put(directly_connected_node)

                while not queue.empty():
                    element = queue.get()
                    visited.add(element.id)
                    element_in_graph[element.id] = hypergraph

                    if isinstance(element, HyperEdge):
                        hypergraph.edges[element.id] = element
                        for elements_node in element.get_target_nodes() + element.get_source_nodes():
                            if elements_node.id not in visited:
                                queue.put(elements_node)

                                for directly_connected_node in elements_node.get_directly_connected_to():
                                    if directly_connected_node.id not in visited:
                                        queue.put(directly_connected_node)
                    else:
                        hypergraph.nodes[element.id] = element
                        if len(element.get_parent_nodes()) == 0:
                            hypergraph.hypergraph_source[element.id] = element
                        for hyper_edge in element.get_output_hyper_edges() + element.get_input_hyper_edges():
                            if hyper_edge.id not in visited:
                                queue.put(hyper_edge)

                        for directly_connected_node in element.get_directly_connected_to():
                            if directly_connected_node.id not in visited:
                                queue.put(directly_connected_node)

                hypergraphs.append(hypergraph)
        return hypergraphs

    @staticmethod
    def get_graph_by_id(graph_id: int) -> Hypergraph | None:
        pass

    @staticmethod
    def add_hypergraph(hypergraph: Hypergraph):
        logger.debug(message_start + f"Adding hypergraph with id {hypergraph.id}" + message_end)

        HypergraphManager.hypergraphs.add(hypergraph)

    @staticmethod
    def remove_hypergraph(hypergraph: Hypergraph):
        logger.debug(
            message_start + f"Removing hypergraph with id {hypergraph.id}" + message_end)

        pass
