import os
from svgserver.app import SVGServer

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
    srv = SVGServer()
    with srv.get(params) as doc:
        content = doc.read()

    assert 'id="sublayer"' in content
