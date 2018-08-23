import os
from svgserver.mapserv import MapServer, InternalError

from pytest import raises

def test_mapserver_invalid_mapfile():
    ms = MapServer()
    with raises(InternalError):
        ms.layer_names({"map": os.path.dirname(__file__) + '/doesnotexist.map'})

def test_mapserver_layers():
    ms = MapServer()
    layers = ms.layer_names({"map": os.path.dirname(__file__) + '/test.map'})
    assert layers == ['root_sublayer_a', 'root_sublayer_b_a', 'root_sublayer_b_b']

def test_mapserver_minmaxscale():
    ms = MapServer()
    size = 1000
    layers = ms.layer_names({"map": os.path.dirname(__file__) + '/test.map', "bbox": "-1000,-1000,1000,1000", "width": size, "height": size})
    assert layers == ['root_sublayer_a', 'root_sublayer_b_a']
    size = 2000
    layers = ms.layer_names({"map": os.path.dirname(__file__) + '/test.map', "bbox": "-1000,-1000,1000,1000", "width": size, "height": size})
    assert layers == ['root_sublayer_b_a']
    size = 5000
    layers = ms.layer_names({"map": os.path.dirname(__file__) + '/test.map', "bbox": "-1000,-1000,1000,1000", "width": size, "height": size})
    assert layers == ['root_sublayer_b_a', 'root_sublayer_b_b']


