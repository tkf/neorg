import os
from neorg import NEORG_HIDDEN_DIR, CONFIG_FILE


class DefaultConfig(object):
    DEBUG = False
    DATABASE = '%(neorg)s/neorg.db'
    DATADIRPATH = '%(root)s'

    # HELPDIRPATH = '%(neorg)s/help'
    # nerog reads help page from `static/help` if HELPDIRPATH is not
    # defined

    SECRET_KEY = None  # needs override (flask build-in)

    ## USERNAME = 'admin'
    ## PASSWORD = 'default'


def neorgpath(dirpath):
    return os.path.join(dirpath, NEORG_HIDDEN_DIR)


def confpath(dirpath):
    return os.path.join(dirpath, NEORG_HIDDEN_DIR, CONFIG_FILE)


def magicwords(dirpath):
    return {
        'neorg': os.path.join(dirpath, NEORG_HIDDEN_DIR),
        'root': dirpath,
        }


def expandall(path):
    return os.path.expandvars(os.path.expanduser(path))


def load_config(app, dirpath=None):
    if dirpath is None:
        dirpath = '.'
    dirpath = os.path.abspath(dirpath)
    app.config.from_pyfile(confpath(dirpath))
    magic = magicwords(dirpath)
    app.config['NEORG_ROOT'] = magic['root']
    app.config['NEORG_DIR'] = magic['neorg']
    app.config['DATADIRURL'] = '/_data'
    for key in ['DATABASE', 'DATADIRPATH', 'HELPDIRPATH']:
        if key in app.config:
            app.config[key] = expandall(app.config[key] % magic)


DEFAULT_CONFIG_FILE = """\
SECRET_KEY = 'development key'
DATADIRPATH = '%(root)s'
"""


def init_config_file(dirpath=None):
    if dirpath is None:
        dirpath = '.'
    dirpath = os.path.abspath(dirpath)
    _neorgpath = neorgpath(dirpath)
    if not os.path.isdir(_neorgpath):
        os.mkdir(_neorgpath, 0700)
    file(confpath(dirpath), 'w').write(DEFAULT_CONFIG_FILE)
