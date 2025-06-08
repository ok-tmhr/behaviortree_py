from behaviortree_py.node import ActionNode, NodeStatus, SequenceNode


class OpenFridge(ActionNode):
    def tick(self):
        print("Open fridge")
        return NodeStatus.SUCCESS


class GrabBeer(ActionNode):
    def tick(self):
        print("Grab beer")
        return NodeStatus.SUCCESS


class CloseFridge(ActionNode):
    def tick(self):
        print("Close fridge")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    tree = SequenceNode([OpenFridge(), GrabBeer(), CloseFridge()])
    s = NodeStatus.RUNNING
    while s == NodeStatus.RUNNING:
        print("tick once")
        s = tree.tick()
    print("tree finished", s.name)
