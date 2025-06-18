import time
from dataclasses import dataclass

import dummy_nodes

from behaviortree_py.bt_factory import BehaviorTreeFactory
from behaviortree_py.node import NodeStatus, StatefulActionNode

dummy_nodes


@dataclass
class Pose2D:
    x: float
    y: float
    theta: float

    @classmethod
    def convert_from_string(cls, string: str):
        x, y, theta = map(float, string.split(";"))
        return cls(x, y, theta)


class MoveBaseAction(StatefulActionNode):
    __alias = "MoveBase"
    _goal: Pose2D
    _completion_time: float

    def on_start(self):
        msg = self.get_input("goal", None, Pose2D)
        if not msg:
            raise ValueError("missing required input [goal]")
        self._goal = msg.value
        print(
            f"[ MoveBase: SEND REQUEST ]. goal: x={self._goal.x} y={self._goal.y} theta={self._goal.theta}"
        )
        self._completion_time = time.time() + 0.22
        return NodeStatus.RUNNING

    def on_running(self):
        time.sleep(0.01)
        if time.time() >= self._completion_time:
            print("[ MoveBase: FINISHED ]")
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING

    def on_halted(self):
        print("[ MoveBase: ABORTED ]")


if __name__ == "__main__":
    from pathlib import Path

    factory = BehaviorTreeFactory()
    factory.register_simple_condition("BatteryOK", dummy_nodes.CheckBattery)

    bt_path = Path(__file__).parent / "bt/reactive_behaviors.json"
    tree = factory.create_tree_from_file(bt_path.as_posix())

    print("--- ticking")
    status = tree.tick()
    print("--- status:", status.name, "\n")

    while status == NodeStatus.RUNNING:
        time.sleep(0.1)

        print("--- ticking")
        status = tree.tick()
        print("--- status:", status.name, "\n")

    # --- ticking
    # [ Battery: OK ]
    # --- status: RUNNING

    # --- ticking
    # Robot says: mission started...
    # --- status: RUNNING

    # --- ticking
    # [ MoveBase: SEND REQUEST ]. goal: x=1.0 y=2.0 theta=3.0
    # --- status: RUNNING

    # --- ticking
    # --- status: RUNNING

    # --- ticking
    # [ MoveBase: FINISHED ]
    # --- status: RUNNING

    # --- ticking
    # Robot says: mission completed!
    # --- status: SUCCESS
