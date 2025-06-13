from collections import defaultdict
from typing import Any, TypeGuard


class Blackboard:
    _data: defaultdict[str, dict[str, Any]] = defaultdict(dict)

    @classmethod
    def get_input(cls, tree_id: str, key: str):
        return cls._data[tree_id][key]

    @classmethod
    def set_output(cls, tree_id, key: str, value: Any):
        cls._data[tree_id][key] = value


class Port:
    def __init__(self, tree_id: str, data: dict[str, Any]):
        self._data = data
        self._id = tree_id

    def get_input(self, port_name: str, default: Any):
        value = self._data.get(port_name, default)
        if self.closed(value):
            return Blackboard.get_input(self._id, value[1:-1])
        return value

    def set_output(self, port_name: str, value: Any):
        key = self._data.get(port_name)
        if isinstance(key, str) and self.closed(key):
            Blackboard.set_output(self._id, key[1:-1], value)

    @staticmethod
    def closed(value: Any, closure="{}") -> TypeGuard[str]:
        return isinstance(value, str) and value[:: len(value) - 1] == closure
