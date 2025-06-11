import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from MVP.refactored.backend.types.connection_info import ConnectionInfo


class DiagramNotation:

    def __init__(self, diagram):
        self.diagram = diagram
        self.graph = None
        self.hypergraph = None
        self.create_graph()

    def create_graph(self):
        self.graph = nx.MultiDiGraph()
        input_count = 0
        output_count = 0

        for box in self.diagram.boxes:
            box_id = f"box_{box.id}"
            self.graph.add_node(box_id, type='box')

        for wire in self.diagram.resources:
            wire_id = f"wire_{wire.id}"

            if wire.left_connection:
                wire_start: ConnectionInfo = wire.left_connection[0]
            else:
                wire_start: ConnectionInfo = wire.spider_connection[0]

            if wire.right_connection:
                wire_end: ConnectionInfo = wire.right_connection[0]
            else:
                spider_index = 1 if len(wire.spider_connection) > 1 else 0
                wire_end: ConnectionInfo = wire.spider_connection[spider_index]

            self.graph.add_node(wire_id, type='wire')

            if not wire_start.has_box():
                start_box = f'input_{input_count}'
                input_count += 1
            else:
                start_box = f"box_{wire_start.get_box_id()}"

            if not wire_end.has_box():
                end_box = f'output_{output_count}'
                output_count += 1
            else:
                end_box = f"box_{wire_end.get_box_id()}"

            if wire_start.side == 'left':
                self.graph.add_edge(wire_id, start_box, port=wire_start.index, connection_type='input')
                self.graph.add_edge(end_box, wire_id, port=wire_end.index, connection_type='output')
            else:
                self.graph.add_edge(wire_id, end_box, port=wire_end.index, connection_type='output')
                self.graph.add_edge(start_box, wire_id, port=wire_start.index, connection_type='input')

        for spider in self.diagram.spiders:
            spider_id = f"spider_{spider.id}"
            self.graph.add_node(spider_id, type='spider')
            for connection in spider.connections:
                port, box_id, side, con_id = connection
                box_node = f"box_{box_id}"
                edge_id = f"{spider_id}_{box_node}_{port}_{side}"

                if side == 'right':
                    self.graph.add_edge(box_node, spider_id, port=port, connection_type='spider', key=edge_id)
                else:
                    self.graph.add_edge(spider_id, box_node, port=port, connection_type='spider', key=edge_id)

    def visualize_hypergraph(self):
        self.get_hypergraph_figure()
        plt.title('Diagram Graph')
        plt.show(block=True)

    def get_hypergraph_figure(self):
        fig, ax = plt.subplots(figsize=(12, 10))
        pos = nx.spring_layout(self.graph, seed=42)
        node_colors = [self.graph.nodes[n].get('type', 'node') for n in self.graph.nodes]
        color_map = {'box': 'lightblue', 'spider': 'lightcoral', 'wire': 'lightgreen'}

        nx.draw_networkx_nodes(self.graph, pos,
                               node_color=[color_map.get(t, 'grey') for t in node_colors],
                               node_size=700)
        nx.draw_networkx_labels(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos, arrowstyle='-|>', arrowsize=20)

        for i, (u, v, k, d) in enumerate(self.graph.edges(keys=True, data=True)):
            label = d.get('port', '')
            if label is not None:
                x = (pos[u][0] + pos[v][0]) / 2
                y = (pos[u][1] + pos[v][1]) / 2

                offset = (i - len(self.graph[u][v]) / 2) * 0.03
                ax.text(x + offset, y + offset, str(label), color='red', fontsize=12, ha='center')

        return fig

    def get_adjacency_matrix_dense(self):
        adj_matrix = nx.adjacency_matrix(self.graph).todense()
        return np.array(adj_matrix)

    def get_adjacency_matrix_sparse(self):
        adj_matrix_sparse = nx.adjacency_matrix(self.graph)
        return np.array(adj_matrix_sparse)

    def get_adjacency_list(self):
        adj_list = nx.generate_adjlist(self.graph)
        return adj_list

    def get_edge_list(self):
        edge_list = list(self.graph.edges())
        return edge_list

    def get_incidence_matrix(self):
        inc_matrix = nx.incidence_matrix(self.graph).todense()
        return np.array(inc_matrix)

    def get_graph_string(self):
        res = "Nodes:"
        for node, data in self.graph.nodes(data=True):
            res += f"\n{node}: {data}"

        res += "\nEdges:"
        for edge in self.graph.edges(data=True):
            res += f"\n{edge}"
        return res
