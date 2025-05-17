class IdGenerator:
    # id_counter: dict[type, int] = dict()  # key is class type, and value is the last created object id
    id_counter = -1

    @staticmethod
    def id(obj):
        # new_id = IdGenerator.id_counter.get(type(obj), -1) + 1
        # IdGenerator.id_counter[type(obj)] = new_id
        # return new_id
        IdGenerator.id_counter += 1  # TODO temp solution
        return IdGenerator.id_counter
