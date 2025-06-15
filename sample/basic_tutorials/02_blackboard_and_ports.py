from behaviortree_py.node import NodeStatus, SyncActionNode


class SaySomething(SyncActionNode):
    def tick(self):
        message = self.get_input("message", "Nothing to say")
        print("Robot says:", message)
        return NodeStatus.SUCCESS


class ThinkWhatToSay(SyncActionNode):
    def tick(self):
        self.set_output("text", "The answer is 42")
        return NodeStatus.SUCCESS


if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_file = Path(__file__, "..", "bt/blackboard_and_ports.json").resolve()

    tree = BehaviorTreeFactory.create_tree_from_file(bt_file.as_posix())
    tree.tick_while_running()

    # Robot says: hello
    # Robot says: The answer is 42
