from queue import Queue

import autopep8

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.code_generation.code_inspector import CodeInspector
from MVP.refactored.backend.diagram import Diagram
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.resource import Resource
from MVP.refactored.backend.types.connection_info import ConnectionInfo
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas


class CodeGenerator:
    @classmethod
    def generate_code(cls, canvas: CustomCanvas) -> str:
        """
        Generates Python code based on the structure and functional elements of the provided canvas and related canvasses.

        This method processes a set of box functions associated with the given canvas, extracts global statements, helper
        functions, and main functions, renames them for uniqueness, and constructs the final composite Python script.
        The resulting script is formatted using the autopep8 library and written to a file named "diagram.py".
        The formatted code is also returned by the method as a string.

        Arguments:
            canvas (CustomCanvas): The main canvas from which the function hierarchy
                and code elements are derived.

        Returns:
            str: The generated and auto formatted Python code as a single string.
        """
        hypergraphs_on_this_canvas: list[Hypergraph] = HypergraphManager.get_graphs_by_canvas_id(canvas.id)

        box_functions: set[BoxFunction] = set()
        for hypergraph in hypergraphs_on_this_canvas:
            box_functions.update(cls.get_all_box_functions(hypergraph))

        box_functions_items_names: dict[BoxFunction, set[str]] = cls.get_box_functions_items_names(box_functions)

        (global_statements,
         helper_functions,
         main_functions,
         main_functions_new_names) = CodeInspector.rename(box_functions_items_names)

        # imports
        file_content: str = "\n".join(set(imp for f in box_functions for imp in f.imports))
        # global statements
        file_content += "".join(global_statements) + "\n"
        # helper functions
        file_content += "\n\n".join(helper_functions) + "\n\n"
        # functions
        file_content += "\n\n".join(main_functions)
        # main functions
        for i, hypergraph in enumerate(hypergraphs_on_this_canvas):
            func_name = f"main_{i}"
            file_content += "\n\n" + cls.construct_main_function(hypergraph,
                                                                 main_functions_new_names,
                                                                 func_name,
                                                                 canvas.receiver)

        return autopep8.fix_code(file_content)

    @classmethod
    def get_all_box_functions(cls, hypergraph: Hypergraph) -> set[BoxFunction]:
        """
        Retrieve all BoxFunction objects from a given hypergraph.

        This method traverses the hypergraph to collect all BoxFunction objects
        associated with its hyper edges. If a hyper edge is compound, it recursively
        explores the nested hypergraphs to gather BoxFunction objects from them.
        """
        box_functions: set[BoxFunction] = set()
        for hyper_edge in hypergraph.get_all_hyper_edges():
            if hyper_edge.is_compound():
                for subgraph in hyper_edge.get_hypergraphs_inside():
                    box_functions.update(cls.get_all_box_functions(subgraph))
            else:
                box_functions.add(hyper_edge.box_function)
        return box_functions

    @classmethod
    def get_box_functions_items_names(cls, box_functions: set[BoxFunction]) -> dict[BoxFunction, set[str]]:
        """
        Retrieve a mapping of BoxFunction objects to the set of names of globals and
        functions associated with each BoxFunction.
        """
        box_functions_items_names: dict[BoxFunction, set[str]] = {}  # {box_func: set (of all names of globals and functions)}

        for box_function in box_functions:
            variables = set()
            variables.update(CodeInspector.get_names(box_function.global_statements))
            variables.update(CodeInspector.get_names(box_function.helper_functions))
            variables.add(box_function.main_function_name)

            box_functions_items_names[box_function] = variables
        return box_functions_items_names

    @classmethod
    def construct_main_function(cls,
                                hypergraph: Hypergraph,
                                renamed_functions: dict[BoxFunction, str],
                                func_name: str,
                                receiver: Receiver
                                ) -> str:
        """
        Construct the main function for a given hypergraph.

        This method generates the complete main function for a hypergraph, including its
        definition, body, and return statement. It processes the hypergraph's structure,
        resolves input and output nodes, and ensures that all hyper edges are executed
        in the correct order.
        """
        diagram_inputs_as_nodes: list[Node] = cls.get_sorted_diagram_inputs(hypergraph, receiver, hypergraph.canvas_id)

        function_definition, name_map = cls.create_definition_of_main_function(func_name, receiver, diagram_inputs_as_nodes)

        hyper_edge_queue: Queue[HyperEdge] = Queue()
        cls.get_queue_of_hyper_edges(hypergraph, hyper_edge_queue)

        function_body, name_map = cls.create_main_function_content(hyper_edge_queue, renamed_functions, name_map, receiver)

        function_return = cls.create_main_function_return(receiver, hypergraph, name_map)

        return function_definition + function_body + function_return

    @classmethod
    def create_definition_of_main_function(cls,
                                           func_name: str,
                                           receiver: Receiver,
                                           diagram_inputs_as_nodes: list[Node]
                                           ) -> (str, dict[int, str]):
        """
        Create the definition of a main function for the given hypergraph.

        This method generates the function signature for a main function, including
        input parameters based on the source nodes of the provided diagram.
        """
        definition: str = f"def {func_name}("

        node_and_hyper_edge_to_variable_name: dict[int, str] = dict()
        index: int = -1

        for node in diagram_inputs_as_nodes:
            actual_hash: int = cls.get_input_actual_node_group_hash(node, receiver)
            index += 1
            var_name = f"input_{index}"
            definition += f"{var_name}, "
            node_and_hyper_edge_to_variable_name[actual_hash] = var_name

        definition = (definition[:-2] if index >= 0 else definition) + "):"

        return definition, node_and_hyper_edge_to_variable_name

    @classmethod
    def create_main_function_content(cls,
                                     queue: Queue[HyperEdge],
                                     renamed_functions: dict[BoxFunction, str],
                                     node_and_hyper_edge_to_variable_name: dict[int, str],
                                     receiver: Receiver
                                     ) -> (str, dict[int, str]):
        """
        Generate the content of the main function for a given hypergraph.

        This method processes a queue of hyper edges and generates Python code
        for executing each hyper edge in the correct order. It maps source nodes
        to input variables and target nodes to output variables or tuple elements.
        """
        main_function_content = ""
        index = 0
        while not queue.empty():
            hyper_edge = queue.get()
            variable = f"res_{index}"
            variable_definition = f"{variable} = {renamed_functions[hyper_edge.get_box_function()]}("

            for source_node in hyper_edge.get_source_nodes():
                actual_hash: int = cls.get_output_actual_node_group_hash(source_node, receiver)
                variable_definition += f"{node_and_hyper_edge_to_variable_name[actual_hash]}, "
            variable_definition = variable_definition[:-2] + ")"
            main_function_content += f"\n\t{variable_definition}"

            if len(hyper_edge.get_target_nodes()) > 1:
                for i, target_node in enumerate(hyper_edge.get_target_nodes()):
                    actual_hash: int = cls.get_input_actual_node_group_hash(target_node, receiver)
                    if actual_hash not in node_and_hyper_edge_to_variable_name:
                        node_and_hyper_edge_to_variable_name[actual_hash] = f"{variable}[{i}]"
            else:
                target_node = hyper_edge.get_target_nodes()[0]
                actual_hash: int = cls.get_input_actual_node_group_hash(target_node, receiver)
                node_and_hyper_edge_to_variable_name[actual_hash] = variable

            index += 1
        return main_function_content, node_and_hyper_edge_to_variable_name

    @classmethod
    def create_main_function_return(cls,
                                    receiver: Receiver,
                                    hypergraph: Hypergraph,
                                    node_and_hyper_edge_to_variable_name: dict[int, str]
                                    ) -> str:
        """
        Generate the return statement for the main function of a given hypergraph.

        This method constructs the return statement for the main function by iterating
        over the output nodes of the hypergraph. It ensures that each output node is
        mapped to its corresponding variable name and includes it in the return statement.
        """
        main_function_return = "\n\treturn "
        added: set[int] = set()
        for output in cls.get_sorted_diagram_outputs(hypergraph, receiver, hypergraph.canvas_id):
            if (cls.get_output_actual_node_group_hash(output, receiver) in node_and_hyper_edge_to_variable_name
                    and cls.get_output_actual_node_group_hash(output, receiver) not in added):
                main_function_return += f"{node_and_hyper_edge_to_variable_name[cls.get_output_actual_node_group_hash(output, receiver)]}, "
                added.add(cls.get_output_actual_node_group_hash(output, receiver))
        main_function_return = main_function_return[:-2 if len(added) > 0 else -1]
        return main_function_return

    @classmethod
    def get_sorted_diagram_inputs(cls, hypergraph: Hypergraph, receiver: Receiver, canvas_id: str) -> list[Node]:
        """
        Retrieve and sort the input nodes of a diagram based on their index.

        This method fetches the source nodes of a given hypergraph that are connected
        to the inputs of a diagram. It then sorts these nodes according to the index
        of their corresponding input connections in the diagram.
        """
        return sorted(
            (s for s in hypergraph.get_hypergraph_source()
             if receiver.diagrams[canvas_id].get_input_by_id(s.id) is not None),
            key=lambda s: receiver.diagrams[canvas_id].get_input_by_id(s.id).index
        )

    @classmethod
    def get_sorted_diagram_outputs(cls, hypergraph: Hypergraph, receiver: Receiver, canvas_id: str) -> list[Node]:
        """
        Retrieve and sort the input nodes of a diagram based on their index.

        This method fetches the source nodes of a given hypergraph that are connected
        to the inputs of a diagram. It then sorts these nodes according to the index
        of their corresponding input connections in the diagram.
        """
        return sorted(
            (s for s in hypergraph.get_hypergraph_target()
             if receiver.diagrams[canvas_id].get_output_by_id(s.id) is not None),
            key=lambda s: receiver.diagrams[canvas_id].get_output_by_id(s.id).index
        )

    @classmethod
    def get_input_actual_node_group_hash(cls, node: Node, receiver: Receiver) -> int:
        """
        Retrieve the actual node group hash for a given input node.

        This method determines the actual node group hash by traversing compound hyper edges
        and resolving nested connections within sub-diagrams. If the node is part of a compound
        hyper edge, it recursively explores the sub-diagram to find the corresponding deeper node
        and retrieves its group hash. Otherwise, it returns the node's own group hash.
        """
        for hyper_edge in node.get_output_hyper_edges():
            if hyper_edge.is_compound():
                con_i: int = next(
                    (k for k, v in hyper_edge.source_nodes.items() if v.node_group_hash() == node.node_group_hash()),
                    None)
                sub_diagram: Diagram = receiver.diagrams[hyper_edge.id]
                sub_diagram_input: ConnectionInfo = sub_diagram.get_input_by_index(con_i)
                resource: Resource = next(r for r in sub_diagram.resources if
                                          sub_diagram_input in (r.get_left_connections() + r.get_right_connections()))
                deeper_node: Node = HypergraphManager.get_node_by_node_id(resource.id)
                return cls.get_input_actual_node_group_hash(deeper_node, receiver)
        return node.node_group_hash()

    @classmethod
    def get_output_actual_node_group_hash(cls, node: Node, receiver: Receiver) -> int:
        """
        Retrieve the actual node group hash for a given output node.

        This method determines the actual node group hash by traversing compound hyper edges
        and resolving nested connections within sub-diagrams. If the node is part of a compound
        hyper edge, it recursively explores the sub-diagram to find the corresponding deeper node
        and retrieves its group hash. Otherwise, it returns the node's own group hash.
        """
        for hyper_edge in node.get_input_hyper_edges():
            if hyper_edge.is_compound():
                con_i: int = next(
                    (k for k, v in hyper_edge.target_nodes.items() if v.node_group_hash() == node.node_group_hash()),
                    None)
                sub_diagram: Diagram = receiver.diagrams[hyper_edge.id]
                sub_diagram_output: ConnectionInfo = sub_diagram.get_output_by_index(con_i)
                resource: Resource = next(r for r in sub_diagram.resources if
                                          sub_diagram_output in (r.get_left_connections() + r.get_right_connections()))
                deeper_node: Node = HypergraphManager.get_node_by_node_id(resource.id)
                return cls.get_output_actual_node_group_hash(deeper_node, receiver)
        return node.node_group_hash()

    @classmethod
    def get_queue_of_hyper_edges(cls,
                                 hypergraph: Hypergraph,
                                 hyper_edge_queue: Queue[HyperEdge],
                                 seen_hyper_edges: set[HyperEdge] = None
                                 ):
        """
        Generate a queue of hyper edges for a given hypergraph in topological order.

        This method processes the hypergraph to ensure that all hyper edges are added
        to the queue in an order that respects their dependencies. It recursively explores
        nested hypergraphs and ensures that each hyper edge is processed only once.
        """
        if seen_hyper_edges is None:
            seen_hyper_edges = set()

        nodes_with_inputs: set[Node] = set(hypergraph.get_hypergraph_source())
        to_check: list[HyperEdge] = hypergraph.get_all_hyper_edges()
        hyper_edge_input_count_check: dict[HyperEdge, int] = {}

        while to_check:
            to_check_new: list[HyperEdge] = []
            for hyper_edge in to_check:
                if hyper_edge in seen_hyper_edges:
                    continue

                if hyper_edge not in hyper_edge_input_count_check:
                    hyper_edge_input_count_check[hyper_edge] = 0
                for node in hyper_edge.get_source_nodes():
                    if node in nodes_with_inputs:
                        hyper_edge_input_count_check[hyper_edge] += 1
                if hyper_edge_input_count_check[hyper_edge] >= len(hyper_edge.get_source_nodes()):
                    # Process this edge first
                    if hyper_edge.box_function is not None:
                        hyper_edge_queue.put(hyper_edge)
                    seen_hyper_edges.add(hyper_edge)
                    for target_node in hyper_edge.get_target_nodes():
                        nodes_with_inputs.add(target_node)
                        nodes_with_inputs.update(target_node.get_united_with_nodes())

                    # Then recursive process inside graphs
                    for subgraph in hyper_edge.get_hypergraphs_inside():
                        cls.get_queue_of_hyper_edges(subgraph, hyper_edge_queue, seen_hyper_edges)
                else:
                    to_check_new.append(hyper_edge)
                    hyper_edge_input_count_check[hyper_edge] = 0

            if to_check == to_check_new:
                break
            to_check = to_check_new
