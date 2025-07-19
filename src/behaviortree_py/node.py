import inspect
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, ClassVar, Protocol, TypeVar, runtime_checkable

from . import scripting
from .bt import Expected, NodeConfig

T = TypeVar("T")


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()
    IDLE = auto()


@runtime_checkable
class TreeNode(Protocol):
    parent: "TreeNode"
    _config: NodeConfig

    def tick(self) -> NodeStatus: ...

    def get_input(
        self, port: str, default: Any, expected: type[T] | None = None
    ) -> Expected[T]: ...

    def set_output(self, port: str, value: Any) -> None: ...


class NodeBase(ABC):
    parent: TreeNode

    def __init__(
        self,
        child: None | TreeNode | list[TreeNode],
        name: str | None = None,
        config=None,
        **kwargs,
    ):
        self.child = child
        self.name = name or self.__class__.__name__
        self._config = config or NodeConfig()
        self._port = kwargs

    @abstractmethod
    def tick(self) -> NodeStatus: ...

    def get_input(
        self, port: str, default: Any, expected: type[T] | None = None
    ) -> Expected[T]:
        value = self._config._get_input(self._port, port, default)
        return Expected(value, expected)

    def set_output(self, port: str, value: Any) -> None:
        self._config._set_output(self._port, port, value)

    def __init_subclass__(cls):
        if not inspect.isabstract(cls):
            NodeLibrary.register_node_type(cls)


class NodeLibrary:
    _node_type: ClassVar[dict[str, type[TreeNode]]] = {}
    _enums: dict[str, Enum | int] = {e.name: e for e in NodeStatus}

    @classmethod
    def register_node_type(cls, node_type: type[TreeNode]):
        node_key = getattr(
            node_type, f"_{node_type.__name__}__alias", node_type.__name__
        )
        cls._node_type[node_key] = node_type

    @classmethod
    def create_node(cls, **kwargs):
        type_name = kwargs.keys() & cls._node_type
        match len(type_name):
            case 0:
                raise IndexError(
                    f"Node type not found in {kwargs}. Registered types are {[key for key in cls._node_type]}"
                )
            case 1:
                id_ = type_name.pop()
                return cls._node_type[id_](kwargs.pop(id_), **kwargs)
            case _:
                raise ValueError(f"Multiple node type found. {type_name}")

    @classmethod
    def get_node_type(cls, ID: str):
        return cls._node_type[ID]

    @classmethod
    def register_simple_action(cls, ID: str, callback: Callable[[], NodeStatus]):
        class SimpleAction(NodeBase):
            parent: TreeNode
            __alias = ID

            def __init__(
                self, child=None, name: str | None = None, config=None, **kwargs
            ):
                self.__callback = callback
                self.name = name or ID
                self._config = config or NodeConfig()

            def tick(self):
                return self.__callback()

        cls.register_node_type(SimpleAction)

    @classmethod
    def register_simple_condition(cls, ID: str, callback: Callable[[], NodeStatus]):
        class SimpleCondition(NodeBase):
            parent: TreeNode
            __alias = ID

            def __init__(
                self, child=None, name: str | None = None, config=None, **kwargs
            ):
                self.__callback = callback
                self.name = name or ID
                self._config = config or NodeConfig()

            def tick(self):
                return self.__callback()

        cls.register_node_type(SimpleCondition)

    @classmethod
    def register_scripting_enums(cls, enum: type[Enum]):
        for item in enum:
            cls._enums[item.name] = item

    @classmethod
    def register_scripting_enum(cls, name: str, value: int):
        cls._enums[name] = value


class ControlNode(NodeBase):
    child: list[TreeNode]

    def __init__(self, child: list[TreeNode], name=None, config=None, **kwargs):
        super().__init__(child, name, config, **kwargs)
        self._index = 0

        for c in child:
            c.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class DecoratorNode(NodeBase):
    child: TreeNode

    def __init__(self, child: TreeNode, name=None, config=None, **kwargs):
        super().__init__(child, name, config, **kwargs)
        child.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class ActionNode(NodeBase):
    __alias = "Action"

    def __new__(cls, child: None, ID: str, name=None, config=None, **kwargs):
        node_type = NodeLibrary.get_node_type(ID)
        self = super().__new__(node_type)
        self.name = name or node_type.__name__
        self._config = config
        self._port = kwargs
        return self

    def __init__(self, child: None, ID: str, name=None, config=None, **kwargs):
        pass

    def tick(self): ...


class SyncActionNode(NodeBase):
    def __init__(self, child, name=None, config=None, **kwargs):
        super().__init__(None, name, config, **kwargs)

    def __init_subclass__(cls):
        NodeLibrary.register_node_type(cls)


class Script(NodeBase):
    def tick(self):
        code = str(self._port.pop("code"))
        parser = scripting.get_parser(
            NodeLibrary._enums, self._config._blackboard._data
        )
        parser.parse(code)
        return NodeStatus.SUCCESS


class StatefulActionNode(NodeBase):
    status: NodeStatus | None

    def __init__(self, child, name=None, config=None, **kwargs):
        super().__init__(None, name, config, **kwargs)
        self.status = None

    def __init_subclass__(cls):
        NodeLibrary.register_node_type(cls)

    def on_start(self):
        return NodeStatus.SUCCESS

    def on_running(self): ...

    def on_halted(self):
        pass

    def tick(self):
        match self.status:
            case None:
                self.status = self.on_start()
            case NodeStatus.RUNNING:
                self.status = self.on_running()
            case _:
                pass
        return self.status
