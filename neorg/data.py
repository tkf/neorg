try:
    import cPickle as pickle
except:
    import pickle

import json

# yaml is optional
try:
    import yaml
except ImportError:
    pass


def load_pyfile(path):
    """Load "python executable" parameter file"""
    params = {}
    execfile(path, params)
    return params


def load_any(path, ftype=None):
    """
    Load any data file from given path (distinguished by file extension)
    """
    def ftype_match(*types):
        return (ftype in types or
                path.lower().endswith(
                    tuple(['.%s' % t for t in types])))

    if ftype_match('pickle'):
        return pickle.load(file(path))
    elif ftype_match('py', 'python'):
        return load_pyfile(path)
    elif ftype_match('yaml', 'yml'):
        return yaml.load(file(path))
    elif ftype_match('json'):
        return json.load(file(path))
    else:
        raise ValueError('data type of "%s" is not recognized' % path)




def get_nested(dct, dictpath, sep='.'):
    """
    Get a element from nested dictionary

    >>> nested = {'a': {'b': {'c': 1}}}
    >>> get_nested(nested, 'a.b.c')
    1
    >>> get_nested(nested, 'a/b/c', sep='/')
    1
    >>> get_nested(nested, 'nonexist')
    Traceback (most recent call last):
    ...
    KeyError: 'nonexist'
    >>> get_nested([[['a'], ['b']]], '0.1.0')
    'b'

    """
    if dictpath == None:
        return dct
    elem = dct
    for key in dictpath.split(sep):
        try:
            elem = elem[key]
        except (KeyError, TypeError):
            if key.isdigit():
                elem = elem[int(key)]
            else:
                raise KeyError(dictpath)
    return elem
