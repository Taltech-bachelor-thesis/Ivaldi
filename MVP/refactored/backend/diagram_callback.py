import logging

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.GeneratorType import GeneratorType
from MVP.refactored.backend.types.connection_info import ConnectionInfo
from MVP.refactored.backend.types.connection_side import ConnectionSide
from MVP.refactored.backend.diagram import Diagram
from MVP.refactored.backend.generator import Generator
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.resource import Resource

logging.basicConfig(level=logging.INFO, format='%(asc_time)s - %(level_name)s - %(message)s')
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self):
        self.listener = True
        # self.diagram = Diagram()
        self.diagrams: dict[int, Diagram] = {}  # key is canvas_id where diagram located
        logger.info("Receiver initialized.")

    def add_new_canvas(self, canvas_id: int):
        self.diagrams[canvas_id] = Diagram()
        return self.diagrams[canvas_id]

    def receiver_callback(self, action: ActionType, **kwargs):
        resource_id = kwargs.get('resource_id')
        start_connection: ConnectionInfo | None = kwargs.get('start_connection')
        end_connection: ConnectionInfo | None = kwargs.get('end_connection')
        connection_id = kwargs.get('connection_id')
        generator_id = kwargs.get('generator_id')
        generator_side = kwargs.get('generator_side')
        connection_nr = kwargs.get('connection_nr')
        connection_side: ConnectionSide = kwargs.get('connection_side')
        operator = kwargs.get('operator')
        canvas_id = kwargs.get('canvas_id')
        new_id = kwargs.get('new_id')
        new_canvas_id = kwargs.get('new_canvas_id')
        resource_ids: list[int] = kwargs.get('resource_ids')
        generator_ids: list[int] = kwargs.get('generator_ids')
        box_function: BoxFunction = kwargs.get('box_function')

        logger.info(f"receiver_callback invoked with action: {action}, kwargs: {kwargs}")
        if action == ActionType.WIRE_CREATE:
            new_node = HypergraphManager.create_new_node(resource_id, canvas_id)

            new_resource = self.create_new_resource(resource_id, canvas_id)
            self.add_connections_to_resource(new_resource, [start_connection, end_connection], canvas_id,
                                             node=new_node)

        elif action == ActionType.WIRE_DELETE:
            self.delete_resource(resource_id, canvas_id)

            HypergraphManager.remove_node(resource_id)
        elif action == ActionType.SPIDER_CREATE:
            new_node = HypergraphManager.create_new_node(resource_id, canvas_id)

            new_resource = self.create_new_resource(resource_id, canvas_id, spider=True)
            new_resource.spider = True
            self.add_connections_to_resource(new_resource, [start_connection, end_connection], canvas_id,
                                             node=new_node)
        elif action == ActionType.SPIDER_PARENT_CREATE:
            pass
        elif action == ActionType.SPIDER_DELETE:
            self.delete_resource(resource_id, canvas_id, spider=True)

            HypergraphManager.remove_node(resource_id)
        elif action == ActionType.BOX_ADD_INNER_LEFT:
            return
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_left_inner(
                ConnectionInfo(connection_nr, ConnectionSide.INNER_LEFT, connection_id, related_object=box))
        elif action == ActionType.BOX_ADD_INNER_RIGHT:
            return
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_right_inner(
                ConnectionInfo(connection_nr, ConnectionSide.INNER_RIGHT, connection_id, related_object=box))
        elif action == ActionType.BOX_REMOVE_INNER_LEFT:
            return
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_left_inner(connection_id)
        elif action == ActionType.BOX_REMOVE_INNER_RIGHT:
            return
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_right_inner(connection_id)
        elif action == ActionType.BOX_ADD_LEFT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_left(ConnectionInfo(connection_nr, ConnectionSide.LEFT, connection_id, related_object=box))
        elif action == ActionType.BOX_ADD_RIGHT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_right(ConnectionInfo(connection_nr, ConnectionSide.RIGHT, connection_id, related_object=box))
        elif action == ActionType.BOX_REMOVE_LEFT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_left(connection_id)
        elif action == ActionType.BOX_REMOVE_RIGHT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_right(connection_id)
        elif action == ActionType.BOX_REMOVE_ALL_CONNECTIONS:
            box = self.get_generator_by_id(generator_id, canvas_id)
            # TODO handle inner connections
            box.remove_all_right()
            box.remove_all_left()
        elif action == ActionType.BOX_CREATE:
            self.create_new_generator(generator_id, canvas_id)
        elif action == ActionType.BOX_DELETE:
            self.delete_generator(generator_id, canvas_id)

            HypergraphManager.remove_hyper_edge(generator_id)
        elif action == ActionType.BOX_COMPOUND:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_type(GeneratorType.COMPOUND)
            box.set_sub_diagram_id(new_canvas_id)

            hyper_edge = HypergraphManager.get_hyper_edge_by_id(generator_id)
            if hyper_edge:
                hyper_edge.set_sub_diagram_canvas_id(new_canvas_id)
        elif action == ActionType.BOX_ATOMIC:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_type(GeneratorType.ATOMIC)
            box.set_sub_diagram_id(-1)

            hyper_edge = HypergraphManager.get_hyper_edge_by_id(generator_id)
            if hyper_edge:
                hyper_edge.set_sub_diagram_canvas_id(-1)
        elif action == ActionType.BOX_SUB_BOX:
            pass
        elif action == ActionType.BOX_ADD_OPERATOR:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_operand(operator)
        elif action == ActionType.BOX_SET_FUNCTION:
            # TODO maybe set box function to generator too?
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_box_function(box_function)
            hyper_edge = HypergraphManager.get_hyper_edge_by_id(generator_id)
            if hyper_edge:
                hyper_edge.set_box_function(box_function)
        elif action == ActionType.BOX_SWAP_ID:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_id(new_id)

            HypergraphManager.swap_hyper_edge_id(generator_id, new_id)
        elif action == ActionType.BOX_SWAP_CONNECTION_ID:
            pass  # In the original diagram callback that events are not in use. In project there are no occurrences for this event
        elif action == ActionType.DIAGRAM_ADD_INPUT:
            self.diagrams[canvas_id].add_input(ConnectionInfo(connection_nr, connection_side, connection_id))

            HypergraphManager.create_new_node(connection_id, canvas_id)
        elif action == ActionType.DIAGRAM_ADD_OUTPUT:
            self.diagrams[canvas_id].add_output(ConnectionInfo(connection_nr, connection_side, connection_id))

            HypergraphManager.create_new_node(connection_id, canvas_id)
        elif action == ActionType.DIAGRAM_REMOVE_INPUT:
            self.diagrams[canvas_id].remove_input(connection_id)

            HypergraphManager.remove_node(connection_id)
        elif action == ActionType.DIAGRAM_REMOVE_OUTPUT:
            self.diagrams[canvas_id].remove_output(connection_id)

            HypergraphManager.remove_node(connection_id)

    def spider_callback(self, action: str, **kwargs):
        pass

    def wire_callback(self, action: str, **kwargs):
        pass

    def box_callback(self, action: str, **kwargs):
        pass

    def create_new_resource(self, resource_id: int, canvas_id: int, spider: bool = False) -> Resource:
        resource = Resource(resource_id)
        if spider:
            self.diagrams[canvas_id].add_spider(resource)
        else:
            self.diagrams[canvas_id].add_resource(resource)
        return resource

    def delete_resource(self, resource_id: int, canvas_id: int, spider: bool = False):
        if spider:
            self.diagrams[canvas_id].remove_spider_by_id(resource_id)
        else:
            self.diagrams[canvas_id].remove_resource_by_id(resource_id)

    def add_connections_to_resource(self, resource: Resource, connections: list[ConnectionInfo | None], canvas_id: int,
                                    node: Node | None = None):
        for connection in connections:
            if connection is None:
                continue

            if connection.side == ConnectionSide.LEFT:
                if connection.has_box():
                    box = self.get_generator_by_id(connection.get_box_id(), canvas_id)
                    if box is None:
                        # TODO it is sub diagram output, that connection from frontend have box = sub diagram box
                        output = self.get_output_by_id(connection.get_id(), canvas_id)
                        resource.add_left_connection(output)

                        HypergraphManager.union_nodes(node, output.get_id())
                        continue
                    resource.add_left_connection(box.get_left_by_id(
                        connection.get_id()))  # We don't simply add connection from loop (connection in connection),
                    # because we want that box(or input/output) connection and wire connection will be the same object,
                    # if we use from frontend connection, they will differ.
                    hyper_edge = HypergraphManager.connect_node_with_output_hyper_edge(node, box.id)
                    hyper_edge.set_box_function(box.get_box_function())
                    hyper_edge.set_sub_diagram_canvas_id(box.get_sub_diagram_id())
                else:  # it is output
                    output = self.get_output_by_id(connection.get_id(), canvas_id)
                    resource.add_left_connection(output)

                    HypergraphManager.union_nodes(node, output.get_id())
            elif connection.side == ConnectionSide.RIGHT:
                if connection.has_box():
                    box = self.get_generator_by_id(connection.get_box_id(), canvas_id)
                    if box is None:
                        # TODO it is sub diagram input, that connection from frontend have box = sub diagram box
                        diagram_input = self.get_input_by_id(connection.get_id(), canvas_id)
                        resource.add_right_connection(diagram_input)

                        HypergraphManager.union_nodes(node, diagram_input.get_id())
                        continue
                    resource.add_right_connection(box.get_right_by_id(connection.get_id()))

                    hyper_edge = HypergraphManager.connect_node_with_input_hyper_edge(node, box.id)
                    hyper_edge.set_box_function(box.get_box_function())
                    hyper_edge.set_sub_diagram_canvas_id(box.get_sub_diagram_id())
                else:  # it is input
                    diagram_input = self.get_input_by_id(connection.get_id(), canvas_id)
                    resource.add_right_connection(diagram_input)

                    HypergraphManager.union_nodes(node, diagram_input.get_id())
            elif connection.side == ConnectionSide.SPIDER:
                spider = self.get_spider_by_id(connection.get_id(), canvas_id)
                connection.index = len(
                    spider.get_spider_connections())  # we use here that rule, that when we add wire to spider
                connection.set_related_object(spider)
                # it always appends to the last connection
                spider.add_spider_connection(connection)
                resource.add_spider_connection(connection)

                HypergraphManager.union_nodes(node, spider.id)

    def create_new_generator(self, box_id: int, canvas_id: int) -> Generator:
        box = Generator(box_id)
        self.diagrams[canvas_id].add_box(box)
        return box

    def delete_generator(self, box_id: int, canvas_id: int):
        self.diagrams[canvas_id].remove_box_by_id(box_id)

    def get_generator_by_id(self, box_id: int, canvas_id: int) -> Generator:
        return self.diagrams[canvas_id].get_generator_by_id(box_id)

    def get_generators_by_ids(self, generator_ids: list[int], canvas_id: int) -> list[Generator]:
        generators: list[Generator] = []
        for generator_id in generator_ids:
            generator = self.get_generator_by_id(generator_id, canvas_id)
            if generator is not None:
                generators.append(generator)
        return generators

    def get_input_by_id(self, input_id: int, canvas_id: int) -> ConnectionInfo:
        return self.diagrams[canvas_id].get_input_by_id(input_id)

    def get_output_by_id(self, output_id: int, canvas_id: int) -> ConnectionInfo:
        return self.diagrams[canvas_id].get_output_by_id(output_id)

    def get_resource_by_id(self, resource_id: int, canvas_id: int) -> Resource:
        return self.diagrams[canvas_id].get_resource_by_id(resource_id)

    def get_resources_by_ids(self, resource_ids: list[int], canvas_id: int) -> list[Resource]:
        resources: list[Resource] = []
        for resource_id in resource_ids:
            resource = self.get_resource_by_id(resource_id, canvas_id)
            if resource is not None:
                resources.append(resource)
        return resources

    def get_spider_by_id(self, spider_id: int, canvas_id: int) -> Resource | None:
        return self.diagrams[canvas_id].get_spider_by_id(spider_id)

    def get_spiders_by_ids(self, spider_ids: list[int], canvas_id: int) -> list[Resource]:
        resources: list[Resource] = []
        for resource_id in spider_ids:
            spider = self.get_spider_by_id(resource_id, canvas_id)
            if spider is not None:
                resources.append(spider)
        return resources
