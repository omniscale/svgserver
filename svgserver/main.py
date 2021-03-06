from __future__ import print_function

from svgserver.wsgi import create_app

import logging

log = logging.getLogger(__name__)

def main():

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--mapserver", help="mapserver binary")
    parser.add_argument("--translations", help="translations")
    parser.add_argument(
        "--url-prefix",
        help="prefix to strip from requested URL. E.g when running behind a frontend "
        "server that uses a different URL. (not available with --develop)",
    )
    parser.add_argument(
        "--develop",
        action="store_true",
        help="start in development mode (reload on code changes)",
    )

    args = parser.parse_args()

    if args.develop:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    from werkzeug.serving import run_simple

    config = {
        "mapserver_binary": args.mapserver,
        "translations_file": args.translations,
    }
    app = create_app(config)
    if args.develop:
        run_simple(
            args.host,
            args.port,
            app,
            use_debugger=True,
            use_reloader=True,
            threaded=True,
        )
    else:
        import waitress

        waitress.serve(app, host=args.host, port=args.port,
                       url_prefix=args.url_prefix,
                       )


if __name__ == "__main__":
    main()
