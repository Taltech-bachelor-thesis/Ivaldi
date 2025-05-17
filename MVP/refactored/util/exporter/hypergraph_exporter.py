from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.util.exporter.exporter import Exporter


class HypergraphExporter(Exporter):

    def create_file_content(self, filename: str) -> dict:
        """Create the hypergraph dictionary content of the file to be exported"""
        canvas_id = self.canvas.id
        graphs = HypergraphManager.get_graphs_by_canvas_id(canvas_id)
        return {"hypergraphs": [graph.to_dict() for graph in graphs]}
