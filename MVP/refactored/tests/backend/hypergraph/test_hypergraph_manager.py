from unittest import TestCase
from unittest.mock import MagicMock, patch

from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph


class TestHypergraphManager(TestCase):

    def setUp(self):
        HypergraphManager.hypergraphs.clear()
        self.sample_node = Node(1)
        self.sample_node_ = Node(2)
        self.sample_hypergraph = Hypergraph(canvas_id=123)
        self.sample_hyper_edge = HyperEdge(10)

    def tearDown(self):
        HypergraphManager.hypergraphs.clear()

    # TEST: Node creation and registration
    # ----------------------------------------------------------
    def test_create_new_node_creates_node_and_registers_hypergraph(self):
        canvas_id = 100
        node = HypergraphManager.create_new_node(node_id=1, canvas_id=canvas_id)

        self.assertIsInstance(node, Node)
        graph = HypergraphManager.get_graph_by_node_id(node.id)
        self.assertIsNotNone(graph)
        self.assertIn(node, graph.get_all_nodes())

    # TEST: Add and remove hypergraphs
    # ----------------------------------------------------------
    def test_add_and_remove_hypergraph(self):
        HypergraphManager.add_hypergraph(self.sample_hypergraph)
        self.assertIn(self.sample_hypergraph, HypergraphManager.hypergraphs)

        HypergraphManager.remove_hypergraph(self.sample_hypergraph)
        self.assertNotIn(self.sample_hypergraph, HypergraphManager.hypergraphs)

    # TEST: Getters
    # ----------------------------------------------------------
    def test_get_graph_by_node_id_returns_correct_hypergraph(self):
        self.sample_hypergraph.add_node(self.sample_node)
        HypergraphManager.add_hypergraph(self.sample_hypergraph)

        graph = HypergraphManager.get_graph_by_node_id(self.sample_node.id)
        self.assertEqual(graph, self.sample_hypergraph)

    def test_get_graph_by_source_node_id_handles_union_properly(self):
        self.sample_node.union(self.sample_node_)
        self.sample_hypergraph.add_hypergraph_source(self.sample_node)
        HypergraphManager.add_hypergraph(self.sample_hypergraph)

        result = HypergraphManager.get_graph_by_source_node_id(self.sample_node_.id)
        self.assertEqual(result, self.sample_hypergraph)

    def test_get_graph_by_hyper_edge_id_returns_correct_hypergraph(self):
        self.sample_hypergraph.add_edge(self.sample_hyper_edge)
        HypergraphManager.add_hypergraph(self.sample_hypergraph)

        graph = HypergraphManager.get_graph_by_hyper_edge_id(self.sample_hyper_edge.id)
        self.assertEqual(graph, self.sample_hypergraph)

    def test_get_graphs_by_canvas_id_returns_all_matching_graphs(self):
        g1 = Hypergraph(canvas_id=5)
        g2 = Hypergraph(canvas_id=5)
        g3 = Hypergraph(canvas_id=99)

        HypergraphManager.add_hypergraph(g1)
        HypergraphManager.add_hypergraph(g2)
        HypergraphManager.add_hypergraph(g3)

        result = HypergraphManager.get_graphs_by_canvas_id(5)
        self.assertIn(g1, result)
        self.assertIn(g2, result)
        self.assertNotIn(g3, result)

    # TEST: Union Nodes
    # ----------------------------------------------------------
    def test_union_nodes_combines_hypergraphs(self):
        node_a = Node(1)
        node_b = Node(2)

        graph_a = Hypergraph(canvas_id=1)
        graph_b = Hypergraph(canvas_id=1)
        graph_a.add_node(node_a)
        graph_b.add_node(node_b)

        HypergraphManager.add_hypergraph(graph_a)
        HypergraphManager.add_hypergraph(graph_b)

        node_a.union = MagicMock()
        node_b.get_united_with_nodes = MagicMock(return_value=[])

        with patch.object(HypergraphManager, "get_node_by_node_id", return_value=node_b):
            HypergraphManager.union_nodes(node_a, node_b.id)

        self.assertIn(node_b, list(HypergraphManager.hypergraphs)[0].get_all_nodes())
        self.assertIn(node_a, list(HypergraphManager.hypergraphs)[0].get_all_nodes())
        self.assertEqual(len(HypergraphManager.hypergraphs), 1)

    # TEST: Edge Connect (input/output) TODO
    # ----------------------------------------------------------
    def test_connect_node_with_input_creates_new_edge_if_none_exists(self):
        node = HypergraphManager.create_new_node(1, 999)
        graph = HypergraphManager.get_graph_by_node_id(node.id)

        HypergraphManager.connect_node_with_input_hyper_edge(node, hyper_edge_id=111)
        self.assertTrue(any(node in edge.target_nodes.values() for edge in graph.get_all_hyper_edges()))
        self.assertIn(111, graph.edges)

    def test_connect_node_with_output_creates_new_edge_if_none_exists(self):
        node = HypergraphManager.create_new_node(2, 888)
        graph = HypergraphManager.get_graph_by_node_id(node.id)

        HypergraphManager.connect_node_with_output_hyper_edge(node, hyper_edge_id=222)
        self.assertTrue(any(node in edge.source_nodes.values() for edge in graph.get_all_hyper_edges()))
        self.assertIn(222, graph.edges)

    # TEST: Node/Edge Removal – Requires internal graph state
    # ----------------------------------------------------------
    def test_remove_node_splits_hypergraph_correctly(self):
        # Create three nodes: A -- B -- C (A connected to B, B connected to C)
        node_a = Node(1)
        node_b = Node(2)
        node_c = Node(3)

        node_a.union(node_b)
        node_b.union(node_c)

        hypergraph = Hypergraph(canvas_id=123)
        hypergraph.add_nodes([node_a, node_b, node_c])
        hypergraph.add_hypergraph_source(node_a)

        HypergraphManager.add_hypergraph(hypergraph)

        HypergraphManager.remove_node(2)

        self.assertEqual(len(HypergraphManager.hypergraphs), 2)

        all_nodes = [list(graph.get_all_nodes()) for graph in HypergraphManager.hypergraphs]
        all_node_ids = sorted([node.id for nodes in all_nodes for node in nodes])
        self.assertEqual(all_node_ids, [1, 3])

    def test_remove_hyper_edge_splits_hypergraph_correctly(self):
        # Create hypergraph: A -- B -- EDGE -- C (A connected to B, B connected to EDGE, EDGE connected to C)
        node_a = HypergraphManager.create_new_node(1, 123)
        node_b = HypergraphManager.create_new_node(2, 123)
        HypergraphManager.union_nodes(node_a, 2)
        node_c = HypergraphManager.create_new_node(3, 123)

        HypergraphManager.connect_node_with_output_hyper_edge(node_b, 12)
        HypergraphManager.connect_node_with_input_hyper_edge(node_c, 12)

        HypergraphManager.remove_hyper_edge(12)

        hypergraph_with_two_nodes = HypergraphManager.get_graph_by_node_id(node_a.id)
        hypergraph_with_one_node = HypergraphManager.get_graph_by_node_id(node_c.id)

        self.assertEqual(2, len(HypergraphManager.hypergraphs))
        self.assertEqual([node_c], hypergraph_with_one_node.get_all_nodes())
        self.assertEqual([node_a, node_b], hypergraph_with_two_nodes.get_all_nodes())

    # TEST: Swap edge ID
    # ----------------------------------------------------------
    def test_swap_hyper_edge_id_delegates_to_hypergraph(self):
        graph = Hypergraph(canvas_id=1)
        graph.swap_hyper_edge_id = MagicMock()
        graph.edges = {10: HyperEdge(10)}

        HypergraphManager.add_hypergraph(graph)

        with patch.object(HypergraphManager, "get_graph_by_hyper_edge_id", return_value=graph):
            HypergraphManager.swap_hyper_edge_id(prev_id=10, new_id=20)

        graph.swap_hyper_edge_id.assert_called_once_with(10, 20)
