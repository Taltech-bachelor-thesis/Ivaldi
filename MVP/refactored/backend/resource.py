from MVP.refactored.backend.types.connection_info import ConnectionInfo


class Resource:
    """Resource is a backend representation of wire and spider."""

    def __init__(self, resource_id):
        self.id = resource_id
        self.connections: list[ConnectionInfo] = []
        self.left_connection: list[ConnectionInfo] = []
        self.right_connection: list[ConnectionInfo] = []
        self.spider_connection: list[ConnectionInfo] = []
        self.spider = False
        self.parent = None

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def add_left_connection(self, connection):
        if connection not in self.left_connection:
            self.left_connection.append(connection)

    def add_right_connection(self, connection):
        if connection not in self.right_connection:
            self.right_connection.append(connection)

    def add_spider_connection(self, connection):
        if not self.spider:
            if connection not in self.spider_connection:
                self.spider_connection.append(connection)
        else:
            # if resource is spider, all connections have the same id as spider so we don't have if
            # and all spider connections should be in order by index
            self.spider_connection.insert(connection.index, connection)

    def remove_spider_connection_by_index(self, index: int):
        is_found_connection_with_index = False
        to_be_removed: ConnectionInfo | None = None
        for connection in self.spider_connection:
            if connection.index == index:
                to_be_removed = connection
                is_found_connection_with_index = True
            elif is_found_connection_with_index:  # From all connections that come after the removed one, is needed to subtract index
                connection.index -= 1
        if to_be_removed is not None:
            self.spider_connection.remove(to_be_removed)

    def get_left_connections(self) -> list[ConnectionInfo]:
        """Return left connections sorted by index.
        Wire will have only one item in the list
        """
        return sorted(self.left_connection, key=lambda connection: connection.index)

    def get_right_connections(self):
        """Return right connections sorted by index.
        Wire will have only one item in the list
        """
        return sorted(self.right_connection, key=lambda connection: connection.index)

    def get_spider_connections(self):
        return self.spider_connection

    def to_dict(self):
        return {
            "id": self.id,
            "connections": map(lambda c: c.to_list(), self.connections)
        }

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.id == other.id
        return False

    @classmethod
    def from_dict(cls, data):
        resource = cls(data["id"])
        resource.connections = map(lambda c: ConnectionInfo.from_list(c), data.get("connections"))
        return resource
