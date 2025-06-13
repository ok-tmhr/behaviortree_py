from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree


def print_node(node: Element, indent: int = 0):
    prefix = "  " * indent
    tag = node.tag
    attrib_str = " ".join(f'{k}="{v}"' for k, v in node.attrib.items())
    print(f"{prefix}{tag} {attrib_str}".rstrip())
    for child in node:
        print_node(child, indent + 1)


bt_path = Path(__file__).parent / "bt" / "my_tree.xml"
doc = ElementTree(file=bt_path.as_posix())

# ルートの <root> の下に複数の BehaviorTree があることを想定
for bt in doc.findall("BehaviorTree"):
    print_node(bt)
