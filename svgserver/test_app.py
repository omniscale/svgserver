import os
from svgserver.app import layered_svg
from contextlib import closing

import pytest


@pytest.fixture
def params():
    return {
        "service": "WMS",
        "version": "1.1.1",
        "request": "GetMap",
        "width": 1000,
        "height": 1000,
        "srs": "EPSG:3857",
        "styles": "",
        "format": "image/svg+xml",
        "bbox": "-1000,-1000,1000,1000",
        "map": os.path.abspath(os.path.dirname(__file__) + "/test.map"),
    }


def test_svgserver(params):
    with closing(layered_svg(params)) as doc:
        content = doc.read()

    assert 'id="root, sublayer"' in content
    assert 'id="a"' in content
    assert 'id="b, a"' in content

def test_svgserver_translations(params):
    translations = {
        "sublayer": "Sublayer",
        "a": "A-Layer",
        "b": "B-Layer",
        "root": "Root",
    }
    with closing(layered_svg(params, translations=translations)) as doc:
        content = doc.read()

    assert 'id="Root, Sublayer"' in content
    assert 'id="A-Layer"' in content
    assert 'id="B-Layer, A-Layer"' in content
