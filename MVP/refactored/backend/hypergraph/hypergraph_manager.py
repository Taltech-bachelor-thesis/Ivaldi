from __future__ import annotations

import logging
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
    hypergraphs: set[Hypergraph] = set()

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

        removed_node_outputs_and_directly_connected = []
        _hypergraph: Hypergraph = None
        for hypergraph in HypergraphManager.hypergraphs:
            node = hypergraph.get_node_by_id(node_id)
            if node is not None:
                _hypergraph = hypergraph
                removed_node_outputs_and_directly_connected = node.get_children_nodes() + node.get_united_with_nodes()
                hypergraph.remove_node(node_id)
                break
        # check if new hyper graphs were created
        if _hypergraph is None:
            return
        source_nodes_and_potentially_source_nodes: list[
            Node] = list(set(_hypergraph.get_hypergraph_source() + removed_node_outputs_and_directly_connected))

        # CHECK ALL NODES, IF THEY DON`T HAVE INPUT NODES => THEY CAN BE SOURCE NODES
        nodes_without_input_nodes = []
        for node in source_nodes_and_potentially_source_nodes:
            if len(node.get_parent_nodes()) == 0:
                nodes_without_input_nodes.append(node)
        source_nodes_and_potentially_source_nodes = nodes_without_input_nodes


        source_nodes_groups: list[list[Node]] = list()  # list of all source nodes groups
        for source_node in source_nodes_and_potentially_source_nodes:
            group: set[Node] | list[Node] = set()
            group.add(source_node)
            group.update(source_node.get_united_with_nodes())
            for next_source_node in source_nodes_and_potentially_source_nodes:
                if next_source_node not in group and next_source_node.is_connected_to(source_node):
                    # TODO add single node
                    group.add(next_source_node)
                    group.update(next_source_node.get_united_with_nodes())
            group = sorted(list(group), key=lambda node_from_group: node_from_group.id)
            if len(group) != 0 and group not in source_nodes_groups:
                source_nodes_groups.append(group)

        logger.debug(message_start + "Source nodes are " + ", ".join(
            f"{n.id}" for n in source_nodes_and_potentially_source_nodes) + message_end)
        logger.debug(message_start + "Source node groups are " + ", ".join(
            f"[{', '.join(map(str, (n.id for n in group)))}]" for group in
            source_nodes_groups) + message_end)

        # if after deleting node hype graph split to two or more hyper graphs, we need to handle that
        if len(source_nodes_groups) > 1:  # If group count isn't 1, so there occurred new hyper graphs
            HypergraphManager.remove_hypergraph(_hypergraph)  # remove old hypergraph

            for group in source_nodes_groups:
                new_hypergraph = Hypergraph(canvas_id=_hypergraph.get_canvas_id())
                new_hypergraph.add_hypergraph_sources(group)
                new_hypergraph.update_source_nodes_descendants()
                new_hypergraph.update_edges()
                HypergraphManager.add_hypergraph(new_hypergraph)
        else:
            if len(source_nodes_groups) == 1:
                _hypergraph.set_hypergraph_sources(source_nodes_groups[0]) # because there can be changes
                _hypergraph.update_source_nodes_descendants() # TODO INSTEAD OF THESE TWO, JUST UPDATE EVERYTHING
                _hypergraph.update_edges()  # after deleting node some hyper edges will not have connections
            else:
                HypergraphManager.remove_hypergraph(_hypergraph)

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

        hypergraph_to_handle: Hypergraph = None
        deleted_hyper_edge = None
        deleted_hyper_edge_target_nodes = []
        for hypergraph in HypergraphManager.hypergraphs:
            if hypergraph.get_hyper_edge_by_id(hyper_edge_id) is not None:
                hypergraph_to_handle = hypergraph
                deleted_hyper_edge_target_nodes = hypergraph.get_hyper_edge_by_id(hyper_edge_id).get_target_nodes()
                deleted_hyper_edge = hypergraph.remove_hyper_edge(hyper_edge_id)  # remove hyper edge from hypergraph
                break

        if deleted_hyper_edge is None:
            return  # TODO, investigate when it can be None
        # check if new hypergraph appears
        source_nodes: list[Node] = hypergraph_to_handle.get_hypergraph_source() + deleted_hyper_edge_target_nodes
        source_nodes_groups: list[list[Node]] = list()  # list of all source nodes groups
        # TODO move duplicated code into another method?
        for source_node in source_nodes:
            group: list[Node] = list()
            group.append(source_node)
            for next_source_node in source_nodes:
                if source_node != next_source_node and source_node.is_connected_to(next_source_node):
                    group.append(next_source_node)
            group = sorted(group, key=lambda node: node.id)
            if group not in source_nodes_groups:
                source_nodes_groups.append(group)

        logger.debug(message_start + "Source nodes are " + ", ".join(
            f"{n.id}" for n in source_nodes) + message_end)
        logger.debug(message_start + "Source node groups are " + ", ".join(
            f"[{', '.join(map(str, (n.id for n in group)))}]" for group in
            source_nodes_groups) + message_end)
        # if after deleting node hype graph split to two or more hyper graphs, we need to handle that
        if len(source_nodes_groups) > 1:  # If group count isn't 1, so there occurred new hyper graphs
            HypergraphManager.remove_hypergraph(hypergraph_to_handle)  # remove old hypergraph

            for group in source_nodes_groups:
                new_hypergraph = Hypergraph(canvas_id=hypergraph_to_handle.get_canvas_id())
                new_hypergraph.add_hypergraph_sources(group)
                new_hypergraph.update_source_nodes_descendants()
                new_hypergraph.update_edges()
                HypergraphManager.add_hypergraph(new_hypergraph)
        else:
            if hypergraph_to_handle.is_empty():
                HypergraphManager.remove_hypergraph(hypergraph_to_handle)

    @staticmethod
    def swap_hyper_edge_id(prev_id: int, new_id: int):
        """
        Replaces a hyper-edge ID in the corresponding hypergraph.

        :param prev_id: The current hyper-edge ID.
        :param new_id: The new hyper-edge ID.
        """
        logger.debug(message_start + f"Swapping hyper edge id from {prev_id} to {new_id}" + message_end)

        hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(prev_id)
        if hypergraph is not None:  # TODO investigate when it is none
            hypergraph.swap_hyper_edge_id(prev_id, new_id)

    @staticmethod
    def create_new_node(node_id: int, canvas_id: int) -> Node:
        """
        Create new hypergraph when spider/diagram input/diagram output/wire is created.

        :return: Created node
        """
        logger.debug(message_start + f"Creating new node with id {node_id}" + message_end)

        new_hypergraph: Hypergraph = Hypergraph(canvas_id=canvas_id)
        new_node = Node(node_id)

        new_hypergraph.add_hypergraph_source(new_node)
        HypergraphManager.add_hypergraph(new_hypergraph)
        return new_node

    @staticmethod
    def union_nodes(node: Node, unite_with_id: int):
        logger.debug(
            message_start + f"Union node with id {node.id} with other node with id {unite_with_id}" + message_end)

        unite_with = HypergraphManager.get_node_by_node_id(unite_with_id)
        unite_with_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(
            unite_with.id)  # always exits, because node is always forms a hypergraph
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)

        node.union(unite_with)
        if not node_hypergraph == unite_with_hypergraph:
            HypergraphManager.combine_hypergraphs([node_hypergraph, unite_with_hypergraph])

    @staticmethod
    def connect_node_with_input_hyper_edge(node: Node, hyper_edge_id: int) -> HyperEdge:
        """
        After hypergraph creation is done, make connectivity of node, with node/hyper edge and
        theirs hyper graphs.
        In this case, to given node (first arg) input should be added node|hyper edge.

        :return: HyperEdge that was added to the node
        """
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)
        connect_to_hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(hyper_edge_id)

        if connect_to_hypergraph is None:
            hyper_edge = HyperEdge(hyper_edge_id)
        else:
            hyper_edge = connect_to_hypergraph.get_hyper_edge_by_id(hyper_edge_id)
        logger.debug(
            message_start + f"Connecting to node with id {node.id} input a hyper edge with id {hyper_edge_id}" + message_end)
        # box = hyper edge
        hyper_edge.append_target_node(node)
        node.append_input(hyper_edge)
        if connect_to_hypergraph is None:  # It is an autonomous box
            node_hypergraph.add_edge(hyper_edge)
        elif not node_hypergraph == connect_to_hypergraph:
            # if node's and hyper edge's hypergraph is the same, it means that new wire between spider and the box is added
            # nothing to combine
            # It is box that already have some connections => forms hypergraph
            HypergraphManager.combine_hypergraphs([node_hypergraph, connect_to_hypergraph])

        return hyper_edge

    @staticmethod
    def connect_node_with_output_hyper_edge(node: Node, hyper_edge_id: int) -> HyperEdge:
        """
        After hypergraph creation is done, make connectivity of node, with node/hyper edge and
        theirs hyper graphs.
        In this case, to given node (first arg) output should be added node|hyper edge.

        :return: HyperEdge that was added to the node
        """
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)
        connect_to_hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(hyper_edge_id)

        if connect_to_hypergraph is None:
            hyper_edge = HyperEdge(hyper_edge_id)
        else:
            hyper_edge = connect_to_hypergraph.get_hyper_edge_by_id(hyper_edge_id)
        logger.debug(
            message_start + f"Connecting to node with id {node.id} output a hyper edge with id {hyper_edge_id}" + message_end)
        # box = hyper edge
        hyper_edge.append_source_node(node)
        node.append_output(hyper_edge)
        if connect_to_hypergraph is None:  # It is an autonomous box
            node_hypergraph.add_edge(hyper_edge)
        elif not node_hypergraph == connect_to_hypergraph:
            # if node's and hyper edge's hypergraph is the same, it means that new wire between spider and the box is added
            # nothing to combine
            # It is box that already have some connections => forms hypergraph
            HypergraphManager.combine_hypergraphs([node_hypergraph, connect_to_hypergraph])

        return hyper_edge

    @staticmethod
    def combine_hypergraphs(hypergraphs: list[Hypergraph]):
        """Combine two or more hypergraphs.

        NB!!!
        When combining hypergraphs from different canvases, new hypergraph will have canvas id from the first element!!!
        """

        logger.debug(message_start + f"Combining hypergraphs with following ids: " + ", ".join(
            map(lambda x: str(x.id), hypergraphs)) + message_end)

        combined_hypergraph = Hypergraph(canvas_id=hypergraphs[0].canvas_id)
        for hypergraph in hypergraphs:
            combined_hypergraph.add_nodes(hypergraph.get_hypergraph_source())  # adding source node
            combined_hypergraph.update_edges()
            combined_hypergraph.update_source_nodes_descendants()
            HypergraphManager.remove_hypergraph(hypergraph)
        HypergraphManager.add_hypergraph(combined_hypergraph)

    @staticmethod
    def get_node_by_node_id(node_id: int):
        for hypergraph in HypergraphManager.hypergraphs:
            node = hypergraph.get_node_by_id(node_id)
            if node is not None:
                return node
        return None

    @staticmethod
    def get_hyper_edge_by_id(hyper_edge_id: int) -> HyperEdge | None:
        graph = HypergraphManager.get_graph_by_hyper_edge_id(hyper_edge_id)
        if graph is not None:
            return graph.get_hyper_edge_by_id(hyper_edge_id)
        return None

    @staticmethod
    def get_graph_by_node_id(node_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            if node_id in hypergraph.get_all_nodes_ids():
                return hypergraph
        return None

    @staticmethod
    def get_graph_by_hyper_edge_id(hyper_edge_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            if hyper_edge_id in hypergraph.edges:
                return hypergraph
        return None

    @staticmethod
    def get_graph_by_source_node_id(source_node_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            for source_node in hypergraph.get_hypergraph_source():
                for source_node_union in source_node.get_united_with_nodes():
                    if source_node_union.id == source_node_id:
                        return hypergraph
        return None

    @staticmethod
    def get_graphs_by_canvas_id(canvas_id: int) -> list[Hypergraph]:
        graphs: set[Hypergraph] = set()
        for graph in HypergraphManager.hypergraphs:
            if graph.get_canvas_id() == canvas_id:
                graphs.add(graph)
        return list(graphs)

    @staticmethod
    def add_hypergraph(hypergraph: Hypergraph):
        logger.debug(message_start + f"Adding hypergraph with id {hypergraph.id}" + message_end)

        HypergraphManager.hypergraphs.add(hypergraph)

    @staticmethod
    def remove_hypergraph(hypergraph: Hypergraph):
        logger.debug(
            message_start + f"Removing hypergraph with id {hypergraph.id}" + message_end)
        HypergraphManager.hypergraphs.remove(hypergraph)
