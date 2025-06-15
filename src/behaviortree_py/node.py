import inspect
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, ClassVar, Protocol, runtime_checkable

from .bt import Port


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


@runtime_checkable
class TreeNode(Protocol):
    parent: "TreeNode"

    def tick(self) -> NodeStatus: ...

    @property
    def tree_id(self) -> str: ...


class NodeBase(ABC):
    parent: TreeNode

    def __init__(
        self, child: None | TreeNode | list[TreeNode], name: str | None = None, **kwargs
    ):
        self.name = name or self.__class__.__name__
        self._port = kwargs
        self._tree_id = ""
        self.child = child

    @abstractmethod
    def tick(self) -> NodeStatus: ...

    def get_input(self, port: str, default: Any, expected: type):
        return Port(self.tree_id, self._port).get_input(port, default, expected)

    def set_output(self, port: str, value: Any) -> None:
        Port(self.tree_id, self._port).set_output(port, value)

    @property
    def tree_id(self) -> str:
        if not self._tree_id:
            self._tree_id = self.parent.tree_id
        return self._tree_id

    def __init_subclass__(cls):
        if not inspect.isabstract(cls):
            NodeLibrary.register_node_type(cls)


class NodeLibrary:
    _node_type: ClassVar[dict[str, type[TreeNode]]] = {}

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
        class SimpleAction:
            parent: TreeNode
            __alias = ID

            def __init__(self, child=None, name: str | None = None, **kwargs):
                self.tick = callback
                self.name = name or ID

            @property
            def tree_id(self):
                return self.parent.tree_id

        cls.register_node_type(SimpleAction)


class ControlNode(NodeBase):
    child: list[TreeNode]

    def __init__(self, child: list[TreeNode], name: str | None = None, **kwargs):
        super().__init__(child, name, **kwargs)
        self._index = 0

        for c in child:
            c.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class DecoratorNode(NodeBase):
    child: TreeNode

    def __init__(self, child: TreeNode, name: str | None = None, **kwargs):
        super().__init__(child, name, **kwargs)
        child.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class ActionNode(NodeBase):
    __alias = "Action"

    def __new__(cls, child: None, ID: str, name=None, **kwargs):
        node_type = NodeLibrary.get_node_type(ID)
        self = super().__new__(node_type)
        self.name = name or node_type.__name__
        self._port = kwargs
        self._tree_id = ""
        return self

    def __init__(self, child: None, ID: str, name=None, **kwargs):
        pass

    def tick(self): ...


class SyncActionNode(NodeBase):
    def __init__(self, child, name=None, **kwargs):
        super().__init__(None, name, **kwargs)

    def __init_subclass__(cls):
        NodeLibrary.register_node_type(cls)


class Script(NodeBase):
    def tick(self):
        code = str(self._port.pop("code"))
        key, value = code.split(":=")
        self._port["code"] = "{" + key + "}"
        self.set_output("code", value)
        return NodeStatus.SUCCESS
