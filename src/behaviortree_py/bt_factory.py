import json
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from . import control, decorator
from .bt import Blackboard, NodeConfig
from .node import (
    ControlNode,
    DecoratorNode,
    NodeBase,
    NodeLibrary,
    NodeStatus,
    TreeNode,
)


class Tree(NodeBase):
    __alias = "BehaviorTree"
    child: TreeNode

    def __init__(self, child: TreeNode, ID: str, name=None, config=None, **kwargs):
        super().__init__(child, name, config, **kwargs)
        self._id = ID
        self.child.parent = self

    def tick(self) -> NodeStatus:
        return self.child.tick()

    def tick_while_running(self):
        status = self.tick()
        while status == NodeStatus.RUNNING:
            status = self.tick()
        return status

    def root_node(self):
        return self.child


class SubTree(NodeBase):
    child: TreeNode

    def __init__(self, child: TreeNode, ID: str, name=None, config=None, **kwargs):
        super().__init__(None, name, config, **kwargs)
        self._id = ID
        self._status = NodeStatus.IDLE

    def tick(self) -> NodeStatus:
        if self._status == NodeStatus.IDLE:
            self._status = NodeStatus.RUNNING
            for key, parent_board_key in self._port.items():
                if value := self.parent._config.get_board_value(parent_board_key):
                    self._config.set_board_value("{" + key + "}", value)
        s = self.child.tick()
        if s == NodeStatus.SUCCESS:
            for key, parent_board_key in self._port.items():
                if self.parent._config.get_board_value(parent_board_key) is None:
                    self.parent._config.set_board_value(
                        parent_board_key, self._config.get_board_value("{" + key + "}")
                    )
        self._status = s
        return s

    def update(self, child: TreeNode):
        self.child = deepcopy(child)
        self.child.parent = self
        self._config = self.child._config


class BehaviorTreeFactory:
    tree: dict[str, Tree] = {}
    btcpp_format = 4
    main_tree_to_execute = "MainTree"
    bt_path: Path

    @classmethod
    def json_hook(cls, obj: dict[str, Any], config: NodeConfig):
        match obj:
            case {"include": x}:
                include_path = Path(x)
                if include_path.is_absolute():
                    return cls.load_tree_from_json(include_path)
                return cls.load_tree_from_json(cls.bt_path.parent / include_path)
            case {"BTCPP_format": x}:
                cls.btcpp_format = x
            case {"BehaviorTree": x, "ID": y}:
                cls.tree[y] = NodeLibrary.create_node(**obj, config=config)
                return cls.tree[y]
            case _:
                return NodeLibrary.create_node(**obj, config=config)

    @classmethod
    def resolve(cls):
        for t in cls.tree.values():
            stack = [t.child]
            while stack:
                match x := stack.pop():
                    case ControlNode():
                        stack.extend(x.child)
                    case DecoratorNode():
                        stack.append(x.child)
                    case SubTree():
                        x.update(cls.tree[x._id].root_node())
                    case _:
                        pass

    @classmethod
    def load_tree_from_json(cls, path: str | Path):
        cls.bt_path = Path(path)
        with open(path, encoding="utf8") as f:
            return json.load(f, object_hook=lambda x: cls.json_hook(x, NodeConfig()))

    @classmethod
    def create_tree_from_file(cls, path: str):
        cls.load_tree_from_json(path)
        cls.resolve()
        if len(cls.tree) == 1:
            return cls.tree.popitem()[1]
        return cls.tree[cls.main_tree_to_execute]

    @staticmethod
    def register_simple_condition(ID: str, callback: Callable[[], NodeStatus]):
        NodeLibrary.register_simple_condition(ID, callback)

    @staticmethod
    def register_simple_action(ID: str, callback: Callable[[], NodeStatus]):
        NodeLibrary.register_simple_action(ID, callback)

    @classmethod
    def register_behavior_tree_from_file(cls, path: str):
        cls.load_tree_from_json(path)

    @classmethod
    def create_tree(cls, ID: str):
        cls.resolve()
        return cls.tree[ID]

    @staticmethod
    def register_scripting_enums(enum: type[Enum]):
        NodeLibrary.register_scripting_enums(enum)

    @staticmethod
    def register_scripting_enum(name: str, value: int):
        NodeLibrary.register_scripting_enum(name, value)


def print_tree_recursively(root: TreeNode):
    def _print_node(node: TreeNode, depth=0):
        name = getattr(
            node, f"_{node.__class__.__name__}__alias", node.__class__.__name__
        )
        print("   " * depth, name)
        match node:
            case ControlNode():
                for c in node.child:
                    _print_node(c, depth + 1)
            case DecoratorNode():
                _print_node(node.child, depth + 1)
            case SubTree():
                _print_node(node.child, depth + 1)

    _print_node(root)
