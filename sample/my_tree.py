from behaviortree_py.node import ActionNodeBase, NodeStatus


class ApproachObject(ActionNodeBase):
    def tick(self):
        print(self.__class__.__name__ + ":", self.name)
        return NodeStatus.SUCCESS


def CheckBattery() -> NodeStatus:
    print("[ Battery: OK ]")
    return NodeStatus.SUCCESS


class GripperInterface:
    def __init__(self):
        self._open = True

    def open(self):
        self._open = True
        print(self.__class__.__name__ + "::" + self.open.__name__)
        return NodeStatus.SUCCESS

    def close(self):
        print(self.__class__.__name__ + "::" + self.close.__name__)
        self._open = False
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    factory = BehaviorTreeFactory()
    factory.register_simple_action("CheckBattery", CheckBattery)
    gripper = GripperInterface()
    factory.register_simple_action("OpenGripper", gripper.open)
    factory.register_simple_action("CloseGripper", gripper.close)
    bt_path = Path(__file__, "..", "bt/my_tree.json").resolve().as_posix()
    tree = factory.create_tree_from_file(bt_path)

    tree.tick_while_running()

    # [ Battery: OK ]
    # GripperInterface::open
    # ApproachObject: approach_object
    # GripperInterface::close
