import re

def cleanup_layer(layer):
    layer = layer.replace('-', '_')
    return re.sub('(_[0-9]+)*$', '', layer)

def build_tree(layers):
    """
    >>> build_tree(['a_a', 'a_b', 'b', 'b_a', 'a'])
    [('a', [('a', ['a_a']), ('b', ['a_b'])]), ('b', ['b', ('a', ['b_a'])]), ('a', ['a'])]
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
        parts = cleanup_layer(lyr).split('_')

        add(root, parts, lyr)

    return root

def print_tree(root):
    def _print(root, indent):
        for (part, subs) in root:
            print(' ' * (4*indent) + part)
            for sub in subs:
                if isinstance(sub, str):
                    print(' ' * (4*(1+indent)) + ':' + sub)
                else:
                    _print([sub], indent+1)
    _print(root, 0)

if __name__ == '__main__':
    test_layers = '''landusages_osm_low
    landusages_osm_9_10
    landusages_osm
    landusages_alkis_low
    landusages_alkis_9_10
    landusages_alkis
    landusages_fnk_low
    landusages_fnk_9_10
    landusages_fnk
    water_osm_low
    water_osm_9_10
    water_osm
    water_atkis_low
    water_atkis_9_10
    water_atkis
    water_atkis_line
    buildings_14
    buildings
    roads_tunnels
    roads_turning_circles_case
    roads_9
    roads_10
    roads
    roads_turning_circles_fill
    roads_bridges
    roads_barrier_points
    city_boundary
    county_boundary
    label_atkis_water_poly
    label_atkis_water_line
    label_atkis_water_line2
    labels_motorway_junctions-text
    labels_motorway_junctions-shields
    labels_roads_names
    labels_roads_refs
    labels_housenumbers
    labels_places
    roads_oneways'''.split('\n')
    print_tree(build_tree(test_layers))

