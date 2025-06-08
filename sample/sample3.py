from behaviortree_py.node import ActionNodeBase, NodeStatus


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


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_path = Path(__file__).with_name("bt/schema.json")
    tree = BehaviorTreeFactory.create_tree(bt_path.as_posix())

    status = NodeStatus.RUNNING
    while status == NodeStatus.RUNNING:
        print("tick once")
        status = tree.tick()
    print("tree finished", status.name)
