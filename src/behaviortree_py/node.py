from abc import ABC, abstractmethod
from collections.abc import Set
from enum import Enum, auto
from functools import partial
from typing import Any, Callable, ClassVar, Protocol, Self, Type, TypeGuard


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class Node(Protocol):
    parent: Self
    name: str

    def __init__(self, name: str, **kwargs): ...

    def tick(self) -> NodeStatus: ...


class TreeNode(ABC):
    __node_type: ClassVar[dict[str, Type[Node]]] = {}

    def __init__(self, name: str | None = None, **kwargs):
        self.name = name or self.__class__.__name__
        self.port = Port()

    @abstractmethod
    def tick(self) -> NodeStatus:
        pass

    @classmethod
    def register(cls):
        print("register", cls.get_id(), cls.__name__)
        TreeNode.__node_type[cls.get_id()] = cls

    @classmethod
    def get_id(cls) -> str:
        return str(getattr(cls, f"_{cls.__name__}__id", cls.__name__))

    @classmethod
    def create(cls, ID: str, **kwargs) -> Node:
        if arg := kwargs.get(ID):
            return cls.__node_type[ID](arg, **kwargs)
        return cls.__node_type[ID](**kwargs)

    @classmethod
    def find_node_type(cls, keys: Set[str]):
        if nt := keys & cls.__node_type.keys():
            return set(nt).pop()

    @staticmethod
    def register_simple_condition(ID: str, callback: Callable[[], NodeStatus]):
        class SimpleCondition:
            def __init__(self, name: str | None = None, **kwargs):
                self.tick = callback
                self.name = name or ID

        TreeNode.__node_type[ID] = SimpleCondition

    @staticmethod
    def register_simple_action(ID: str, callback: Callable[[], NodeStatus]):
        class SimpleAction:
            def __init__(self, name: str | None = None, **kwargs):
                self.tick = callback
                self.name = name or ID

        TreeNode.__node_type[ID] = SimpleAction


class LeafNode(TreeNode):
    pass


class ActionNode(LeafNode):
    pass


class DecoratorNode(TreeNode):
    def __init__(self, child: TreeNode, **kwargs):
        super().__init__(**kwargs)
        self.child = child

    def __init_subclass__(cls):
        super().register()


class ControlNode(TreeNode):
    __id = "Control"

    def __init__(self, children: list[TreeNode], **kwargs):
        super().__init__(**kwargs)
        self.children = children
        self._index = 0

    def __init_subclass__(cls):
        super().register()


class ConditionNode(LeafNode):
    pass


class SequenceNode(ControlNode):
    __id = "Sequence"

    def tick(self) -> NodeStatus:
        s = self.children[self._index].tick()
        if s == NodeStatus.SUCCESS and self._index < len(self.children) - 1:
            self._index += 1
            return NodeStatus.RUNNING
        return s


class FallbackNode(ControlNode):
    __id = "Fallback"

    def tick(self) -> NodeStatus:
        s = self.children[self._index].tick()
        if s == NodeStatus.FAILURE and self._index < len(self.children) - 1:
            self._index += 1
            return NodeStatus.RUNNING
        return s


class Inverter(DecoratorNode):
    def tick(self) -> NodeStatus:
        match self.child.tick():
            case NodeStatus.SUCCESS:
                return NodeStatus.FAILURE
            case NodeStatus.FAILURE:
                return NodeStatus.SUCCESS
            case s:
                return s


class RetryUntilSuccessful(DecoratorNode):
    def __init__(self, child: TreeNode, num_attempts: int, **kwargs):
        super().__init__(child, **kwargs)
        self.num_attempts = num_attempts
        self._attempt = 0

    def tick(self) -> NodeStatus:
        self._attempt += 1
        s = self.child.tick()
        if s == NodeStatus.FAILURE and self._attempt < self.num_attempts:
            return NodeStatus.RUNNING
        return s


class Blackboard:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get_input(self, key: str):
        return self._data[key]

    def set_output(self, key: str, value: Any):
        self._data[key] = value


class Port:
    def __init__(self, board: Blackboard, data: dict[str, Any]):
        self._data = data
        self._board = board

    def get_input(self, port_name: str, default: Any):
        value = self._data.get(port_name, default)
        if self.closed(value):
            return self._board.get_input(value[1:-1])
        return value

    def set_output(self, port_name: str, value: Any):
        key = self._data.get(port_name)
        if isinstance(key, str) and self.closed(key):
            self._board.set_output(key[1:-1], value)

    @staticmethod
    def closed(value: Any, closure="{}") -> TypeGuard[str]:
        return isinstance(value, str) and value[:: len(value) - 1] == closure


class ActionNodeBase(ActionNode):
    def __init__(self, name: str | None = None, **kwargs):
        super().__init__(name, **kwargs)

    def __init_subclass__(cls):
        super().register()
