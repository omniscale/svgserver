import re
import sys

from xml.etree.ElementTree import parse
from itertools import groupby
from contextlib import closing

import requests

from svgserver.combine import CombineSVG


def get_layer_names(client, params):
    params = {k.upper(): v for k, v in params.items()}
    params['REQUEST'] = 'GetCapabilities'
    params['SERVICE'] = 'WMS'
    params['VERSION'] = '1.3.0' # force 1.3.0 for Max/MinScaleDenominator

    scale_denom = mapserver_scaledenom_from_params(params)
    cap = client.open(params)

    for layer in filter_layers(parse_layer_names(cap), scale_denom):
        yield layer

def get_wms_layer_names(base_url, params={}):
    with closing(requests.get(base_url, params=params, stream=True)) as r:
        for layer in parse_layer_names(r.raw):
            yield layer

NS = {'wms': 'http://www.opengis.net/wms'}

def parse_layer_names(f):
    tree = parse(f)
    root = tree.getroot()

    for elem in root.findall( './wms:Capability/wms:Layer/wms:Layer', NS):
        name = elem.find('./wms:Name', NS).text

        minscaled = elem.find('./wms:MaxScaleDenominator', NS)
        if minscaled is not None:
            minscaled = float(minscaled.text)
        maxscaled = elem.find('./wms:MinScaleDenominator', NS)
        if maxscaled is not None:
            maxscaled = float(maxscaled.text)
        yield name, minscaled, maxscaled


def combined_mapserv_svg(base_url, print_params, output=sys.stdout):
    layers = get_wms_layer_names(base_url)

    c = CombineSVG(output)
    for layer_name, sublayers in groupby(layers, lambda l: re.sub('[-_].*$', '', l)):
        params = {k.upper(): v for k, v in print_params.items()}
        params['LAYERS'] = ','.join(sublayers)
        with closing(requests.get(base_url, params=params, stream=True)) as r:
            c.add(layer_name, r.raw)

    c.close()

def mapserver_scaledenom_from_params(params):
    bbox = map(float, params['BBOX'].split(','))
    size = int(params['WIDTH']), int(params['HEIGHT'])
    res = int(params.get('MAP_RESOLUTION', '72'))
    return mapserver_scaledenom(bbox, size, res)

def mapserver_scaledenom(bbox, size, resolution=72):
    inchPerM = 39.3701
    md = (size[0]-1)/(resolution*inchPerM)
    gd = bbox[2] - bbox[0]
    return gd/md

def filter_layers(layers, scaledenom):
    for layer, minsd, maxsd in layers:
        if scaledenom:
            if minsd and scaledenom > minsd:
                continue
            if maxsd and scaledenom <= maxsd:
                continue
        yield layer



if __name__ == '__main__':
    from svgserver.cgi import CGIClient
    from svgserver.tree import build_tree, print_tree
    import os
    import logging
    logging.basicConfig(level=logging.DEBUG)

    client = CGIClient('/usr/local/bin/mapserv')
    params = {
        'service': 'WMS',
        'version': '1.1.1',
        'request': 'GetMap',
        'width': 1234,
        'height': 769,
        'srs': 'EPSG:3857',
        'styles': '',
        'format': 'image/svg+xml',
        'bbox': '775214.9923087133,6721788.224989068,776688.4414913012,6722705.993822992',
        'map': os.path.abspath(os.path.dirname(__file__) + '/../tests/ms.map'),
    }
    layers = get_layer_names(client, params)
    tree = build_tree(layers)

    with open('/tmp/out.svg', 'wb') as f:
        with CombineSVG(f) as c:
            def add_layer(root):
                for (part, subs) in root:
                    c.push_group(part)
                    for sub in subs:
                        if isinstance(sub, str):
                            params['layers'] = sub
                            c.add(client.open(params))
                        else:
                            add_layer([sub])
                    c.pop_group()
            add_layer(tree)
