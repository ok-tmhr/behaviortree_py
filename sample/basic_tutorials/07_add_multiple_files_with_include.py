from pathlib import Path

import dummy_nodes

from behaviortree_py.bt_factory import BehaviorTreeFactory

if __name__ == "__main__":
    factory = BehaviorTreeFactory()

    bt_file = "bt/add_multiple_files_with_include.json"
    bt_path = Path(__file__).parent / bt_file
    factory.register_behavior_tree_from_file(bt_path.as_posix())

    print("----- MainTree tick ----")
    main_tree = factory.create_tree("MainTree")
    main_tree.tick_while_running()

    print("----- SubA tick ----")
    sub_a_tree = factory.create_tree("SubTreeA")
    sub_a_tree.tick_while_running()
