from behaviortree_py.core import NodeBase, NodeLibrary, NodeStatus

from . import scripting

__all__ = "ActionNode", "Script"


class ActionNode(NodeBase):
    __alias = "Action"

    def __new__(cls, child: None, ID: str, name=None, **kwargs):
        node_type = NodeLibrary.get_node_type(ID)
        self = super().__new__(node_type)
        self.name = name or node_type.__name__
        self._port = kwargs
        return self

    def __init__(self, child: None, ID: str, name=None, **kwargs):
        pass

    def tick(self): ...


class Script(NodeBase):
    def tick(self):
        code = str(self._port.pop("code"))
        parser = scripting.get_parser(
            NodeLibrary._enums, self._config._blackboard._data
        )
        parser.parse(code)
        return NodeStatus.SUCCESS
