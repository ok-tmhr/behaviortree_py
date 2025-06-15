import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from . import control, decorator
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

    def __init__(self, child: TreeNode, ID: str, name: str | None = None, **kwargs):
        super().__init__(child, name, **kwargs)
        self._tree_id = ID
        self.child.parent = self

    def tick(self) -> NodeStatus:
        return self.child.tick()

    def tick_while_running(self):
        status = self.tick()
        while status == NodeStatus.RUNNING:
            status = self.tick()
        return status


class SubTree(NodeBase):
    child: TreeNode

    def __init__(self, child: TreeNode, ID: str, name: str | None = None, **kwargs):
        super().__init__(None, name, **kwargs)
        self._tree_id = ID

    def tick(self) -> NodeStatus:
        return self.child.tick()

    def update(self, child: TreeNode):
        self.child = deepcopy(child)
        self.child.parent = self


class BehaviorTreeFactory:
    tree: dict[str, Tree] = {}
    btcpp_format: int = 4
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
                match x := stack.pop():
                    case ControlNode():
                        stack.extend(x.child)
                    case DecoratorNode():
                        stack.append(x.child)
                    case SubTree():
                        x.update(cls.tree[x.tree_id])
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

    # def register_simple_condition(self, ID: str, callback: Callable[[], NodeStatus]):
    #     TreeNode.register_simple_condition(ID, callback)

    def register_simple_action(self, ID: str, callback: Callable[[], NodeStatus]):
        NodeLibrary.register_simple_action(ID, callback)
