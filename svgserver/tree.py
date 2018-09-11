import re
from collections import namedtuple


def cleanup_layer(layer):
    layer = layer.replace("-", "_")
    return re.sub("(_[0-9]+)*$", "", layer)


node = namedtuple("node", ["name", "subs", "layer"])


def build_tree(layers, cleanup=cleanup_layer):
    """
    >>> build_tree(['a'])
    [node(name='a', subs=None, layer='a')]
    """

    def add(root, parts, name):
        if not root or root[-1].name != parts[0]:
            root.append(node(parts[0], [], None))

        if len(parts) > 1:
            add(root[-1][1], parts[1:], name)
        else:
            root[-1][1].append(node(parts[0], None, name))

    root = []
    for lyr in layers:
        parts = cleanup(lyr).split("_")

        add(root, parts, lyr)

    return [truncate_single_leafs(nd) for nd in root]


def truncate_single_leafs(nd):
    """
    >>> truncate_single_leafs(node(name='a', subs=[node(name='a', subs=None, layer='a')], layer=None))
    node(name='a', subs=None, layer='a')
    """
    if nd.layer:
        return nd
    if nd.subs and len(nd.subs) == 1:
        if nd.subs[0].layer:
            return node(nd.name, None, nd.subs[0].layer)

        nd2 = truncate_single_leafs(nd.subs[0])
        return node(name=(nd.name, nd.subs[0].name),
            subs=nd2.subs,
            layer=nd2.layer,
        )
    return node(nd.name, [truncate_single_leafs(n) for n in nd.subs], None)
