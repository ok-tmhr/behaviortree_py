from behaviortree_py.node import NodeStatus, SyncActionNode


class SaySomething(SyncActionNode):
    def tick(self):
        message = str(self.get_input("message", None))
        print(message)
        return NodeStatus.SUCCESS


class OpenGripper(SyncActionNode):
    def tick(self):
        print("open gripper")
        return NodeStatus.SUCCESS


class ApproachObject(SyncActionNode):
    def tick(self):
        print("approach object")
        return NodeStatus.SUCCESS


class CloseGripper(SyncActionNode):
    def tick(self):
        print("close gripper")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_path = Path(__file__, "..", "bt/schema.json")
    tree = BehaviorTreeFactory.create_tree_from_file(bt_path.as_posix())

    status = NodeStatus.RUNNING
    while status == NodeStatus.RUNNING:
        print("tick once")
        status = tree.tick()
    print("tree finished", status.name)
