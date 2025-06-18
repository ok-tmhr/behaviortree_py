from behaviortree_py.bt_factory import BehaviorTreeFactory
from behaviortree_py.node import NodeStatus


class CrossDoor:
    def __init__(self):
        self._door_open = False
        self._door_locked = True
        self._pick_attempts = 0

    def is_door_closed(self):
        if self._door_open:
            print("door is open")
            return NodeStatus.FAILURE
        print("door is closed")
        return NodeStatus.SUCCESS

    def pass_through_door(self):
        if self._door_open:
            print("pass through door")
            return NodeStatus.SUCCESS
        print("cannot pass through door")
        return NodeStatus.FAILURE

    def pick_lock(self):
        self._pick_attempts += 1
        if self._pick_attempts > 3:
            print("successfully picked lock")
            self._door_locked = False
            self._door_open = True
            return NodeStatus.SUCCESS
        print("attempt to pick lock")
        return NodeStatus.FAILURE

    def open_door(self):
        if self._door_locked:
            print("door will not open")
            return NodeStatus.FAILURE
        print("open door")
        self._door_open = True
        return NodeStatus.SUCCESS

    def smash_door(self):
        print("smash door")
        self._door_open = True
        return NodeStatus.SUCCESS

    def register_nodes(self, factory: BehaviorTreeFactory):
        factory.register_simple_condition("IsDoorClosed", lambda: self.is_door_closed())

        factory.register_simple_action(
            "PassThroughDoor", lambda: self.pass_through_door()
        )

        factory.register_simple_action("OpenDoor", lambda: self.open_door())

        factory.register_simple_action("PickLock", lambda: self.pick_lock())

        factory.register_simple_condition("SmashDoor", lambda: self.smash_door())


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import print_tree_recursively

    factory = BehaviorTreeFactory()

    cross_door = CrossDoor()
    cross_door.register_nodes(factory)

    bt_path = Path(__file__).parent / "bt/using_subtrees.json"
    factory.register_behavior_tree_from_file(bt_path.as_posix())
    tree = factory.create_tree("MainTree")

    print_tree_recursively(tree.root_node())
    tree.tick_while_running()
