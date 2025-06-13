from .node import DecoratorNode, Node, NodeStatus


class Inverter(DecoratorNode):
    def tick(self) -> NodeStatus:
        match self.child.tick():
            case NodeStatus.SUCCESS:
                return NodeStatus.FAILURE
            case NodeStatus.FAILURE:
                return NodeStatus.SUCCESS
            case s:
                return s


class RetryUntilSuccessful(DecoratorNode):
    num_attempts: int

    def __init__(self, child: Node, name: str | None = None, **kwargs):
        super().__init__(child, name, **kwargs)
        self._attempt = 0

    def tick(self) -> NodeStatus:
        self._attempt += 1
        s = self.child.tick()
        if s == NodeStatus.FAILURE and self._attempt < self.num_attempts:
            return NodeStatus.RUNNING
        return s
