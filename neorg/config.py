import os
from neorg import NEORG_DIR, CONFIG_FILE


class DefaultConfig(object):
    DATABASE = '%(neorg)s/neorg.db'
    DATADIRPATH = '%(root)s'

    SECRET_KEY = None  # needs override (flask build-in)

    ## USERNAME = 'admin'
    ## PASSWORD = 'default'


def neorgpath(dirpath):
    return os.path.join(dirpath, NEORG_DIR)


def confpath(dirpath):
    return os.path.join(dirpath, NEORG_DIR, CONFIG_FILE)


def magicwords(dirpath):
    return {
        'neorg': os.path.join(dirpath, NEORG_DIR),
        'root': dirpath,
        }


def load_config(app, dirpath=None):
    if dirpath is None:
        dirpath = '.'
    dirpath = os.path.abspath(dirpath)
    app.config.from_pyfile(confpath(dirpath))
    magic = magicwords(dirpath)
    app.config.update(
        DATABASE = app.config['DATABASE'] % magic,
        DATADIRPATH = app.config['DATADIRPATH'] % magic,
        )


DEFAULT_CONFIG_FILE = """
DEBUG = True
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
