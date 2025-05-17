import unittest
from unittest.mock import MagicMock

from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge


def _create_nodes(count: int) -> list[Node]:
    return [Node(i) for i in range(count)]


def _create_mock_edges(count: int) -> list[HyperEdge]:
    return [MagicMock(spec=HyperEdge) for _ in range(count)]


class TestNode(unittest.TestCase):
    def setUp(self):
        self.nodes = _create_nodes(4)
        self.node0, self.node1, self.node2, self.node3 = self.nodes

        self.edges = _create_mock_edges(3)
        self.edge0, self.edge1, self.edge2 = self.edges

    def test_get_hypergraph_source_nodes(self):
        pass

    def test_get_hypergraph_target_nodes(self):
        pass

    def test_get_children_nodes_should_include_targets_and_united(self):
        self.edge0.get_target_nodes.return_value = [self.node1]
        self.node0.outputs = [self.edge0]
        self.node1.union(self.node2)
        children = self.node0.get_children_nodes()
        self.assertIn(self.node1, children)
        self.assertIn(self.node2, children)

    def test_get_parent_nodes_should_include_sources_and_united(self):
        self.edge0.get_source_nodes.return_value = [self.node1]
        self.node0.inputs = [self.edge0]
        self.node1.union(self.node2)
        parents = self.node0.get_parent_nodes()
        self.assertIn(self.node1, parents)
        self.assertIn(self.node2, parents)

    def test_get_input_hyper_edges_should_accumulate_from_united_nodes(self):
        self.node0.append_input(self.edge0)
        self.node1.append_input(self.edge1)
        self.node0.union(self.node1)
        inputs = self.node0.get_input_hyper_edges()
        self.assertIn(self.edge0, inputs)
        self.assertIn(self.edge1, inputs)

    def test_get_output_hyper_edges_should_accumulate_from_united_nodes(self):
        self.node0.append_output(self.edge0)
        self.node1.append_output(self.edge1)
        self.node0.union(self.node1)
        outputs = self.node0.get_output_hyper_edges()
        self.assertIn(self.edge0, outputs)
        self.assertIn(self.edge1, outputs)

    def test_get_united_with_nodes_should_return_all_directly_and_indirectly_connected(self):
        self.node0.union(self.node1)
        self.node1.union(self.node2)
        united_nodes = self.node0.get_united_with_nodes()
        self.assertIn(self.node1, united_nodes)
        self.assertIn(self.node2, united_nodes)

    def test_get_node_children_should_include_all_united_targets(self):
        self.edge0.get_target_nodes.return_value = [self.node1]
        self.node0.outputs = [self.edge0]
        self.node1.union(self.node2)
        children = self.node0.get_children_nodes()
        self.assertIn(self.node1, children)
        self.assertIn(self.node2, children)

    def test_append_input_should_add_unique_edge(self):
        self.node0.append_input(self.edge0)
        self.assertIn(self.edge0, self.node0.inputs)
        self.node0.append_input(self.edge0)  # Should not duplicate
        self.assertEqual(len(self.node0.inputs), 1)

    def test_append_output_should_add_unique_edge(self):
        self.node0.append_output(self.edge0)
        self.assertIn(self.edge0, self.node0.outputs)
        self.node0.append_output(self.edge0)
        self.assertEqual(len(self.node0.outputs), 1)

    def test_remove_self_should_disconnect_and_clear_edges(self):
        self.node0.union(self.node1)
        self.node0.append_input(self.edge0)
        self.node0.append_output(self.edge1)

        self.edge0.remove_target_node_by_reference = MagicMock()
        self.edge1.remove_source_node_by_reference = MagicMock()

        self.node0.remove_self()

        self.assertEqual(len(self.node0.inputs), 0)
        self.assertEqual(len(self.node0.outputs), 0)
        self.assertEqual(len(self.node0.directly_connected_to), 0)
        self.assertNotIn(self.node0, self.node1.directly_connected_to)
        self.edge0.remove_target_node_by_reference.assert_called_once_with(self.node0)
        self.edge1.remove_source_node_by_reference.assert_called_once_with(self.node0)

    def test_remove_input_should_remove_existing(self):
        self.node0.append_input(self.edge0)
        self.node0.remove_input(self.edge0)
        self.assertNotIn(self.edge0, self.node0.inputs)

    def test_remove_output_should_remove_existing(self):
        self.node0.append_output(self.edge0)
        self.node0.remove_output(self.edge0)
        self.assertNotIn(self.edge0, self.node0.outputs)

    def test_union_should_connect_nodes_bidirectionally(self):
        self.node0.union(self.node1)
        self.assertIn(self.node1, self.node0.directly_connected_to)
        self.assertIn(self.node0, self.node1.directly_connected_to)

    def test_is_connected_to_should_detect_direct_and_indirect_connections(self):
        self.node0.union(self.node1)
        self.node1.union(self.node2)
        self.assertTrue(self.node0.is_connected_to(self.node2))

    def test_is_connected_to_should_return_false_if_no_path(self):
        self.assertFalse(self.node0.is_connected_to(self.node1))

    def test_is_connected_to_should_return_true_for_self(self):
        self.assertTrue(self.node0.is_connected_to(self.node0))

    def test_eq_should_return_true_for_same_id_or_united_nodes(self):
        another_node = Node(0)
        self.assertTrue(self.node0.equals_to_node_group(another_node))

        self.node0.union(self.node1)
        node_same_as_1 = Node(self.node1.id)
        self.assertTrue(self.node0.equals_to_node_group(node_same_as_1))

    def test_eq_should_return_false_for_unrelated_nodes(self):
        self.assertFalse(self.node0 == self.node1)

    def test_hash_should_be_based_on_node_id(self):
        self.assertEqual(hash(self.node0), hash(self.node0.id))
