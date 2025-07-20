import json
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from .core import (
    NodeConfig,
    NodeLibrary,
    NodeStatus,
    TreeNode,
)
from .node import ControlNode, DecoratorNode, NodeBase

__all__ = "Tree", "BehaviorTreeFactory", "print_tree_recursively", "NodeStatus"


class Tree(NodeBase):
    __alias = "BehaviorTree"
    child: TreeNode

    def __init__(self, child: TreeNode, ID: str, name=None, **kwargs):
        super().__init__(child, name, **kwargs)
        self._id = ID
        self.child.parent = self
        self._config = NodeConfig()

    def tick(self) -> NodeStatus:
        return self.child.tick()

    def tick_while_running(self):
        status = self.tick()
        while status == NodeStatus.RUNNING:
            status = self.tick()
        return status

    def root_node(self):
        return self.child

    def _update(self):
        pass


class SubTree(NodeBase):
    child: TreeNode

    def __init__(self, child: TreeNode, ID: str, name=None, **kwargs):
        super().__init__(None, name, **kwargs)
        self._id = ID
        self._status = NodeStatus.IDLE

    def tick(self) -> NodeStatus:
        if self._status == NodeStatus.IDLE:
            self.map_(self.parent._config, self._config, self.swap(self._port))
        self._status = self.child.tick()
        if self._status == NodeStatus.SUCCESS:
            self.map_(self._config, self.parent._config, self._port)
        return self._status

    def copy_tree(self, child: TreeNode):
        self.child = deepcopy(child)
        self.child.parent = self
        self._config = NodeConfig()

    def map_(self, from_: NodeConfig, to: NodeConfig, mapping: dict[str, str]):
        keys = from_._blackboard.keys() & mapping.keys()
        for key in keys:
            to._set_output(mapping, key, from_._blackboard[key])

    def swap(self, mapping: dict[str, str]):
        return {v.strip("{}"): "{" + k + "}" for k, v in mapping.items()}

    def _update(self):
        pass


class BehaviorTreeFactory:
    tree: dict[str, Tree] = {}
    btcpp_format = 4
    main_tree_to_execute = "MainTree"
    bt_path: Path

    @classmethod
    def json_hook(cls, obj: dict[str, Any]):
        match obj:
            case {"include": x}:
                include_path = Path(x)
                if include_path.is_absolute():
                    return cls.load_tree_from_json(include_path)
                return cls.load_tree_from_json(cls.bt_path.parent / include_path)
            case {"BTCPP_format": x}:
                cls.btcpp_format = x
            case {"BehaviorTree": x, "ID": y}:
                cls.tree[y] = NodeLibrary.create_node(**obj)
                return cls.tree[y]
            case _:
                return NodeLibrary.create_node(**obj)

    @classmethod
    def resolve(cls):
        for t in cls.tree.values():
            stack = [t.child]
            while stack:
                x = stack.pop()
                x._update()
                match x:
                    case ControlNode():
                        stack.extend(x.child)
                    case DecoratorNode():
                        stack.append(x.child)
                    case SubTree():
                        x.copy_tree(cls.tree[x._id].root_node())
                        stack.append(x.child)
                    case _:
                        pass

    @classmethod
    def load_tree_from_json(cls, path: str | Path):
        cls.bt_path = Path(path)
        with open(path, encoding="utf8") as f:
            return json.load(f, object_hook=cls.json_hook)

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
