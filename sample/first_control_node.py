from behaviortree_py.control import Sequence
from behaviortree_py.node import NodeStatus, SyncActionNode


class OpenFridge(SyncActionNode):
    def tick(self):
        print("Open fridge")
        return NodeStatus.SUCCESS


class GrabBeer(SyncActionNode):
    def tick(self):
        print("Grab beer")
        return NodeStatus.SUCCESS


class CloseFridge(SyncActionNode):
    def tick(self):
        print("Close fridge")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_file = Path(__file__).parent / "bt/first_control_node.json"
    try:
        tree = BehaviorTreeFactory.create_tree_from_file(bt_file.as_posix())
        tree.tick_while_running()
    except Exception as e:
        print(e)
