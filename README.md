svgserver
=========

Renders maps with Mapserver into layered SVG files where each layer is a separate SVG layer (group).

svgserver makes direct calls to the Mapserver binary. HTTP calls to an an existing Mapserver WMS are not supported.

svgserver accepts WMS requests at the /svg URL. It requires a `map` parameter with the absolute filename of the Mapserver mapfile. 
It requests all available layer with a GetCapabilities, requests each layer as an SVG and combines each result into a single SVG document.
svgserver builds a layer tree based on the layer names. Layer names are split at dash and underscore characters.
Empty layers (with no data in the requested scale or bounding box) are not added to the final SVG.

For example, the following list of layers ist converted to the following layer tree:

    roads_highway,roads_minor,buildings,buildings_industrial,labels_roads,labels_places

    - map
    - roads
        - highway
        - minor
    - buildings
        - buildings
        - industrial
    - labels
        - roads
        - places

The WMS `layers` parameter is ignored and all layers that are visible in the requested scale are added (Min/MaxScaleDenominator). 
The WMS `format` parameter is always set to `image/svg+xml`. Make sure your mapfile support this with an `OUTPUTFORMAT` similar to:

    OUTPUTFORMAT
        NAME "svg"
        DRIVER CAIRO/SVG
        MIMETYPE "image/svg+xml"
        IMAGEMODE RGB
        EXTENSION "svg"
    END


Installation
------------

svgserver is written in Python and requires Werkzeug. To install both:

    cd path-to-this-repo
    pip install ./


Running
-------

You can run svgserver from command line with:

    python -m svgserver.app


Call svgserver with `--help` to see all available command line options.


### WSGI ###


You can serve svgserver as a WSGI application. Here is an example WSGI configuration:

    from svgserver.wsgi import create_app

    application = create_app({
        'translations_file': 'translations.txt',
        'mapserver_binary': '/usr/local/bin/mapserv',
    })


Making requests
---------------

You can make regular WMS requests to the /svg URL:

    http://127.0.0.1:5000/svg?map=/path/to/mapfile.map&request=GetMap&service=WMS&version=1.1.1&srs=EPSG:3857&BBOX=0,0,100000,100000&width=1000&height=1000"

Instead of providing `width` and `height`, you can also provide the desired map scale with the `scaledenom` parameter:

    http://127.0.0.1:5000/svg?map=/path/to/mapfile.map&request=GetMap&service=WMS&version=1.1.1&srs=EPSG:3857&BBOX=0,0,100000,100000&scaledenom=100000



Translations
------------

svgserver can translate layer names to localized, human-readable names. You can privide a translations file with `--translations` command line option or with the `translations_file` configuration for WSGI applications.

A translation file is a simple UTF-8 encoded text file with `layer=Translation` on each line. Empty lines and lines starting with `#` are ignored.
The translations are applied to each part individually (see above how the layer tree is generated).

Example translation file:

    map=Stadtplan
    boundary=Grenzen
    bridges=Brücken
    buildings=Gebäude
    housenumbers=Hausnummern
    labels=Beschriftungen
    motorway=Autobahnen
