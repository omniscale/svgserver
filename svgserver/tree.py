import re

def cleanup_layer(layer):
    layer = layer.replace('-', '_')
    return re.sub('(_[0-9]+)*$', '', layer)

def build_tree(layers, cleanup=cleanup_layer):
    """
    >>> build_tree(['a_a', 'a_b', 'b', 'b_a', 'a'])
    [('a', [('a', ['a_a']), ('b', ['a_b'])]), ('b', ['b', ('a', ['b_a'])]), ('a', ['a'])]
    >>> build_tree(['a-a', 'a_b', 'b_13', 'b_a_12', 'a_12-14'])
    [('a', [('a', ['a-a']), ('b', ['a_b'])]), ('b', ['b_13', ('a', ['b_a_12'])]), ('a', ['a_12-14'])]
    """
    def add(root, parts, name):
        if not root or root[-1][0] != parts[0]:
            root.append((parts[0], []))

        if len(parts) > 1:
            add(root[-1][1], parts[1:], name)
        else:
            root[-1][1].append(name)

    root = []
    for lyr in layers:
        parts = cleanup(lyr).split('_')

        add(root, parts, lyr)

    return root
