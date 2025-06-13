from behaviortree_py.control import Sequence
from behaviortree_py.node import ActionNodeBase, NodeStatus


class OpenFridge(ActionNodeBase):
    def tick(self):
        print("Open fridge")
        return NodeStatus.SUCCESS


class GrabBeer(ActionNodeBase):
    def tick(self):
        print("Grab beer")
        return NodeStatus.SUCCESS


class CloseFridge(ActionNodeBase):
    def tick(self):
        print("Close fridge")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    tree = Sequence([OpenFridge(), GrabBeer(), CloseFridge()])
    s = NodeStatus.RUNNING
    while s == NodeStatus.RUNNING:
        print("tick once")
        s = tree.tick()
    print("tree finished", s.name)
