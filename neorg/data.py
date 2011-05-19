from fnmatch import fnmatchcase

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


def _nested_fnmatch(subdct, keylist):
    if not keylist:
        yield (keylist, subdct)
        return

    key_pat = keylist[0]
    key_rest = keylist[1:]
    if key_pat.isdigit():
        try:
            key_int = int(key_pat)
            for (k0, v0) in _nested_fnmatch(subdct[key_int], key_rest):
                yield ([key_int] + k0, v0)
        except (KeyError, IndexError, TypeError):
            pass
    try:
        key_cand_list = list(subdct)
    except TypeError:
        return
    key_cand_list = list(subdct)
    for key_cand in key_cand_list:
        if fnmatchcase(str(key_cand), key_pat):
            for (k0, v0) in _nested_fnmatch(subdct[key_cand], key_rest):
                yield ([key_cand] + k0, v0)



def get_nested_fnmatch(dct, dictpath, sep='.'):
    """
    Get a element from nested dictionary

    >>> dct = {'a': {'b': {'c': 1}, 'd': {'c': 2}}}
    >>> list(get_nested_fnmatch(dct, 'a.b.c'))
    [('a.b.c', 1)]
    >>> list(get_nested_fnmatch(dct, 'a.*.c'))
    [('a.b.c', 1), ('a.d.c', 2)]
    >>> dct2 = {'a': {'b': {'c': 1}, 'd': 2}}
    >>> list(get_nested_fnmatch(dct2, 'a.*.c'))
    [('a.b.c', 1)]
    >>> list(get_nested_fnmatch(dct2, 'a.*'))
    [('a.b', {'c': 1}), ('a.d', 2)]

    """
    for (keylist, val) in sorted(_nested_fnmatch(dct,
                                                 dictpath.split(sep))):
        yield (sep.join(map(str, keylist)), val)
