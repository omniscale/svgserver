import tempfile
from contextlib import contextmanager

from .cgi import CGIClient
from .combine import CombineSVG

from .mapserv import MapServer, InternalError
from .tree import build_tree


class SVGServer(object):
    def __init__(self, mapserver_binary="mapserv"):
        self.mapserver = MapServer(binary=mapserver_binary)

    def _recursive_add_layer(self, root, params, svg):
        for (part, subs) in root:
            svg.push_group(part)
            for sub in subs:
                if isinstance(sub, str):
                    params["layers"] = sub
                    resp = self.mapserver.get(params)
                    if resp.headers["Content-type"] != "image/svg+xml":
                        raise InternalError(
                            "received non SVG response for layer %s:\n%s\n%s"
                            % (sub, resp.headers, resp.read())
                        )
                    svg.add(resp)
                else:
                    self._recursive_add_layer([sub], params, svg)
            svg.pop_group()

    @contextmanager
    def get(self, params):
        layers = self.mapserver.layer_names(params)
        tree = build_tree(layers)

        with tempfile.TemporaryFile() as f:
            with CombineSVG(f) as svg:
                self._recursive_add_layer(tree, params, svg)

            f.seek(0)
            yield f


if __name__ == "__main__":
    import os
    import logging

    logging.basicConfig(level=logging.DEBUG)

    srv = SVGServer()

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

    with srv.request_svg(params) as f:
        print(f.read())
