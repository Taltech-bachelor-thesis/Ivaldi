from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager


class HypergraphNotation:

    def get_all_hypergraph_notations(self) -> str:
        hypergraphs = HypergraphManager.hypergraphs
        return "\n\n".join([str(hypergraph) for hypergraph in hypergraphs])
