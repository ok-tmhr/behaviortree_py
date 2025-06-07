from random import random

from node import (
    ActionNode,
    NodeStatus,
)


class IsDoorOpen(ActionNode):
    def tick(self):
        if random() > 0.5:
            print("Door is open")
            return NodeStatus.SUCCESS
        print("Door is closed")
        return NodeStatus.FAILURE


class OpenDoor(ActionNode):
    def tick(self):
        if random() > 0.8:
            print("The door got opened")
            return NodeStatus.SUCCESS
        print("The door won't open")
        return NodeStatus.FAILURE


class EnterRoom(ActionNode):
    def tick(self):
        print("Enter the room")
        return NodeStatus.SUCCESS


class CloseDoor(ActionNode):
    def tick(self):
        print("Close the door")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from node import (
        FallbackNode,
        RetryUntilSuccessful,
        SequenceNode,
    )

    tree = SequenceNode(
        None,
        FallbackNode(
            None,
            IsDoorOpen(),
            RetryUntilSuccessful(None, OpenDoor(), num_attempts=5),
        ),
        EnterRoom(),
        CloseDoor(),
    )

    s = NodeStatus.RUNNING
    while s == NodeStatus.RUNNING:
        print("tick once")
        s = tree.tick()
    print("The action finished", s.name)
