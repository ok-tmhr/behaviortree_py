from collections import defaultdict
from typing import Any, Protocol, Self, TypeGuard, runtime_checkable


@runtime_checkable
class ConvertProtocol[T](Protocol):
    @classmethod
    def convert_from_string(cls, string: str) -> T: ...


def convert_from_string(cls: type, string: str):
    if isinstance(cls, ConvertProtocol):
        return cls.convert_from_string(string)
    return cls(string)


class Expected[T]:
    __value: T | None
    __error: str

    def __init__(self, value: Any, exp: type[T]):
        if isinstance(value, exp):
            self.__value = value
            self.__error = ""
        elif isinstance(value, str):
            try:
                self.__value = convert_from_string(exp, value)
                self.__error = ""
            except Exception as e:
                self.__value = None
                self.__error = str(e)
        else:
            self.__value = None
            self.__error = f"Expected value must be a {exp.__name__}, otherwise must convert with {exp.__name__}.convert_from_string."

    def __bool__(self):
        return self.value is not None

    @property
    def error(self):
        return self.__error

    @property
    def value(self) -> T:
        if self.__value is None:
            raise ValueError(self.__error)
        return self.__value


class Blackboard:
    _data: dict[str, Any] = {}

    def __getitem__(self, key: str):
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value


# class Port:
#     def __init__(self, tree_id: str, data: dict[str, Any]):
#         self._data = data
#         self._id = tree_id

#     def get_input(self, port_name: str, expected: type, default: Any):
#         value = self._data.get(port_name, default)
#         if self.closed(value):
#             value = Blackboard.get_input(self._id, value[1:-1])
#         if self.closed(value, "''"):
#             value = expected.convert_from_string(value.strip("'"))
#         return Expected(value, None)

#     def set_output(self, port_name: str, value: Any):
#         key = self._data.get(port_name)
#         if self.closed(key):
#             Blackboard.set_output(self._id, key[1:-1], value)
#         elif isinstance(key, str) and self.closed(value, "''"):
#             Blackboard.set_output(self._id, key, value)

#     @staticmethod
#     def closed(value: Any, closure="{}") -> TypeGuard[str]:
#         return isinstance(value, str) and value[:: len(value) - 1] == closure


class NodeConfig:
    def __init__(self):
        self._blackboard = Blackboard()

    def _get_input(self, port: dict[str, Any], name: str, default=None):
        port_value = port.get(name, default)
        if isinstance(port_value, str) and NodeConfig.is_closed(port_value):
            return self._blackboard[port_value[1:-1]]
        return port_value

    def _set_output(self, port: dict[str, Any], name: str, value: Any):
        port_value = port.get(name)
        if isinstance(port_value, str) and NodeConfig.is_closed(port_value):
            self._blackboard[port_value[1:-1]] = value

    @staticmethod
    def is_closed(value: str, closure="{}"):
        return value[:: len(value) - 1] == closure
