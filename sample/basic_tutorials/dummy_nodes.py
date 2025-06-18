from typing import NamedTuple

from behaviortree_py.node import NodeStatus, SyncActionNode


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
        message = self.get_input("message", "Nothing to say", str).value
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
