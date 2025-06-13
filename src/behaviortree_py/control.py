from .node import ControlNode, NodeStatus


class Sequence(ControlNode):
    def tick(self) -> NodeStatus:
        s = self.children[self._index].tick()
        if s == NodeStatus.SUCCESS and self._index < len(self.children) - 1:
            self._index += 1
            return NodeStatus.RUNNING
        return s


class Fallback(ControlNode):
    def tick(self) -> NodeStatus:
        s = self.children[self._index].tick()
        if s == NodeStatus.FAILURE and self._index < len(self.children) - 1:
            self._index += 1
            return NodeStatus.RUNNING
        return s
