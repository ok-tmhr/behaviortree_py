import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .node import ControlNode, DecoratorNode, NodeStatus, TreeNode


class Tree:
    def __init__(self, ID: str, root: TreeNode | None):
        self.id_ = ID
        self.root = root

    def tick(self) -> NodeStatus:
        if self.root:
            return self.root.tick()
        raise AttributeError("No root found")


class BehaviorTreeFactory:
    tree: dict[str, Tree] = {}
    btcpp_format: int = 4
    main_tree_to_execute = "MainTree"
    bt_path: str = ""

    @classmethod
    def json_hook(cls, obj: dict[str, Any]):
        if nt := TreeNode.find_node_type(obj.keys()):
            return TreeNode.create(nt, **obj)
        match obj:
            case {"BehaviorTree": x, "ID": y}:
                tree = Tree(y, x)
                cls.tree[y] = tree
                return tree
            case {"ID": x}:
                return TreeNode.create(**obj)
            case {"BTCPP_format": x, "root": y}:
                cls.btcpp_format = x
            case {"SubTree": x}:
                return Tree(x, None)
            case {"include": x}:
                rel_path = Path(cls.bt_path).with_name(x)
                with open(rel_path, encoding="utf8") as f:
                    return json.load(f, object_hook=cls.json_hook)
            case _:
                return obj

    @classmethod
    def resolve(cls):
        for t in cls.tree.values():
            stack = [t.root]
            while stack:
                match x := stack.pop():
                    case ControlNode():
                        stack.extend(x.children)
                    case DecoratorNode():
                        stack.append(x.child)
                    case Tree():
                        x.root = deepcopy(cls.tree[x.id_])

    @classmethod
    def create_tree(cls, path: str):
        cls.bt_path = path
        with open(path, encoding="utf8") as f:
            json.load(f, object_hook=cls.json_hook)
        cls.resolve()
        return cls.tree[cls.main_tree_to_execute]
