from enum import auto, StrEnum

class ActionType(StrEnum):
    WIRE_CREATE = auto(), # canvas_id, start and end connections
    WIRE_DELETE = auto(),

    SPIDER_CREATE = auto(),
    SPIDER_PARENT_CREATE = auto(),
    SPIDER_DELETE = auto(),

    BOX_ADD_INNER_LEFT = auto(),
    BOX_ADD_INNER_RIGHT = auto(),
    BOX_REMOVE_INNER_LEFT = auto(),
    BOX_REMOVE_INNER_RIGHT = auto(),

    BOX_ADD_LEFT = auto(),
    BOX_ADD_RIGHT = auto(),
    BOX_REMOVE_LEFT = auto(),
    BOX_REMOVE_RIGHT = auto(),
    BOX_REMOVE_ALL_CONNECTIONS = auto(),

    BOX_CREATE = auto(),
    BOX_DELETE = auto(),

    BOX_COMPOUND = auto(),
    BOX_ATOMIC = auto(),
    BOX_SUB_BOX = auto(),

    BOX_ADD_OPERATOR = auto(),
    BOX_SET_FUNCTION = auto(),

    BOX_SWAP_ID = auto(),
    BOX_SWAP_CONNECTION_ID = auto(),

    DIAGRAM_ADD_INPUT = auto(),
    DIAGRAM_ADD_OUTPUT = auto(),
    DIAGRAM_REMOVE_INPUT = auto(),
    DIAGRAM_REMOVE_OUTPUT = auto(),

    SUB_DIAGRAM_CREATE = auto(), # canvas_id(old), new_canvas_id, resource_ids(wires and spiders), generator_ids(boxes)
