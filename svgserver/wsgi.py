from __future__ import print_function

import json
import gzip
import io
import os
from datetime import datetime

from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response, Request
from werkzeug.wsgi import SharedDataMiddleware

from svgserver.mapserv import MapServer, InternalError
from svgserver.app import layered_svg, load_translations

import logging

log = logging.getLogger(__name__)


class Server(object):
    def __init__(self, config):
        self.url_map = Map([Rule("/svg", endpoint="svg")])
        self.mapserver_binary = config["mapserver_binary"]
        self.translations_file = config["translations_file"]
        # init MapServer to check if mapserver_binary is found
        MapServer(self.mapserver_binary)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, "on_" + endpoint)(request, **values)
        except ValueError as e:
            return Response("request error: {}".format(e), status=400)
        except InternalError as e:
            return Response("request error: {}".format(e), status=400)
        except NotFound:
            return Response("not found", status=404)
        except Exception as e:
            log.exception("Dispatching query {}".format(request))
            return HTTPException("Internal error")

    def json_error(self, request, code, msg):
        return self.json_resp(request, {"status": code, "message": msg}, code=code)

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def on_svg(self, request):
        mapname = os.path.splitext(os.path.basename(request.args.get("map", "")))[0]
        filename = "svg-plot-{}-{}.svg".format(
            mapname, datetime.now().strftime("%Y%m%dT%H%M%S")
        )
        headers = Headers()
        headers.add("Content-Disposition", "attachment", filename=filename)

        params = parse_params(request)
        translations = load_translations(self.translations_file)
        svg = layered_svg(
            params, mapserver_binary=self.mapserver_binary, translations=translations
        )
        return Response(svg, content_type="text/svg+xml", headers=headers)


def parse_params(request):
    params = {}
    for k, v in request.args.iteritems(multi=False):
        params[k.lower()] = v

    if "scaledenom" in params:
        dpi = 72.0
        scaledenom = float(params["scaledenom"])
        bbox = [float(x) for x in params["bbox"].split(",")]
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        px_width = width / scaledenom * 1000 / 25.4 * dpi
        px_height = height / scaledenom * 1000 / 25.4 * dpi
        params["width"] = px_width
        params["height"] = px_height

    return params


def create_app(config):
    app = Server(config)
    return app

