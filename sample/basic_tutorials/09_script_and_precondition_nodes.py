from enum import Enum, auto

import dummy_nodes

from behaviortree_py.bt_factory import BehaviorTreeFactory


class Color(Enum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()


if __name__ == "__main__":
    from pathlib import Path

    factory = BehaviorTreeFactory()

    factory.register_scripting_enums(Color)
    factory.register_scripting_enum("THE_ANSWER", 42)
    bt = Path(__file__).parent / "bt/script_and_precondition_nodes.json"
    tree = factory.create_tree_from_file(bt.as_posix())
    tree.tick_while_running()
