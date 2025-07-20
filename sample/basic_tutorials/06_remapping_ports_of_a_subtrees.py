from pathlib import Path

import dummy_nodes

from behaviortree_py.bt_factory import BehaviorTreeFactory

dummy_nodes

factory = BehaviorTreeFactory()

bt_file = Path(__file__).parent / "bt/remapping_ports_of_a_subtrees.json"
factory.register_behavior_tree_from_file(bt_file.as_posix())
tree = factory.create_tree("MainTree")

tree.tick_while_running()

print("----- First BB -----")
tree.subtrees[0].blackboard.debug_message()

print("----- Second BB -----")
tree.subtrees[1].blackboard.debug_message()
