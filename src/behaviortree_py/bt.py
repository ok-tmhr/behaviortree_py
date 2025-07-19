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

    def __init__(self, value: Any, exp: type[T] | None):
        if exp is None or isinstance(value, exp):
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

    def __contains__(self, key: str):
        return key in self._data

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()


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

    def get_board_value(self, closed_key: str):
        return self._blackboard.get(closed_key[1:-1])

    def set_board_value(self, closed_key: str, value: Any):
        self._blackboard[closed_key[1:-1]] = value
