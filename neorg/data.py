import re
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


def iteritemsdeep(dct):
    """
    Works like ``dict.iteritems`` but iterate over all descendant items

    >>> dct = dict(a=1, b=2, c=dict(d=3, e=4))
    >>> sorted(iteritemsdeep(dct))
    [(('a',), 1), (('b',), 2), (('c', 'd'), 3), (('c', 'e'), 4)]

    """
    for (key, val) in dct.iteritems():
        if isinstance(val, dict):
            for (key_child, val_child) in iteritemsdeep(val):
                yield ((key,) + key_child, val_child)
        else:
            yield ((key,), val)


class DictTable(object):
    """
    Store similar dict-like objects

    >>> dt = DictTable()
    >>> dt.append('A', dict(a=1, b=2, c=[1,2], d=dict(e=1), f=''))
    >>> dt.append('B', dict(a=1, b=3, c=[2,3], d=dict(e=2)))
    >>> dt.print_diff()
    b
    A: 2
    B: 3
    <BLANKLINE>
    c
    A: [1, 2]
    B: [2, 3]
    <BLANKLINE>
    d.e
    A: 1
    B: 2
    <BLANKLINE>
    f
    A: ''
    B:
    >>> dt.print_diff_as_table(deco_border=True, deco_header=True,
    ...                        deco_vlines=True)
    +-----+--------+--------+
    |     |   A    |   B    |
    +=====+========+========+
    | b   | 2      | 3      |
    | c   | [1, 2] | [2, 3] |
    | d.e | 1      | 2      |
    | f   | ''     |        |
    +-----+--------+--------+

    """

    sep = '.'

    def __init__(self):
        # dict of dict. access via self._table[(k1, k2, ...)][name]
        self._table = {}
        # original dict.
        self._original = {}
        # list of name
        self._name = []
        # set of key
        self._keys = set()

    def append(self, name, dct):
        """Append a dict-like object with name"""
        self._name.append(name)
        self._original[name] = dct
        for (key, val) in iteritemsdeep(dct):
            self._table.setdefault(key, {})
            self._table[key][name] = val
            self._keys.add(key)

    def parse_key(self, key):
        if isinstance(key, tuple):
            return key
        else:
            return tuple(key.split(self.sep))

    def as_list(self, key_list=None, name_list=None, deficit=None):
        """
        Get stored dictionaries as list-of-list

        >>> dt = DictTable()
        >>> dt.append('A', dict(a=1, b=2, c=[1,2], d=dict(e=1, f='')))
        >>> dt.append('B', dict(a=1, b=3, c=[2,3], d=dict(e=2)))
        >>> dt.as_list()
        [[1, 2, [1, 2], 1, ''], [1, 3, [2, 3], 2, None]]
        >>> dt.as_list(key_list=['a', 'b', 'd.f'])
        [[1, 2, ''], [1, 3, None]]

        """
        key_list = sorted(self._keys) if key_list is None else key_list
        name_list = self._name if name_list is None else name_list
        data = [
            [self._table.get(self.parse_key(key), {}).get(name, deficit)
             for key in key_list]
            for name in name_list]
        return data

    def get_by_name(self, name):
        return self._original[name]

    def get_nested_fnmatch(self, name, key_list, *args, **kwds):
        data = []
        for key in key_list:
            data += get_nested_fnmatch(
                self.get_by_name(name), key, *args, **kwds)
        return data

    @staticmethod
    def _identical(iterative):
        """
        Test if values in given dictionary are identical

        >>> DictTable._identical(['x', 'x', 'x'])
        True
        >>> DictTable._identical(['x', 'x', 'o'])
        False
        >>> DictTable._identical(['1', '1', 1])
        False
        >>> DictTable._identical([True, True])
        True
        >>> DictTable._identical([True, 'True'])
        False
        >>> DictTable._identical([[1, 2], [1, 2]])  # works with list
        True
        >>> DictTable._identical([[1, 2], [1, '2']])
        False
        >>> DictTable._identical([{'a': 1}, {'a': 1}])  # works with dict
        True
        >>> DictTable._identical([{'a': 1}, {'a': '1'}])
        False

        .. note::

           This is not equivalent to ``len(set(iterative)) == 1``,
           because `set` cannot take unhashable type.

        """
        # use repr(val) because val can be "unhashable type" such as list
        return len(set([repr(val) for val in iterative])) == 1



    @staticmethod
    def _filter_by_re_list(keyiter, include=None, exclude=None):
        """
        Filter for DictTable._table (helper for DictTable.dict)

        Parameters
        ----------
        keyiter : iterative of iterative of str
            * `keyiter` is list (iterative) of `key`
            * `key` is list (iterative) of `k`
            * `k` is a str
        include : iterative of RE string
            If any `k` in `key` matches this regular expression pattern,
            `key` will be included.
        exclude : iterative of RE string
            If any `k` in `key` matches this regular expression pattern,
            `key` will be excluded.

        Examples
        --------
        >>> keyiter = [('aaa',), ('bbb',), ('abc',), ('111',)]
        >>> def f(*args, **kwds):
        ...     return list(DictTable._filter_by_re_list(*args, **kwds))
        ...
        >>> f(keyiter)
        [('aaa',), ('bbb',), ('abc',), ('111',)]
        >>> f(keyiter, include=['a+$'])
        [('aaa',)]
        >>> f(keyiter, include=['a.*', 'b.*'])
        [('aaa',), ('bbb',), ('abc',)]
        >>> f(keyiter, exclude=['a.*', 'b.*'])
        [('111',)]
        >>> f(keyiter, include=['a.*', 'b.*'], exclude=['a+$'])
        [('bbb',), ('abc',)]

        """
        if include is None:
            include = []
        if exclude is None:
            exclude = []
        # compile include/exclude
        re_include = [re.compile(inc) for inc in include]
        re_exclude = [re.compile(exc) for exc in exclude]

        for key in keyiter:
            include_key = not include or any(
                inc.match(k) for inc in re_include for k in key)
            exclude_key = any(
                exc.match(k) for exc in re_exclude for k in key)
            if (include_key and not exclude_key):
                yield key

    def diff(self, include=None, exclude=None):
        """Get 'diff' of stored dict-like objects"""
        diff_key_list = []
        num_name = len(self._name)
        for key in self._filter_by_re_list(self._table, include, exclude):
            val_dict = self._table[key]
            if (num_name != len(val_dict) or
                # some dict doesn't have this key, or
                not self._identical(val_dict.itervalues())
                ):
                diff_key_list.append(key)

        diffdict = {}
        for (i, key) in enumerate(diff_key_list):
            val_dict = self._table[key]
            keystr = self.sep.join([str(k) for k in key])
            diffdict[keystr] = dict(
                (name, val_dict[name])
                for name in self._name if name in val_dict)
        return diffdict

    @staticmethod
    def _getrepr(dct, key, default=''):
        if key in dct:
            return repr(dct[key])
        else:
            return default

    def print_diff(self, include=None, exclude=None):
        diffdict = self.diff(include, exclude)
        if not diffdict:
            return

        sortedkey = sorted(diffdict)
        last = len(sortedkey) - 1
        for (i, keystr) in enumerate(sortedkey):
            print keystr
            for name in self._name:
                val = self._getrepr(diffdict[keystr], name)
                if val == '':
                    print "%s:" % name
                else:
                    print "%s: %s" % (name, val)
            if i != last:
                print

    def print_diff_as_table(self, include=None, exclude=None,
                            deco_border=False, deco_header=False,
                            deco_hlines=False, deco_vlines=False):
        diffdict = self.diff(include, exclude)
        if not diffdict:
            return

        from texttable import Texttable
        table = Texttable()
        deco = 0
        if deco_border: deco |= Texttable.BORDER
        if deco_header: deco |= Texttable.HEADER
        if deco_hlines: deco |= Texttable.HLINES
        if deco_vlines: deco |= Texttable.VLINES
        table.set_deco(deco)

        sortedkey = sorted(diffdict)
        table.add_rows(
            [[''] + self._name] +
            [[keystr] + [self._getrepr(diffdict[keystr], name)
                         for name in self._name]
             for keystr in sortedkey]
            )
        print table.draw()

    @classmethod
    def from_path_list(cls, path_list, name_list=None):
        name_list = path_list if name_list is None else name_list
        dt = cls()
        for (path, name) in zip(path_list, name_list):
            try:
                dt.append(name, load_any(path))
            except ValueError:
                pass
        return dt



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
