import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from . import control, decorator
from .node import ControlNode, DecoratorNode, Node, NodeLibrary, NodeStatus, TreeNode

# class Tree:
#     def __init__(self, ID: str, root: TreeNode | None):
#         self.id_ = ID
#         self.root = root

#     def tick(self) -> NodeStatus:
#         if self.root:
#             return self.root.tick()
#         raise AttributeError("No root found")

#     def tick_while_running(self):
#         status = self.tick()
#         while status == NodeStatus.RUNNING:
#             status = self.tick()
#         return status


class BehaviorTreeFactory:
    tree: dict[str, TreeNode] = {}
    btcpp_format: int = 4
    main_tree_to_execute = "MainTree"
    bt_path: str = ""

    @classmethod
    def json_hook(cls, obj: dict[str, Any]):
        match obj:
            case {"include": x}:
                rel_path = Path(cls.bt_path).with_name(x)
                with open(rel_path, encoding="utf8") as f:
                    return json.load(f, object_hook=cls.json_hook)
            case {"BTCPP_format": x}:
                cls.btcpp_format = x
            case {"BehaviorTree": x, "ID": y}:
                cls.tree[y] = NodeLibrary.create_node(**obj)
                return cls.tree[y]
            case {"SubTree": x, "ID": y}:
                NodeLibrary.register_simple_action(
                    y + "-SubTree", lambda: NodeStatus.SUCCESS
                )
                child = NodeLibrary.create_node(child=None, ID=y + "-SubTree")
                return NodeLibrary.create_node(child=child, **obj)
            case _:
                return NodeLibrary.create_node(**obj)

    @classmethod
    def resolve(cls):
        parent: Node | None = None
        for t in cls.tree.values():
            stack: list[Node] = [t]
            while stack:
                match x := stack.pop():
                    case ControlNode():
                        stack.extend(x.children)
                        parent = x
                    case DecoratorNode():
                        stack.append(x.child)
                        parent = x
                    case TreeNode():
                        if parent:
                            parent.child = deepcopy(cls.tree[x._tree_id])
                    case _:
                        pass

    @classmethod
    def create_tree_from_file(cls, path: str):
        cls.bt_path = path
        with open(path, encoding="utf8") as f:
            json.load(f, object_hook=cls.json_hook)
        cls.resolve()
        return cls.tree[cls.main_tree_to_execute]

    # def register_simple_condition(self, ID: str, callback: Callable[[], NodeStatus]):
    #     TreeNode.register_simple_condition(ID, callback)

    def register_simple_action(self, ID: str, callback: Callable[[], NodeStatus]):
        NodeLibrary.register_simple_action(ID, callback)
