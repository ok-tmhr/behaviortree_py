from behaviortree_py.node import ActionNodeBase, NodeStatus


class SaySomething(ActionNodeBase):
    def tick(self):
        print("Robot says:", self.message)
        return NodeStatus.SUCCESS


class ThinkWhatToSay(ActionNodeBase):
    def tick(self):
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_file = Path(__file__, "..", "bt/blackboard_and_ports.json").resolve()

    tree = BehaviorTreeFactory.create_tree_from_file(bt_file.as_posix())
    tree.tick_while_running()
