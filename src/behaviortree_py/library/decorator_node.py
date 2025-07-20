from behaviortree_py.core import NodeLibrary, NodeStatus, TreeNode
from behaviortree_py.node import DecoratorNode

from . import scripting

__all__ = (
    "Inverter",
    "RetryUntilSuccessful",
    "ForceFailure",
    "AlwaysSuccess",
    "Precondition",
)


class Inverter(DecoratorNode):
    def tick(self) -> NodeStatus:
        match self.child.tick():
            case NodeStatus.SUCCESS:
                return NodeStatus.FAILURE
            case NodeStatus.FAILURE:
                return NodeStatus.SUCCESS
            case s:
                return s


class ForceSuccess(DecoratorNode):
    def tick(self):
        status = self.child.tick()
        if status == NodeStatus.RUNNING:
            return status
        return NodeStatus.SUCCESS


class ForceFailure(DecoratorNode):
    def tick(self):
        status = self.child.tick()
        if status == NodeStatus.RUNNING:
            return status
        return NodeStatus.FAILURE


class AlwaysSuccess(DecoratorNode):
    def tick(self):
        status = self.child.tick()
        if status == NodeStatus.RUNNING:
            return status
        return NodeStatus.SUCCESS


class Repeat(DecoratorNode):
    def __init__(self, child, name=None, **kwargs):
        super().__init__(child, name, **kwargs)
        self.cycle = 0

    def tick(self):
        num_cycles = self.get_input("num_cycles", 3, int).value

        while (
            self.cycle < num_cycles and (s := self.child.tick()) == NodeStatus.SUCCESS
        ):
            self.cycle += 1

        return s


class RetryUntilSuccessful(DecoratorNode):
    def __init__(self, child: TreeNode, name=None, **kwargs):
        super().__init__(child, name, **kwargs)
        self._attempt = 0

    def tick(self) -> NodeStatus:
        self._attempt += 1
        result = self.get_input("num_attempts", 5, int)
        if not result:
            raise ValueError(result.error)
        num_attempts = result.value
        s = self.child.tick()
        if s == NodeStatus.FAILURE and self._attempt < num_attempts:
            return NodeStatus.RUNNING
        return s


class Precondition(DecoratorNode):
    def tick(self):
        result = self.get_input("if", "True", str)
        if not result:
            raise ValueError(result.error)
        parser = scripting.get_parser(
            NodeLibrary._enums, self._config._blackboard._data
        )
        if parser.parse(result.value):
            return self.child.tick()
        result = self.get_input("else", "FAILURE", str)
        if not result:
            raise ValueError(result.error)
        return parser.parse(result.value)
