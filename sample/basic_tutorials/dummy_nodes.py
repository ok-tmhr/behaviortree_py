import time
from dataclasses import dataclass
from typing import Any, NamedTuple

from behaviortree_py.node import NodeStatus, StatefulActionNode, SyncActionNode


class ApproachObject(SyncActionNode):
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


class SaySomething(SyncActionNode):
    def tick(self):
        message = self.get_input("message", "Nothing to say").value
        print("Robot says:", message)
        return NodeStatus.SUCCESS


class ThinkWhatToSay(SyncActionNode):
    def tick(self):
        self.set_output("text", "The answer is 42")
        return NodeStatus.SUCCESS


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
        target = self.get_input("target", None, Position2D).value
        if target is None:
            raise ValueError("error reading port [target]")
        print(f"Target positions: [ {target.x}, {target.y} ]")
        return NodeStatus.SUCCESS


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
