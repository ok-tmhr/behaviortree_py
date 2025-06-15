from random import random

from behaviortree_py.node import (
    NodeStatus,
    SyncActionNode,
)


class IsDoorOpen(SyncActionNode):
    def tick(self):
        if random() > 0.5:
            print("Door is open")
            return NodeStatus.SUCCESS
        print("Door is closed")
        return NodeStatus.FAILURE


class OpenDoor(SyncActionNode):
    def tick(self):
        if random() > 0.8:
            print("The door got opened")
            return NodeStatus.SUCCESS
        print("The door won't open")
        return NodeStatus.FAILURE


class EnterRoom(SyncActionNode):
    def tick(self):
        print("Enter the room")
        return NodeStatus.SUCCESS


class CloseDoor(SyncActionNode):
    def tick(self):
        print("Close the door")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory
    from behaviortree_py.node import NodeStatus

    bt_file = Path(__file__).parent / "bt/decorators.json"

    tree = BehaviorTreeFactory.create_tree_from_file(bt_file.as_posix())

    s = NodeStatus.RUNNING
    while s == NodeStatus.RUNNING:
        print("tick once")
        s = tree.tick()
    print("The action finished", s.name)
