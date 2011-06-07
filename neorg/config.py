import os
from neorg import NEORG_HIDDEN_DIR, CONFIG_FILE


class DefaultConfig(object):
    DEBUG = False
    DATABASE = '%(neorg)s/neorg.db'
    DATADIRPATH = '%(root)s'
    SEARCHINDEX = '%(neorg)s/searchindex'

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


def expandall(path):
    return os.path.expandvars(os.path.expanduser(path))


def expand_magic_words(config):
    magic = {
        'neorg': config['NEORG_DIR'],
        'root': config['NEORG_ROOT'],
        }
    for key in ['DATABASE', 'DATADIRPATH', 'HELPDIRPATH', 'SEARCHINDEX']:
        if key in config:
            config[key] = expandall(config[key] % magic)


def set_neorg_dir(config, dirpath):
    config.update(
        NEORG_ROOT=dirpath,
        NEORG_DIR=os.path.join(dirpath, NEORG_HIDDEN_DIR),
        )


def load_config(app, dirpath=None):
    if dirpath is None:
        dirpath = '.'
    dirpath = os.path.abspath(dirpath)
    app.config.from_pyfile(confpath(dirpath))
    set_config(app.config, dirpath)


def set_config(config, dirpath):
    set_neorg_dir(config, dirpath)
    config['DATADIRURL'] = '/_data'
    expand_magic_words(config)


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
