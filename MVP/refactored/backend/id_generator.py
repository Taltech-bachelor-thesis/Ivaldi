class IdGenerator:
    # id_counter: dict[type, int] = dict()  # key is class type, and value is the last created object id
    id_counter = -1
    ids_in_use: set[int] = set()

    @staticmethod
    def id(obj):
        # new_id = IdGenerator.id_counter.get(type(obj), -1) + 1
        # IdGenerator.id_counter[type(obj)] = new_id
        # return new_id
        IdGenerator.id_counter += 1  # TODO temp solution
        new_id = IdGenerator.id_counter
        if IdGenerator.id_counter in IdGenerator.ids_in_use:
            new_id = IdGenerator.id(obj)
        IdGenerator.ids_in_use.add(new_id)
        return new_id

    @staticmethod
    def use_id(id: int):
        IdGenerator.ids_in_use.add(id)
