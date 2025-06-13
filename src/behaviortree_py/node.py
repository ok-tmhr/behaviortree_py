from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, ClassVar, Protocol, TypeGuard, runtime_checkable

from .bt import Port


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


@runtime_checkable
class Node(Protocol):
    parent: "Node"

    def tick(self) -> NodeStatus: ...

    def get_tree_id(self) -> str: ...


class NodeLibrary:
    _node_type: ClassVar[dict[str, type[Node]]] = {}

    @classmethod
    def register_node_type(cls, node_type: type[Node]):
        alias = getattr(node_type, f"_{node_type.__name__}__alias", node_type.__name__)
        if isinstance(alias, str):
            cls._node_type[alias] = node_type
        else:
            for name in alias:
                cls._node_type[name] = node_type

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
                print(kwargs)
                return cls._node_type[id_](kwargs.get(id_), **kwargs)
            case _:
                raise ValueError(f"Multiple node type found. {type_name}")

    @classmethod
    def get_node_type(cls, ID: str):
        return cls._node_type[ID]

    @classmethod
    def register_simple_action(cls, ID: str, callback: Callable[[], NodeStatus]):
        class SimpleAction:
            __alias = ID
            parent: Node

            def __init__(self, name: str | None = None, **kwargs):
                self.tick = callback
                self.name = name or ID
                self._port = kwargs

            def get_tree_id(self) -> str:
                return self.parent.get_tree_id()

        cls.register_node_type(SimpleAction)


class NodeBase(ABC):
    parent: Node
    _tree_id: str

    def __init__(self, child: None, name: str | None = None, **kwargs):
        self.name = name or self.__class__.__name__
        self._port = kwargs

    @abstractmethod
    def tick(self) -> NodeStatus: ...

    def get_input(self, port: str, default: Any) -> Any:
        return Port(self.get_tree_id(), self._port).get_input(port, default)

    def set_output(self, port: str, value: Any) -> None:
        Port(self.get_tree_id(), self._port).set_output(port, value)

    def get_tree_id(self) -> str:
        if not hasattr(self, "_tree_id"):
            self._tree_id = self.parent.get_tree_id()
        return self._tree_id


class TreeNode(NodeBase):
    __alias = "BehaviorTree"
    parent: Node

    def __init__(self, child: Node, ID: str, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.parent = self
        self.child = child
        self._tree_id = ID

        self.child.parent = self

    def tick(self) -> NodeStatus:
        return self.child.tick()

    def tick_while_running(self):
        status = self.tick()
        while status == NodeStatus.RUNNING:
            status = self.tick()
        return status

    def get_tree_id(self) -> str:
        if self._tree_id is None:
            raise ValueError("Tree ID not assigned")
        return self._tree_id


class ControlNode(NodeBase):
    def __init__(self, children: list[Node], name: str | None = None, **kwargs):
        super().__init__(None, name, **kwargs)
        self.children = children
        self._index = 0

        for c in self.children:
            c.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class DecoratorNode(NodeBase):
    def __init__(self, child: Node, name: str | None = None, **kwargs):
        super().__init__(None, name, **kwargs)
        self.child = child
        self.child.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class ActionNode(NodeBase):
    __alias = "Action"

    def __new__(cls, child: None, ID: str, name=None, **kwargs):
        node_type = NodeLibrary.get_node_type(ID)
        self = super().__new__(node_type)
        self.name = name or node_type.__name__
        self._port = kwargs
        return self

    def __init__(self, child: None, ID: str, name=None, **kwargs):
        pass

    def tick(self):
        return super().tick()


class ActionNodeBase(NodeBase):
    def __init_subclass__(cls):
        NodeLibrary.register_node_type(cls)


NodeLibrary.register_node_type(TreeNode)
NodeLibrary.register_node_type(ActionNode)
