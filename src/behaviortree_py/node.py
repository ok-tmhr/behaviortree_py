from behaviortree_py.core import NodeBase, NodeLibrary, NodeStatus, TreeNode

__all__ = "ControlNode", "DecoratorNode", "SyncActionNode", "StatefulActionNode"


class ControlNode(NodeBase):
    child: list[TreeNode]

    def __init__(self, child: list[TreeNode], name=None, **kwargs):
        super().__init__(child, name, **kwargs)
        self._index = 0

        for c in child:
            c.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class DecoratorNode(NodeBase):
    child: TreeNode

    def __init__(self, child: TreeNode, name=None, **kwargs):
        super().__init__(child, name, **kwargs)
        child.parent = self

    def __init_subclass__(cls):
        return NodeLibrary.register_node_type(cls)


class SyncActionNode(NodeBase):
    def __init__(self, child, name=None, **kwargs):
        super().__init__(None, name, **kwargs)

    def __init_subclass__(cls):
        NodeLibrary.register_node_type(cls)


class StatefulActionNode(NodeBase):
    status: NodeStatus | None

    def __init__(self, child, name=None, **kwargs):
        super().__init__(None, name, **kwargs)
        self.status = None

    def __init_subclass__(cls):
        NodeLibrary.register_node_type(cls)

    def on_start(self):
        return NodeStatus.SUCCESS

    def on_running(self): ...

    def on_halted(self):
        pass

    def tick(self):
        match self.status:
            case None:
                self.status = self.on_start()
            case NodeStatus.RUNNING:
                self.status = self.on_running()
            case _:
                pass
        return self.status
