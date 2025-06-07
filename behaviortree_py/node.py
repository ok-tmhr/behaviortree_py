from abc import ABC, abstractmethod
from enum import Enum, auto


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class TreeNode(ABC):
    def __init__(self, name: str | None = None):
        self.name = name or self.__class__.__name__.removesuffix("Node")

    @abstractmethod
    def tick(self) -> NodeStatus:
        pass


class LeafNode(TreeNode):
    def tick(self):
        pass


class ActionNode(LeafNode):
    def tick(self):
        pass


class DecoratorNode(TreeNode):
    def __init__(self, name, child: TreeNode):
        super().__init__(name)
        self.child = child

    pass


class ControlNode(TreeNode):
    def __init__(self, name, *children: TreeNode):
        super().__init__(name)
        self.children = children

    pass


class ConditionNode(LeafNode):
    pass


class SequenceNode(ControlNode):
    def __init__(self, name, *children):
        super().__init__(name, *children)
        self._index = 0

    def tick(self):
        s = self.children[self._index].tick()
        if s == NodeStatus.SUCCESS and self._index < len(self.children) - 1:
            self._index += 1
            return NodeStatus.RUNNING
        else:
            return s
