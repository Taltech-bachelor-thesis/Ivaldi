from unittest import TestCase
from unittest.mock import MagicMock

from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge


def _create_nodes(count: int) -> list[Node]:
    return [Node(node_id=i) for i in range(count)]


def _create_edges(ids: list[int]) -> list[HyperEdge]:
    return [HyperEdge(edge_id) for edge_id in ids]


def _create_hypergraph(hypergraph_id: int) -> Hypergraph:
    return Hypergraph(hypergraph_id)


class TestHypergraph(TestCase):
    def setUp(self):
        self.nodes = _create_nodes(6)
        self.node0, self.node1, self.node2, self.node3, self.node4, self.node5 = self.nodes

        self.edges = _create_edges([100, 101, 102, 103])
        self.edge0, self.edge1, self.edge2, self.edge3 = self.edges

        self.hypergraph = _create_hypergraph(hypergraph_id=201)

    # Tests add_node/add_nodes
    # --------------------------------------
    def test_add_single_node(self):
        self.hypergraph.add_node(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertEqual(self.hypergraph.nodes[self.node1.id], self.node1)

    def test_add_single_node_as_source(self):
        self.hypergraph.add_node(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)

    def test_add_node_with_parents(self):
        self.node2.get_parent_nodes = MagicMock(return_value=[self.node1])

        self.hypergraph.add_node(self.node2)

        self.assertNotIn(self.node2.id, self.hypergraph.hypergraph_source)

    def test_add_directly_connected_nodes(self):
        self.node1.directly_connected_to = [self.node2, self.node3]

        self.hypergraph.add_node(self.node1)

        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)

    def test_add_multiple_nodes(self):
        self.hypergraph.add_nodes([self.node1, self.node2, self.node3])

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)

    def test_add_multiple_nodes_as_sources(self):
        self.hypergraph.add_nodes([self.node1, self.node2])

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)

    def test_add_multiple_nodes_with_united_nodes(self):
        self.node1.directly_connected_to = [self.node2]
        self.node2.directly_connected_to = [self.node3]

        self.hypergraph.add_nodes([self.node1, self.node2])

        self.assertIn(self.node3.id, self.hypergraph.nodes)

    # Test add_hypergraph_source/add_hypergraph_sources
    # --------------------------------------
    def test_add_single_hypergraph_source(self):
        self.hypergraph.add_hypergraph_source(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)

    def test_add_hypergraph_source_with_directly_connected_nodes(self):
        self.node1.directly_connected_to = [self.node2, self.node3]
        self.hypergraph.add_hypergraph_source(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node3.id, self.hypergraph.hypergraph_source)

    def test_add_multiple_hypergraph_sources(self):
        self.node1.directly_connected_to = [self.node2]
        self.node2.directly_connected_to = [self.node3]

        self.hypergraph.add_hypergraph_sources([self.node1, self.node2])

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node3.id, self.hypergraph.hypergraph_source)

    def test_add_multiple_hypergraph_sources_with_no_direct_connections(self):
        self.hypergraph.add_hypergraph_sources([self.node1, self.node4])

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node4.id, self.hypergraph.hypergraph_source)

    # Test remove_node
    # --------------------------------------
    def test_remove_single_node(self):
        self.hypergraph.add_node(self.node1)
        self.hypergraph.remove_node(self.node1.id)

        self.assertNotIn(self.node1.id, self.hypergraph.nodes)

    # def test_remove_source_node(self):
    #     self.hypergraph.add_node(self.node1)
    #     self.hypergraph.remove_node(self.node1.id)
    #
    #     self.assertNotIn(self.node1.id, self.hypergraph.hypergraph_source)

    # def test_remove_node_with_directly_connected(self):
    #     self.node0.union(self.node1)
    #     self.node1.union(self.node2)
    #     self.node2.union(self.node3)
    #     self.node3.union(self.node4)
    #
    #     self.hypergraph.add_nodes([self.node0, self.node1, self.node2, self.node3, self.node4])
    #     self.hypergraph.remove_node(self.node1.id)
    #
    #     self.assertNotIn(self.node0.id, self.hypergraph.nodes)
    #     self.assertNotIn(self.node1.id, self.hypergraph.nodes)

        # self.assertNotIn(self.node0.id, self.hypergraph.hypergraph_source)
        # self.assertNotIn(self.node1.id, self.hypergraph.hypergraph_source)
        #
        # self.assertIn(self.node2.id, self.hypergraph.nodes)
        # self.assertIn(self.node3.id, self.hypergraph.nodes)
        # self.assertIn(self.node4.id, self.hypergraph.nodes)
        #
        # self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)
        # self.assertIn(self.node3.id, self.hypergraph.hypergraph_source)
        # self.assertIn(self.node4.id, self.hypergraph.hypergraph_source)

    # def test_remove_node_does_not_affect_unconnected_nodes(self):
    #     self.node1.is_connected_to = MagicMock(return_value=False)
    #     self.node2.is_connected_to = MagicMock(return_value=False)
    #
    #     self.hypergraph.add_node(self.node1)
    #     self.hypergraph.add_node(self.node2)
    #     self.hypergraph.remove_node(self.node1.id)
    #
    #     self.assertNotIn(self.node1.id, self.hypergraph.nodes)
    #     self.assertNotIn(self.node1.id, self.hypergraph.hypergraph_source)

    # def test_remove_node_calls_remove_self(self):
    #     self.node1.remove_self = MagicMock()
    #
    #     self.hypergraph.add_node(self.node1)
    #     self.hypergraph.remove_node(self.node1.id)
    #
    #     self.node1.remove_self.assert_called_once()

    # Test remove_hyper_edge
    # --------------------------------------
    def test_remove_single_hyper_edge(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.remove_hyper_edge(self.edge1.id)

        self.assertNotIn(self.edge1.id, self.hypergraph.edges)

    def test_remove_hyper_edge_not_found(self):
        with self.assertRaises(KeyError):
            self.hypergraph.remove_hyper_edge(999)

    def test_remove_multiple_hyper_edges(self):
        self.hypergraph.add_edges([self.edge1, self.edge2, self.edge3])

        self.hypergraph.remove_hyper_edge(self.edge1.id)
        self.hypergraph.remove_hyper_edge(self.edge2.id)

        self.assertNotIn(self.edge1.id, self.hypergraph.edges)
        self.assertNotIn(self.edge2.id, self.hypergraph.edges)
        self.assertIn(self.edge3.id, self.hypergraph.edges)

    def test_remove_hyper_verify_remove_self_called(self):
        self.edge1.remove_self = MagicMock()

        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.remove_hyper_edge(self.edge1.id)

        self.edge1.remove_self.assert_called_once()

    # Test swap_hyper_edge_id
    # --------------------------------------
    def test_swap_hyper_edge_id_valid(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.add_edge(self.edge2)

        self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge2.id)

        self.assertEqual(self.hypergraph.edges[self.edge2.id], self.edge1)
        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge2)

    def test_swap_hyper_edge_id_with_nonexistent_edge(self):
        self.assertFalse(self.hypergraph.swap_hyper_edge_id(999, self.edge2.id))
        self.assertFalse(self.hypergraph.swap_hyper_edge_id(self.edge1.id, 999))

    def test_swap_hyper_edge_id_same_id(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge1.id)

        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge1)

    def test_swap_hyper_edge_id_with_mocked_swap_id(self):
        prev_id = self.edge1.id
        new_id = 201
        self.hypergraph.add_edge(self.edge1)

        self.hypergraph.swap_hyper_edge_id(prev_id, new_id)

        self.assertIn(new_id, self.hypergraph.edges)
        self.assertEqual(self.edge1.id, new_id)

    def test_swap_hyper_edge_id_after_removal(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.add_edge(self.edge2)
        self.hypergraph.remove_hyper_edge(self.edge1.id)

        self.assertFalse(self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge2.id))

    # Test update_source_nodes_descendants
    # --------------------------------------
    def test_update_source_nodes_descendants_single_source(self):
        self.node1.get_children_nodes = MagicMock(return_value=[self.node2])
        self.node1.directly_connected_to = [self.node3]

        self.hypergraph.add_hypergraph_source(self.node1)
        self.hypergraph.update_source_nodes_descendants()

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)

    def test_update_source_nodes_descendants_multiple_sources(self):
        self.node1.get_children_nodes = MagicMock(return_value=[self.node2])
        self.node1.directly_connected_to = [self.node3]
        self.node2.get_children_nodes = MagicMock(return_value=[self.node4])
        self.node2.directly_connected_to = [self.node5]

        self.hypergraph.add_hypergraph_sources([self.node1, self.node2])
        self.hypergraph.update_source_nodes_descendants()

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)
        self.assertIn(self.node4.id, self.hypergraph.nodes)
        self.assertIn(self.node5.id, self.hypergraph.nodes)

    def test_update_source_nodes_descendants_empty_source(self):
        self.hypergraph.update_source_nodes_descendants()
        self.assertEqual(len(self.hypergraph.nodes), 0)

    def test_update_source_nodes_descendants_with_complex_graph_one_source(self):
        nodes = [Node(i) for i in range(12)]

        nodes[0].get_children_nodes = MagicMock(return_value=[nodes[6], nodes[5], nodes[11], nodes[8], nodes[10]])
        nodes[1].get_children_nodes = MagicMock(return_value=[nodes[6], nodes[5], nodes[11], nodes[8], nodes[10]])
        nodes[2].get_children_nodes = MagicMock(return_value=[nodes[6], nodes[5], nodes[11], nodes[8], nodes[10]])
        nodes[3].get_children_nodes = MagicMock(return_value=[nodes[6], nodes[5], nodes[11], nodes[8], nodes[10]])
        nodes[4].get_children_nodes = MagicMock(return_value=[nodes[6], nodes[5], nodes[11], nodes[8], nodes[10]])
        nodes[5].get_children_nodes = MagicMock(return_value=[nodes[7], nodes[9]])
        nodes[6].get_children_nodes = MagicMock(return_value=[])
        nodes[7].get_children_nodes = MagicMock(return_value=[])
        nodes[8].get_children_nodes = MagicMock(return_value=[])
        nodes[9].get_children_nodes = MagicMock(return_value=[])
        nodes[10].get_children_nodes = MagicMock(return_value=[])
        nodes[11].get_children_nodes = MagicMock(return_value=[])

        nodes[0].union(nodes[1])
        nodes[0].union(nodes[2])
        nodes[0].union(nodes[3])
        nodes[0].union(nodes[4])
        nodes[1].union(nodes[2])
        nodes[1].union(nodes[3])
        nodes[1].union(nodes[4])
        nodes[2].union(nodes[3])
        nodes[2].union(nodes[4])
        nodes[3].union(nodes[4])
        nodes[6].union(nodes[8])
        nodes[6].union(nodes[10])
        nodes[6].union(nodes[11])
        nodes[7].union(nodes[9])
        nodes[8].union(nodes[10])
        nodes[8].union(nodes[11])
        nodes[10].union(nodes[11])

        edge1 = HyperEdge(100)
        edge1.append_source_node(nodes[1])
        edge1.append_target_node(nodes[5])

        edge2 = HyperEdge(101)
        edge2.append_source_node(nodes[5])
        edge2.append_target_node(nodes[7])

        edge3 = HyperEdge(102)
        edge3.append_source_node(nodes[4])
        edge3.append_target_node(nodes[6])

        self.hypergraph.add_edge(edge1)
        self.hypergraph.add_edge(edge2)
        self.hypergraph.add_edge(edge3)
        self.hypergraph.add_hypergraph_source(nodes[0])
        self.hypergraph.update_source_nodes_descendants()

        for node in nodes:
            self.assertIn(node.id, self.hypergraph.nodes)
        for edge in self.hypergraph.edges.values():
            for node in edge.get_source_nodes() + edge.get_target_nodes():
                self.assertIn(node.id, self.hypergraph.nodes)
        # TODO check structure of hypergraph

    def test_update_source_nodes_descendants_with_complex_graph_two_sources(self):
        nodes = [Node(i) for i in range(0, 17)]

        nodes[0].get_children_nodes = MagicMock(return_value=[nodes[3]])
        nodes[1].get_children_nodes = MagicMock(return_value=[nodes[4], nodes[5], nodes[6], nodes[7], nodes[11],
                                                              nodes[12], nodes[13], nodes[14], nodes[15]])
        nodes[2].get_children_nodes = MagicMock(return_value=[nodes[3]])
        nodes[3].get_children_nodes = MagicMock(return_value=[nodes[4], nodes[5], nodes[6], nodes[7], nodes[11],
                                                              nodes[12], nodes[13], nodes[14], nodes[15]])
        nodes[4].get_children_nodes = MagicMock(return_value=[])
        nodes[5].get_children_nodes = MagicMock(return_value=[])
        nodes[6].get_children_nodes = MagicMock(return_value=[])
        nodes[7].get_children_nodes = MagicMock(return_value=[])
        nodes[8].get_children_nodes = MagicMock(return_value=[nodes[4], nodes[5], nodes[6], nodes[7], nodes[11],
                                                              nodes[12], nodes[13], nodes[14], nodes[15]])
        nodes[9].get_children_nodes = MagicMock(return_value=[nodes[4], nodes[5], nodes[6], nodes[7], nodes[11],
                                                              nodes[12], nodes[13], nodes[14], nodes[15]])
        nodes[10].get_children_nodes = MagicMock(return_value=[nodes[4], nodes[5], nodes[6], nodes[7], nodes[11],
                                                               nodes[12], nodes[13], nodes[14], nodes[15]])
        nodes[11].get_children_nodes = MagicMock(return_value=[])
        nodes[12].get_children_nodes = MagicMock(return_value=[])
        nodes[13].get_children_nodes = MagicMock(return_value=[])
        nodes[14].get_children_nodes = MagicMock(return_value=[])
        nodes[15].get_children_nodes = MagicMock(return_value=[])
        nodes[16].get_children_nodes = MagicMock(return_value=[nodes[4], nodes[5], nodes[6], nodes[7], nodes[11],
                                                               nodes[12], nodes[13], nodes[14], nodes[15]])

        nodes[0].union(nodes[2])
        nodes[1].union(nodes[8])
        nodes[1].union(nodes[9])
        nodes[1].union(nodes[10])
        nodes[1].union(nodes[16])
        nodes[4].union(nodes[5])
        nodes[4].union(nodes[6])
        nodes[4].union(nodes[7])
        nodes[4].union(nodes[11])
        nodes[4].union(nodes[12])
        nodes[4].union(nodes[13])
        nodes[4].union(nodes[14])
        nodes[4].union(nodes[15])
        nodes[5].union(nodes[6])
        nodes[5].union(nodes[7])
        nodes[5].union(nodes[11])
        nodes[6].union(nodes[7])
        nodes[6].union(nodes[11])
        nodes[6].union(nodes[12])
        nodes[6].union(nodes[13])
        nodes[6].union(nodes[14])
        nodes[6].union(nodes[15])
        nodes[11].union(nodes[12])
        nodes[11].union(nodes[13])
        nodes[11].union(nodes[14])
        nodes[11].union(nodes[15])

        edge1 = HyperEdge(100)
        edge1.append_source_nodes([nodes[3]])
        edge1.append_target_node(nodes[4])

        edge2 = HyperEdge(101)
        edge2.append_source_nodes([nodes[4], nodes[10]])
        edge2.append_target_node(nodes[5])

        edge3 = HyperEdge(102)
        edge3.append_source_nodes([nodes[11]])
        edge3.append_target_node(nodes[12])

        self.hypergraph.add_edge(edge1)
        self.hypergraph.add_edge(edge2)
        self.hypergraph.add_edge(edge3)
        self.hypergraph.add_hypergraph_sources([nodes[0], nodes[1]])
        self.hypergraph.update_source_nodes_descendants()

        for node in nodes:
            self.assertIn(node.id, self.hypergraph.nodes)
        for edge in self.hypergraph.edges.values():
            for node in edge.get_source_nodes() + edge.get_target_nodes():
                self.assertIn(node.id, self.hypergraph.nodes)

    # Test update_edges
    # --------------------------------------
    def test_update_edges_with_single_source_node(self):
        self.hypergraph.add_hypergraph_source(self.node1)
        self.node1.outputs = [self.edge1]
        self.node1.inputs = []
        self.node1.get_children_nodes = MagicMock(return_value=[])
        self.node1.directly_connected_to = []

        self.hypergraph.update_edges()

        self.assertIn(self.edge1.id, self.hypergraph.edges)
        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge1)

    def test_update_edges_with_multiple_source_nodes(self):
        self.hypergraph.add_hypergraph_sources([self.node1, self.node2])
        self.node1.outputs = [self.edge1]
        self.node1.inputs = []
        self.node2.outputs = [self.edge2]
        self.node2.inputs = []

        self.hypergraph.update_edges()

        self.assertIn(self.edge1.id, self.hypergraph.edges)
        self.assertIn(self.edge2.id, self.hypergraph.edges)
        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge1)
        self.assertEqual(self.hypergraph.edges[self.edge2.id], self.edge2)

    def test_update_edges_with_connected_nodes(self):
        self.hypergraph.add_hypergraph_source(self.node1)
        self.node1.outputs = [self.edge1]
        self.node1.inputs = []
        self.node1.get_children_nodes = MagicMock(return_value=[self.node2])
        self.node1.directly_connected_to = []

        self.node2.outputs = [self.edge2]
        self.node2.inputs = [self.edge1]
        self.node2.get_children_nodes = MagicMock(return_value=[])
        self.node2.directly_connected_to = []

        self.hypergraph.update_edges()

        self.assertIn(self.edge1.id, self.hypergraph.edges)
        self.assertIn(self.edge2.id, self.hypergraph.edges)
        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge1)
        self.assertEqual(self.hypergraph.edges[self.edge2.id], self.edge2)

    def test_update_edges_with_united_nodes(self):
        self.hypergraph.add_hypergraph_source(self.node1)
        self.node1.outputs = [self.edge1]
        self.node1.inputs = []
        self.node1.get_children_nodes = MagicMock(return_value=[])
        self.node1.directly_connected_to = [self.node2]

        self.node2.outputs = [self.edge2]
        self.node2.inputs = []
        self.node2.get_children_nodes = MagicMock(return_value=[])
        self.node2.directly_connected_to = []

        self.hypergraph.update_edges()

        self.assertIn(self.edge1.id, self.hypergraph.edges)
        self.assertIn(self.edge2.id, self.hypergraph.edges)
        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge1)
        self.assertEqual(self.hypergraph.edges[self.edge2.id], self.edge2)
