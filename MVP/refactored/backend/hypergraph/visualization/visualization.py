import math
import matplotlib.pyplot as plt
import hypernetx as hnx
import matplotlib.patches as patches
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node


class Visualization:

    @classmethod
    def create_visualization_of_hypergraphs(cls, canvas_id: int) -> plt.Figure:
        """
        Create a visualization of all hypergraphs associated with a given canvas ID.

        This method retrieves all hypergraphs linked to the specified canvas ID and
        generates a grid of subplots, each displaying a visualization of a hypergraph.
        If no hypergraphs are found, it returns None.
        """
        hypergraphs: list[Hypergraph] = HypergraphManager.get_graphs_by_canvas_id(canvas_id)
        n = len(hypergraphs)
        if n == 0:
            return None

        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)

        fig, axs = plt.subplots(rows, cols, figsize=(cols * 8, rows * 8))
        fig.patch.set_facecolor('white')
        axs = axs.flatten() if n > 1 else [axs]

        for i, hypergraph in enumerate(hypergraphs):
            outer_ax = axs[i]
            outer_ax.set_xticks([])
            outer_ax.set_yticks([])
            outer_ax.set_title(f"Hypergraph {hypergraph.id}", fontsize=14)
            outer_ax.set_frame_on(False)

            rect = patches.Rectangle(
                (0, 0), 1, 1,
                transform=outer_ax.transAxes,
                linewidth=2,
                edgecolor='black',
                facecolor='none',
                zorder=10
            )
            outer_ax.add_patch(rect)

            inset_box = [0.125, 0.125, 0.75, 0.75]  # [x0, y0, width, height]
            inset_ax = outer_ax.inset_axes(inset_box)
            inset_ax.axis('off')

            cls.create_visualization_of_hypergraph(hypergraph, ax=inset_ax)

        for j in range(len(hypergraphs), len(axs)):
            axs[j].set_visible(False)

        plt.tight_layout()
        return fig

    @classmethod
    def create_visualization_of_hypergraph(cls, hypergraph: Hypergraph, ax=None) -> None:
        """
        Create a visualization of a single hypergraph.

        This method generates a visualization of the given hypergraph, including its
        nodes and edges. Nodes are color-coded based on their roles (source or target),
        and a legend is added to the plot.
        """
        edge_dict = {}
        node_roles = {}
        for edge in hypergraph.get_all_hyper_edges():
            source_nodes: list[Node] = edge.get_source_nodes()
            target_nodes: list[Node] = edge.get_target_nodes()

            united_source_nodes: list[Node] = [n for src in source_nodes for n in src.get_united_with_nodes()]
            united_target_nodes: list[Node] = [n for tgt in target_nodes for n in tgt.get_united_with_nodes()]

            all_nodes: list[Node] = set(source_nodes + target_nodes + united_source_nodes + united_target_nodes)

            edge_dict[edge.id] = {node.id for node in all_nodes}

            for node in all_nodes:
                if node not in node_roles:
                    node_roles[node] = set()
                if node in hypergraph.get_hypergraph_source():
                    node_roles[node].add('source')
                if node in hypergraph.get_hypergraph_target():
                    node_roles[node].add('target')

        color_map = {
            frozenset(['source']): 'darkgreen',
            frozenset(['target']): 'red',
        }

        node_facecolors = {
            node.id: color_map.get(frozenset(roles), 'black')
            for node, roles in node_roles.items()
        }

        H = hnx.Hypergraph(edge_dict)
        hnx.draw(H, with_node_labels=True, with_edge_labels=True, ax=ax,
                 nodes_kwargs={"facecolors": node_facecolors})

        # Add legend
        if ax is not None:
            legend_elements = [
                patches.Patch(facecolor='darkgreen', label='Source Node'),
                patches.Patch(facecolor='red', label='Target Node'),
            ]
            ax.legend(handles=legend_elements, loc='lower left', fontsize=10, frameon=True)
