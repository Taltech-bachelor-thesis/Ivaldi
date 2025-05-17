from unittest import TestCase
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

def _create_nodes(count: int) -> list[Node]:
    return [Node(node_id=i) for i in range(count)]


def _create_edges(ids: list[int]) -> list[HyperEdge]:
    return [HyperEdge(edge_id) for edge_id in ids]


def _create_hypergraph(hypergraph_id: int) -> Hypergraph:
    return Hypergraph(hypergraph_id)


class TestHyperEdge(TestCase):
    def setUp(self):
        self.nodes = _create_nodes(6)
        self.node0, self.node1, self.node2, self.node3, self.node4, self.node5 = self.nodes

        self.edges = _create_edges([100, 101, 102, 103])
        self.edge0, self.edge1, self.edge2, self.edge3 = self.edges

        self.hypergraph = _create_hypergraph(hypergraph_id=201)

    def test_get_source_node_connection_index(self):
        self.edge0.source_nodes = {
            0: self.node0,
            1: self.node1,
            2: self.node2
        }

        self.assertEqual(self.edge0.get_source_node_connection_index(self.node0), 0)
        self.assertEqual(self.edge0.get_source_node_connection_index(self.node1), 1)
        self.assertEqual(self.edge0.get_source_node_connection_index(self.node2), 2)
        self.assertIsNone(self.edge0.get_source_node_connection_index(self.node3))

    def test_get_target_node_connection_index(self):
        self.edge0.target_nodes = {
            0: self.node2,
            1: self.node3
        }

        self.assertEqual(self.edge0.get_target_node_connection_index(self.node2), 0)
        self.assertEqual(self.edge0.get_target_node_connection_index(self.node3), 1)
        self.assertIsNone(self.edge0.get_target_node_connection_index(self.node0))
        self.assertIsNone(self.edge0.get_target_node_connection_index(self.node1))

    def test_remove_source_connection_by_index(self):
        edge = HyperEdge(200)
        edge.source_nodes = {
            0: self.node0,
            1: self.node1,
            2: self.node2,
            3: self.node3
        }

        edge.remove_source_connection_by_index(1)
        expected = {
            0: self.node0,
            1: self.node2,
            2: self.node3
        }
        self.assertEqual(edge.source_nodes, expected)

        edge.remove_source_connection_by_index(0)
        expected = {
            0: self.node2,
            1: self.node3
        }
        self.assertEqual(edge.source_nodes, expected)

    def test_remove_target_connection_by_index(self):
        edge = HyperEdge(201)
        edge.target_nodes = {
            0: self.node0,
            1: self.node1,
            2: self.node2,
            3: self.node3
        }

        edge.remove_target_connection_by_index(2)
        expected = {
            0: self.node0,
            1: self.node1,
            2: self.node3
        }
        self.assertEqual(edge.target_nodes, expected)

        edge.remove_target_connection_by_index(1)
        expected = {
            0: self.node0,
            1: self.node3
        }
        self.assertEqual(edge.target_nodes, expected)
