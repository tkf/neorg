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

    def __init__(self, data=None):
        # dict of dict. access via self._table[(k1, k2, ...)][name]
        self._table = {}
        # original dict.
        self._original = {}
        # list of name
        self._name = []
        # set of key
        self._keys = set()

        if data is not None:
            for (name, dct) in data.iteritems():
                self.append(name, dct)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self._table == other._table and
                self._name == other._name and
                self._keys == other._keys)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'DictTable(%r)' % self._original

    @property
    def names(self):
        return self._name[:]  # return copy

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

    def key_as_str(self, key):
        if isinstance(key, basestring):
            return key
        else:
            return self.sep.join(key)

    def as_list(self, key_list=None, name_list=None, deficit=None,
                with_key=True, with_name=True, left_top='', as_str=repr):
        """
        Get stored dictionaries as list-of-list

        >>> dt = DictTable()
        >>> dt.append('A', dict(a=1, b=2, c=[1,2], d=dict(e=1, f='')))
        >>> dt.append('B', dict(a=1, b=3, c=[2,3], d=dict(e=2)))
        >>> dt.as_list() #doctest: +NORMALIZE_WHITESPACE
        [['', 'a', 'b', 'c', 'd.e', 'd.f'],
         ['A', '1', '2', '[1, 2]', '1', "''"],
         ['B', '1', '3', '[2, 3]', '2', None]]
        >>> dt.as_list(key_list=['a', 'b', 'd.f'])
        [['', 'a', 'b', 'd.f'], ['A', '1', '2', "''"], ['B', '1', '3', None]]

        """
        key_list = sorted(self._keys) if key_list is None else key_list
        name_list = self._name if name_list is None else name_list
        if with_key:
            first_row = [self.key_as_str(key) for key in key_list]
            if with_name:
                first_row = [left_top] + first_row
        else:
            first_row = []
        notfound = object()  # unique object

        def get(name, key):
            value = self._table.get(
                self.parse_key(key), {}).get(name, notfound)
            if value is notfound:
                return deficit
            return as_str(value)

        data = [first_row]
        for name in name_list:
            if with_name:
                row = [name]
            else:
                row = []
            row += [get(name, key) for key in key_list]
            data.append(row)
        return data

    def _gene_dict(self, key_val_list):
        dct = {}
        for (key, val) in key_val_list:
            key = self.parse_key(key)
            last = len(key) - 1
            subdct = dct
            for (i, k) in enumerate(key):
                if i == last:
                    subdct[k] = val
                else:
                    subdct = subdct.setdefault(k, {})
        return dct

    def filter_by_fnmatch(self, key_list, *args, **kwds):
        """
        Make new DictTable filtered by fnmatch given fnmatch patterns
        """
        newdt = DictTable()
        def filtered(name):
            return self._gene_dict(
                self.get_nested_fnmatch(name, key_list, *args, **kwds))
        for name in self._name:
            newdt.append(name, filtered(name))
        return newdt

    def get_by_name(self, name):
        return self._original[name]

    def get_nested_fnmatch(self, name, key_list, *args, **kwds):
        data = []
        for key in key_list:
            data += get_nested_fnmatch(
                self.get_by_name(name), key, *args, **kwds)
        return data

    def sort_names_by_values(self, key_list, reverse=False):
        """
        Sort stored names given list of key

        >>> dt = DictTable()
        >>> dt.append('A', dict(int=1, float=3.0, str="y", mix=1))
        >>> dt.append('B', dict(int=2, float=2.0, str="x", mix="b"))
        >>> dt.append('C', dict(int=3, float=-1.0, str="z"))
        >>> dt.sort_names_by_values(['int'])
        >>> dt.names
        ['A', 'B', 'C']
        >>> dt.sort_names_by_values(['float'])
        >>> dt.names
        ['C', 'B', 'A']
        >>> dt.sort_names_by_values(['str'])
        >>> dt.names
        ['B', 'A', 'C']
        >>> dt.sort_names_by_values(['mix'])
        >>> dt.names
        ['A', 'B', 'C']
        >>> dt2 = DictTable()
        >>> dt2.append('A', dict(int=0, float=3.0))
        >>> dt2.append('B', dict(int=0, float=2.0))
        >>> dt2.append('C', dict(int=0, float=-1.0))
        >>> dt2.sort_names_by_values(['int', 'float'])
        >>> dt2.names
        ['C', 'B', 'A']

        """
        # use last ASCII character to say deficit value should come at last.
        # maybe i should change this later using the `cmp` function.
        deficit = chr(255)
        def key(name):
            vals = []
            for keystr in key_list:
                keytuple = self.parse_key(keystr)
                vals.append(self._table.get(keytuple, {}).get(name, deficit))
            return tuple(vals)
        self._name.sort(key=key, reverse=reverse)

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
                dt.append(name, cls.load_any(path))
            except ValueError:
                pass
        return dt

    load_any = staticmethod(load_any)

    def grid_dict(self, key_list):
        gd = GridDict(len(key_list))
        for name in self.names:
            value = tuple(
                self._table.get(self.parse_key(key), {}).get(name)
                for key in key_list)
            gd.append(value, name)
        return gd


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


