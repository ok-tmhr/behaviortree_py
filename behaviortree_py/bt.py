import json
from typing import Any

from node import ActionNodeBase, NodeStatus, TreeNode


class SaySomething(ActionNodeBase):
    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def tick(self):
        print(self.message)
        return NodeStatus.SUCCESS


class OpenGripper(ActionNodeBase):
    def tick(self):
        print("open gripper")
        return NodeStatus.SUCCESS


class ApproachObject(ActionNodeBase):
    def tick(self):
        print("approach object")
        return NodeStatus.SUCCESS


class CloseGripper(ActionNodeBase):
    def tick(self):
        print("close gripper")
        return NodeStatus.SUCCESS


def json_hook(obj: dict[str, Any]):
    if nt := TreeNode.find_node_type(obj.keys()):
        return TreeNode.create(nt, **obj)
    match obj:
        case {"BehaviorTree": x}:
            return x
        case {"ID": x}:
            return TreeNode.create(**obj)
        case _:
            return obj


if __name__ == "__main__":
    with open(
        "D:\\kokur\\GitHub\\python_workspace\\src\\behaviortree_py\\behaviortree_py\\schema.json",
        encoding="utf8",
    ) as f:
        bt = json.load(f, object_hook=json_hook)
        from pprint import pprint

        pprint(bt)

    status = NodeStatus.RUNNING
    tree = bt["root"][0]
    while status == NodeStatus.RUNNING:
        print("tick once")
        status = tree.tick()
    print("tree finished", status.name)
