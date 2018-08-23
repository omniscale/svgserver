import re
import sys

from xml.etree.ElementTree import parse
from itertools import groupby
from contextlib import closing

from svgserver.cgi import CGIClient
from svgserver.combine import CombineSVG


class InternalError(Exception):
    pass


class MapServer(object):
    def __init__(self, binary="mapserv"):
        self.client = CGIClient(binary)

    def get(self, params):
        return self.client.get(params)

    def layer_names(self, params):
        params = {k.upper(): v for k, v in params.items()}

        if "MAP" not in params:
            raise ValueError("MAP not set in params")

        cap_params = {
            "MAP": params["MAP"],
            "REQUEST": "GetCapabilities",
            "SERVICE": "WMS",
            "VERSION": "1.3.0",  # force 1.3.0 for Max/MinScaleDenominator
        }
        cap = self.client.get(cap_params)
        if not cap.headers["Content-type"].startswith("text/xml"):
            raise InternalError(
                "invalid response for GetCapabilities:\n%s" % cap.read()
            )

        scale_denom = mapserver_scaledenom_from_params(params)
        layers = []
        for layer in filter_layers(parse_layer_names(cap), scale_denom):
            layers.append(layer)

        return layers


NS = {"wms": "http://www.opengis.net/wms"}


def parse_layer_names(f):
    tree = parse(f)
    root = tree.getroot()

    root_layer = root.find("./wms:Capability/wms:Layer", NS)
    if root_layer is None:
        f.seek(0)
        content = f.read(1000)
        raise ValueError("not a WMS capabilities document:\n%s" % content)

    for elem in root_layer.findall("./wms:Layer", NS):
        name = elem.find("./wms:Name", NS).text

        minscaled = elem.find("./wms:MaxScaleDenominator", NS)
        if minscaled is not None:
            minscaled = float(minscaled.text)
        maxscaled = elem.find("./wms:MinScaleDenominator", NS)
        if maxscaled is not None:
            maxscaled = float(maxscaled.text)
        yield name, minscaled, maxscaled


def mapserver_scaledenom_from_params(params):
    if "BBOX" not in params or "WIDTH" not in params:
        return None
    bbox = map(float, params["BBOX"].split(","))
    size = int(params["WIDTH"]), int(params["HEIGHT"])
    res = int(params.get("MAP_RESOLUTION", "72"))
    return mapserver_scaledenom(bbox, size, res)


def mapserver_scaledenom(bbox, size, resolution=72):
    inchPerM = 39.3701
    md = (size[0] - 1) / (resolution * inchPerM)
    gd = bbox[2] - bbox[0]
    return gd / md


def filter_layers(layers, scaledenom):
    for layer, minsd, maxsd in layers:
        if scaledenom:
            if minsd and scaledenom > minsd:
                continue
            if maxsd and scaledenom <= maxsd:
                continue
        yield layer
