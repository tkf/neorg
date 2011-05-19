def serve(port, debug=None, browser=None):
    from neorg.web import app
    from neorg.config import load_config
    from neorg.wiki import register_neorg_directives
    load_config(app)
    if debug is not None:
        app.config['DEBUG'] = debug
    if browser:
        from threading import Timer
        from webbrowser import open_new_tab
        Timer(1, open_new_tab,
              args=['http://localhost:%d' % port]).start()
    register_neorg_directives(app.config['DATADIRPATH'], '_data')
    app.run(port=port)


def init(dest):
    from neorg.web import app, init_db
    from neorg.config import init_config_file, load_config

    init_config_file(dest)
    load_config(app, dest)
    init_db()


def applyargs(func, **kwds):
    return func(**kwds)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Process some integers.')
    subparsers = parser.add_subparsers()

    # init
    parser_init = subparsers.add_parser(
        'init', help='initialize neorg directory')
    parser_init.add_argument(
        'dest', default='.', nargs='?',
        help='root directory to initialize (default: "%(default)s")')
    parser_init.set_defaults(func=init)

    # serve
    parser_serve = subparsers.add_parser(
        'serve', help='start stand-alone webserver')
    parser_serve.add_argument(
        '-p', '--port', type=int, default=8000,
        help='port to listen (default: %(default)s)')
    parser_serve.add_argument(
        '-b', '--browser', action='store_true', default=False,
        help='open web browser',
        )
    parser_serve.add_argument(
        '--debug', action='store_true')
    parser_serve.set_defaults(func=serve)

    args = parser.parse_args()
    return applyargs(**vars(args))


if __name__ == '__main__':
    main()
