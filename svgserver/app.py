import codecs
import tempfile
from contextlib import closing

from .cgi import CGIClient
from .combine import CombineSVG

from .mapserv import MapServer, InternalError
from .tree import build_tree


def _recursive_add_layer(nodes, params, svg, mapserver, translations):
    for node in nodes:
        group_name = format_group_name(node, translations)
        svg.push_group(group_name)
        if node.layer:
            params["layers"] = node.layer
            params["format"] = "image/svg+xml"
            resp = mapserver.get(params)
            if resp.headers["Content-type"] != "image/svg+xml":
                raise InternalError(
                    "received non SVG response for layer %s:\n%s\n%s"
                    % (node.layer, resp.headers, resp.read())
                )
            svg.add(resp)
        if node.subs:
            _recursive_add_layer(node.subs, params, svg, mapserver, translations)
        svg.pop_group()

def format_group_name(node, translations):
    if isinstance(node.name, tuple):
        return ', '.join(translations.get(n, n) for n in node.name)
    return translations.get(node.name, node.name)

def layered_svg(params, translations={}, mapserver_binary="mapserv", root_id='map'):
    mapserver = MapServer(binary=mapserver_binary)
    layers = mapserver.layer_names(params)
    nodes = build_tree(layers)
    root_id = translations.get(root_id, root_id)

    f = tempfile.TemporaryFile()
    try:
        with CombineSVG(f, root_id=root_id) as svg:
            _recursive_add_layer(
                nodes,
                params=params,
                svg=svg,
                mapserver=mapserver,
                translations=translations,
            )

        f.seek(0)
        return f
    except:
        # close to remove temporary file
        f.close()
        raise


def load_translations(filename):
    if not filename:
        return {}

    translations = {}
    with codecs.open(filename, encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, translation = line.split('=', 1)

            translations[key.strip()] = translation.strip()
    return translations

if __name__ == "__main__":
    import os
    import logging

    logging.basicConfig(level=logging.DEBUG)

    params = {
        "service": "WMS",
        "version": "1.1.1",
        "request": "GetMap",
        "width": 1234,
        "height": 769,
        "srs": "EPSG:3857",
        "styles": "",
        "format": "image/svg+xml",
        "bbox": "775214.9923087133,6721788.224989068,776688.4414913012,6722705.993822992",
        "map": os.path.abspath(os.path.dirname(__file__) + "/../tests/ms.map"),
    }

    with closing(layered_svg(params)) as f:
        print(f.read())