class GridDict(object):
    """
    Dict-like object which has key on "grid"

    >>> gd = GridDict(2)  # create 2dim grid
    >>> gd.append((0, 0), '0.0')
    >>> gd.append((1, 1), '1.1')
    >>> gd.append((0, 2), '0.2')
    >>> gd.append((0, 2), 'another 0.2')
    >>> gd[0][0]
    ['0.0']
    >>> gd[0, 0]
    ['0.0']
    >>> gd[0, 2]
    ['0.2', 'another 0.2']
    >>> gd[0, 1]  # if you are on the grid, you always get a list
    []
    >>> gd[0, 3]  # if you are outside the grid, you get:
    Traceback (most recent call last):
        ...
    KeyError: "'(0, 3)' is not the grid_key"
    >>> gd.sorted_axes()
    [[0, 1], [0, 1, 2]]
    >>> gd0 = gd[0]
    >>> gd0.sorted_axes()  # child GridDict shares data and axes
    [[0, 1, 2]]

    """

    def __init__(self, num):
        if not num > 0:
            raise ValueError('num (=%d) must be larger than 0' % num)
        self.num = num
        self.axes = [set() for dummy in range(num)]
        self._data = {}

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if not self.has_grid_key(key):
                raise KeyError("'%r' is not the grid_key" % (key,))
            return self.get(key)
        else:
            if key not in self.axes[0]:
                raise KeyError("'%r' is not the first key" % (key,))
            return self._data_get(key)

    def append(self, key, val):
        if not (isinstance(key, tuple) and len(key) == self.num):
            raise KeyError('key must be a tuple with length=%d'
                           % self.num)
        self.get(key).append(val)

    def get(self, key):
        val = self
        for (i, k) in enumerate(key):
            val = val._data_get(k)
            self.axes[i].add(k)
        return val

    def _data_get(self, k):
        if k in self._data:
            return self._data[k]
        else:
            return self._data.setdefault(k, self.new_child())

    def new_child(self):
        newnum = self.num - 1
        child = self.new(newnum)
        if newnum > 0:
            child.axes = self.axes[1:]
        return child

    @classmethod
    def new(cls, num):
        if num > 0:
            return cls(num)
        else:
            return []

    def has_grid_key(self, key):
        try:
            return all(k in self.axes[i] for (i, k) in enumerate(key))
        except TypeError:
            return False

    def sorted_axes(self, reverse={}):
        if reverse == 'all':
            return [sorted(a, reverse=True) for a in self.axes]
        else:
            return [sorted(a, reverse=reverse.get(i, False))
                    for (i, a) in enumerate(self.axes)]
