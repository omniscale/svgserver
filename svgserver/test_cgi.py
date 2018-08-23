import subprocess

from svgserver.cgi import CGIClient

def test_mapserver_cgi():
    client = CGIClient('mapserv')
    resp = client.get({"request": "GetCapabilities", "service": "WMS"})
