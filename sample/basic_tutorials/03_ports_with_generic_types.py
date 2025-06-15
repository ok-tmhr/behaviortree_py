from typing import NamedTuple

from behaviortree_py.node import NodeStatus, SyncActionNode


class Position2D(NamedTuple):
    x: float
    y: float

    @classmethod
    def convert_from_string(cls, args: str):
        parts = args.split(";")
        if len(parts) != 2:
            raise ValueError("Invalid input")
        x, y = map(float, parts)
        return cls(x, y)


class CalculateGoal(SyncActionNode):
    def tick(self):
        my_goal = Position2D(1.1, 2.3)
        self.set_output("goal", my_goal)
        return NodeStatus.SUCCESS


class PrintTarget(SyncActionNode):
    def tick(self):
        target = self.get_input("target", None, Position2D)
        if target is None:
            raise ValueError("error reading port [target]")
        print(f"Target positions: [ {target.x}, {target.y} ]")
        return NodeStatus.SUCCESS


def main():
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_path = Path(__file__).parent / "bt/ports_with_generic_types.json"
    tree = BehaviorTreeFactory.create_tree_from_file(bt_path)
    tree.tick_while_running()


if __name__ == "__main__":
    main()

    # Target positions: [ 1.1, 2.3 ]
    # Target positions: [ -1.0, 3.0 ]
