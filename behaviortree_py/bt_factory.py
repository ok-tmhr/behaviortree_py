import json
from copy import deepcopy
from typing import Any

from node import ControlNode, DecoratorNode, NodeStatus, TreeNode


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
        with open(path, encoding="utf8") as f:
            json.load(f, object_hook=cls.json_hook)
        cls.resolve()
        return cls.tree[cls.main_tree_to_execute]


if __name__ == "__main__":
    from pathlib import Path

    import bt

    bt

    path = Path(__file__, "..", "subtrees.json").resolve()
    tree = BehaviorTreeFactory.create_tree(path.as_posix())
    status = NodeStatus.RUNNING
    while status == NodeStatus.RUNNING:
        print("tick once")
        status = tree.tick()
    print("completed", status.name)
