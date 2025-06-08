from behaviortree_py.node import NodeStatus

if __name__ == "__main__":
    from pathlib import Path

    from behaviortree_py.bt_factory import BehaviorTreeFactory

    bt_path = Path(__file__).with_name("bt/subtrees.json")
    tree = BehaviorTreeFactory.create_tree(bt_path.as_posix())

    status = NodeStatus.RUNNING
    while status == NodeStatus.RUNNING:
        print("tick once")
        status = tree.tick()
    print("tree finished", status.name)
